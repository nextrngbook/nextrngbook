# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2025 chintunglin

"""
NextRNGBook is a random number generator (RNG) package compatible with NumPy.
It currently includes an implementation of the DX generator for random number
generation, with plans to introduce additional generators in the future.

**Subpackages:**

- [`dx_generator`](dx_generator.md): Implements the DX algorithm for random number generation.
    - `DX`: The recommended faster 32-bit DX generator with fixed
            ``p = 2^31 - 1``.
    - `DX32`: The general 32-bit DX generator corresponding to the previous
            ``create_dx()`` API.

"""

from . import dx_generator