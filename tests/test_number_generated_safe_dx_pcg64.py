# -*- coding: utf-8 -*-

from copy import deepcopy

from nextrngbook.safe_dx_pcg64 import SAFE_DX_PCG64, eSAFE_DX_PCG64_M4, eSAFE_DX_PCG64_M8
import numpy as np
from numpy.random import Generator
import pytest


safe_test_data = [SAFE_DX_PCG64, eSAFE_DX_PCG64_M4, eSAFE_DX_PCG64_M8]
seed_test_data = list(range(10))


def copy_python_state(rng):
    state = deepcopy(rng.state["state"])
    state["DX generator"]["XX"] = state["DX generator"]["XX"].tolist()
    state["table_x"] = state["table_x"].tolist()
    state["table_y"] = state["table_y"].tolist()
    state["SAFE_T"] = state["SAFE_T"].tolist()
    return state


def rotate_right(x, n, bits=32):
    return ((x >> n) | (x << (bits - n))) % (2 ** bits)


def dx_next32(state):
    previous = state["II"]
    state["II"] = (previous + 1) % state["kk"]
    i = state["II"]

    if state["ss"] == 1:
        z = state["bb"] * state["XX"][i] + state["XX"][previous]
    else:
        z = state["bb"] * (state["XX"][i] + state["XX"][previous])

    # Keep the DX fast-update reduction used by this generator.
    state["XX"][i] = ((z & state["pp"]) + (z >> 31)) & state["pp"]
    return state["XX"][i]


def pcg64_next(state):
    old_state = state["state"]
    state["state"] = (old_state * state["multiplier"] + state["inc"]) % (2 ** 128)
    x = (old_state >> 64) ^ (old_state % (2 ** 64))
    return rotate_right(x, old_state >> 122, bits=64)


def safe_refill(state):
    x0 = dx_next32(state["DX generator"])
    y0 = pcg64_next(state["PCG64"])
    y0_hi = y0 >> 32
    y0_lo = y0 % (2 ** 32)

    x_index = x0 % state["table_size"]
    y_index = y0_lo % state["table_size"]
    vv = state["table_x"][y_index]
    ww = state["table_y"][x_index]
    state["table_x"][y_index] = x0
    state["table_y"][x_index] = y0_lo

    outputs = [rotate_right(x0, 25) + rotate_right(y0_hi, 23) + rotate_right(ww, 10)]
    if state["safe_max"] >= 4:
        outputs.extend([
            rotate_right(x0, 15) + rotate_right(y0_lo, 13) + rotate_right(vv, 22),
            rotate_right(x0, 11) + rotate_right(vv, 9) + rotate_right(ww, 5),
            rotate_right(y0_lo, 7) + rotate_right(vv, 29) + rotate_right(ww, 25),
        ])
    if state["safe_max"] == 8:
        outputs.extend([
            rotate_right(x0, 19) + rotate_right(y0_lo, 6) + rotate_right(ww, 14),
            rotate_right(x0, 19) + rotate_right(y0_hi, 2) + rotate_right(vv, 24),
            rotate_right(y0_lo, 28) + rotate_right(vv, 18) + rotate_right(ww, 30),
            rotate_right(y0_hi, 26) + rotate_right(vv, 31) + rotate_right(ww, 1),
        ])
    state["SAFE_T"][:state["safe_max"]] = [x % (2 ** 32) for x in outputs]


def safe_next32(state):
    state["SAFE_II"] += 1
    if state["SAFE_II"] >= state["safe_max"]:
        safe_refill(state)
        state["SAFE_II"] = 0
    return state["SAFE_T"][state["SAFE_II"]]


def safe_next_double(state):
    return safe_next32(state) / (2 ** 32)


# Test all three RNGs with seeds 0–9, starting from the same state as the
# Python version. Compare one million random_raw outputs, followed by
# one million uniform(0, 1) outputs, for exact equality.
@pytest.mark.parametrize("rng_factory", safe_test_data)
@pytest.mark.parametrize("seed", seed_test_data)
def test_safe_dx_pcg64(rng_factory, seed, n_tests_per_fun=1000000):
    rng = rng_factory(seed=seed, randomize=False)
    state = copy_python_state(rng)

    # random_raw testing (next_32)
    package_raw = rng.random_raw(size=n_tests_per_fun)
    python_raw = np.array([safe_next32(state) for _ in range(n_tests_per_fun)])
    assert np.array_equal(package_raw, python_raw), (
        f"random_raw failed. {rng_factory.__name__}. seed={seed}."
    )

    # Continue from the states left by random_raw (next_double).
    package_double = Generator(rng).uniform(0, 1, size=n_tests_per_fun)
    python_double = np.array([safe_next_double(state) for _ in range(n_tests_per_fun)])
    assert np.array_equal(package_double, python_double), (
        f"uniform failed. {rng_factory.__name__}. seed={seed}."
    )


buffer_test_data = (
    [(eSAFE_DX_PCG64_M4, i) for i in range(4)]
    + [(eSAFE_DX_PCG64_M8, i) for i in range(8)]
)


# Test every M4/M8 buffer position with seeds 0–9. Check that random_raw
# and uniform(0, 1) outputs match the Python version exactly, both when
# consuming the remaining buffer and after refilling it.
@pytest.mark.parametrize("rng_factory, buffer_index", buffer_test_data)
@pytest.mark.parametrize("seed", seed_test_data)
def test_safe_dx_pcg64_buffer(rng_factory, buffer_index, seed):
    rng = rng_factory(seed=seed, randomize=False)
    output_size = rng.state["state"]["safe_max"]

    # Advance naturally to each buffer position before copying the state.
    rng.random_raw(size=output_size)
    while rng.state["state"]["SAFE_II"] != buffer_index:
        rng.random_raw()
    state = copy_python_state(rng)
    n_outputs = 2 * output_size + 1

    package_raw = rng.random_raw(size=n_outputs)
    python_raw = np.array([safe_next32(state) for _ in range(n_outputs)])
    assert np.array_equal(package_raw, python_raw), (
        f"random_raw failed. {rng_factory.__name__}. "
        f"seed={seed}. buffer_index={buffer_index}."
    )

    package_double = Generator(rng).uniform(0, 1, size=n_outputs)
    python_double = np.array([safe_next_double(state) for _ in range(n_outputs)])
    assert np.array_equal(package_double, python_double), (
        f"uniform failed. {rng_factory.__name__}. "
        f"seed={seed}. buffer_index={buffer_index}."
    )
