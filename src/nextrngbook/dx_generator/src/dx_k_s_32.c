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


#include "dx_k_s_32.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>     // uint16_t; uint32_t; uint64_t


void dx_k_s_32_set_seed(dx_k_s_32_state *state, uint32_t bb, uint32_t pp, int kk, uint32_t seed){
    
    // specify dx-k-1 or dx-k-2
    state->bb = bb;
    state->pp = pp;
    state->kk = kk;
    state->hh = 1 / (2 * (double) state->pp);
    
    // set initial values
    state->XX[0] = seed % (state->pp - 1) + 1; // reset the first seed to be in {1, ..., pp-1} (seed can't be all zero)
    for (int i = 1; i < state->kk; i++){
        
        // LCG for seeding (with modulus = 2^31 - 1 = 2147483647)
        // % pp to scale XX[i] to the correct range
        state->XX[i] = ((B_LCG * (uint64_t) state->XX[i - 1]) % 2147483647) % state->pp;
    }
    
    // initialize running index
    state->II = state->kk - 1;
}


void dx_k_1(dx_k_s_32_state *state){
    
    int II0 = state->II;
    
    // wrap around running index
    if (++state->II == state->kk) {
        state->II = 0; 
    }
    
    state->XX[state->II] = (uint32_t)((state->bb * (uint64_t) state->XX[state->II] + 
                                                       state->XX[II0]) % state->pp);
    
    return;
}


void dx_k_2(dx_k_s_32_state *state){
    
    int II0 = state->II;
    
    // wrap around running index
    if (++state->II == state->kk) {
        state->II = 0; 
    }
    
    state->XX[state->II] = (uint32_t)((state->bb * (state->XX[state->II] + 
                                        (uint64_t) state->XX[II0])) % state->pp);
    
    return;
}

void dx_k_1_fast(dx_k_s_32_state *state){

    int II0 = state->II;

    // wrap around running index
    if (++state->II == state->kk) {
        state->II = 0;
    }

    state->XX[state->II] = (uint32_t) MOD_fast(state->bb * (uint64_t) state->XX[state->II] + 
                                                       state->XX[II0]);

    return;
}

void dx_k_2_fast(dx_k_s_32_state *state){

    int II0 = state->II;

    // wrap around running index
    if (++state->II == state->kk) {
        state->II = 0;
    }

    state->XX[state->II] = (uint32_t) MOD_fast(state->bb * (state->XX[state->II] +
                                        (uint64_t) state->XX[II0]));

    return;
}


extern inline uint32_t dx_k_1_next32(dx_k_s_32_state *state);
                                     
extern inline uint64_t dx_k_1_next64(dx_k_s_32_state *state);

extern inline double dx_k_1_next_double(dx_k_s_32_state *state);

extern inline uint32_t dx_k_1_fast_next32(dx_k_s_32_state *state);

extern inline uint64_t dx_k_1_fast_next64(dx_k_s_32_state *state);

extern inline double dx_k_1_fast_next_double(dx_k_s_32_state *state);
                                        
extern inline uint32_t dx_k_2_next32(dx_k_s_32_state *state);
                                     
extern inline uint64_t dx_k_2_next64(dx_k_s_32_state *state);

extern inline double dx_k_2_next_double(dx_k_s_32_state *state);

extern inline uint32_t dx_k_2_fast_next32(dx_k_s_32_state *state);

extern inline uint64_t dx_k_2_fast_next64(dx_k_s_32_state *state);

extern inline double dx_k_2_fast_next_double(dx_k_s_32_state *state);