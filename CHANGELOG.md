# Changelog

## 0.3.0

### Added

- Added the `nextrngbook.safe_dx_pcg64` subpackage with three NumPy-compatible BitGenerator interfaces.
- Added `SAFE_DX_PCG64()`, which combines a 32-bit DX generator and PCG64 through mutual shuffling and output transformations, producing one 32-bit output per internal update.
- Added `eSAFE_DX_PCG64_M4()` and `eSAFE_DX_PCG64_M8()`, which buffer four and eight 32-bit outputs per internal update, respectively, to reduce the average update cost per returned value.
- Added seed-based selection of DX and PCG64 parameters, shuffle-table size, and burn-in length for SAFE and eSAFE generators.
- Added SAFE and eSAFE quick starts, API and construction references, and generator evaluation documentation.
- Added tests comparing SAFE and eSAFE outputs with a Python reference implementation, including M4 and M8 buffer transitions.
- Added internal benchmarking support for DX, DX32, SAFE, and eSAFE generators.

### Notes

- SAFE and eSAFE generators can be used with NumPy's `Generator` for random arrays, sampling, and distributions.
- The new interfaces default to `randomize=True`, mixing fresh system entropy and the current time with the optional seed. Providing the same seed alone does not reproduce the sequence.
- For reproducible configurations and output sequences, provide a fixed seed and set `randomize=False`. Calling with `seed=None` and `randomize=False` emits a warning and remains non-reproducible.

## 0.2.0

### Changed
- Updated the DX generator API structure.
- `DX()` is now the recommended fast 32-bit DX generator.
- `DX32()` is the general 32-bit DX generator interface.
- Updated documentation to clarify the difference between `DX()` and `DX32()`.

### Notes
- `DX()` fixes the modulus at \(2^{31} - 1\) and uses a fast reduction step for improved speed.
- `DX()` should be understood as a fast DX implementation rather than the fully general DX generator.
- Users who require the general DX generator should use `DX32()`.
