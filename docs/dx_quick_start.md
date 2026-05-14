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

After installing NextRNGBook, you can start by importing the package in your 
Python script. You will need to import both NextRNGBook and NumPy. 
NextRNGBook is designed to work with the underlying uniform random number generators (RNGs), 
while NumPy is used for higher-level operations such as generating random arrays, 
matrices, and distributions.

```python

from nextrngbook.dx_generator import DX
from numpy.random import Generator

``` 

## Create DX generators

NextRNGBook provides the `DX` function to initialize a specific DX generator 
from the DX generator family, which includes over 10,000 built-in DX generators. 
By calling this function, you can create an instance of a 32-bit 
DX generator that can be used for further operations.

```python

>>> DX()
_DXGenerator(bb=24184, pp=2147483647, kk=47, ss=2, log10_period=438.6000061035156)

```

`DX(dx_id, seed)` takes two parameters:

- dx_id: Selects a specific DX generator from the DX generator family (over 10,000 options).
- seed: Sets the RNG state for reproducibility, provided that the seed is not `None`.

```python

>>> DX(dx_id=10000, seed=308)
_DXGenerator(bb=646323, pp=2147483647, kk=47, ss=2, log10_period=438.6000061035156)

```

In short, `dx_id` determines the specific DX generator, 
and `seed` ensures reproducibility.
For more details on potential issues with `dx_id` values and reproducibility,
refer to the [API Reference section](dx_generator.md).


## View DX generator info 

To obtain information about the created DX generator, you can print it out.

```python

rng = DX(dx_id=9999)
print(rng)

``` 

    DX-47-2 generator
    Multiplier = 646173
    Modulus    = 2147483647
    The log₁₀(period) of the PRNG is 438.6

## Use NumPy's Generator class with DX generator

After creating a DX generator with `DX()`, you can easily connect it to 
NumPy's `Generator` class.

```python

>>> rng = Generator(rng)
>>> rng
Generator(_DXGenerator) at ...

``` 

## Generate random numbers

Once you have connected the DX generator to NumPy's `Generator` class, 
you can begin generating random numbers. This step enables you to create 
random numbers based on your desired distribution or for various operations. 
To generate random numbers, simply call the appropriate method from 
the Generator class, such as `integers()`, `random()`, or others, 
depending on your specific needs. 
For more information about the available methods, you can consult the 
[NumPy documentation](https://numpy.org/doc/stable/reference/random/generator.html).
Here are some examples of generating random numbers using NumPy’s 
`Generator` with the DX generator.


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

    [ 1.85811761  1.51038657 -0.46972854  2.54010018  1.3581735  -0.19969388
    -0.76451271  0.19767763 -0.80287183 -0.45321281  1.30631922  1.62328021        
    -0.87913752 -0.25868414 -0.47459769 -0.11657998  1.16520699 -0.08221444        
    0.72956116 -0.80021773]
    [0.49784149 0.08103851 0.51156899 0.31261863 0.0444274  0.35562973
    0.90995614 0.64610098 0.69553556 0.1983629 ]
    ['D' 'B' 'B' 'A' 'A' 'A' 'E' 'C' 'D' 'E' 'C' 'D' 'E' 'E' 'B' 'D' 'B' 'B'        
    'B' 'A' 'E' 'D' 'E' 'B' 'B' 'D' 'E' 'B' 'A' 'B']
    ['A', 'E', 'C', 'D', 'B']


## Parallel random number generation

To enable parallel computation, you can create multiple DX generators with 
different `dx_id` values. This approach enables the creation of multiple 
low-correlation generators, 
reducing dependencies between random sequences in parallel processes.

```python

from nextrngbook.dx_generator import DX
from numpy.random import Generator

# Create multiple DX generators with different dx_id values
generators = [Generator(DX(dx_id=i)) for i in range(14760, 14769)]

``` 


## Extend usage with other libraries

NumPy’s `Generator`, beyond basic random number generation, can be integrated 
with libraries such as SciPy for scientific computing and SymPy for symbolic 
computation. For more information, refer to their respective documentation.
