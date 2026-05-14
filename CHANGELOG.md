# Changelog

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