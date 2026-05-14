# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2025 chintunglin

"""Provides an interface for generating `_DX32Generator` and `_DXGenerator` objects from `dx_id` values.

Provides an end-user interface for generating `_DX32Generator` and `_DXGenerator` objects 
based on `dx_id` values. It also allows users to access the internal table of `dx_id` 
values and their parameters, as well as retrieve the maximum allowed `dx_id`.
 
``DX()`` is the recommended faster 32-bit DX generator. It uses parameter
sets with fixed modulus ``pp = 2^31 - 1`` and dispatches to the optimized
Mersenne modular reduction implementation.

``DX32()`` is the general 32-bit DX generator. It corresponds to the
previously released ``create_dx()`` API and supports the general DX parameter
table.

Both APIs produce 32-bit random integers, but they differ in how the modulus
parameter ``pp`` is handled.

The internal parameter tables are organized such that each `dx_id`
corresponds to a unique set of parameters. The `dx_id` values are assigned
in ascending order based on the `log10(period)` value of the parameters.

Examples:
    >>> from nextrngbook.dx_generator import DX
    >>> DX()
    _DXGenerator(
        bb=522882, pp=2147483647, kk=6, ss=2, log10_period=56.0
    )

    >>> from nextrngbook.dx_generator import DX32
    >>> DX32()
    _DX32Generator(
        bb=32643, pp=2147483587, kk=7, ss=1, log10_period=65.30000305175781
    )

    >>> from nextrngbook import dx_generator
    >>> dx_id_table = dx_generator.get_dx_id_table()
    >>> print(dx_id_table)
    {0: {'kk': '3', 'ss': '1', 'bb': '523697', 'pp': '2147483647', 'log10(period)': '28.0'}, 
     1: {'kk': '3', 'ss': '1', 'bb': '523703', 'pp': '2147483647', 'log10(period)': '28.0'},
     ...}
    >>> max_dx_id = dx_generator.get_dx_max_id()
    >>> print(max_dx_id)
    14601

**Functions:**

- `DX(dx_id, seed=None)` - Returns a `_DXGenerator` object 
    generated from the internal parameters with modulus `pp = 2^31 - 1`.
- `get_dx_id_table()` - Returns the internal table of `dx_id` values 
    and their associated parameters for `DX()`.
- `get_dx_max_id()` - Returns the maximum allowed `dx_id` value for `DX()`.

- `DX32(dx_id, seed=None)` - Returns a `_DX32Generator` object 
    generated from the internal parameters.
- `get_dx32_id_table()` - Returns the internal table of `dx_id` values 
    and their associated parameters for `DX32()`.
- `get_dx32_max_id()` - Returns the maximum allowed `dx_id` value for `DX32()`.

**Type Aliases:**
    
- `SeedType` - Type alias for valid seed input types. Can be `None`, `int`, 
`NDArray[np.integer]`, `SeedSequence`, or a sequence of integers.
"""

from ._dx_generator32 import _DX32Generator, _DXGenerator
import csv
import os
import time
import warnings
import random
import numpy as np
from numpy.typing import NDArray
from numpy.random import SeedSequence
from typing import Union, Sequence

__all__ = [
    "DX", 
    "get_dx_id_table",
    "get_dx_max_id",
    "DX32",
    "get_dx32_id_table",
    "get_dx32_max_id"
]

SeedType = Union[None, int, NDArray[np.integer], SeedSequence, Sequence[int]]

# read parameters
current_dir = os.path.dirname(os.path.abspath(__file__))

# Fast DX table: fixed pp = 2^31 - 1
with open(os.path.join(current_dir, "data", "dx_fast32_parameters.csv"),
          "r", newline="") as dx_fast_csv:
    
    dx_fast_parameter_reader = csv.DictReader(dx_fast_csv, delimiter=",")

    _dx_parameter_table = {
        int(parameter.pop("dx_id")): parameter
        for parameter in dx_fast_parameter_reader
    }

    _dx_id_max = max(_dx_parameter_table.keys())


# General DX32 table: original create_dx() parameter table
with open(os.path.join(current_dir, "data", "dx32_parameters.csv"), 
          "r", newline="") as dx32_csv:
    
    dx32_parameter_reader = csv.DictReader(dx32_csv, delimiter=",")
    
    _dx32_parameter_table = {
        int(parameter.pop("dx_id")): parameter
        for parameter in dx32_parameter_reader
    }
    
    _dx32_id_max = max(_dx32_parameter_table.keys())

del current_dir
del dx_fast_csv
del dx_fast_parameter_reader
del dx32_csv
del dx32_parameter_reader


def DX(dx_id: Union[float, int, None] = None, 
              seed: SeedType = None) -> _DXGenerator:
    """Returns a `_DXGenerator` object generated from the internal parameters.
    
    Retrieves the corresponding parameters from the internal table based on 
    the given `dx_id`, and then returns the corresponding `_DXGenerator` object
    based on these parameters.

    This function is a specialized fast interface for DX generators with
    modulus `pp = 2^31 - 1` so that the optimized Mersenne modular reduction
    path can be used.

    If `dx_id` is None, a valid `dx_id` will be randomly selected based on the
    current time.
    
    If `dx_id` exceeds the maximum allowed value, it is mapped to a fixed value 
    within the valid range, with the specific mapping depending on the given 
    `dx_id`. Regardless of whether `dx_id` is within the valid range or has
    been mapped, the function will always return the generated object with the 
    same parameter settings for the same `dx_id` on every call.
    
    The maximum allowed `dx_id` value can be retrieved using the function 
    `get_dx_max_id`. To inspect the full table of `dx_id` values and their 
    corresponding parameters, use the function `get_dx_id_table`.

    
    Args:
        dx_id: A non-negative integer representing the identifier used to 
            retrieve the corresponding parameters from the internal table.
        seed: A value used to initialize the random number generator. If None, 
            fresh and unpredictable entropy will be retrieved from the OS. 
            If an int or array-like of integers is provided, it will be passed 
            to `SeedSequence` to set the initial state of the BitGenerator. 
            Alternatively, a `SeedSequence` instance can also be used directly. 
            This function uses the same seeding mechanism as NumPy's random system.

    Returns:
        A `_DXGenerator` object using a parameter set from the fast DX table.

    Raises:
        ValueError: If `dx_id` is not an integer-valued number.
        ValueError: If `dx_id` is negative.

    Examples:
        >>> from nextrngbook.dx_generator import DX
        >>> DX()
        _DXGenerator(
            bb=1073738158, pp=2147483647, kk=20897, ss=2, log10_period=195009.296875
        )
        >>> DX(dx_id=300)
        _DXGenerator(
            bb=17301504, pp=2147483647, kk=24, ss=1, log10_period=224.0
        )
    """
    if dx_id is None:
        time_seed = time.time_ns()
        rng = random.Random(time_seed)
        dx_id = rng.randint(0, _dx_id_max)

    if int(dx_id) != dx_id:
        raise ValueError(
            f"Invalid id: {dx_id}. Must be an integer with int or float type "
            "(e.g., 270 or 270.0)."
        )
        
    if dx_id < 0:
        raise ValueError(f"Invalid id: {dx_id}. Must be non-negative.")
        
    if dx_id > _dx_id_max:
        
        rng = random.Random(dx_id)

        rand_id = rng.randint(0, _dx_id_max)
        
        warnings.warn(
            f"dx_id {dx_id} exceeds the maximum value {_dx_id_max}. "
            f"For consistency, the id has been mapped to a fixed value within range: {rand_id}. "
            f"This value may be the same for different out-of-range ids. "
        )
        
        dx_id = rand_id
    
    
    target_dx_parameters = _dx_parameter_table[dx_id]
    
    target_dx_parameters = \
        {key: float(value) for key, value in target_dx_parameters.items()}
    
    return _DXGenerator(target_dx_parameters["bb"], 
                        target_dx_parameters["pp"], 
                        target_dx_parameters["kk"], 
                        target_dx_parameters["ss"], 
                        target_dx_parameters["log10(period)"], 
                        seed)


def get_dx_id_table() -> dict:
    """Returns the internal parameter table for `DX()`.

    The `DX()` table contains parameter sets for the faster DX generator with
    fixed `pp = 2^31 - 1`.

    Returns:
        A dictionary mapping each `dx_id` to its corresponding fast DX
        parameter set.
    """
    return _dx_parameter_table


def get_dx_max_id() -> int:
    """Returns the maximum allowed `dx_id` value for `DX()`."""
    return _dx_id_max


def DX32(dx_id: Union[float, int, None] = None,
                seed: SeedType = None) -> _DX32Generator:
    """Returns a `_DX32Generator` object generated from the internal parameters.

    Retrieves the corresponding parameters from the internal table based on
    the given `dx_id`, and then returns the corresponding `_DX32Generator`
    object based on these parameters.

    If `dx_id` is None, a valid `dx_id` will be randomly selected based on the
    current time.

    If `dx_id` exceeds the maximum allowed value, it is mapped to a fixed value
    within the valid range, with the specific mapping depending on the given
    `dx_id`. Regardless of whether `dx_id` is within the valid range or has
    been mapped, the function will always return the generated object with the
    same parameter settings for the same `dx_id` on every call.

    The maximum allowed `dx_id` value can be retrieved using the function
    `get_dx32_max_id`. To inspect the full table of `dx_id` values and their
    corresponding parameters, use the function `get_dx32_id_table`.

    Args:
        dx_id: A non-negative integer representing the identifier used to
            retrieve the corresponding parameters from the internal table.
        seed: A value used to initialize the random number generator. If None,
            fresh and unpredictable entropy will be retrieved from the OS.
            If an int or array-like of integers is provided, it will be passed
            to `SeedSequence` to set the initial state of the BitGenerator.
            Alternatively, a `SeedSequence` instance can also be used directly.
            This function uses the same seeding mechanism as NumPy's random system.

    Returns:
        A `_DX32Generator` object using a parameter set from the general DX32
        table.

    Raises:
        ValueError: If `dx_id` is not an integer-valued number.
        ValueError: If `dx_id` is negative.
        
    Examples:
        >>> DX32()
        _DX32Generator(
            bb=1016882, pp=2146123787, kk=50873, ss=2, log10_period=474729.3125
        )
        >>> DX32(dx_id=4000)
        _DX32Generator(
            bb=1046381, pp=2147472413, kk=1301, ss=2, log10_period=12140.7998046875
        )
    """
    if dx_id is None:
        time_seed = time.time_ns()
        rng = random.Random(time_seed)
        dx_id = rng.randint(0, _dx32_id_max)

    if int(dx_id) != dx_id:
        raise ValueError(
            f"Invalid id: {dx_id}. Must be an integer with int or float type "
            "(e.g., 270 or 270.0)."
        )
        
    if dx_id < 0:
        raise ValueError(f"Invalid id: {dx_id}. Must be non-negative.")
    
    if dx_id > _dx32_id_max:
        
        rng = random.Random(dx_id)

        rand_id = rng.randint(0, _dx32_id_max)
        
        warnings.warn(
            f"dx_id {dx_id} exceeds the maximum value {_dx32_id_max}. "
            f"For consistency, the id has been mapped to a fixed value within range: {rand_id}. "
            f"This value may be the same for different out-of-range ids. "
        )
        
        dx_id = rand_id
    
    
    target_dx32_parameters = _dx32_parameter_table[dx_id]
    
    target_dx32_parameters = \
        {key: float(value) for key, value in target_dx32_parameters.items()}
    
    return _DX32Generator(target_dx32_parameters["bb"], 
                        target_dx32_parameters["pp"], 
                        target_dx32_parameters["kk"], 
                        target_dx32_parameters["ss"], 
                        target_dx32_parameters["log10(period)"], 
                        seed)


def get_dx32_id_table() -> dict:
    """Returns the internal table of `dx_id` values for `DX32()`.

    The `DX32()` table contains the general 32-bit DX generator parameter sets.
    This corresponds to the parameter table used by the original `create_dx()`
    API.

    Returns:
        A dictionary mapping each `dx_id` to its corresponding general DX32
        parameter set.
    """
    return _dx32_parameter_table


def get_dx32_max_id() -> int:
    """Returns the maximum allowed `dx_id` value for `DX32()`."""
    return _dx32_id_max

