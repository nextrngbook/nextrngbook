This section will guide you through the steps to install **NextRNGBook** and begin
using **SAFE-DX-PCG64**. SAFE combines a DX generator and PCG64 through mutual
shuffling and output transformations. For faster generation with the same style
of interface, see the [eSAFE quick start](esafe_quick_start.md).

## Installation

To install NextRNGBook, use the Python package manager `pip` in your terminal:

```bash
pip install nextrngbook
```

## Import the package

NextRNGBook provides the underlying random number generator (RNG), while NumPy's
`Generator` provides random arrays, matrices, and distributions.

```python
from nextrngbook.safe_dx_pcg64 import SAFE_DX_PCG64
from numpy.random import Generator
```

## Create SAFE generators

Use `SAFE_DX_PCG64(seed=None, randomize=True)` to create a 32-bit SAFE-DX-PCG64
BitGenerator. For reproducible initialization, provide a fixed seed and set
`randomize=False`:

```python

>>> SAFE_DX_PCG64(seed=308, randomize=False)
Done. SAFE-DX-PCG64 generator combining DX and PCG64. Use print() function for details.

```
`SAFE_DX_PCG64(seed, randomize)` takes two parameters:

- seed: Selects the generator configuration and initializes its random state.
- randomize: Defaults to `True`, mixing fresh system entropy and the current time with the optional seed. Set it to `False` with a fixed seed for reproducible results.

With a fixed seed and `randomize=False`, recreating the same generator and making
the same calls in the same order reproduces the output. Setting only the seed
while leaving `randomize=True` does not reproduce the sequence. Omitting the seed
also gives non-reproducible initialization; using `seed=None` with
`randomize=False` emits a warning.

### How the seed selects the generators

The seed selects a specific DX generator from the built-in DX family, the
increment and multiplier of PCG64's underlying 128-bit LCG, and the SAFE
parameters: shuffle-table size and burn-in length.

When `randomize=True`, the supplied seed is mixed with the current time and
fresh system entropy at each initialization. As a result, two calls with the
same seed can select different DX generators and PCG64 parameter combinations:

```python

first_rng = SAFE_DX_PCG64(seed=308, randomize=True)
second_rng = SAFE_DX_PCG64(seed=308, randomize=True)

print(first_rng)
print(second_rng)

```

The following output was captured from one run. Your selected parameters will
vary between runs.

```text

SAFE-DX-PCG64 generator
RNGX = DX-643-2 generator
  Multiplier = 1005698
  k = 643
  s = 2
RNGY = PCG64 XSL-RR 128/64
  Increment = 321810466811985332752222242645818879953
  Multiplier = 209395773
Output size = 1
DX log10(period) = 6000.4
PCG64 log10(period) = 38.5
SAFE-DX-PCG64 log10(period) bounds:
  6038.4 <= log10(period) <= 6038.7

SAFE-DX-PCG64 generator
RNGX = DX-47-2 generator
  Multiplier = 655233
  k = 47
  s = 2
RNGY = PCG64 XSL-RR 128/64
  Increment = 154616762995081233930611975525065660705
  Multiplier = 2367324325
Output size = 1
DX log10(period) = 438.6
PCG64 log10(period) = 38.5
SAFE-DX-PCG64 log10(period) bounds:
  476.5 <= log10(period) <= 476.8

```

For reproducible results, use the same seed with `randomize=False`.
You can check that the same seed reproduces the same displayed configuration:

```python

first_rng = SAFE_DX_PCG64(seed=308, randomize=False)
second_rng = SAFE_DX_PCG64(seed=308, randomize=False)

print(first_rng)
print(second_rng)

```

```
SAFE-DX-PCG64 generator
RNGX = DX-21-2 generator
  Multiplier = 1044843
  k = 21
  s = 2
RNGY = PCG64 XSL-RR 128/64
  Increment = 135935203381921163399322660603397037679
  Multiplier = 1040453069
Output size = 1
DX log10(period) = 196.0
PCG64 log10(period) = 38.5
SAFE-DX-PCG64 log10(period) bounds:
  233.9 <= log10(period) <= 234.2

SAFE-DX-PCG64 generator
RNGX = DX-21-2 generator
  Multiplier = 1044843
  k = 21
  s = 2
RNGY = PCG64 XSL-RR 128/64
  Increment = 135935203381921163399322660603397037679
  Multiplier = 1040453069
Output size = 1
DX log10(period) = 196.0
PCG64 log10(period) = 38.5
SAFE-DX-PCG64 log10(period) bounds:
  233.9 <= log10(period) <= 234.2

```


## View SAFE generator info

Print the generator to view the selected DX and PCG64 parameters and period bounds.
With the default `randomize=True`, the selected parameters vary between runs.
The following is an example output; your selected parameters may differ.


```python

rng = SAFE_DX_PCG64(seed=1234)
print(rng)

```

```text

SAFE-DX-PCG64 generator
RNGX = DX-16-1 generator
  Multiplier = 1045946
  k = 16
  s = 1
RNGY = PCG64 XSL-RR 128/64
  Increment = 288090240644259864889480483407394584165
  Multiplier = 3735789477
Output size = 1
DX log10(period) = 149.3
PCG64 log10(period) = 38.5
SAFE-DX-PCG64 log10(period) bounds:
  166.8 <= log10(period) <= 177.3

```

`DX-k-s` identifies the selected DX generator. Its multiplier appears under
`RNGX`; PCG64's increment and multiplier appear under `RNGY`.
The component periods and SAFE period bounds are displayed as base-10 logarithms,
rounded to one decimal place.
Use `SAFE_DX_PCG64(seed=1234, randomize=False)` for reproducible parameters.



## Use NumPy's Generator class with SAFE generator

Connect the BitGenerator to NumPy's `Generator` class:

```python

>>> rng = Generator(rng)
>>> rng
Generator(_SAFE_DX_PCG64_Generator) at ...

```

## Generate random numbers

Once you have connected the SAFE generator to NumPy's `Generator` class, 
you can begin generating random numbers. This step enables you to create 
random numbers based on your desired distribution or for various operations. 
To generate random numbers, simply call the appropriate method from 
the Generator class, such as `integers()`, `random()`, or others, 
depending on your specific needs. 
For other methods, see the
[NumPy Generator documentation](https://numpy.org/doc/stable/reference/random/generator.html).

These results are examples only and vary because `rng` was initialized with
the default `randomize=True`.


```python

# sampling from distributions
print(rng.normal(0, 1, 20)) # generate twenty N(0, 1) data
print(rng.uniform(0, 1, 10)) # generate ten U(0, 1) data

# randomly choose
print(rng.choice(["A", "B", "C", "D", "E"], size=30)) # choose thirty elements with replacement

# randomly shuffle
sample_lst = ["A", "B", "C", "D", "E"]
rng.shuffle(sample_lst)
print(sample_lst)

```

```text

[-0.11485027  0.94695846  0.95250857 -0.34313106 -0.3635657  -0.50845618
  1.10615555 -1.29093797  0.08192415 -1.58250026  0.16862057  0.54727044
 -0.1975976  -0.83586377  0.30800551 -0.85332542  0.59108671 -0.88084771
  1.04877814  0.31928561]
[0.98075742 0.43397456 0.12049828 0.20096091 0.41844404 0.85844287
 0.73067284 0.44902526 0.90271112 0.75760493]
['C' 'D' 'C' 'E' 'C' 'A' 'D' 'E' 'B' 'C' 'B' 'C' 'C' 'E' 'E' 'B' 'A' 'E'
 'C' 'E' 'D' 'E' 'D' 'B' 'D' 'D' 'B' 'E' 'A' 'B']
['D', 'A', 'B', 'E', 'C']

```

## Parallel random number generation

To enable parallel computation, you can create multiple SAFE generators with 
different `seed` values. This approach enables the creation of multiple 
low-correlation generators, 
reducing dependencies between random sequences in parallel processes.

```python

seeds = [308, 1, 2026]
generators = [
    Generator(SAFE_DX_PCG64(seed=seed, randomize=False))
    for seed in seeds
]

```

## Extend usage with other libraries

NumPy's `Generator` can also be used with libraries such as SciPy that accept a
NumPy generator. Consult the library's documentation for the relevant interface.
