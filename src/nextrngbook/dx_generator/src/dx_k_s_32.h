/*
 * The C source and header files are part of the Python package: NextRNGBook.
 * 
 * The core random number generator (RNG) is the 
 * 32-bit DX-k-s generator (for k <= KK, s = 1, 2 in this file) described in:
 *
 *     A system of high-dimensional, efficient, long-cycle and portable uniform random 
 *     number generators, Deng, Lih-Yuan et al., ACM Trans. Model. Comput. Simul., 2003.
 *     Available at: https://dl.acm.org/doi/10.1145/945511.945513
 * 
 * The implementation is based on the algorithm in the paper, 
 * with some variables and function names following the C code provided, but the code is 
 * independently written for this package.
 * 
 * The implementation was carried out by Chin-Tung Lin, 
 * with theoretical guidance and suggestions from Prof. Lih-Yuan Deng <lihdeng@memphis.edu>, 
 * Prof. Henry Horng-Shing Lu <henryhslu@nycu.edu.tw>, and Prof. Ching-Chi Yang <cyang3@memphis.edu>.
 *
 * The code structure has been adapted to follow the layout and design 
 * patterns of NumPy's and randomgen's RNG implementation, 
 * as described in their source code:
 * 
 *      Numpy: https://github.com/numpy/numpy/tree/main/numpy/random/src
 * 
 *      randomgen: https://github.com/bashtage/randomgen/tree/main/randomgen/src
 * 
 * For further details on the DX generator and related works, visit Prof. Deng's webpage:
 *      https://www.memphis.edu/msci/people/lihdeng.php
 *
 * Copyright (c) 2025 Chin-Tung Lin <tonylin8704@gmail.com>
 * 
 * This code is licensed under the MIT License. 
 * See the LICENSE file in the project root for more information.
 */

/*
 * Update note (DX fast):
 *   The dx_k_*_fast_* functions were updated to provide a fast path for specific DX generator
 *   parameter p = 2^31 - 1. DX fast avoids (%) by using MOD_fast() and returns the
 *   updated state value directly (instead of mapping via double * 2^32).
 *
 * The dx_fast update was carried out by Meng-Xun Cai, 2026,
 * with theoretical guidance and suggestions from Prof. Lih-Yuan Deng <lihdeng@memphis.edu>, 
 * Prof. Henry Horng-Shing Lu <henryhslu@nycu.edu.tw>, and Prof. Ching-Chi Yang <cyang3@memphis.edu>.
 * 
 * Copyright (c) 2026 Meng-Xun Cai <rr991370@gmail.com>
 * 
 * This code is licensed under the MIT License. 
 * See the LICENSE file in the project root for more information.
 */

#ifndef DX_K_S_32_H
#define DX_K_S_32_H


#include <stdint.h> // uint16_t; uint32_t; uint64_t

#if defined(_WIN32) && !defined (__MINGW32__)
#define inline __forceinline
#endif

#define B_LCG 16807     // multiplier of LCG for seeding by dx_k_s_32_set_seed
#define KK 50873       // upper limit of kk (KK should be <= 2^31 - 1 in this code)
#define TWO_POWER_32 (1ULL << 32)
#define TWO_POWER_31 (1ULL << 31)
#define PP 2147483647 


// the state information
typedef struct s_dx_k_s_32_state {
    uint32_t XX[KK];  // states with at most KK terms
    int II;           // running index
    uint32_t bb;      // multiplier
    uint32_t pp;      // modulus
    int kk;           // the order of recurrence (kk <= KK)
    double hh;        // hh = 1 / (2 * pp)
} dx_k_s_32_state;


// seeding
void dx_k_s_32_set_seed(dx_k_s_32_state *state, uint32_t bb, uint32_t pp, int kk, uint32_t seed);


// update functions
void dx_k_1(dx_k_s_32_state *state);
void dx_k_1_fast(dx_k_s_32_state *state);
void dx_k_2(dx_k_s_32_state *state);
void dx_k_2_fast(dx_k_s_32_state *state);

static inline uint32_t MOD_fast(uint64_t z) {return ((((z)&PP)+((z)>>31))&PP); }

// for dx_k_1 generator
// generate a double in (0, 1)
static inline double dx_k_1_next_double(dx_k_s_32_state *state) {
    
    dx_k_1(state); // update the state
    
    return ((double) state->XX[state->II] / state->pp) + state->hh;
}

// generate a 32 bit random number
static inline uint32_t dx_k_1_next32(dx_k_s_32_state *state) {

  return (uint32_t)(dx_k_1_next_double(state) * TWO_POWER_32);
}

// generate a 64 bit random number (combine two 32 bit random numbers)
static inline uint64_t dx_k_1_next64(dx_k_s_32_state *state) {
    
  return (uint64_t) dx_k_1_next32(state) << 32 | 
                    dx_k_1_next32(state);
}


// for pp = 2^31 - 1
// generate a double in (0, 1)
static inline double dx_k_1_fast_next_double(dx_k_s_32_state *state) {

    dx_k_1_fast(state);

    return ((double) state->XX[state->II] / state->pp) + state->hh;
}

// generate a 32 bit random number
static inline uint32_t dx_k_1_fast_next32(dx_k_s_32_state *state) {

  return (uint32_t)(dx_k_1_fast_next_double(state) * TWO_POWER_32);
}

// generate a 64 bit random number (combine two 32 bit random numbers)
static inline uint64_t dx_k_1_fast_next64(dx_k_s_32_state *state) {

  return (uint64_t) dx_k_1_fast_next32(state) << 32 |
                    dx_k_1_fast_next32(state);
}

// for dx_k_2 generator
// generate a double in (0, 1)
static inline double dx_k_2_next_double(dx_k_s_32_state *state) {
  
    dx_k_2(state); // update the state
    
    return ((double) state->XX[state->II] / state->pp) + state->hh;
}

// generate a 32 bit random number
static inline uint32_t dx_k_2_next32(dx_k_s_32_state *state) {

  return (uint32_t)(dx_k_2_next_double(state) * TWO_POWER_32);
}

// generate a 64 bit random number (combine two 32 bit random numbers)
static inline uint64_t dx_k_2_next64(dx_k_s_32_state *state) {
    
  return (uint64_t) dx_k_2_next32(state) << 32 | 
                    dx_k_2_next32(state);
}

// for pp = 2^31 - 1
// generate a double in (0, 1)
static inline double dx_k_2_fast_next_double(dx_k_s_32_state *state) {

    dx_k_2_fast(state);

    return ((double) state->XX[state->II] / state->pp) + state->hh;
}

// generate a 32 bit random number
static inline uint32_t dx_k_2_fast_next32(dx_k_s_32_state *state) {

    return (uint32_t) (dx_k_2_fast_next_double(state) * TWO_POWER_32);
}

// generate a 64 bit random number (combine two 32 bit random numbers)
static inline uint64_t dx_k_2_fast_next64(dx_k_s_32_state *state) {

  return (uint64_t) dx_k_2_fast_next32(state) << 32 |
                    dx_k_2_fast_next32(state);
}

#endif