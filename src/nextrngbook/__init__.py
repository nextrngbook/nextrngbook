# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2025 chintunglin

"""
NextRNGBook is a random number generator (RNG) package compatible with NumPy.
It currently includes an implementation of the DX, SAFE and eSAFE generators for random number
generation, with plans to introduce additional generators in the future.

**Subpackages:**

- [`dx_generator`](dx_generator.md): Implements the DX algorithm for random number generation.
    - `DX`: The recommended faster 32-bit DX generator with fixed
            ``p = 2^31 - 1``.
    - `DX32`: The general 32-bit DX generator corresponding to the previous
            ``create_dx`` API.

- [`safe_dx_pcg64`](safe_dx_pcg64_generator.md): Implements the SAFE-DX-PCG64 generator, which is a combination of the DX generator and PCG64 for enhanced randomness and security.
    - `SAFE_DX_PCG64`: The general SAFE-DX-PCG64 generator.

    - `eSAFE_DX_PCG64_M4`: The 4 outputs version of the SAFE-DX-PCG64 generator.

    - `eSAFE_DX_PCG64_M8`: The 8 outputs version of the SAFE-DX-PCG64 generator.
"""

from . import dx_generator
from . import safe_dx_pcg64