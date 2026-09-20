This section will guide you through the steps to install **NextRNGBook** and begin
using **eSAFE-DX-PCG64-M4** and **eSAFE-DX-PCG64-M8**. Both combine a DX generator
and PCG64, just like [SAFE-DX-PCG64](safe_quick_start.md), and work with NumPy's
`Generator` class.

**M8 offers substantially faster generation than SAFE-DX-PCG64** in the package's
[published evaluation](evaluation.md#numpy-generator-speed-comparison): about
**1.65 times the overall throughput** and **1.69 times the uniform throughput**.

## Installation

To install NextRNGBook, use the Python package manager `pip` in your terminal:

```bash

pip install nextrngbook

```

## Import the package

NextRNGBook provides the underlying random number generators (RNGs), while NumPy's
`Generator` provides random arrays, matrices, and distributions.

```python

from nextrngbook.safe_dx_pcg64 import eSAFE_DX_PCG64_M4, eSAFE_DX_PCG64_M8
from numpy.random import Generator

```

## Create eSAFE generators

Use `eSAFE_DX_PCG64_M4(seed=None, randomize=True)` or
`eSAFE_DX_PCG64_M8(seed=None, randomize=True)` to create a 32-bit eSAFE
BitGenerator. For reproducible initialization, provide a fixed seed and set
`randomize=False`:

```python

>>> eSAFE_DX_PCG64_M4(seed=308, randomize=False)
Done. eSAFE-DX-PCG64-M4 generator combining DX and PCG64. Use print() function for details.

>>> eSAFE_DX_PCG64_M8(seed=308, randomize=False)
Done. eSAFE-DX-PCG64-M8 generator combining DX and PCG64. Use print() function for details.

```

Both functions take two parameters:

- seed: Selects the generator configuration and initializes its random state.
- randomize: Defaults to `True`, mixing fresh system entropy and the current time with the optional seed. Set it to `False` with a fixed seed for reproducible results.

With a fixed seed and `randomize=False`, recreating the same variant and making
the same calls in the same order reproduces the output. M4 and M8 have their own
output sequences. Setting only the seed while leaving `randomize=True` does not
reproduce the sequence. Omitting the seed also gives non-reproducible
initialization; using `seed=None` with `randomize=False` emits a warning.

The variants differ in the number of outputs produced per internal update:

| Generator | 32-bit outputs per internal update |
|---|---:|
| SAFE-DX-PCG64 | 1 |
| eSAFE-DX-PCG64-M4 | 4 |
| eSAFE-DX-PCG64-M8 | 8 |

M4 and M8 buffer multiple outputs, spreading the internal update cost over more
values. NumPy consumes these outputs as needed for the requested data type or
distribution.

### How the seed selects the generators


The seed selects a specific DX generator from the built-in DX family, the
increment and multiplier of PCG64's underlying 128-bit LCG, and the SAFE
parameters: shuffle-table size and burn-in length.

When `randomize=True`, the supplied seed is mixed with the current time and
fresh system entropy at each initialization. As a result, two calls with the
same seed can select different DX generators and PCG64 parameter combinations.
The following examples show this for M4 and M8.

#### eSAFE-DX-PCG64-M4

```python

first_rng_m4 = eSAFE_DX_PCG64_M4(seed=308, randomize=True)
second_rng_m4 = eSAFE_DX_PCG64_M4(seed=308, randomize=True)

print(first_rng_m4)
print(second_rng_m4)

```

The following output was captured from one run. Your selected parameters will
vary between runs.

```text

eSAFE-DX-PCG64-M4 generator
RNGX = DX-51-2 generator
  Multiplier = 1046670
  k = 51
  s = 2
RNGY = PCG64 XSL-RR 128/64
  Increment = 88987673469695325059029160966457235609
  Multiplier = 1409120141
Output size = 4
DX log10(period) = 475.9
PCG64 log10(period) = 38.5
eSAFE-DX-PCG64-M4 log10(period) bounds:
  513.9 <= log10(period) <= 514.2

eSAFE-DX-PCG64-M4 generator
RNGX = DX-120-1 generator
  Multiplier = 505803
  k = 120
  s = 1
RNGY = PCG64 XSL-RR 128/64
  Increment = 71599123040861671238866430186765622201
  Multiplier = 3832300597
Output size = 4
DX log10(period) = 1119.8
PCG64 log10(period) = 38.5
eSAFE-DX-PCG64-M4 log10(period) bounds:
  1137.9 <= log10(period) <= 1148.1

```

For reproducible results, use the same seed with `randomize=False`.
You can check that the same seed reproduces the same displayed configuration:

```python

first_rng_m4 = eSAFE_DX_PCG64_M4(seed=309, randomize=False)
second_rng_m4 = eSAFE_DX_PCG64_M4(seed=309, randomize=False)

print(first_rng_m4)
print(second_rng_m4)

```

```text

eSAFE-DX-PCG64-M4 generator
RNGX = DX-26-2 generator
  Multiplier = 1043567
  k = 26
  s = 2
RNGY = PCG64 XSL-RR 128/64
  Increment = 301549040784724452349154388386474624911
  Multiplier = 1239250421
Output size = 4
DX log10(period) = 242.6
PCG64 log10(period) = 38.5
eSAFE-DX-PCG64-M4 log10(period) bounds:
  261.9 <= log10(period) <= 271.5

eSAFE-DX-PCG64-M4 generator
RNGX = DX-26-2 generator
  Multiplier = 1043567
  k = 26
  s = 2
RNGY = PCG64 XSL-RR 128/64
  Increment = 301549040784724452349154388386474624911
  Multiplier = 1239250421
Output size = 4
DX log10(period) = 242.6
PCG64 log10(period) = 38.5
eSAFE-DX-PCG64-M4 log10(period) bounds:
  261.9 <= log10(period) <= 271.5

```

#### eSAFE-DX-PCG64-M8

```python

first_rng_m8 = eSAFE_DX_PCG64_M8(seed=308, randomize=True)
second_rng_m8 = eSAFE_DX_PCG64_M8(seed=308, randomize=True)

print(first_rng_m8)
print(second_rng_m8)

```

The following output was captured from one run. Your selected parameters will
vary between runs.

```text

eSAFE-DX-PCG64-M8 generator
RNGX = DX-18-1 generator
  Multiplier = 521230
  k = 18
  s = 1
RNGY = PCG64 XSL-RR 128/64
  Increment = 61441981387953557022605883906289817941
  Multiplier = 1585631517
Output size = 8
DX log10(period) = 168.0
PCG64 log10(period) = 38.5
eSAFE-DX-PCG64-M8 log10(period) bounds:
  187.2 <= log10(period) <= 196.9

eSAFE-DX-PCG64-M8 generator
RNGX = DX-47-2 generator
  Multiplier = 658296
  k = 47
  s = 2
RNGY = PCG64 XSL-RR 128/64
  Increment = 169712264287761689464537911035566906195
  Multiplier = 3112087829
Output size = 8
DX log10(period) = 438.6
PCG64 log10(period) = 38.5
eSAFE-DX-PCG64-M8 log10(period) bounds:
  476.5 <= log10(period) <= 476.8

```
For reproducible results, use the same seed with `randomize=False`.
You can check that the same seed reproduces the same displayed configuration:

```python

first_rng_m8 = eSAFE_DX_PCG64_M8(seed=308, randomize=False)
second_rng_m8 = eSAFE_DX_PCG64_M8(seed=308, randomize=False)

print(first_rng_m8)
print(second_rng_m8)

```

```text

eSAFE-DX-PCG64-M8 generator
RNGX = DX-21-2 generator
  Multiplier = 1044843
  k = 21
  s = 2
RNGY = PCG64 XSL-RR 128/64
  Increment = 135935203381921163399322660603397037679
  Multiplier = 1040453069
Output size = 8
DX log10(period) = 196.0
PCG64 log10(period) = 38.5
eSAFE-DX-PCG64-M8 log10(period) bounds:
  233.9 <= log10(period) <= 234.2

eSAFE-DX-PCG64-M8 generator
RNGX = DX-21-2 generator
  Multiplier = 1044843
  k = 21
  s = 2
RNGY = PCG64 XSL-RR 128/64
  Increment = 135935203381921163399322660603397037679
  Multiplier = 1040453069
Output size = 8
DX log10(period) = 196.0
PCG64 log10(period) = 38.5
eSAFE-DX-PCG64-M8 log10(period) bounds:
  233.9 <= log10(period) <= 234.2

```

## View eSAFE generator info

Print the generators to view the selected DX and PCG64 parameters and period bounds.
With the default `randomize=True`, the selected parameters vary between runs.
The following is an example output; your selected parameters may differ.


```python

rng_m4 = eSAFE_DX_PCG64_M4(seed=1234)
rng_m8 = eSAFE_DX_PCG64_M8(seed=1234)
print(rng_m4)
print(rng_m8)

```

```text

eSAFE-DX-PCG64-M4 generator
RNGX = DX-30-1 generator
  Multiplier = 1043282
  k = 30
  s = 1
RNGY = PCG64 XSL-RR 128/64
  Increment = 326307785045038373804293307865519234683
  Multiplier = 287840645
Output size = 4
DX log10(period) = 280.0
PCG64 log10(period) = 38.5
eSAFE-DX-PCG64-M4 log10(period) bounds:
  299.2 <= log10(period) <= 308.9

eSAFE-DX-PCG64-M8 generator
RNGX = DX-643-1 generator
  Multiplier = 187576
  k = 643
  s = 1
RNGY = PCG64 XSL-RR 128/64
  Increment = 133671686100213584896546080929544229227
  Multiplier = 818069925
Output size = 8
DX log10(period) = 6000.4
PCG64 log10(period) = 38.5
eSAFE-DX-PCG64-M8 log10(period) bounds:
  6038.4 <= log10(period) <= 6038.7

```

`DX-k-s` identifies the selected DX generator. Its multiplier appears under
`RNGX`; PCG64's increment and multiplier appear under `RNGY`.
The component periods and eSAFE period bounds are displayed as base-10 logarithms,
rounded to one decimal place.
Set `randomize=False` with a fixed seed for reproducible parameters.

## Use NumPy's Generator class with eSAFE generators

Connect the BitGenerators to NumPy's `Generator` class:

```python

>>> rng_m4 = Generator(rng_m4)
>>> rng_m4
Generator(_eSAFE_DX_PCG64_M4_Generator) at ...
>>> rng_m8 = Generator(rng_m8)
>>> rng_m8
Generator(_eSAFE_DX_PCG64_M8_Generator) at ...

```

## Generate random numbers


Once you have connected an eSAFE generator to NumPy's `Generator` class, 
you can begin generating random numbers. This step enables you to create 
random numbers based on your desired distribution or for various operations. 
To generate random numbers, simply call the appropriate method from 
the Generator class, such as `integers()`, `random()`, or others, 
depending on your specific needs. 
For other methods, see the
[NumPy Generator documentation](https://numpy.org/doc/stable/reference/random/generator.html).

These results are examples only and vary because the generators were initialized with
the default `randomize=True`.

### eSAFE-DX-PCG64-M4


```python

# sampling from distributions
print(rng_m4.normal(0, 1, 20)) # generate twenty N(0, 1) data
print(rng_m4.uniform(0, 1, 10)) # generate ten U(0, 1) data

# randomly choose
print(rng_m4.choice(["A", "B", "C", "D", "E"], size=30)) # choose thirty elements with replacement

# randomly shuffle
sample_m4 = ["A", "B", "C", "D", "E"]
rng_m4.shuffle(sample_m4)
print(sample_m4)

```

```text

[ 0.28229253 -0.61972031  0.91943674  0.23272928  1.43809961 -2.54698424
  0.35536073  0.18689282  0.33563218  0.65272061 -0.4014093   0.69678603
  0.1775565   1.18971809  0.8827062  -1.0257905   0.6752083   1.10724409
 -0.45134983  1.11178711]
[0.75393736 0.92056047 0.60859473 0.41986108 0.76181609 0.07393635
 0.44962221 0.69440046 0.20334808 0.58865514]
['E' 'B' 'A' 'E' 'A' 'D' 'E' 'C' 'D' 'D' 'D' 'E' 'C' 'D' 'D' 'E' 'B' 'B'
 'C' 'E' 'C' 'E' 'D' 'A' 'E' 'C' 'A' 'D' 'C' 'E']
['D', 'C', 'B', 'A', 'E']

```

### eSAFE-DX-PCG64-M8


```python

# sampling from distributions
print(rng_m8.normal(0, 1, 20)) # generate twenty N(0, 1) data
print(rng_m8.uniform(0, 1, 10)) # generate ten U(0, 1) data

# randomly choose
print(rng_m8.choice(["A", "B", "C", "D", "E"], size=30)) # choose thirty elements with replacement

# randomly shuffle
sample_m8 = ["A", "B", "C", "D", "E"]
rng_m8.shuffle(sample_m8)
print(sample_m8)

```

```text

[ 0.40620447  0.14056887  1.11489947 -2.03575715 -2.14711043  0.07681384
  1.38466229  0.08060586  0.51544986 -0.0230052  -0.62310468  0.79999741
 -1.35367978 -1.13678832 -0.91429379 -0.12897527  1.54652899 -0.44690311
  0.17522315  0.92325644]
[0.76046304 0.63745761 0.02117026 0.72118989 0.7717352  0.5639265
 0.84517745 0.7636521  0.61613797 0.66604258]
['B' 'A' 'A' 'D' 'A' 'C' 'D' 'D' 'C' 'B' 'E' 'B' 'D' 'E' 'B' 'D' 'C' 'B'
 'E' 'E' 'B' 'A' 'A' 'B' 'D' 'A' 'A' 'B' 'B' 'A']
['B', 'A', 'E', 'C', 'D']

```

## Parallel random number generation

To enable parallel computation, you can create multiple eSAFE generators with 
different `seed` values. This approach enables the creation of multiple 
low-correlation generators, 
reducing dependencies between random sequences in parallel processes.

```python

seeds = [308, 1, 2026]
generators = [
    Generator(eSAFE_DX_PCG64_M8(seed=seed, randomize=False))
    for seed in seeds
]

```

Use `eSAFE_DX_PCG64_M4` in the same pattern to create M4 generators.

## Compare generation speed

The [Evaluation](evaluation.md#numpy-generator-speed-comparison) reports the
following throughput indices, with MT19937 set to 100:

| Generator | Uniform | Overall |
|---|---:|---:|
| SAFE-DX-PCG64 | 114.0 | 68.9 |
| eSAFE-DX-PCG64-M4 | 164.0 | 101.8 |
| eSAFE-DX-PCG64-M8 | 193.0 | 113.6 |

M8's uniform throughput is approximately `193.0 / 114.0 = 1.69` times SAFE's;
its overall throughput is approximately `113.6 / 68.9 = 1.65` times SAFE's.
The overall index is the geometric mean across UInt32, UInt64, uniform, normal,
and exponential generation. These measurements used Windows 10 on an Intel
Core i5-8250 processor, with one million values per repetition and the minimum
elapsed time over 20 repetitions.