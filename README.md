# NextRNGBook: A Random Number Generation Package for RNG Book

## Introduction

The goal of **NextRNGBook** package is to incorporate a variety of high-quality random number 
generators (RNGs) from 
*Random Number Generators for Computer Simulation and Cyber Security* [[1]](#references). 
NextRNGBook currently provides a Python package designed for seamless compatibility with **NumPy**, allowing it to integrate easily into existing scientific computing workflows. It offers a range of modern random number generation techniques for scientific computing, large-scale simulations, reinforcement learning and cryptographic applications. In addition to the Python implementation, C and R implementations are planned to provide users with more options across different programming environments.


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

## Current Python Package APIs

NextRNGBook currently provides two DX generator interfaces:

- `DX()`: the recommended fast 32-bit DX generator.
- `DX32()`: a more general 32-bit DX generator family with broader parameter choices.

Version 0.3.0 adds three SAFE and eSAFE generator interfaces in `nextrngbook.safe_dx_pcg64`:

- `SAFE_DX_PCG64()`: combines a 32-bit DX generator and PCG64 through mutual shuffling and output transformations, producing one 32-bit output per internal update.
- `eSAFE_DX_PCG64_M4()`: a multi-output SAFE variant that produces and buffers four 32-bit outputs per internal update.
- `eSAFE_DX_PCG64_M8()`: a multi-output SAFE variant that produces and buffers eight 32-bit outputs per internal update.

All five APIs provide BitGenerators that work with NumPy's `Generator` for random arrays, sampling, and distributions.

## Documentation & Distribution

For full details, please refer to the links.
- **Documentation**: [NextRNGBook Documentation](https://nextrngbook.github.io/nextrngbook/)
- **PyPI**: [NextRNGBook on PyPI](https://pypi.org/project/nextrngbook/)


## References

[1] Deng, L.-Y., Kumar, N., Lu, H. H.-S., & Yang, C.-C. (2025). 
*Random Number Generators for Computer Simulation and Cyber Security:
 Design, Search, Theory, and Application* (1st ed.). Springer. 
 [https://doi.org/10.1007/978-3-031-76722-7](https://doi.org/10.1007/978-3-031-76722-7)
