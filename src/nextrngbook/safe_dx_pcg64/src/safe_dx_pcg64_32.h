/*
 * The C source and associated header file are part of the Python package
 * NextRNGBook.
 *
 * This module implements the 32-bit eSAFE-DX-PCG64 random number generator
 * is implemented as a multi-output extension of the SAFE generator construction.
 *
 * The generator combines two baseline random number generators:
 *
 *       1. a 32-bit DX-k-s generator, where s = 1 or s = 2; and
 *       2. PCG64.
 *
 * The SAFE construction is described in:
 *
 *       Secure and Fast Encryption (SAFE) with Classical Random Number
 *       Generators, Deng, Lih-Yuan, Shiau, Jeng-Jong H., Lu, Henry Horng-Shing,
 *       and Bowman, Douglas, ACM Transactions on Mathematical Software, 2018.
 *       Available at: https://dl.acm.org/doi/10.1145/3212673
 *
 * The DX component uses the optimized DX fast-update implementation provided
 * by NextRNGBook.
 *
 * Portions of the PCG64 state-transition, 128-bit arithmetic, output, and
 * seeding routines were adapted from the corresponding implementations in
 * NumPy and randomgen:
 *
 *       NumPy: https://github.com/numpy/numpy/tree/main/numpy/random/src/pcg64
 *
 *       randomgen: https://github.com/bashtage/randomgen/tree/main/randomgen/src/pcg64
 *
 * The adapted PCG64 code remains subject to the copyright and license
 * terms of its original authors and source projects.
 *
 * The integration of the DX and PCG64 components, including the eSAFE state
 * organization, burn-in procedure, shuffle-table initialization, mutual
 * shuffling, output transformations, and buffered multi-output mechanism,
 * was implemented by Meng-Xun Cai in 2026.
 *
 * The eSAFE-DX-PCG64 implementation was carried out with theoretical guidance
 * and suggestions from
 * Prof. Lih-Yuan Deng <lihdeng@memphis.edu>,
 * Prof. Henry Horng-Shing Lu <henryhslu@nycu.edu.tw>, and
 * Prof. Ching-Chi Yang <cyang3@memphis.edu>.
 *
 * Copyright (c) 2026 Meng-Xun Cai <rr991370@gmail.com>
 *
 * The original NextRNGBook code and modifications are licensed under the
 * MIT License. See the LICENSE file in the project root for more information.
 */

#ifndef SAFE_DX_PCG64_32_H
#define SAFE_DX_PCG64_32_H

#include <stdint.h>


/*
 * Compiler portability helpers.
 *
 * ESAFE_FORCEINLINE requests aggressive inlining for performance-critical
 * state-transition and output functions.
 *
 * ESAFE_RESTRICT indicates that the referenced shuffle tables do not alias
 * other pointers used within the same function.
 *
 * esafe_rotr32() and esafe_rotr64() provide compiler-independent right
 * rotations. Rotation counts are interpreted modulo 32 and 64,
 * respectively.
 */


#if defined(_MSC_VER)
  #include <intrin.h>
  #define ESAFE_FORCEINLINE __forceinline
  #define ESAFE_RESTRICT __restrict
  static ESAFE_FORCEINLINE uint32_t esafe_rotr32(uint32_t x, unsigned int r) { return _rotr(x, (int)r); }
  static ESAFE_FORCEINLINE uint64_t esafe_rotr64(uint64_t x, unsigned int r) { return _rotr64(x, (int)r); }
#elif defined(__clang__) || defined(__GNUC__)
  #define ESAFE_FORCEINLINE inline __attribute__((always_inline))
  #define ESAFE_RESTRICT __restrict__
  static ESAFE_FORCEINLINE uint32_t esafe_rotr32(uint32_t x, unsigned int r) { return (x >> r) | (x << ((32u - r) & 31u)); }
  static ESAFE_FORCEINLINE uint64_t esafe_rotr64(uint64_t x, unsigned int r) { return (x >> r) | (x << ((-r) & 63u)); }
#else
  #define ESAFE_FORCEINLINE inline
  #define ESAFE_RESTRICT
  static ESAFE_FORCEINLINE uint32_t esafe_rotr32(uint32_t x, unsigned int r) { return (x >> r) | (x << ((32u - r) & 31u)); }
  static ESAFE_FORCEINLINE uint64_t esafe_rotr64(uint64_t x, unsigned int r) { return (x >> r) | (x << ((-r) & 63u)); }
#endif

#if defined(_WIN32) && !defined(__MINGW32__)
#define inline __forceinline
#endif

#define KK 50873  // upper limit of kk (KK should be <= 2^31 - 1 in this code)
#define TWO_POWER_32 (1ULL << 32)
#define SAFE_MAX_TABLE_SIZE 512  // upper limit of shuffle table size (must be power-of-two)
#define SAFE_CAPACITY 8  // Maximum number of entries in each mutual-shuffling table
#define SAFE_MAX SAFE_CAPACITY // Maximum number of buffered outputs produced by one eSAFE update

// #define PCG64_MULT_HIGH 0x2360ed051fc65da4ULL
// #define PCG64_MULT_LOW  0x4385df649fccf645ULL

// the state information for the DX-k-s generator
typedef struct s_dx_k_s_32_state {
    uint32_t XX[KK];  // states with at most KK terms
    int II;           // running index
    uint32_t bb;      // multiplier
    uint32_t pp;      // modulus
    int kk;           // the order of recurrence (kk <= KK)
    double hh;        // hh = 1 / (2 * pp)
} dx_k_s_32_state;

// the state information for the PCG64 generator
typedef struct s_pcg64_state {
    uint64_t state_high; // high 64 bits of the 128-bit state
    uint64_t state_low;  // low 64 bits of the 128-bit state
    uint64_t inc_high;   // high 64 bits of the 128-bit increment
    uint64_t inc_low;    // low 64 bits of the 128-bit increment
    uint64_t mult_high;  // high 64 bits of the 128-bit multiplier
    uint64_t mult_low;   // low 64 bits of the 128-bit multiplier
} pcg64_state;

// the state information for the eSAFE-DX-PCG64 generator
typedef struct s_esafe_dx_pcg64_state {
    dx_k_s_32_state dx;                     // DX-k-s generator state
    pcg64_state pcg64;                      // PCG64 generator state
    uint32_t table_x[SAFE_MAX_TABLE_SIZE];  // shuffle table for DX outputs
    uint32_t table_y[SAFE_MAX_TABLE_SIZE];  // shuffle table for PCG64 outputs
    int table_size;                         // size of the shuffle tables (must be power-of-two)
    int burn_in;                            // number of initial outputs to discard for burn-in  
    int safe_max;                           // maximum number of buffered outputs produced by one eSAFE update (<= SAFE_CAPACITY)
    uint32_t SAFE_T[SAFE_CAPACITY];         // buffered outputs produced by one eSAFE update
    int SAFE_II;                            // running index for the buffered outputs
} esafe_dx_pcg64_state;


typedef struct s_pcg128_parts {
    uint64_t high;
    uint64_t low;
} pcg128_parts;


// DX generator update functions
void dx_k_1_fast(dx_k_s_32_state *state);
void dx_k_2_fast(dx_k_s_32_state *state);

// PCG64 generator functions
void pcg64_srandom_r(
    pcg64_state *state, 
    uint64_t *initstate, 
    uint64_t *initseq, 
    uint32_t multiplier_id
);
uint64_t pcg64_random_r(pcg64_state *state);


static inline uint32_t MOD_fast(uint64_t z, uint32_t p) {
    z = ((z & p) + (z >> 31)) & p;
    return (uint32_t)z;
}

// rotation function
static ESAFE_FORCEINLINE uint32_t rot_r(uint32_t x, int n) { return esafe_rotr32(x, (unsigned int)n); }


/*
 * PCG64 128-bit arithmetic and output helpers.
 *
 * The PCG64 state is represented using two 64-bit words so that the
 * implementation does not depend on native 128-bit integer support.
 *
 * These routines implement:
 *     - 128-bit addition with carry;
 *     - construction of an odd LCG increment;
 *     - portable 64-by-64 multiplication producing a 128-bit result;
 *     - multiplication by the seed-derived PCG64 128-bit multiplier;
 *     - the XSL-RR output transformation; and
 *     - one complete PCG64 state transition.
 *
 * The PCG64-derived routines retain the original source project's
 * copyright and license terms.
 */


static ESAFE_FORCEINLINE void pcg128_add_assign(pcg128_parts *a, pcg128_parts b) {
    uint64_t old_low = a->low;
    a->low += b.low;
    a->high += b.high + (a->low < old_low);
}

static ESAFE_FORCEINLINE pcg128_parts pcg128_shl1_or1(pcg128_parts x) {
    pcg128_parts out;
    out.high = (x.high << 1u) | (x.low >> 63u);
    out.low = (x.low << 1u) | 1u;
    return out;
}

static ESAFE_FORCEINLINE void esafe_mul64(uint64_t x, uint64_t y, uint64_t *high, uint64_t *low) {
#if defined(__SIZEOF_INT128__)
    __uint128_t product = (__uint128_t)x * (__uint128_t)y;
    *low = (uint64_t)product;
    *high = (uint64_t)(product >> 64);
#elif defined(_MSC_VER) && defined(_M_X64)
    *low = _umul128(x, y, high);
#else
    uint64_t x0 = x & 0xffffffffULL;
    uint64_t x1 = x >> 32;
    uint64_t y0 = y & 0xffffffffULL;
    uint64_t y1 = y >> 32;
    uint64_t w0 = x0 * y0;
    uint64_t t = x1 * y0 + (w0 >> 32);
    uint64_t w1 = t & 0xffffffffULL;
    uint64_t w2 = t >> 32;
    w1 += x0 * y1;
    *low = x * y;
    *high = x1 * y1 + w2 + (w1 >> 32);
#endif
}

// static ESAFE_FORCEINLINE pcg128_parts pcg128_mul_const(pcg128_parts a) {
//     pcg128_parts out;
//     uint64_t product_high;
//     esafe_mul64(a.low, PCG64_MULT_LOW, &product_high, &out.low);
//     out.high = product_high + a.high * PCG64_MULT_LOW + a.low * PCG64_MULT_HIGH;
//     return out;
// }

static ESAFE_FORCEINLINE pcg128_parts pcg128_mul(pcg128_parts a, pcg128_parts b) {
    pcg128_parts out;
    uint64_t product_high;

    esafe_mul64(a.low, b.low, &product_high, &out.low);
    out.high = product_high + a.high * b.low + a.low * b.high;
    return out;
}

static ESAFE_FORCEINLINE uint64_t pcg64_output_xsl_rr(pcg128_parts state) {
    uint64_t xsl = state.high ^ state.low;
    unsigned int rot = (unsigned int)(state.high >> 58u);
    return esafe_rotr64(xsl, rot);
}

static ESAFE_FORCEINLINE uint64_t pcg64_step_inline(pcg64_state *state) {
    pcg128_parts oldstate = {state->state_high, state->state_low};
    pcg128_parts multiplier = {state->mult_high, state->mult_low};
    pcg128_parts next = pcg128_mul(oldstate, multiplier);
    pcg128_parts inc = {state->inc_high, state->inc_low};
    pcg128_add_assign(&next, inc);
    state->state_high = next.high;
    state->state_low = next.low;
    return pcg64_output_xsl_rr(oldstate);
}


/*
 * Refill the eSAFE output buffer from one DX output and one PCG64 output.
 *
 * x0:
 *     Current 32-bit DX output.
 *
 * y0:
 *     Current 64-bit PCG64 output. Its upper and lower 32-bit words are
 *     denoted by y0_hi and y0_lo.
 *
 * Mutual shuffling:
 *     Y0 = y0_lo & (table_size - 1) selects an entry in table_x.
 *     X0 = x0    & (table_size - 1) selects an entry in table_y.
 *
 *     vv = table_x[Y0], followed by table_x[Y0] = x0.
 *     ww = table_y[X0], followed by table_y[X0] = y0_lo.
 *
 * Output values are formed by adding rotated 32-bit words. Unsigned
 * 32-bit overflow implements reduction modulo 2^32.
 *
 * Preconditions:
 *     - table_size is a positive power of two;
 *     - table_size <= SAFE_MAX_TABLE_SIZE;
 *     - safe_max matches the selected refill function.
 */


// produce one buffered output from the current eSAFE internal values
static ESAFE_FORCEINLINE void esafe_dx_pcg64_refill_safe_t_1b(esafe_dx_pcg64_state *state, uint32_t x0, uint64_t y0) {
    uint32_t y0_hi = (uint32_t)(y0 >> 32);
    uint32_t y0_lo = (uint32_t)y0;
    uint32_t mask = (uint32_t)(state->table_size - 1);
    uint32_t *ESAFE_RESTRICT tx = state->table_x;
    uint32_t *ESAFE_RESTRICT ty = state->table_y;

    uint32_t Y0 = y0_lo & mask;
    uint32_t X0 = x0 & mask;
    uint32_t ww = ty[X0];
    tx[Y0] = x0;
    ty[X0] = y0_lo;

    state->SAFE_T[0] = rot_r(x0, 25) + rot_r(y0_hi, 23) + rot_r(ww, 10);
}


// produce four buffered outputs from the current eSAFE internal values
static ESAFE_FORCEINLINE void esafe_dx_pcg64_refill_safe_t_4b(esafe_dx_pcg64_state *state, uint32_t x0, uint64_t y0) {
    uint32_t y0_hi = (uint32_t)(y0 >> 32);
    uint32_t y0_lo = (uint32_t)y0;
    uint32_t mask = (uint32_t)(state->table_size - 1);
    uint32_t *ESAFE_RESTRICT tx = state->table_x;
    uint32_t *ESAFE_RESTRICT ty = state->table_y;

    uint32_t Y0 = y0_lo & mask;
    uint32_t X0 = x0 & mask;
    uint32_t vv = tx[Y0]; tx[Y0] = x0;
    uint32_t ww = ty[X0]; ty[X0] = y0_lo;

    state->SAFE_T[0] = rot_r(x0,    25) + rot_r(y0_hi, 23) + rot_r(ww, 10);
    state->SAFE_T[1] = rot_r(x0,    15) + rot_r(y0_lo, 13) + rot_r(vv, 22);
    state->SAFE_T[2] = rot_r(x0,    11) + rot_r(vv,     9) + rot_r(ww,  5);
    state->SAFE_T[3] = rot_r(y0_lo,  7) + rot_r(vv,    29) + rot_r(ww, 25);
}


// produce eight buffered outputs from the current eSAFE internal values
static ESAFE_FORCEINLINE void esafe_dx_pcg64_refill_safe_t_8b(esafe_dx_pcg64_state *state, uint32_t x0, uint64_t y0) {
    uint32_t y0_hi = (uint32_t)(y0 >> 32);
    uint32_t y0_lo = (uint32_t)y0;
    uint32_t mask = (uint32_t)(state->table_size - 1);
    uint32_t *ESAFE_RESTRICT tx = state->table_x;
    uint32_t *ESAFE_RESTRICT ty = state->table_y;

    uint32_t Y0 = y0_lo & mask;
    uint32_t X0 = x0 & mask;
    uint32_t vv = tx[Y0]; tx[Y0] = x0;
    uint32_t ww = ty[X0]; ty[X0] = y0_lo;

    state->SAFE_T[0] = rot_r(x0,    25) + rot_r(y0_hi, 23) + rot_r(ww, 10);
    state->SAFE_T[1] = rot_r(x0,    15) + rot_r(y0_lo, 13) + rot_r(vv, 22);
    state->SAFE_T[2] = rot_r(x0,    11) + rot_r(vv,     9) + rot_r(ww,  5);
    state->SAFE_T[3] = rot_r(y0_lo,  7) + rot_r(vv,    29) + rot_r(ww, 25);
    state->SAFE_T[4] = rot_r(x0,    19) + rot_r(y0_lo,  6) + rot_r(ww, 14);
    state->SAFE_T[5] = rot_r(x0,    19) + rot_r(y0_hi,  2) + rot_r(vv, 24);
    state->SAFE_T[6] = rot_r(y0_lo, 28) + rot_r(vv,    18) + rot_r(ww, 30);
    state->SAFE_T[7] = rot_r(y0_hi, 26) + rot_r(vv,    31) + rot_r(ww,  1);
}

static ESAFE_FORCEINLINE void esafe_dx_pcg64_refill_safe_t(esafe_dx_pcg64_state *state, uint32_t x0, uint64_t y0) {
    if (state->safe_max == 1) {
        esafe_dx_pcg64_refill_safe_t_1b(state, x0, y0);
    } else if (state->safe_max == 8) {
        esafe_dx_pcg64_refill_safe_t_8b(state, x0, y0);
    } else {
        esafe_dx_pcg64_refill_safe_t_4b(state, x0, y0);
    }
}

static ESAFE_FORCEINLINE uint32_t dx_k_1_fast_step_inline(dx_k_s_32_state *dx) {
    int II0 = dx->II;
    int II = II0 + 1;
    if (II == dx->kk) II = 0;
    dx->II = II;

    uint64_t z = (uint64_t)dx->bb * (uint64_t)dx->XX[II] + (uint64_t)dx->XX[II0];
    uint32_t p = dx->pp;
    z = ((z & p) + (z >> 31)) & p;
    dx->XX[II] = (uint32_t)z;
    return dx->XX[II];
}

static ESAFE_FORCEINLINE uint32_t dx_k_2_fast_step_inline(dx_k_s_32_state *dx) {
    int II0 = dx->II;
    int II = II0 + 1;
    if (II == dx->kk) II = 0;
    dx->II = II;

    uint64_t z = (uint64_t)dx->bb * (uint64_t)((uint64_t)dx->XX[II] + (uint64_t)dx->XX[II0]);
    uint32_t p = dx->pp;
    z = ((z & p) + (z >> 31)) & p;
    dx->XX[II] = (uint32_t)z;
    return dx->XX[II];
}


static inline uint32_t dx_k_1_fast_next32(dx_k_s_32_state *state) {

    dx_k_1_fast(state); // update the DX-k-1 state
    
    return (uint32_t)state->XX[state->II];
}

static inline uint32_t dx_k_2_fast_next32(dx_k_s_32_state *state) {
    
    dx_k_2_fast(state); // update the DX-k-2 state
    
    return (uint32_t)state->XX[state->II];
}

void esafe_dx_s1_pcg64_fast_init(esafe_dx_pcg64_state *state);
void esafe_dx_s2_pcg64_fast_init(esafe_dx_pcg64_state *state);


// for SAFE-DX-PCG64, eSAFE-DX-PCG64-M4, and eSAFE-DX-PCG64-M8 (use DX-k-1 generator)
// generate a 32-bit random number
static ESAFE_FORCEINLINE uint32_t esafe_dx_s1_pcg64_fast_next32(esafe_dx_pcg64_state *state) {
    int ii = state->SAFE_II + 1;
    if (ii >= state->safe_max) {
        ii = 0;

        uint32_t x0 = dx_k_1_fast_step_inline(&state->dx);
        uint64_t y0 = pcg64_step_inline(&state->pcg64);
        esafe_dx_pcg64_refill_safe_t(state, x0, y0);
    }

    state->SAFE_II = ii;
    return state->SAFE_T[ii];
}

// generate a 64 bit random number (combine two 32 bit random numbers)
static inline uint64_t esafe_dx_s1_pcg64_fast_next64(esafe_dx_pcg64_state *state) {
    return (uint64_t)esafe_dx_s1_pcg64_fast_next32(state) << 32 |
           esafe_dx_s1_pcg64_fast_next32(state);
}

// generate a double in (0, 1)
static inline double esafe_dx_s1_pcg64_fast_next_double(esafe_dx_pcg64_state *state) {
    return (double)esafe_dx_s1_pcg64_fast_next32(state) / (double)TWO_POWER_32;
}


// for SAFE-DX-PCG64, eSAFE-DX-PCG64-M4, and eSAFE-DX-PCG64-M8 (use DX-k-2 generator)
// generate a 32-bit random number
static ESAFE_FORCEINLINE uint32_t esafe_dx_s2_pcg64_fast_next32(esafe_dx_pcg64_state *state) {
    int ii = state->SAFE_II + 1;
    if (ii >= state->safe_max) {
        ii = 0;

        uint32_t x0 = dx_k_2_fast_step_inline(&state->dx);
        uint64_t y0 = pcg64_step_inline(&state->pcg64);
        esafe_dx_pcg64_refill_safe_t(state, x0, y0);
    }

    state->SAFE_II = ii;
    return state->SAFE_T[ii];
}

// generate a 64 bit random number (combine two 32 bit random numbers)
static inline uint64_t esafe_dx_s2_pcg64_fast_next64(esafe_dx_pcg64_state *state) {
    return (uint64_t)esafe_dx_s2_pcg64_fast_next32(state) << 32 |
           esafe_dx_s2_pcg64_fast_next32(state);
}

// generate a double in (0, 1)
static inline double esafe_dx_s2_pcg64_fast_next_double(esafe_dx_pcg64_state *state) {
    return (double)esafe_dx_s2_pcg64_fast_next32(state) / (double)TWO_POWER_32;
}


#endif
