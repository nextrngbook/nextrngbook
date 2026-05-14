# -*- coding: utf-8 -*-

from nextrngbook import dx_generator
from nextrngbook.dx_generator import DX, get_dx_max_id
import numpy as np
import pandas as pd
from numpy.random import Generator, randint
import pytest
import os

# prepare _DXGenerator objects
dx_data_path = os.path.join(os.path.dirname(dx_generator.__file__), "data", "dx_fast32_parameters.csv")
dx_data = pd.read_csv(dx_data_path)
dx_k_1 = dx_data[dx_data["ss"] == 1]
dx_k_2 = dx_data[dx_data["ss"] == 2]

## Default and Boundary Testing (#7)
default_dx = DX()

largest_kk_1 = DX(dx_k_1.iloc[dx_k_1["kk"].argmax()]["dx_id"])
largest_kk_2 = DX(dx_k_2.iloc[dx_k_2["kk"].argmax()]["dx_id"])

largest_bb_1 = DX(dx_k_1.iloc[dx_k_1["bb"].argmax()]["dx_id"])
largest_bb_2 = DX(dx_k_2.iloc[dx_k_2["bb"].argmax()]["dx_id"])

largest_pp_1 = DX(dx_k_1.iloc[dx_k_1["pp"].argmax()]["dx_id"])
largest_pp_2 = DX(dx_k_2.iloc[dx_k_2["pp"].argmax()]["dx_id"])

## Random testing (#3)
current_max_dx_id = get_dx_max_id()
rand_t_1, rand_t_2, rand_t_3 = [DX(randint(0, current_max_dx_id + 1)) for _ in range(3)]

dx_test_data = [default_dx, largest_kk_1, largest_kk_2,
                largest_bb_1, largest_bb_2, largest_pp_1,
                largest_pp_2, rand_t_1, rand_t_2, rand_t_3]

seed_test_data = [randint(1, 1000000000) for _ in range(10)]

dx_num_generated_test_cases = list(zip(dx_test_data, seed_test_data))

def dx_k_s_32_set_seed(bb, pp, kk, seed, ss):

    state = dict()
    
    state["bb"] = bb
    state["pp"] = pp
    state["kk"] = kk
    state["hh"] = 1 / (2 * pp)
    
    xx = np.zeros(kk, int)
    xx[0] = seed % (pp - 1) + 1
    for i in range(1, kk):
        xx[i] = ((16807 * xx[i - 1]) % 2147483647) % pp

    state["xx"] = xx

    state["II"] = kk - 1

    state["ss"] = ss

    return state

def mod_fast(z, PP):

    return ((((z)&PP)+((z)>>31))&PP)


def dx_k_s(state):

    II0 = state["II"] # preserve x_{i - 1}

    # update the running index
    state["II"] += 1 
    if state["II"] == state["kk"]:
        state["II"] = 0

    # update the states
    if state["ss"] == 1:
        state["xx"][state["II"]] = mod_fast(state["bb"] * state["xx"][state["II"]] + state["xx"][II0], state["pp"])

    elif state["ss"] == 2:
        state["xx"][state["II"]] = mod_fast(state["bb"] * (state["xx"][state["II"]] + state["xx"][II0]), state["pp"])


def dx_k_s_next_double(state):

    dx_k_s(state) # update the state

    return (state["xx"][state["II"]] / state["pp"]) + state["hh"]

def dx_k_s_next32(state):

    return int(dx_k_s_next_double(state) * (2 ** 32))

def dx_k_s_next64(state):

    return (dx_k_s_next32(state) << 32) | dx_k_s_next32(state)

@pytest.mark.parametrize("dx_rng, seed", dx_num_generated_test_cases)
def test_dx(dx_rng, seed, n_tests_per_fun=1000000):

    # Python dx setting
    bb = dx_rng.state["state"]["bb"]
    pp = dx_rng.state["state"]["pp"]
    kk = dx_rng.state["state"]["kk"]
    ss = dx_rng.state["state"]["ss"]
    state = dx_k_s_32_set_seed(bb, pp, kk, seed, ss)

    # Using Python xx as the testing seeds
    temp_state = dx_rng.state
    temp_state["state"]["XX"] = state["xx"]
    dx_rng.state = temp_state

    # random_raw testing (next_32)
    package_raw = dx_rng.random_raw(size=n_tests_per_fun)
    python_raw = np.array([dx_k_s_next32(state) for _ in range(n_tests_per_fun)])
    raw_result = np.array_equal(package_raw, python_raw)

    # uniform testing (next double)
    dx_generator = Generator(dx_rng)
    package_double = dx_generator.uniform(0, 1, size=n_tests_per_fun)
    python_double = np.array([dx_k_s_next_double(state) for _ in range(n_tests_per_fun)])
    uni_result = np.allclose(package_double, python_double, rtol=0, atol=1e-12)

    assert raw_result, f"random_raw failed. {dx_rng}. seed={seed}."
    assert uni_result, f"uniform failed. {dx_rng}. seed={seed}."