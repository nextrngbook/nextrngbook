# -*- coding: utf-8 -*-

from nextrngbook import dx_generator
from nextrngbook.dx_generator import DX32, get_dx32_max_id
import numpy as np
import pandas as pd
from numpy.random import Generator, randint
import pytest
import os

# prepare _DX32Generator objects
dx_data_path = os.path.join(os.path.dirname(dx_generator.__file__), "data", "dx32_parameters.csv")
dx_data = pd.read_csv(dx_data_path)
dx_k_1 = dx_data[dx_data["ss"] == 1]
dx_k_2 = dx_data[dx_data["ss"] == 2]

## Default and Boundary Testing (#7)
default_dx32 = DX32()

largest_kk_1 = DX32(dx_k_1.iloc[dx_k_1["kk"].argmax()]["dx_id"])
largest_kk_2 = DX32(dx_k_2.iloc[dx_k_2["kk"].argmax()]["dx_id"])

largest_bb_1 = DX32(dx_k_1.iloc[dx_k_1["bb"].argmax()]["dx_id"])
largest_bb_2 = DX32(dx_k_2.iloc[dx_k_2["bb"].argmax()]["dx_id"])

largest_pp_1 = DX32(dx_k_1.iloc[dx_k_1["pp"].argmax()]["dx_id"])
largest_pp_2 = DX32(dx_k_2.iloc[dx_k_2["pp"].argmax()]["dx_id"])

## Random testing (#3)
current_max_dx32_id = get_dx32_max_id()
rand_t_1, rand_t_2, rand_t_3 = [DX32(randint(0, current_max_dx32_id + 1)) for _ in range(3)]

dx32_test_data = [default_dx32, largest_kk_1, largest_kk_2, 
                  largest_bb_1, largest_bb_2, largest_pp_1,
                  largest_pp_2, rand_t_1, rand_t_2, rand_t_3]

seed_test_data = [randint(1, 1000000000) for _ in range(10)]

dx32_num_generated_test_cases = list(zip(dx32_test_data, seed_test_data))

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


def dx_k_s(state):

    II0 = state["II"] # preserve x_{i - 1}

    # update the running index
    state["II"] += 1 
    if state["II"] == state["kk"]:
        state["II"] = 0

    # update the states
    if state["ss"] == 1:
        state["xx"][state["II"]] = (state["bb"] * state["xx"][state["II"]] + state["xx"][II0]) % state["pp"]

    elif state["ss"] == 2:
        state["xx"][state["II"]] = (state["bb"] * (state["xx"][state["II"]] + state["xx"][II0])) % state["pp"]


def dx_k_s_next_double(state):

    dx_k_s(state) # update the state

    return (state["xx"][state["II"]] / state["pp"]) + state["hh"]

def dx_k_s_next32(state):

    return int(dx_k_s_next_double(state) * (2 ** 32))

def dx_k_s_next64(state):

    return (dx_k_s_next32(state) << 32) | dx_k_s_next32(state)


@pytest.mark.parametrize("dx32_rng, seed", dx32_num_generated_test_cases)
def test_dx32(dx32_rng, seed, n_tests_per_fun=1000000):

    # Python dx32 setting
    bb = dx32_rng.state["state"]["bb"]
    pp = dx32_rng.state["state"]["pp"]
    kk = dx32_rng.state["state"]["kk"]
    ss = dx32_rng.state["state"]["ss"]
    state = dx_k_s_32_set_seed(bb, pp, kk, seed, ss)
    
    
    # Using Python xx as the testing seeds
    temp_state = dx32_rng.state
    temp_state["state"]["XX"] = state["xx"]
    dx32_rng.state = temp_state
    
    # random_raw testing (next_32)
    package_raw = dx32_rng.random_raw(size=n_tests_per_fun)
    python_raw = np.array([dx_k_s_next32(state) for _ in range(n_tests_per_fun)])
    raw_result = np.array_equal(package_raw, python_raw)
    
    # uniform testing (next_double)
    dx32_generator = Generator(dx32_rng)
    package_double = dx32_generator.uniform(0, 1, size=n_tests_per_fun)
    python_double = np.array([dx_k_s_next_double(state) for _ in range(n_tests_per_fun)])
    uni_result = np.allclose(package_double, python_double, rtol=0, atol=1e-12)
    
    assert raw_result, f"random_raw failed. {dx32_rng}. seed={seed}."
    assert uni_result, f"uniform failed. {dx32_rng}. seed={seed}."