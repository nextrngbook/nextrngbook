/*
 * The C source and associated header file are part of the Python package
 * NextRNGBook.
 *
 * This module implements the 32-bit eSAFE-DX-PCG64 random number generator
 * is implemented as a multi-output extension of the SAFE generator construction.
 *
 * The generator combines two baseline random number generators:
 *
 *        1. a 32-bit DX-k-s generator, where s = 1 or s = 2; and
 *        2. PCG64.
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



#include "safe_dx_pcg64_32.h"
#include <stdint.h>


void dx_k_1_fast(dx_k_s_32_state *state) {

    int II0 = state->II;

    // wrap around running index
    if (++state->II == state->kk) {
        state->II = 0;
    }

    uint64_t temp_state = state->bb * (uint64_t)state->XX[state->II] + state->XX[II0];
    state->XX[state->II] = (uint32_t)MOD_fast(temp_state, state->pp);
}


void dx_k_2_fast(dx_k_s_32_state *state) {

    int II0 = state->II;

    // wrap around running index
    if (++state->II == state->kk) {
        state->II = 0;
    }

    uint64_t temp_state = state->bb * (uint64_t)((uint64_t)state->XX[state->II] + state->XX[II0]);
    state->XX[state->II] = (uint32_t)MOD_fast(temp_state, state->pp);
}


uint64_t pcg64_random_r(pcg64_state *state) {

    return pcg64_step_inline(state);
}


void pcg64_srandom_r(pcg64_state *state, uint64_t *initstate, uint64_t *initseq, uint32_t multiplier_id) {
    pcg128_parts init_state = {initstate[0], initstate[1]};
    pcg128_parts init_seq = {initseq[0], initseq[1]};
    pcg128_parts inc = pcg128_shl1_or1(init_seq);

    const uint32_t A = 1664525;
    const uint32_t C = 1013904223;
    const uint32_t mask = (1 << 29) - 1;

    uint32_t q = (A * multiplier_id + C) & mask;

    state->mult_high = 0u;
    state->mult_low = ((uint64_t)q << 3u) | 5ULL;
    state->state_high = 0u;
    state->state_low = 0u;
    state->inc_high = inc.high;
    state->inc_low = inc.low;

    (void)pcg64_random_r(state);

    pcg128_parts seeded = {state->state_high, state->state_low};
    pcg128_add_assign(&seeded, init_state);
    state->state_high = seeded.high;
    state->state_low = seeded.low;

    (void)pcg64_random_r(state);
}


void esafe_dx_s1_pcg64_fast_init(esafe_dx_pcg64_state *state) {

    // Burn-in the DX and PCG64 generators
    for (int i = 0; i < state->burn_in; ++i) {
        dx_k_1_fast_next32(&state->dx);
        pcg64_random_r(&state->pcg64);
    }

    // Fill the shuffle tables with respective outputs from DX and PCG64
    for (int i = 0; i < state->table_size; ++i) {
        state->table_x[i] = dx_k_1_fast_next32(&state->dx);
        state->table_y[i] = (uint32_t)pcg64_random_r(&state->pcg64);
    }

    state->SAFE_II = state->safe_max - 1;
}

void esafe_dx_s2_pcg64_fast_init(esafe_dx_pcg64_state *state) {

    // Burn-in the DX and PCG64 generators
    for (int i = 0; i < state->burn_in; ++i) {
        dx_k_2_fast_next32(&state->dx);
        pcg64_random_r(&state->pcg64);
    }

    // Fill the shuffle tables with respective outputs from DX and PCG64
    for (int i = 0; i < state->table_size; ++i) {
        state->table_x[i] = dx_k_2_fast_next32(&state->dx);
        state->table_y[i] = (uint32_t)pcg64_random_r(&state->pcg64);
    }

    state->SAFE_II = state->safe_max - 1;
}
