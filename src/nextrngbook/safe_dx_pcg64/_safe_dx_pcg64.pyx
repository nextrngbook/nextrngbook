# cython: binding=True
# MIT License
# Copyright (c) 2026 Meng-Xun Cai

"""Defines internal BitGenerator classes for 32-bit SAFE-DX-PCG64 and
eSAFE-DX-PCG64 random number generators.

Not intended for direct use by end users.

The generators combine a 32-bit DX generator with PCG64. The SAFE variant
produces one output per internal update, while the eSAFE variants produce and
buffer four or eight outputs per internal update.

Classes:
    `_eSAFE_DX_PCG64_Generator` - Common implementation shared by the
    SAFE and ESAFE-DX-PCG64 generators.

    `_SAFE_DX_PCG64_Generator` - A SAFE-DX-PCG64 generator that produces one
    output per internal update.

    `_eSAFE_DX_PCG64_M4_Generator` - A eSAFE-DX-PCG64 generator that produces
    four buffered outputs per internal update.

    `_eSAFE_DX_PCG64_M8_Generator` - A eSAFE-DX-PCG64 generator that produces
    eight buffered outputs per internal update.
"""

import math
import numpy as np
cimport numpy as np
from libc.stdint cimport uint32_t, uint64_t
from numpy.random cimport BitGenerator, bitgen_t
from numpy.typing import NDArray
from typing import Union, Sequence

__all__ = [
    "_eSAFE_DX_PCG64_Generator",
    "_SAFE_DX_PCG64_Generator",
    "_eSAFE_DX_PCG64_M4_Generator",
    "_eSAFE_DX_PCG64_M8_Generator",
]

SeedType = Union[None, int, NDArray[np.integer], np.random.SeedSequence, Sequence[int]]

np.import_array()

ctypedef uint32_t (*next32_t)(void*) noexcept nogil
ctypedef uint64_t (*next64_t)(void*) noexcept nogil
ctypedef double (*next_double_t)(void*) noexcept nogil

cdef extern from "src/safe_dx_pcg64_32.h":

    enum: KK
    enum: SAFE_MAX
    enum: SAFE_CAPACITY
    enum: SAFE_MAX_TABLE_SIZE

    struct s_dx_k_s_32_state:
        uint32_t XX[KK]
        int II
        uint32_t bb
        uint32_t pp
        int kk
        double hh

    ctypedef s_dx_k_s_32_state dx_k_s_32_state

    struct s_pcg64_state:
        uint64_t state_high
        uint64_t state_low
        uint64_t inc_high
        uint64_t inc_low
        uint64_t mult_high
        uint64_t mult_low

    ctypedef s_pcg64_state pcg64_state

    struct s_esafe_dx_pcg64_state:
        dx_k_s_32_state dx
        pcg64_state pcg64
        uint32_t table_x[SAFE_MAX_TABLE_SIZE]
        uint32_t table_y[SAFE_MAX_TABLE_SIZE]
        int table_size
        int burn_in
        int safe_max
        uint32_t SAFE_T[SAFE_CAPACITY]
        int SAFE_II

    ctypedef s_esafe_dx_pcg64_state esafe_dx_pcg64_state

    void pcg64_srandom_r(pcg64_state *state, uint64_t *initstate, uint64_t *initseq, uint32_t multiplier_id) noexcept nogil

    void esafe_dx_s1_pcg64_fast_init(esafe_dx_pcg64_state *state) noexcept nogil
    void esafe_dx_s2_pcg64_fast_init(esafe_dx_pcg64_state *state) noexcept nogil

    uint32_t esafe_dx_s1_pcg64_fast_next32(esafe_dx_pcg64_state *state) noexcept nogil
    uint64_t esafe_dx_s1_pcg64_fast_next64(esafe_dx_pcg64_state *state) noexcept nogil
    double esafe_dx_s1_pcg64_fast_next_double(esafe_dx_pcg64_state *state) noexcept nogil

    uint32_t esafe_dx_s2_pcg64_fast_next32(esafe_dx_pcg64_state *state) noexcept nogil
    uint64_t esafe_dx_s2_pcg64_fast_next64(esafe_dx_pcg64_state *state) noexcept nogil
    double esafe_dx_s2_pcg64_fast_next_double(esafe_dx_pcg64_state *state) noexcept nogil


cdef uint32_t esafe_dx_s1_pcg64_fast_uint32(void *st) noexcept nogil:
    return esafe_dx_s1_pcg64_fast_next32(<esafe_dx_pcg64_state *>st)

cdef uint64_t esafe_dx_s1_pcg64_fast_uint64(void *st) noexcept nogil:
    return esafe_dx_s1_pcg64_fast_next64(<esafe_dx_pcg64_state *>st)

cdef double esafe_dx_s1_pcg64_fast_double(void *st) noexcept nogil:
    return esafe_dx_s1_pcg64_fast_next_double(<esafe_dx_pcg64_state *>st)

cdef uint64_t esafe_dx_s1_pcg64_fast_raw(void *st) noexcept nogil:
    return esafe_dx_s1_pcg64_fast_next32(<esafe_dx_pcg64_state *>st)

cdef uint32_t esafe_dx_s2_pcg64_fast_uint32(void *st) noexcept nogil:
    return esafe_dx_s2_pcg64_fast_next32(<esafe_dx_pcg64_state *>st)

cdef uint64_t esafe_dx_s2_pcg64_fast_uint64(void *st) noexcept nogil:
    return esafe_dx_s2_pcg64_fast_next64(<esafe_dx_pcg64_state *>st)

cdef double esafe_dx_s2_pcg64_fast_double(void *st) noexcept nogil:
    return esafe_dx_s2_pcg64_fast_next_double(<esafe_dx_pcg64_state *>st)

cdef uint64_t esafe_dx_s2_pcg64_fast_raw(void *st) noexcept nogil:
    return esafe_dx_s2_pcg64_fast_next32(<esafe_dx_pcg64_state *>st)



cdef object benchmark_esafe_dx_pcg64(bitgen_t *bitgen, object lock, Py_ssize_t cnt, object method):
    cdef Py_ssize_t i

    if method == "uint64":
        with lock, nogil:
            for i in range(cnt):
                bitgen.next_uint64(bitgen.state)
    elif method == "uint32":
        with lock, nogil:
            for i in range(cnt):
                bitgen.next_uint32(bitgen.state)
    elif method == "double":
        with lock, nogil:
            for i in range(cnt):
                bitgen.next_double(bitgen.state)
    else:
        raise ValueError("Unknown method")


cdef class _eSAFE_DX_PCG64_Generator(BitGenerator):
    """Common implementation for the 32-bit SAFE-DX-PCG64 and eSAFE-DX-PCG64 generators.

    This class manages the DX and PCG64 states, mutual-shuffling tables,
    output buffer, and NumPy BitGenerator callbacks.

    Not intended for direct use by end users.
    """

    _ss_support = {1, 2}

    cdef int _ss_value
    cdef float _log10_period
    cdef int _table_size
    cdef int _safe_table_size
    cdef int _burn_in
    cdef np.ndarray pcg_seed
    cdef uint32_t multiplier_seed
    cdef esafe_dx_pcg64_state _rng_state

    def __init__(self,
                 bb: Union[float, int],
                 pp: Union[float, int],
                 kk: Union[float, int],
                 ss: Union[float, int],
                 log10_period: Union[float, int] = np.nan,
                 table_size: int = 512,
                 burn_in: int = 5,
                 output_size: int = 4,
                 seed: SeedType = None):

        cdef int i
        cdef np.ndarray pcg_seed

        BitGenerator.__init__(self, seed)

        self._rng_state.dx.bb = <uint32_t>bb
        self._rng_state.dx.pp = <uint32_t>pp
        self._rng_state.dx.kk = <int>kk
        self._rng_state.dx.hh = 1 / (2 * <double>self._rng_state.dx.pp)
        self._log10_period = log10_period

        self._table_size = table_size
        self._burn_in = burn_in
        self._safe_table_size = output_size

        if self._table_size < 1 or self._table_size > SAFE_MAX_TABLE_SIZE:
            raise ValueError(f"table_size must be in [1, {SAFE_MAX_TABLE_SIZE}].")
        if self._table_size & (self._table_size - 1):
            raise ValueError("table_size must be a power of two.")
        if self._safe_table_size not in (1, 4, 8):
            raise ValueError("output_size must be 1, 4, or 8.")

        dx = self._seed_seq.generate_state(self._rng_state.dx.kk, np.uint32)
        self._rng_state.dx.XX[0] = dx[0] % (self._rng_state.dx.pp - <uint32_t>1) + <uint32_t>1

        for i in range(1, self._rng_state.dx.kk):
            self._rng_state.dx.XX[i] = dx[i] % self._rng_state.dx.pp

        self._rng_state.dx.II = i

        pcg_seed = <np.ndarray>self._seed_seq.generate_state(5, np.uint64)
        multiplier_seed = <uint32_t>(
            int(pcg_seed[4]) & ((1 << 29) - 1)
        )

        pcg64_srandom_r(
            &self._rng_state.pcg64,
            <uint64_t *>np.PyArray_DATA(pcg_seed),
            (<uint64_t *>np.PyArray_DATA(pcg_seed) + 2),
            multiplier_seed,
        )

        for i in range(self._table_size):
            self._rng_state.table_x[i] = 0
            self._rng_state.table_y[i] = 0

        for i in range(SAFE_CAPACITY):
            self._rng_state.SAFE_T[i] = 0

        self._rng_state.table_size = self._table_size
        self._rng_state.burn_in = self._burn_in
        self._rng_state.safe_max = self._safe_table_size

        self._bitgen.state = &self._rng_state
        self._ss = ss

    def __repr__(self):
        name = (
            "SAFE-DX-PCG64" if self._rng_state.safe_max == 1
            else f"eSAFE-DX-PCG64-M{self._rng_state.safe_max}"
        )
        return (
            f"Done. {name} generator combining DX and PCG64. "
            f"Use print() function for details."
        )

    def __str__(self):
        name = (
            "SAFE-DX-PCG64" if self._rng_state.safe_max == 1
            else f"eSAFE-DX-PCG64-M{self._rng_state.safe_max}"
        )

        # Convert to Python integers before shifting the high 64-bit words.
        increment = (int(self._rng_state.pcg64.inc_high) << 64) | int(self._rng_state.pcg64.inc_low)
        multiplier = (int(self._rng_state.pcg64.mult_high) << 64) | int(self._rng_state.pcg64.mult_low)
        p = int(self._rng_state.dx.pp)
        k = int(self._rng_state.dx.kk)

        # Calculate log10(p**k - 1) without expanding the DX period.
        dx_log_period = k * math.log10(p) + math.log1p(
            -math.exp(-k * math.log(p))
        ) / math.log(10)
        pcg_period = 1 << 128
        pcg_log_period = 128 * math.log10(2)

        # gcd(a, m) == gcd(a % m, m); modular power keeps integers small.
        common_period = math.gcd(pow(p, k, pcg_period) - 1, pcg_period)
        common_log_period = math.log10(common_period)

        # lcm(P_X, P_Y) = P_X * P_Y / gcd(P_X, P_Y).
        upper_log_period = dx_log_period + pcg_log_period - common_log_period
        lower_log_period = upper_log_period - common_log_period

        return (
            f"{name} generator\n"
            f"RNGX = DX-{self._rng_state.dx.kk}-{self._ss} generator\n"
            f"  Multiplier = {self._rng_state.dx.bb}\n"
            f"  k = {self._rng_state.dx.kk}\n"
            f"  s = {self._ss}\n"
            f"RNGY = PCG64 XSL-RR 128/64\n"
            f"  Increment = {increment}\n"
            f"  Multiplier = {multiplier}\n"
            f"Output size = {self._rng_state.safe_max}\n"
            f"DX log10(period) = {dx_log_period:.1f}\n"
            f"PCG64 log10(period) = {pcg_log_period:.1f}\n"
            f"{name} log10(period) bounds:\n"
            f"  {lower_log_period:.1f} <= log10(period) <= {upper_log_period:.1f}\n"
        )

    @property
    def _ss(self):
        return self._ss_value

    def _bind_ss_callbacks(self, value):
        if value == 1:
            if self._safe_table_size == 1:
                self._bitgen.next_uint32 = &esafe_dx_s1_pcg64_fast_uint32
                self._bitgen.next_uint64 = &esafe_dx_s1_pcg64_fast_uint64
                self._bitgen.next_double = &esafe_dx_s1_pcg64_fast_double
                self._bitgen.next_raw = &esafe_dx_s1_pcg64_fast_raw
            elif self._safe_table_size == 4:
                self._bitgen.next_uint32 = &esafe_dx_s1_pcg64_fast_uint32
                self._bitgen.next_uint64 = &esafe_dx_s1_pcg64_fast_uint64
                self._bitgen.next_double = &esafe_dx_s1_pcg64_fast_double
                self._bitgen.next_raw = &esafe_dx_s1_pcg64_fast_raw
            elif self._safe_table_size == 8:
                self._bitgen.next_uint32 = &esafe_dx_s1_pcg64_fast_uint32
                self._bitgen.next_uint64 = &esafe_dx_s1_pcg64_fast_uint64
                self._bitgen.next_double = &esafe_dx_s1_pcg64_fast_double
                self._bitgen.next_raw = &esafe_dx_s1_pcg64_fast_raw
            else:
                raise ValueError("output_size must be 1, 4, or 8.")
        elif value == 2:
            if self._safe_table_size == 1:
                self._bitgen.next_uint32 = &esafe_dx_s2_pcg64_fast_uint32
                self._bitgen.next_uint64 = &esafe_dx_s2_pcg64_fast_uint64
                self._bitgen.next_double = &esafe_dx_s2_pcg64_fast_double
                self._bitgen.next_raw = &esafe_dx_s2_pcg64_fast_raw
            elif self._safe_table_size == 4:
                self._bitgen.next_uint32 = &esafe_dx_s2_pcg64_fast_uint32
                self._bitgen.next_uint64 = &esafe_dx_s2_pcg64_fast_uint64
                self._bitgen.next_double = &esafe_dx_s2_pcg64_fast_double
                self._bitgen.next_raw = &esafe_dx_s2_pcg64_fast_raw
            elif self._safe_table_size == 8:
                self._bitgen.next_uint32 = &esafe_dx_s2_pcg64_fast_uint32
                self._bitgen.next_uint64 = &esafe_dx_s2_pcg64_fast_uint64
                self._bitgen.next_double = &esafe_dx_s2_pcg64_fast_double
                self._bitgen.next_raw = &esafe_dx_s2_pcg64_fast_raw
            else:
                raise ValueError("output_size must be 1, 4, or 8.")
        else:
            raise ValueError(f"ss must be in {_eSAFE_DX_PCG64_Generator._ss_support}.")

    @_ss.setter
    def _ss(self, value):
        if value == 1:
            self._bind_ss_callbacks(value)
            esafe_dx_s1_pcg64_fast_init(&self._rng_state)
        elif value == 2:
            self._bind_ss_callbacks(value)
            esafe_dx_s2_pcg64_fast_init(&self._rng_state)
        else:
            raise ValueError(f"ss must be in {_eSAFE_DX_PCG64_Generator._ss_support}.")

        self._ss_value = value

    @property
    def state(self) -> dict:
        cdef int i
        XX = np.zeros(self._rng_state.dx.kk, dtype=np.uint32)
        table_x = np.zeros(self._rng_state.table_size, dtype=np.uint32)
        table_y = np.zeros(self._rng_state.table_size, dtype=np.uint32)
        safe_t = np.zeros(SAFE_CAPACITY, dtype=np.uint32)

        for i in range(self._rng_state.dx.kk):
            XX[i] = self._rng_state.dx.XX[i]

        for i in range(self._rng_state.table_size):
            table_x[i] = self._rng_state.table_x[i]
            table_y[i] = self._rng_state.table_y[i]

        for i in range(SAFE_CAPACITY):
            safe_t[i] = self._rng_state.SAFE_T[i]

        return {
            "bit_generator": self.__class__.__name__,
            "state": {
                "DX generator": {
                    "XX": XX,
                    "II": self._rng_state.dx.II,
                    "bb": self._rng_state.dx.bb,
                    "pp": self._rng_state.dx.pp,
                    "kk": self._rng_state.dx.kk,
                    "ss": self._ss,
                    "log10_period": self._log10_period,
                },
                "PCG64": {
                    "state": (int(self._rng_state.pcg64.state_high) << 64)
                             | int(self._rng_state.pcg64.state_low),
                    "multiplier": (int(self._rng_state.pcg64.mult_high) << 64)
                             | int(self._rng_state.pcg64.mult_low),
                    "inc": (int(self._rng_state.pcg64.inc_high) << 64)
                           | int(self._rng_state.pcg64.inc_low),
                },
                "table_x": table_x,
                "table_y": table_y,
                "table_size": self._rng_state.table_size,
                "burn_in": self._rng_state.burn_in,
                "safe_max": self._rng_state.safe_max,
                "output_size": self._rng_state.safe_max,
                "SAFE_T": safe_t,
                "SAFE_II": self._rng_state.SAFE_II,
            },
        }

    @state.setter
    def state(self, value):
        cdef int i
        cdef object pcg_state
        cdef object pcg_multiplier
        cdef object pcg_inc

        if not isinstance(value, dict):
            raise TypeError("State must be a dict.")

        bitgen = value.get("bit_generator", "")
        if bitgen != self.__class__.__name__:
            raise ValueError(f"State must be for a {self.__class__.__name__} PRNG.")

        dx_state = value["state"]["DX generator"]
        self._rng_state.dx.II = dx_state["II"]
        self._rng_state.dx.bb = dx_state["bb"]
        self._rng_state.dx.pp = dx_state["pp"]
        self._rng_state.dx.kk = dx_state["kk"]
        self._rng_state.dx.hh = 1 / (2 * <double>self._rng_state.dx.pp)

        XX = dx_state["XX"]
        for i in range(len(XX)):
            self._rng_state.dx.XX[i] = XX[i]

        self._log10_period = dx_state["log10_period"]

        pcg_state = value["state"]["PCG64"]["state"]
        pcg_multiplier = value["state"]["PCG64"]["multiplier"]

        if not 0 <= pcg_multiplier < (1 << 128):
            raise ValueError("PCG64 multiplier must be a 128-bit unsigned integer.")
        if pcg_multiplier % 8 != 5:
            raise ValueError("PCG64 multiplier must satisfy multiplier % 8 == 5.")

        self._rng_state.pcg64.mult_high = <uint64_t>(pcg_multiplier >> 64)
        self._rng_state.pcg64.mult_low = <uint64_t>(
            pcg_multiplier & ((1 << 64) - 1)
        )
        pcg_inc = value["state"]["PCG64"]["inc"]

        self._rng_state.pcg64.state_high = <uint64_t>(pcg_state >> 64)
        self._rng_state.pcg64.state_low = <uint64_t>(pcg_state & ((1 << 64) - 1))
        self._rng_state.pcg64.inc_high = <uint64_t>(pcg_inc >> 64)
        self._rng_state.pcg64.inc_low = <uint64_t>(pcg_inc & ((1 << 64) - 1))

        self._rng_state.table_size = value["state"]["table_size"]
        self._rng_state.burn_in = value["state"]["burn_in"]
        self._rng_state.safe_max = value["state"].get(
            "safe_max", value["state"].get("output_size", len(value["state"]["SAFE_T"]))
        )
        if self._rng_state.safe_max not in (1, 4, 8):
            raise ValueError("State output_size must be 1, 4, or 8.")
        self._safe_table_size = self._rng_state.safe_max

        table_x = value["state"]["table_x"]
        table_y = value["state"]["table_y"]
        for i in range(self._rng_state.table_size):
            self._rng_state.table_x[i] = table_x[i]
            self._rng_state.table_y[i] = table_y[i]

        SAFE_T = value["state"]["SAFE_T"]
        if len(SAFE_T) < self._rng_state.safe_max:
            raise ValueError("State SAFE_T is shorter than output_size.")
        if len(SAFE_T) > SAFE_CAPACITY:
            raise ValueError(f"State SAFE_T must have at most {SAFE_CAPACITY} entries.")
        for i in range(len(SAFE_T)):
            self._rng_state.SAFE_T[i] = SAFE_T[i]

        self._rng_state.SAFE_II = value["state"]["SAFE_II"]
        self._bind_ss_callbacks(dx_state["ss"])
        self._ss_value = dx_state["ss"]

    def _benchmark(self, Py_ssize_t cnt, method="uint64"):
        """Used in tests."""
        return benchmark_esafe_dx_pcg64(&self._bitgen, self.lock, cnt, method)

cdef class _SAFE_DX_PCG64_Generator(_eSAFE_DX_PCG64_Generator):
    """A 32-bit SAFE-DX-PCG64 generator.

    Produces one output value per internal update.

    Not intended for direct use; instances should be created via
    `esafe_dx_pcg64.SAFE_DX_PCG64()`.
    """

    def __init__(self, *args, **kwargs):
        kwargs.pop("output_size", None)
        super().__init__(*args, output_size=1, **kwargs)


cdef class _eSAFE_DX_PCG64_M4_Generator(_eSAFE_DX_PCG64_Generator):
    """A 32-bit eSAFE-DX-PCG64 generator with four buffered outputs.

    Produces four output values per internal update.

    Not intended for direct use; instances should be created via
    `esafe_dx_pcg64.eSAFE_DX_PCG64_M4()`.
    """

    def __init__(self, *args, **kwargs):
        kwargs.pop("output_size", None)
        super().__init__(*args, output_size=4, **kwargs)


cdef class _eSAFE_DX_PCG64_M8_Generator(_eSAFE_DX_PCG64_Generator):
    """A 32-bit eSAFE-DX-PCG64 generator with eight buffered outputs.

    Produces eight output values per internal update.

    Not intended for direct use; instances should be created via
    `esafe_dx_pcg64.eSAFE_DX_PCG64_M8()`.
    """
    
    def __init__(self, *args, **kwargs):
        kwargs.pop("output_size", None)
        super().__init__(*args, output_size=8, **kwargs)
