# What is New

## Version 0.3.0

## SAFE and eSAFE Generators

NextRNGBook now adds NumPy-compatible SAFE and eSAFE generator interfaces based on the SAFE construction. The new [`SAFE_DX_PCG64`](safe_dx_pcg64_generator.md#safe_dx_pcg64seed-randomize) generator combines a 32-bit DX generator and PCG64 through mutual shuffling and nonlinear output transformations. It produces one output value per internal SAFE update.

We also introduce two multi-output eSAFE variants, [`eSAFE_DX_PCG64_M4`](safe_dx_pcg64_generator.md#esafe_dx_pcg64_m4seed-randomize) and [`eSAFE_DX_PCG64_M8`](safe_dx_pcg64_generator.md#esafe_dx_pcg64_m8seed-randomize). These generators use the same DX-PCG64 baseline combination, but produce four or eight buffered output values per internal update. This design reduces the average update cost per returned value and improves throughput compared with the one-output SAFE construction.

For these generators, the DX parameter set, shuffle-table size, and burn-in length are selected internally from the resolved seed. By default, `randomize=True` mixes fresh system entropy and the current time with the optional user-provided seed, so repeated calls with the same seed are not reproducible. Users who need reproducible configurations and output sequences should set `randomize=False` and provide a fixed seed.

The SAFE and eSAFE generators are designed for workflows that require stronger mixing than a single classical generator while remaining convenient to use through NumPy's random `Generator` interface. For the construction details and notation, see [SAFE and eSAFE Generators](safe_generator.md).

## Version 0.2.0

We introduce a new faster DX generator API, [`DX`](dx_generator.md#dxdx_id-seed), which produces 32-bit random integers. 
At the same time, the previously released API `create_dx` has been renamed to [`DX32`](dx_generator.md#dx32dx_id-seed) to provide a cleaner and more consistent interface.

The [`DX`](dx_generator.md#dxdx_id-seed) is the recommended 32-bit pseudo-random number generator in this package. 
Its integer generation speed is close to PCG64 and comparable to MT19937 in our benchmark results. 
This naming scheme also leaves room for future extensions such as `DX64` and `DX128`, allowing generators with different output bit-widths to be distinguished more naturally.

In [`DX`](dx_generator.md#dxdx_id-seed), the parameter $p$ is fixed at $2^{31} - 1$ in order to accelerate the modular reduction step [[10]](index.md#references). 
However, this restriction does not reduce the number of distinct DX generators available in the package. 
Users who do not want to use DX generators with fixed $p = 2^{31} - 1$ can instead use [`DX32`](dx_generator.md#dx32dx_id-seed).

For generating $U(0,1)$ random numbers, [`DX`](dx_generator.md#dxdx_id-seed) is also slightly faster than MT19937 in our benchmark results. 
The tables below compare the generation speed of different RNGs.

For large-scale parallel computing, the DX generator provides a large number of distinct parameter sets. 
Different **dx_id** values in [`DX`](dx_generator.md#dxdx_id-seed) correspond to distinct parameterized generators rather than jumped positions within a single cycle. 
They also correspond to different period lengths, allowing users to choose generators with periods ranging from approximately $10^{28}$ to $10^{195009.3}$. 
In addition, the parameter $k$ in [`DX`](dx_generator.md#dxdx_id-seed) ranges from $3$ to $20897$, providing users with a wide spectrum of generator configurations. 
The longest available DX generator has a substantially longer period than both PCG64 and MT19937.