This section will guide you through the steps to install **NextRNGBook** and begin 
applying its functionality. If you're new to this package, follow the instructions 
below to get started smoothly.

## Installation

To install NextRNGBook, you can use the Python package manager `pip` 
in your terminal or command line interface:

```bash
pip install nextrngbook

``` 

## Import the package

After installing NextRNGBook, you can start by importing the package in your Python script.
You will need to import both NextRNGBook and NumPy.
NextRNGBook is designed to work with the underlying uniform random number generators (RNGs), 
while NumPy is used for higher-level operations such as generating random arrays, 
matrices, and distributions.

```python

from nextrngbook.dx_generator import DX32
from numpy.random import Generator

```

## Create the DX32 generators

NextRNGBook provides the `DX32` function to initialize a specific DX generator 
from the DX generator family, which includes over 4,000 built-in DX generators.
By calling this function, you can create an instance of a 32-bit 
DX generator that can be used for further operations.

```python

>>> DX32()
_DX32Generator(bb=1016882, pp=2146123787, kk=50873, ss=2, log10_period=474729.3125)

```

`DX32(dx_id, seed)` takes two parameters:

- dx_id: Select a specific DX generator from the DX generator family (over 4,000 options).
- seed: Sets the RNG state for reproducibility, provided that the seed is not `None`.

```python

>>> DX32(dx_id=4000, seed=101)
_DX32Generator(bb=1046381, pp=2147472413, kk=1301, ss=2, log10_period=12140.7998046875)

``` 

In short, `dx_id` determines the specific DX generator, 
and `seed` ensures reproducibility.
For more details on potential issues with `dx_id` values and reproducibility,
refer to the [API Reference section](dx_generator.md).

## View DX32 generator info

To obtain information about the created DX32 generator, you can print it out.

```python

rng = DX32(dx_id=3999)
print(rng)

``` 

    DX-1301-2 generator
    Multiplier = 1073694173
    Modulus    = 2146412747
    The log₁₀(period) of the PRNG is 12140.6

## Use NumPy's Generator class with DX32 generator

After creating a DX generator with `DX32()`, you can easily connect it to NumPy's `Generator` class.

```python

>>> rng = Generator(rng)
>>> rng
Generator(_DX32Generator) at ...

```

## Generate random numbers

Once you have connected the DX32 generator to NumPy's `Generator` class, 
you can begin generating random numbers. This step enables you to create 
random numbers based on your desired distribution or for various operations. 
To generate random numbers, simply call the appropriate method from 
the Generator class, such as `integers()`, `random()`, or others, 
depending on your specific needs. 
For more information about the available methods, you can consult the 
[NumPy documentation](https://numpy.org/doc/stable/reference/random/generator.html).
Here are some examples of generating random numbers using NumPy’s 
`Generator` with the DX32 generator.

```python

# sampling from distributions
print(rng.normal(0, 1, 20)) # generate twenty N(0, 1) numbers
print(rng.uniform(0, 1, 10)) # generate ten U(0, 1) numbers

# randomly choose
print(rng.choice(["A", "B", "C", "D", "E"], size=30)) # choose thirty characters with replacement

# randomly shuffle
sample_list = ["A", "B", "C", "D", "E"]
rng.shuffle(sample_list)
print(sample_list)

```

    [ 0.9675613   0.02286751 -0.38035958 -0.01384253  0.6106962  -1.92184568
    -0.45067837  0.0921393   0.69926803 -0.95657378  0.92652911 -0.24563696
    0.15562752 -0.12132903 -0.65024288  1.15093465 -1.18781621  0.71311705        
    -1.78001902 -0.1650059 ]
    [0.6201113  0.87789956 0.53011399 0.34411134 0.49926639 0.71827615
    0.98419978 0.69029694 0.5248014  0.89018867]
    ['A' 'B' 'D' 'A' 'B' 'D' 'C' 'E' 'B' 'D' 'D' 'D' 'A' 'E' 'A' 'E' 'B' 'D'        
    'C' 'C' 'D' 'D' 'A' 'E' 'C' 'C' 'C' 'C' 'E' 'A']
    ['C', 'A', 'D', 'E', 'B']


## Parallel random number generation

To enable parallel computation, you can create multiple DX generators with 
different `dx_id` values. This approach enables the creation of multiple 
low-correlation generators, 
reducing dependencies between random sequences in parallel processes.

```python

from nextrngbook.dx_generator import DX32
from numpy.random import Generator

# creat multiple DX32 generators with different dx_id values
generators = [Generator(DX32(dx_id=i)) for i in range(4100, 4108)]

```

## Extend usage with other libraries 

NumPy's `Generator`, beyond basic random number generation, can be integrated
with libraries such as SciPy for scientific computing and SymPy for symbolic
computation. For more information, refer to their respective documentation.