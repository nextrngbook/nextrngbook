#cython: binding=True
# MIT License
# Copyright (c) 2025 chintunglin

"""Defines the internal _DX32Generator and _DXGenerator classes for 32-bit DX random number generators.

Not intended for direct use by end users.

_DX32Generator implements the general 32-bit DX generator and is instantiated
via the public interface `dx_generator.DX32()`.

_DXGenerator implements the faster 32-bit DX generator with fixed
p = 2^31 - 1 and is instantiated via the public interface `dx_generator.DX()`.

Classes:
    `_DX32Generator` - A general 32-bit DX random number generator that supports
    DX parameter sets with arbitrary supported modulus p.

    `_DXGenerator` - A faster 32-bit DX random number generator with fixed
    p = 2^31 - 1 and fast Mersenne modular reduction.
"""

import numpy as np
cimport numpy as np
from libc.stdint cimport uint32_t, uint64_t
from numpy.random cimport BitGenerator, SeedSequence
from numpy.typing import NDArray
from typing import Union, Sequence

__all__ = ["_DX32Generator", "_DXGenerator"]

SeedType = Union[None, int, NDArray[np.integer], SeedSequence, Sequence[int]]

np.import_array()

cdef extern from "src/dx_k_s_32.h":
    
    enum: KK # supported upper limit of kk argument for _DXGenerator and _DX32Generator

    struct s_dx_k_s_32_state:
        uint32_t XX[KK]   # states with at most KK terms
        int II            # running index
        uint32_t bb       # multiplier
        uint32_t pp       # modulus
        int kk            # the order of recurrence (kk <= KK)
        double hh         # hh = 1 / (2 * pp)

    ctypedef s_dx_k_s_32_state dx_k_s_32_state # rename (to match C codes)

    # declare functions for random number generation
    ## dx_k_1
    uint32_t dx_k_1_next32(dx_k_s_32_state *state) noexcept nogil
    
    uint64_t dx_k_1_next64(dx_k_s_32_state *state) noexcept nogil
    
    double dx_k_1_next_double(dx_k_s_32_state *state) noexcept nogil

    ## dx_k_1_fast
    uint32_t dx_k_1_fast_next32(dx_k_s_32_state *state) noexcept nogil

    uint64_t dx_k_1_fast_next64(dx_k_s_32_state *state) noexcept nogil

    double dx_k_1_fast_next_double(dx_k_s_32_state *state) noexcept nogil
    
    ## dx_k_2
    uint32_t dx_k_2_next32(dx_k_s_32_state *state) noexcept nogil
    
    uint64_t dx_k_2_next64(dx_k_s_32_state *state) noexcept nogil
    
    double dx_k_2_next_double(dx_k_s_32_state *state) noexcept nogil

    ## dx_k_2_fast
    uint32_t dx_k_2_fast_next32(dx_k_s_32_state *state) noexcept nogil
    
    uint64_t dx_k_2_fast_next64(dx_k_s_32_state *state) noexcept nogil
    
    double dx_k_2_fast_next_double(dx_k_s_32_state *state) noexcept nogil

    uint32_t MOD_fast(uint64_t z) noexcept nogil
    

# Define functions of required format
## dx_k_1
cdef uint32_t dx_k_1_uint32(void *st) noexcept nogil:
    return dx_k_1_next32(<dx_k_s_32_state *> st)

cdef uint64_t dx_k_1_uint64(void *st) noexcept nogil:
    return dx_k_1_next64(<dx_k_s_32_state *> st)

cdef double dx_k_1_double(void *st) noexcept nogil:
    return dx_k_1_next_double(<dx_k_s_32_state *> st)

cdef uint64_t dx_k_1_raw(void *st) noexcept nogil:
    return <uint64_t>dx_k_1_next32(<dx_k_s_32_state *> st)

## dx_k_1_fast
cdef uint32_t dx_k_1_fast_uint32(void *st) noexcept nogil:
    return dx_k_1_fast_next32(<dx_k_s_32_state *> st)

cdef uint64_t dx_k_1_fast_uint64(void *st) noexcept nogil:
    return dx_k_1_fast_next64(<dx_k_s_32_state *> st)

cdef double dx_k_1_fast_double(void *st) noexcept nogil:
    return dx_k_1_fast_next_double(<dx_k_s_32_state *> st)

cdef uint64_t dx_k_1_fast_raw(void *st) noexcept nogil:
    return <uint64_t>dx_k_1_fast_next32(<dx_k_s_32_state *> st)

## dx_k_2
cdef uint32_t dx_k_2_uint32(void *st) noexcept nogil:
    return dx_k_2_next32(<dx_k_s_32_state *> st)

cdef uint64_t dx_k_2_uint64(void *st) noexcept nogil:
    return dx_k_2_next64(<dx_k_s_32_state *> st)

cdef double dx_k_2_double(void *st) noexcept nogil:
    return dx_k_2_next_double(<dx_k_s_32_state *> st)

cdef uint64_t dx_k_2_raw(void *st) noexcept nogil:
    return <uint64_t>dx_k_2_next32(<dx_k_s_32_state *> st)

## dx_k_2_fast
cdef uint32_t dx_k_2_fast_uint32(void *st) noexcept nogil:
    return dx_k_2_fast_next32(<dx_k_s_32_state *> st)

cdef uint64_t dx_k_2_fast_uint64(void *st) noexcept nogil:
    return dx_k_2_fast_next64(<dx_k_s_32_state *> st)

cdef double dx_k_2_fast_double(void *st) noexcept nogil:
    return dx_k_2_fast_next_double(<dx_k_s_32_state *> st)

cdef uint64_t dx_k_2_fast_raw(void *st) noexcept nogil:
    return <uint64_t>dx_k_2_fast_next32(<dx_k_s_32_state *> st)


cdef class _DX32Generator(BitGenerator):
    """A 32-bit DX random number generator.
    
    The DX family consists of multiple RNGs characterized by different 
    parameter sets. This class implements a specific DX generator based 
    on provided parameters.

    Not intended for direct use; instances should be created via 
    `dx_generator.DX32()`.    
    """
    
    _ss_support = {1, 2} # supported ss argument for _DX32Generator and _DXGenerator
    
    cdef int __ss
    cdef float _log10_period
    cdef dx_k_s_32_state _rng_state

    def __init__(self, 
                 bb: Union[float, int], 
                 pp: Union[float, int], 
                 kk: Union[float, int], 
                 ss: Union[float, int], 
                 log10_period: float = np.nan, 
                 seed: SeedType = None):

        BitGenerator.__init__(self, seed)
        
        # specify dx_k_s
        self._rng_state.bb = bb
        self._rng_state.pp = pp
        self._rng_state.kk = kk
        self._rng_state.hh = 1 / (2 * <double> pp)
        self._ss = ss
        self._log10_period = log10_period
        
        # initial seeding
        val = self._seed_seq.generate_state(self._rng_state.kk, np.uint32)
        
        ## reset the first seed to be in {1, ..., pp-1} (seed can't be all zero)
        self._rng_state.XX[0] = val[0] % (self._rng_state.pp - <uint32_t> 1) + <uint32_t> 1
        
        for i in range(1, self._rng_state.kk):
            self._rng_state.XX[i] = val[i] % self._rng_state.pp # {0, ..., pp-1}
        
        # initialize running index
        self._rng_state.II = i
        
        # connect to _bitgen
        self._bitgen.state = &self._rng_state

    def __repr__(self):
        
        return (
            f"{self.__class__.__name__}("
            f"bb={self._rng_state.bb}, "
            f"pp={self._rng_state.pp}, "
            f"kk={self._rng_state.kk}, "
            f"ss={self._ss}, "
            f"log10_period={self._log10_period}"
            ")"
        )
    
    def __str__(self):
        
        return (
            f"DX-{self._rng_state.kk}-{self._ss} generator\n"
            f"Multiplier = {self._rng_state.bb}\n"
            f"Modulus    = {self._rng_state.pp}\n"
            f"The log₁₀(period) of the PRNG is {self._log10_period:.1f}\n"
        )

    @property
    def _ss(self):
        
        return self.__ss
    
    @_ss.setter
    def _ss(self, value):
        
        if value == 1: # dx_k_1
            self._bitgen.next_uint32 = &dx_k_1_uint32
            self._bitgen.next_uint64 = &dx_k_1_uint64
            self._bitgen.next_double = &dx_k_1_double
            self._bitgen.next_raw = &dx_k_1_raw
            
        elif value == 2: #dx_k_2
            self._bitgen.next_uint32 = &dx_k_2_uint32
            self._bitgen.next_uint64 = &dx_k_2_uint64
            self._bitgen.next_double = &dx_k_2_double
            self._bitgen.next_raw = &dx_k_2_raw
    
        else:
            raise ValueError(f"ss must be in {_DX32Generator._ss_support}.")

        self.__ss = value

    @property
    def state(self) -> dict:
        """The PRNG state.
        
        Information that describes the current state of the PRNG.
        """

        XX = np.zeros(self._rng_state.kk, dtype=np.uint32)
        
        for i in range(self._rng_state.kk):
            XX[i] = self._rng_state.XX[i]

        return {"bit_generator": self.__class__.__name__,
                "state": {"XX": XX, "II": self._rng_state.II,
                          "bb": self._rng_state.bb,
                          "pp": self._rng_state.pp,
                          "kk": self._rng_state.kk,
                          "ss": self._ss,
                          "log10_period": self._log10_period}}

    @state.setter
    def state(self, value):

        if not isinstance(value, dict):
            raise TypeError("State must be a dict.")
            
        bitgen = value.get("bit_generator", "")
        if bitgen != self.__class__.__name__:
            raise ValueError(
                f"State must be for a {self.__class__.__name__} PRNG."
            )

        self._ss = value["state"]["ss"]
        self._rng_state.II = value["state"]["II"]
        self._rng_state.bb = value["state"]["bb"]
        self._rng_state.pp = value["state"]["pp"]
        self._rng_state.kk = value["state"]["kk"]
        self._rng_state.hh = 1 / (2 * <double> self._rng_state.pp)
            
        XX = value["state"]["XX"]
        for i in range(self._rng_state.kk):
            self._rng_state.XX[i] = XX[i]
            
        self._log10_period = value["state"]["log10_period"]

    


cdef class _DXGenerator(_DX32Generator):
    """A faster 32-bit DX random number generator with fixed p = 2^31 - 1.
    
    This class implements the recommended fast DX generator. It is restricted
    to pp = 2^31 - 1 so that fast Mersenne modular reduction can be used.

    Not intended for direct use; instances should be created via 
    `dx_generator.DX()`.    
    """

    cdef int __ss

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self._rng_state.pp != 2147483647:
            raise ValueError("This class only supports pp = 2^31 - 1.")

    @property
    def _ss(self):
        
        return self.__ss
    
    @_ss.setter
    def _ss(self, value):

        if value == 1: # dx_k_1
            self._bitgen.next_uint32 = &dx_k_1_fast_uint32
            self._bitgen.next_uint64 = &dx_k_1_fast_uint64
            self._bitgen.next_double = &dx_k_1_fast_double
            self._bitgen.next_raw = &dx_k_1_fast_raw
            
        elif value == 2: #dx_k_2
            self._bitgen.next_uint32 = &dx_k_2_fast_uint32
            self._bitgen.next_uint64 = &dx_k_2_fast_uint64
            self._bitgen.next_double = &dx_k_2_fast_double
            self._bitgen.next_raw = &dx_k_2_fast_raw
    
        else:
            raise ValueError(f"ss must be in {_DXGenerator._ss_support}.")

        self.__ss = value