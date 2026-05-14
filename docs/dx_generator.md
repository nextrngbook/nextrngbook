!!! danger "Caution"
    The `dx_generator` subpackage is 
    **not recommended for cryptographic applications**.  
    It is intended for statistical simulations or machine learning tasks only.

!!! note "DX and DX32"
    The `DX()` API is the recommended fast 32-bit DX generator in this package.
    It fixes the modulus parameter at \(2^{31} - 1\) to accelerate modular
    reduction.

    The `DX32()` API provides a more general 32-bit DX generator family with
    broader parameter choices. Use `DX()` when speed and the default
    recommended configuration are preferred, and use `DX32()` when more
    flexible parameter selection is needed.

::: src.nextrngbook.dx_generator
    options:
        members: false
        show_root_heading: false
        show_source: false
        
---

### `DX(dx_id, seed)`

!!! tip "Example `dx_id` values"
    | dx_id | k  | s | B      | p         | log₁₀(period) |
    |-------|-----|----|---------|------------|---------------|
    | 0     | 3    | 1  | 523697      | 2147483647 | 28.0         |
    | 556   | 4    | 2  | 523345      | 2147483647 | 37.3         |
    | 1030  | 6    | 2  | 523867      | 2147483647 | 56           |
    | 2500  | 13   | 1  | 1046957     | 2147483647 | 121.3        |
    | 5000  | 24   | 2  | 518514      | 2147483647 | 224          |
    | 10000 | 47   | 2  | 646323      | 2147483647 | 438.6        |
    | 14769 | 20897| 2  | 1028880     | 2147483647 | 195009.3     |

Since `DX` with $k=2$ showed relatively poor performance in the Crush tests, they are currently excluded from the provided parameter set.

::: src.nextrngbook.dx_generator.DX
    options:
        show_signature: true
        show_source: false
        show_root_heading: false


!!! note "To ensure reproducibility for the RNG"    
    1. The `seed` should be provided with a fixed value (non-None).    
    2. The `dx_id` should be fixed by explicitly providing a specific integer
    value, such as `270`. Do not rely on the default `dx_id=None` if exact
    reproducibility is required.    
         
!!! danger "Caution" 
    If multiple `dx_id` values exceeding the valid range are provided, 
    they might be mapped to the same internal `dx_id`. This could lead to 
    the misconception that different, independent RNGs are being used, while 
    in fact they are the same. A warning will be issued to inform the user 
    about this mapping. Care should be taken when applying such mappings across 
    multiple threads or processes, 
    as they may introduce high correlations among results. <br><br>
    
    The fast reduction used in `DX()` is designed for speed. It maps
    intermediate values into the range \([0, 2^{31}-1]\), but it is not the
    same as the fully general modular reduction used by the general DX
    generator definition. For applications that require the general DX
    formulation, use `DX32()` instead.

---

### `get_dx_max_id()`

::: src.nextrngbook.dx_generator.get_dx_max_id
    options:
        show_signature: true
        show_source: false
        show_root_heading: false

---

### `get_dx_id_table()`

::: src.nextrngbook.dx_generator.get_dx_id_table
    options:
        show_signature: true
        show_source: false
        show_root_heading: false


### `DX32(dx_id, seed)` 


!!! tip "Example `dx_id` values"
    | dx_id | k  | s | B      | p         | log₁₀(period) |
    |-------|-----|----|---------|------------|---------------|
    | 0     | 2   | 1  | 32693   | 2147483249 | 18.7          |
    | 556   | 3   | 2  | 32736   | 2147483579 | 28            |
    | 1030  | 5   | 1  | 32711   | 2147483497 | 46.7          |
    | 2000  | 8   | 1  | 32743   | 2147483269 | 74.7          |
    | 3000  | 13  | 2  | 32754   | 2147481143 | 121.3         |
    | 4000  | 1301| 2  | 1046381 | 2147472413 | 12140.8       |
    | 4194  | 50873| 2 | 1016882 | 2146123787 | 474729.3      |


::: src.nextrngbook.dx_generator.DX32
    options:
        show_signature: true
        show_source: false
        show_root_heading: false


!!! note "To ensure reproducibility for the RNG"    
    1. The `seed` should be provided with a fixed value (non-None).    
    2. The `dx_id` should be fixed by explicitly providing a specific integer
    value, such as `270`. Do not rely on the default `dx_id=None` if exact
    reproducibility is required.   
         
!!! danger "Caution" 
    If multiple `dx_id` values exceeding the valid range are provided, 
    they might be mapped to the same internal `dx_id`. This could lead to 
    the misconception that different, independent RNGs are being used, while 
    in fact they are the same. A warning will be issued to inform the user 
    about this mapping. Care should be taken when applying such mappings across 
    multiple threads or processes, 
    as they may introduce high correlations among results.


---

### `get_dx32_max_id()`

::: src.nextrngbook.dx_generator.get_dx32_max_id
    options:
        show_signature: true
        show_source: false
        show_root_heading: false

---

### `get_dx32_id_table()`

::: src.nextrngbook.dx_generator.get_dx32_id_table
    options:
        show_signature: true
        show_source: false
        show_root_heading: false

