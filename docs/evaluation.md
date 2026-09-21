# Evaluation of random number generators

## Overview: PCG64, MT19937, DX, SAFE and eSAFE generators

The generators currently provided in this package include the **DX**, **SAFE**, and **eSAFE** generators. Here we compare them with two widely used generators, **PCG64** and **MT19937**.

PCG64 is a modern RNG with strong practical performance and fast output generation [[11]](index.md#references). MT19937 is the classical Mersenne Twister, well known for its long period and extensive use in simulation and scientific computing [[13]](index.md#references). The DX generator is a family of multiple recursive generators (MRGs) with flexible parameterization, very long periods, and strong equidistribution properties [[1]](index.md#references). SAFE is a combined-generator framework that uses two baseline generators together with mutual shuffling and output transformation, while eSAFE extends SAFE by producing multiple buffered outputs per internal update to improve generation efficiency.

The following sections compare these generators in terms of **speed**, **period**, **parallelization**, **flexibility and portability**, **equidistribution**, and **empirical testing with TestU01**.

## NumPy Generator Speed Comparison

The NumPy Generator benchmark measures relative throughput using
**MT19937 as the reference generator**, with the MT19937 throughput set
to 100. For each output type or distribution, each generator produces
$10^6$ random values per repetition. The benchmark is repeated **20
times**, and the **minimum elapsed time** is used to compute throughput.
The **overall** column is the geometric mean of the five relative
throughput indices [[1]](#references).

| Generator | UInt32 | UInt64 | Uniform | Normal | Exp. | Overall |
|---|---:|---:|---:|---:|---:|---:|
| MT19937 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| PCG64 | 149.5 | 160.6 | 186.0 | 134.3 | 155.8 | 156.3 |
| DX | 94.1 | 80.8 | 172.0 | 70.9 | 83.7 | 95.0 |
| SAFE-DX-PCG64 | 61.4 | 44.2 | 114.0 | 76.2 | 65.8 | 68.9 |
| eSAFE-DX-PCG64-M4 | 90.1 | 78.8 | 164.0 | 101.2 | 92.6 | 101.8 |
| eSAFE-DX-PCG64-M8 | 99.0 | 89.4 | 193.0 | 107.0 | 103.4 | 113.6 |

### Interpretation of Package RNG Performance

Among the NextRNGBook generators, DX achieves an overall relative throughput of 95.0. Its uniform generation is fast, although its overall performance is slightly lower than that of MT19937.

SAFE-DX-PCG64 has the lowest overall performance among the package generators because each output requires two baseline generators, mutual shuffling, and output transformation.

The buffered eSAFE variants substantially improve the generation speed relative to the original SAFE implementation. eSAFE-DX-PCG64-M4 achieves an overall relative throughput of 101.8, making it approximately 1.8% faster than MT19937. eSAFE-DX-PCG64-M8 reaches 113.6, corresponding to an approximately 13.6% improvement over MT19937.

!!! Note
    All timings were taken using Windows 10 on an Intel Core i5-8250 processor.


## Period Length

Period length is one of the key properties used to evaluate the quality of a random number generator (RNG). It refers to the number of generated values before the sequence starts repeating itself. In other words, once an RNG returns to the same state and begins producing the same sequence again, the number of generated values in that cycle is called its period. A good RNG should ideally have a sufficiently long period.

For the well-known PCG64, the generator is based on a 128-bit Linear Congruential Generator (LCG) and outputs 64-bit integers. Its period is $2^{128} \approx 10^{38.5}$. If the period of PCG64 is considered insufficient for a specific application, it can be extended by using the extension array technique [[1]](index.md#references). However, this extension comes at the cost of additional computation time.

The DX generator is a class of Multiple Recursive Generators (MRGs), and its period can be expressed as $p^{k} - 1$, where $p$ is the modulus and $k$ is the order of the recurrence, that is, the number of previous values stored and used to generate the next one [[3]](index.md#references). In the current package, the largest available DX generator can reach approximately $10^{195009.3}$ in period length.

Unlike PCG64, whose period can be enlarged by using an extension array with additional computational cost, the DX generator can achieve a much longer period simply by increasing the value of $k$. In practice, increasing $k$ mainly increases the amount of memory required to store previous states, but does not necessarily lead to a substantial increase in generation time. This gives users a flexible way to choose an appropriate DX generator according to the trade-off between period length and memory usage.

For SAFE, the period depends on the periods of its two baseline generators. If their periods are $P_X$ and $P_Y$, the combined period can be as large as $\operatorname{lcm}(P_X,P_Y)$ under suitable conditions [[2, 3]](#references). When the two periods are relatively prime, this becomes $P_XP_Y$. Therefore, the period of SAFE-DX-PCG64 depends on the selected DX configuration together with the period of PCG64.

The eSAFE generator uses the same baseline-generator combination and SAFE-style internal update while producing multiple buffered outputs from each internal update. Therefore, its period characteristics are also determined primarily by the underlying SAFE construction and its baseline generators.

Among the individual generators considered here, PCG64 has the shortest period, followed by MT19937 with period $2^{19937} - 1 \approx 10^{6001}$ [[13]](index.md#references), while the DX generator has the longest period overall. SAFE and eSAFE combine the state evolution of their baseline generators, so their period characteristics depend on the selected generator combination rather than on a single fixed period. Therefore, the DX, SAFE, and eSAFE generators provide users with considerable flexibility in selecting configurations with sufficiently long periods for their applications. Moreover, the set of DX generator parameters currently included in the package is not yet exhaustive, and more parameter combinations can be found through further algorithmic search.


## Parallelization

PCG64 can be used for parallel applications by creating multiple distinct streams.  
In the PCG framework, streams are mainly obtained by changing the **increment** of the underlying LCG [[17]](index.md#references). According to the PCG discussion, these streams are intended to be **distinct and useful**, but they should not be interpreted as being strictly statistically independent [[15]](index.md#references).

In practice, NumPy users usually use `spawn()` to create multiple PCG64 generators.  
Another option is **jump-ahead**, which moves the state forward by a large number of steps so that different generators start at distant positions in the same cycle.

For MT19937, jump-ahead can in principle be implemented through repeated multiplication of the transition matrix. In practice, this is not used directly because the matrix is too large. Instead, modern implementations rely on the characteristic polynomial and its corresponding jump polynomial [[13]](index.md#references). NumPy follows this latter approach. Although effective, this [method](https://numpy.org/doc/2.2/reference/random/bit_generators/generated/numpy.random.MT19937.jumped.html) is mathematically and computationally more complicated.

The DX generator can also be parallelized through jump-ahead in principle [[1]](index.md#references). 
However, in the current package, parallelization is achieved by selecting different **dx_id** values, each corresponding to a different RNG.
Unlike jump-ahead, where generators are taken from different positions of the same cycle, different `dx_id` values correspond to different cycles. As a result, this approach avoids the risk of overlapping sequences and is also much simpler to implement in practice.

SAFE provides additional flexibility for parallel workflows because different workers can use different combinations of baseline generators. In NextRNGBook, workers can use different DX parameter configurations and seeds together with PCG64, allowing the SAFE construction to combine different underlying random streams across parallel workers.

The eSAFE generator uses the same baseline-generator structure as SAFE, so the same approach can also be applied to eSAFE configurations. Different workers can use different DX configurations and seeds while retaining the buffered multi-output construction of eSAFE.

In parallel settings, PCG64 and MT19937 rely on stream spawning or jump-ahead methods to produce multiple usable substreams. These methods are practical, but they still derive streams within the same generator family. For PCG64 streams, even the PCG discussion notes that such streams are distinct and useful rather than strictly statistically independent. By contrast, DX allows users to select different `dx_id` values corresponding to different parameter configurations, while SAFE and eSAFE can additionally combine different baseline-generator configurations across workers. This gives the NextRNGBook generators a flexible way to construct multiple random streams for parallel applications.


## Flexibility and Portability

The [PCG family](https://www.pcg-random.org/using-pcg-c.html) provides random number generators with multiple output sizes, including 8-, 16-, 32-, and 64-bit variants. For example, PCG64 uses a 128-bit linear congruential generator (LCG) to update its internal state and produces 64-bit random numbers as output.

From a strict hardware perspective, this does not necessarily mean that the LCG update is performed as a native 128-bit integer operation. Most mainstream processors do not execute a full 128-bit LCG state update as a single scalar integer instruction. Instead, the 128-bit update is usually decomposed into multiple lower-width operations, commonly using 64-bit arithmetic.

Therefore, PCG64 remains portable across systems, but its performance may depend on how efficiently the compiler and platform implement the required 128-bit arithmetic. Implementations of PCG are available in multiple programming languages. 

MT19937 is a 32-bit random number generator and is one of the default random number generators in [R](https://stat.ethz.ch/R-manual/R-devel/library/base/html/Random.html). A 64-bit variant, MT19937-64 [[14]](index.md#references), is also available. Because Mersenne Twister has been widely used for many years, stable implementations can be found across different operating systems and programming languages.

The current version of our DX generator package mainly provides a 32-bit implementation. However, from an algorithmic point of view, the DX generator can also be extended to 64-bit and 128-bit versions[[16]](index.md#references). This gives it the potential to be applied across different operating systems and programming languages as well.

In addition to output-width flexibility, the DX generator allows users to select different parameter configurations through `dx_id`. Each configuration corresponds to a different set of DX parameters, allowing users to choose among different generators according to their application requirements.

SAFE provides another form of flexibility because its construction can combine any two random number generators as its baseline generators. Users can therefore select different RNG combinations according to their application requirements rather than being restricted to a fixed pair of generators. For example, NextRNGBook currently provides SAFE and eSAFE configurations based on the DX generator and PCG64. The flexibility of the DX parameter configurations can also be retained within these combined generators by selecting different DX configurations.


## Equidistribution

Equidistribution describes whether an RNG can provide different possible outputs with nearly equal frequency over a long sequence.
If an RNG has this property, then in sufficiently many generated values, different outcomes will appear with approximately the same frequency.  

### Definition 

Suppose an RNG generates the sequence $X_{-k}, \dots, X_{-1}, X_{0}, X_{1}, \dots$ where $X_{i} \in \mathbb{Z}_{p}$, and
let its period be $r$. The RNG is said to be equidistributed in t dimensions, if the following property holds true for every $1 \leq d \leq t$: Consider all $r$ possible distinct $d$-tuples of successive elements from $i$, i.e., $(X_{i}, \dots, X_{i+d-1}), (X_{i+1}, \dots, X_{i+d}), \dots, (X_{i+r-1}, \dots, X_{i+r+d-2}).$
Then, amongst them all the possible $P^{t}$ tuples will occur with almost equal frequency. [[1]](index.md#references)

The equidistribution property of PCG64 is not explicitly stated on its official website, and the upper limit depends on the specific construction being used. For the PCG64 currently provided in NumPy, whose period is $2^{128}$, the theoretical upper bound implied by the definition of equidistribution is $4$. As mentioned earlier, the extension array technique can be used to increase the equidistribution dimension.

MT19937 is 623-dimensionally equidistributed at 32-bit accuracy [[13]](index.md#references).
For the DX generator, the equidistribution dimension is determined by the order $k$ of the underlying MRG. [[3]](index.md#references)

High-dimensional equidistribution is also considered in the design of SAFE. By combining baseline generators with strong statistical properties, such as a high-dimensional DX generator, SAFE is designed to retain the favorable properties of its components while adding mutual shuffling and output transformations. [[2]](#references)

eSAFE uses the same baseline-generator construction as SAFE but produces multiple buffered outputs per internal update. It therefore retains the advantage of selecting generators with strong equidistribution properties.

Based on the discussion above, PCG64 has the lowest equidistribution dimension among the three individual generators, followed by MT19937. For the parameter sets currently provided in this package, the DX generator can achieve the upper limit of 20897-dimensional equidistribution. This indicates that, in terms of high-dimensional equidistribution, the DX generator performs best among the three individual RNGs.


## Empirical Test: TestU01 Results

TestU01 [[9]](index.md#references) is a widely used empirical test suite for random number generators, designed to detect statistical bias, correlation, and other structural defects in generated sequences. In this empirical comparison, we use **PCG32** instead of **PCG64** so that all generators are evaluated on the same 32-bit output basis. This makes the comparison with **MT19937**, **DX-k-1**, **DX-k-2** and **eSAFE-DX1-PCG64-M8** more consistent and fair.

For the DX generators, the notation **DX-k-1** and **DX-k-2** is used in the empirical evaluation. Here, $k$ denotes the recurrence order of the DX generator, while the final number denotes the DX generator type $s$. Therefore, **DX-k-1** represents a DX generator with recurrence order $k$ and type $s=1$, whereas **DX-k-2** represents a DX generator with recurrence order $k$ and type $s=2$.

When the recurrence order is not explicitly included in a combined-generator name, **DX1** and **DX2** denote DX generators of type $s=1$ and $s=2$, respectively. The exact recurrence order and parameter configuration are determined by the corresponding evaluation setup.

For **PCG32** and **MT19937**, we used seeds from 1234 to 1258, resulting in 25 independent Crush runs for each generator. Since the Crush battery reports 144 test statistics, each of these generators produced $144 \times 25$ p-values in total.

For **DX-k-1** and **DX-k-2**, we also performed 25 Crush runs for each generator class. These two classes correspond to the two recurrence structures of the DX generator family described in the [DX generator section](index.md#dx-generators-a-class-of-efficient-mrgs). In each class, we selected 25 different values of $k$, each paired with a corresponding multiplier $B$. The detailed parameter settings are listed below.

For **eSAFE-DX1-PCG64-M8**, we performed 25 Crush runs using the same 25
DX-k-1 parameter configurations described above.

To summarize the empirical results, we recorded the proportions of p-values falling into several extreme ranges. An RNG is considered to perform well if these observed proportions are close to the theoretical proportions expected under a uniform distribution.


| p-value | $<10^{-4}$ | $<10^{-3}$ | $>1-10^{-3}$ | $>1-10^{-4}$ | $>1-10^{-15}$ |
|---|---:|---:|---:|---:|---:|
| **PCG32** |  |  |  |  |  |
| Proportion | 0.000278 | 0.000556 | 0.001111 | 0 | 0 |
| **MT19937** |  |  |  |  |  |
| Proportion | 0.000278 | 0.001389 | 0.014722 | 0.013889 | 0.013889 |
| **DX-k-1** |  |  |  |  |  |
| Proportion | 0 | 0.002222 | 0.000556 | 0 | 0 |
| **DX-k-2** |  |  |  |  |  |
| Proportion | 0.000278 |	0.001111 | 0.000556 |	0.000278 | 0 |
| **eSAFE-DX1-PCG64-M8** |  |  |  |  |  |
| Proportion | 0.000000 | 0.001111 | 0.001111 | 0.000278 | 0.000000 |

The detailed $(k, B)$ pairs used for **DX-k-1** and **DX-k-2** are listed below. Since DX generators with $k=2$ showed relatively poor performance in the Crush tests, they are currently excluded from the provided parameter set.

??? info "Parameter settings used in the Crush tests"
    **DX-k-1**
    
    ```text
    (3, 523793), (4, 1048274), (5, 524251), (20, 1045152), (21, 1045311),
    (22, 523411), (23, 1046670), (24, 521749), (26, 1044443), (27, 523797),
    (30, 1043894), (34, 524043), (39, 522706), (42, 1044205), (47, 2096778),
    (48, 1040215), (51, 521799), (52, 523729), (60, 1037046), (102, 1042679),
    (120, 1028648), (643, 4178499), (1597, 918398), (7499, 876798), (20897, 900942)
    ```

    **DX-k-2**
    
    ```text
    (3, 524055), (4, 1048421), (5, 523992), (20, 1044873), (21, 1045412),
    (22, 522821), (23, 1046205), (24, 522948), (26, 1044091), (27, 520325),
    (30, 519311), (34, 1044586), (39, 1044247), (42, 521662), (47, 99565),
    (48, 1044752), (51, 519906), (52, 1047593), (60, 519980), (102, 1037411),
    (120, 522191), (643, 201330), (1597, 893161), (7499, 768842), (20897, 1028880)
    ```

#### Interpretation of the TestU01 Results

When a generator behaves like an ideal uniform random number generator, its p-values should approximately follow the uniform distribution over $(0,1)$. Therefore, the observed proportions of p-values in the specified ranges can be compared with their expected proportions.

A very small p-value indicates a more significant test result and may suggest that the generator performs poorly in that test. A p-value extremely close to $1$ is also undesirable because the result may appear too regular to be truly random. The table reports the proportions of p-values near these two extremes. In general, proportions closer to their expected values indicate better empirical behavior.

DX-k-1, DX-k-2, eSAFE-DX1-PCG64-M8, and PCG32 produce only small proportions of p-values near $0$ or $1$. Their proportions around the $10^{-3}$ threshold are generally close to the expected value of $0.001$, and they produce few or no p-values beyond the more extreme thresholds.

In contrast, MT19937 produces a much larger proportion of p-values close to $1$. In particular, the proportion above $1-10^{-15}$ is $0.013889$, which is much larger than the expected value. Therefore, MT19937 shows poorer empirical behavior than the other generators in this evaluation.


## Summary

The benchmark results show that the DX generator delivers performance close to MT19937, with overall relative-throughput scores of 95.0 and 100.0, respectively. SAFE-DX-PCG64 is substantially slower because each output requires advancing two baseline generators, performing mutual shuffling, and applying the output-mixing transformation. eSAFE reduces this average cost by producing and buffering multiple outputs during each internal update. The results also demonstrate that the number of buffered outputs affects performance: eSAFE-DX-PCG64-M8 achieves an overall score of 113.6, compared with 101.8 for eSAFE-DX-PCG64-M4. Thus, in this benchmark, both eSAFE variants outperform MT19937 in terms of overall throughput, while the eight-output configuration is faster than the four-output configuration.

PCG64 remains the fastest generator in this benchmark, with an overall relative-throughput score of 156.3. However, speed should not be the only criterion used to select a random number generator. NumPy's PCG64 has a maximal period of $2^{128}$, whereas maximal-period DX generators can provide substantially longer periods depending on the modulus and recurrence order, together with an explicit high-dimensional equidistribution guarantee. DX also provides flexibility through different parameter configurations, while SAFE and eSAFE can combine different baseline generators and retain the favorable properties of the selected components. Deng et al. [[2]](#references) recommend DX and MT19937 for their HELP properties, but the SAFE construction also supports other RNG combinations, such as DX and PCG64 used here. These features also provide additional flexibility for constructing random streams in parallel applications.

The TestU01 results further show that PCG32, DX-k-1, DX-k-2, and eSAFE-DX1-PCG64-M8 produce only small proportions of extreme p-values in this evaluation, while MT19937 produces a noticeably larger proportion of p-values close to $1$. Overall, the results indicate that generator selection should consider not only generation speed, but also period length, equidistribution, empirical statistical performance, flexibility, portability, and behavior in parallel environments.


## references

[1] https://numpy.org/doc/stable/reference/random/performance.html

[2] Deng, L. Y., Shiau, J. J. H., Lu, H. H. S., & Bowman, D. (2018). 
*Secure and fast encryption (SAFE) with classical random number generators.* ACM Transactions on Mathematical Software (TOMS), 44(4), 1-17.

[3] Li, C. Y., Chen, Y. H., Chang, T. Y., Deng, L. Y., & To, K. (2011). 
Period extension and randomness enhancement using high-throughput reseeding-mixing PRNG. IEEE Transactions on Very Large Scale Integration (VLSI) Systems, 20(2), 385-389.