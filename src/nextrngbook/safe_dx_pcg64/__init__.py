# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2026 Meng-Xun Cai

"""Provides public interfaces for SAFE-DX-PCG64 and eSAFE-DX-PCG64 generators.

This module provides end-user interfaces for constructing NumPy-compatible
BitGenerator objects that combine a 32-bit DX generator and PCG64 through
mutual shuffling and output transformations.

``SAFE_DX_PCG64()`` produces one output value per internal update.

``eSAFE_DX_PCG64_M4()`` and ``eSAFE_DX_PCG64_M8()`` are multi-output extensions
that produce and buffer four and eight output values per internal update,
respectively.

For each generator, the DX parameter set, shuffle-table size, burn-in
length, and the PCG64 state, increment, and multiplier are derived from the
seed. The shuffle-table size is selected from 32, 64, 128, 256, and 512, while the
burn-in length is selected from 1 through 5.

By default, ``randomize=True`` mixes fresh system entropy and the current time
with the optional user-provided seed. Consequently, repeated calls with the
same seed are not reproducible. Set ``randomize=False`` and provide a fixed
seed when reproducible generator configurations and output sequences are
required.

Examples:
    >>> from nextrngbook.safe_dx_pcg64 import SAFE_DX_PCG64
    >>> SAFE_DX_PCG64()
    Done. SAFE-DX-PCG64 generator combining DX and PCG64. Use print() function for details.

    >>> from nextrngbook.safe_dx_pcg64 import eSAFE_DX_PCG64_M4
    >>> eSAFE_DX_PCG64_M4()
    Done. eSAFE-DX-PCG64-M4 generator combining DX and PCG64. Use print() function for details.

    >>> from nextrngbook.safe_dx_pcg64 import eSAFE_DX_PCG64_M8
    >>> eSAFE_DX_PCG64_M8()
    Done. eSAFE-DX-PCG64-M8 generator combining DX and PCG64. Use print() function for details.


**Functions:**
    
- `SAFE_DX_PCG64(seed=None, randomize=True)`
    Creates a SAFE-DX-PCG64 generator with one output per internal update.

- `eSAFE_DX_PCG64_M4(seed=None, randomize=True)`
    Creates a eSAFE-DX-PCG64 generator with four buffered outputs per internal update.

- `eSAFE_DX_PCG64_M8(seed=None, randomize=True)`
    Creates a eSAFE-DX-PCG64 generator with eight buffered outputs per internal update.

**Type Aliases:**
    
- `SeedType` - Type alias for valid seed input types. Can be `None`, `int`, 
`NDArray[np.integer]`, `SeedSequence`, or a sequence of integers.
"""

from numpy.random import RandomState, SeedSequence
from numpy.typing import NDArray
from typing import Sequence, Type, Union
import numpy as np
import secrets
import time
import warnings

from nextrngbook.dx_generator import get_dx_id_table, get_dx_max_id
from ._safe_dx_pcg64 import (
    _eSAFE_DX_PCG64_M4_Generator,
    _eSAFE_DX_PCG64_M8_Generator,
    _eSAFE_DX_PCG64_Generator,
    _SAFE_DX_PCG64_Generator,
)

__all__ = ["SAFE_DX_PCG64", "eSAFE_DX_PCG64_M4", "eSAFE_DX_PCG64_M8"]

SeedType = Union[None, int, Sequence[int], NDArray[np.integer], SeedSequence]


def _resolve_seed(seed: SeedType = None, randomize: bool = True) -> SeedType:
    """Resolves the seed used to configure and initialize the generator.

    When ``randomize`` is True, fresh system entropy and the current time are
    combined with the optional user-provided seed. Therefore, repeated calls
    with the same seed do not produce the same generator configuration or
    output sequence.

    When ``randomize`` is False, the supplied seed is returned unchanged so
    that it can be used for reproducible initialization. If no seed is
    provided, a warning is issued because the resulting generator will not be
    reproducible.

    Args:
        seed: Seed used to initialize the generator.
        randomize: Whether to mix fresh entropy into the supplied seed.

    Returns:
        The resolved seed used for parameter selection and generator
        initialization.

    Warns:
        UserWarning: If ``randomize`` is False and ``seed`` is None.
    """
    if randomize:
        entropy_sources = [secrets.randbits(128), time.time_ns()]
        if seed is not None:
            entropy_sources.append(seed)
        return SeedSequence(entropy_sources).generate_state(10, dtype=np.uint32)

    if seed is None:
        warnings.warn(
            "`randomize=False` was specified, but `seed` is `None`. "
            "The resulting generator will NOT be reproducible. "
            "Please provide a seed for reproducible results.",
            UserWarning,
        )
    return seed


def _create_general_esafe_dx_pcg64(generator_cls: Type[_eSAFE_DX_PCG64_Generator],
                                  seed: SeedType = None,
                                  randomize: bool = True) -> _eSAFE_DX_PCG64_Generator:
    """Creates a configured SAFE-DX-PCG64 or eSAFE-DX-PCG64 generator.

    The seed is used to select a DX parameter set, a shuffle-table
    size, burn-in length, PCG64 multiplier, and PCG64 increment. 
    The table size is selected from 32, 64, 128,
    256, and 512, and the burn-in length is selected from 1 through 5.

    Args:
        generator_cls: Internal generator class to instantiate.
        seed: Seed used for parameter selection and generator initialization.
        randomize: Whether to mix fresh entropy into the supplied seed.

    Returns:
        An initialized instance of ``generator_cls``.
    """
    final_seed = _resolve_seed(seed, randomize)
    rs = RandomState(final_seed)

    exp = int(rs.randint(5, 10))
    burn_in = int(rs.randint(1, 6))
    dx_id = int(rs.randint(0, get_dx_max_id() + 1))
    table_size = 1 << exp

    target_dx_parameters = get_dx_id_table()[dx_id]
    target_dx_parameters = {
        key: float(value) for key, value in target_dx_parameters.items()
    }

    return generator_cls(
        target_dx_parameters["bb"],
        target_dx_parameters["pp"],
        target_dx_parameters["kk"],
        target_dx_parameters["ss"],
        log10_period=target_dx_parameters["log10(period)"],
        table_size=table_size,
        burn_in=burn_in,
        seed=final_seed
    )


def SAFE_DX_PCG64(seed: SeedType = None, randomize: bool = True) -> _SAFE_DX_PCG64_Generator:
    """Creates a 32-bit SAFE-DX-PCG64 BitGenerator.

    The generator combines a 32-bit DX generator and PCG64 through mutual
    shuffling and output transformations. One output value is produced during
    each internal update.

    The DX parameter set, shuffle-table size, burn-in length, PCG64 multiplier, and PCG64 increment are selected
    internally from the seed.

    Args:
        seed: Seed used for parameter selection and generator initialization.
            If ``randomize`` is False, the same seed reproduces the same
            configuration and output sequence.
        randomize: If True, mix fresh system entropy and the current time with
            the optional seed. If False, use the supplied seed directly for
            reproducible initialization.

    Returns:
        A `_SAFE_DX_PCG64_Generator` BitGenerator object.

    Examples:
        >>> from nextrngbook.safe_dx_pcg64 import SAFE_DX_PCG64
        >>> SAFE_DX_PCG64()
        Done. SAFE-DX-PCG64 generator combining DX and PCG64. Use print() function for details.

    """
    return _create_general_esafe_dx_pcg64(_SAFE_DX_PCG64_Generator, seed=seed, randomize=randomize)


def eSAFE_DX_PCG64_M4(seed: SeedType = None, randomize: bool = True) -> _eSAFE_DX_PCG64_M4_Generator:
    """Creates a 32-bit eSAFE-DX-PCG64-M4 BitGenerator.

    The generator combines a 32-bit DX generator and PCG64 through mutual
    shuffling and output transformations. Four output values are produced and
    buffered during each internal update.

    The DX parameter set, shuffle-table size, burn-in length, PCG64 multiplier, and PCG64 increment are selected
    internally from the seed.

    Args:
        seed: Seed used for parameter selection and generator initialization.
            If ``randomize`` is False, the same seed reproduces the same
            configuration and output sequence.
        randomize: If True, mix fresh system entropy and the current time with
            the optional seed. If False, use the supplied seed directly for
            reproducible initialization.

    Returns:
        A `_eSAFE_DX_PCG64_M4_Generator` BitGenerator object.

    Examples:
        >>> from nextrngbook.safe_dx_pcg64 import eSAFE_DX_PCG64_M4
        >>> eSAFE_DX_PCG64_M4()
        Done. eSAFE-DX-PCG64-M4 generator combining DX and PCG64. Use print() function for details.
    """
    return _create_general_esafe_dx_pcg64(_eSAFE_DX_PCG64_M4_Generator, seed=seed, randomize=randomize)


def eSAFE_DX_PCG64_M8(seed: SeedType = None, randomize: bool = True) -> _eSAFE_DX_PCG64_M8_Generator:
    """Creates a 32-bit eSAFE-DX-PCG64-M8 BitGenerator.

    The generator combines a 32-bit DX generator and PCG64 through mutual
    shuffling and output transformations. Eight output values are produced and
    buffered during each internal update.

    The DX parameter set, shuffle-table size, burn-in length, PCG64 multiplier, and PCG64 increment are selected
    internally from the seed.

    Args:
        seed: Seed used for parameter selection and generator initialization.
            If ``randomize`` is False, the same seed reproduces the same
            configuration and output sequence.
        randomize: If True, mix fresh system entropy and the current time with
            the optional seed. If False, use the supplied seed directly for
            reproducible initialization.

    Returns:
        A `_eSAFE_DX_PCG64_M8_Generator` BitGenerator object.

    Examples:
        >>> from nextrngbook.safe_dx_pcg64 import eSAFE_DX_PCG64_M8
        >>> eSAFE_DX_PCG64_M8()
        Done. eSAFE-DX-PCG64-M8 generator combining DX and PCG64. Use print() function for details.
    """
    return _create_general_esafe_dx_pcg64(_eSAFE_DX_PCG64_M8_Generator, seed=seed, randomize=randomize)
