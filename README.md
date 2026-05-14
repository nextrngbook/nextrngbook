# NextRNGBook: A Python Random Number Generation Package for RNG Book

## Introduction

The goal of **NextRNGBook** package is to incorporate a variety of high-quality random number 
generators (RNGs) from 
*Random Number Generators for Computer Simulation and Cyber Security* [[1]](#references). 
Designed for seamless compatibility with **NumPy**, 
this Python package can integrate easily into existing workflows, 
offering a wide range of selections from state-of-the-art random number generation techniques 
suitable for scientific computing, large-scale simulations, and cryptographic applications.

The goal of designing high-quality random number generators is to produce variates 
that behave like truly random numbers. 
This means the generated variates can cover the space evenly over high dimensions, 
and do not repeat for a very long time. 
They can be generated efficiently across different systems, 
and they can pass a wide range of statistical tests that detect hidden patterns. 
A good RNG should perform reliably for large-scale simulations with 
a strong support for parallel computing, 
and an easy integration across various computing platforms. 
For security applications,  generated variates need to be unpredictable, 
so that future values cannot be inferred from past outputs.

There are several  high-quality RNGs to be implemented in this NextRNGBook Package which should provide a solid foundation 
for better statistical simulation and/or secure applications. 
Combining strong theoretical supports and great practical performance, 
NextRNGBook can help users to explore, evaluate, and 
apply high-quality RNGs in a modern Python environment.

## Current APIs

NextRNGBook currently provides two DX generator interfaces:

- `DX()`: the recommended fast 32-bit DX generator.
- `DX32()`: a more general 32-bit DX generator family with broader parameter choices.

Both APIs are compatible with NumPy's `Generator` interface.

## Documentation & Distribution

For full details, please refer to the links.
- **Documentation**: [NextRNGBook Documentation](https://nextrngbook.github.io/nextrngbook/)
- **PyPI**: [NextRNGBook on PyPI](https://pypi.org/project/nextrngbook/)


## References

[1] Deng, L.-Y., Kumar, N., Lu, H. H.-S., & Yang, C.-C. (2025). 
*Random Number Generators for Computer Simulation and Cyber Security:
 Design, Search, Theory, and Application* (1st ed.). Springer. 
 [https://doi.org/10.1007/978-3-031-76722-7](https://doi.org/10.1007/978-3-031-76722-7)