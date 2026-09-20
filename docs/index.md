# NextRNGBook: A Python Random Number Generation Package for RNG Book


## Introduction

The goal of **NextRNGBook** package is to incorporate a variety of high-quality random number 
generators (RNGs) from 
*Random Number Generators for Computer Simulation and Cyber Security* [[1]](#references). 
Designed for seamless compatibility with **NumPy**, 
this Python package can integrate easily into existing workflows, 
offering a wide range of selections from state-of-the-art random number generation techniques 
suitable for scientific computing, large-scale simulations, reinforcement learning, and cryptographic applications.

The goal of designing high-quality random number generators is to produce variates 
that behave like truly random numbers. 
This means the generated variates can cover the space evenly over high dimensions, 
and do not repeat for a very long time. 
They can be generated efficiently across different systems, 
and they can pass a wide range of statistical tests that detect hidden patterns. 
A good RNG should perform reliably for large-scale simulations with strong support for parallel computing, easy integration across various computing platforms, and sufficient statistical quality for applications such as reinforcement learning, where randomness can affect exploration behavior, training stability, and the reproducibility of empirical evaluation [[18, 19, 20]](#references).
For security applications,  generated variates need to be unpredictable, 
so that future values cannot be inferred from past outputs.

There are several high-quality RNGs to be implemented in this NextRNGBook Package which should provide a solid foundation 
for better statistical simulation and/or secure applications. 
Combining strong theoretical supports and great practical performance, 
NextRNGBook can help users to explore, evaluate, and 
apply high-quality RNGs in a modern Python environment.

## What is New

- Added the SAFE generator [``SAFE_DX_PCG64``](safe_dx_pcg64_generator.md#safe_dx_pcg64seed-randomize), which combines the DX generator with PCG64, as well as the more efficient [``eSAFE_DX_PCG64_M4``](safe_dx_pcg64_generator.md#esafe_dx_pcg64_m4seed-randomize) and [``eSAFE_DX_PCG64_M8``](safe_dx_pcg64_generator.md#esafe_dx_pcg64_m8seed-randomize)

- Renamed ``create_dx`` to [``DX``](dx_generator.md#dxdx_id-seed), and added [``DX32``](dx_generator.md#dx32dx_id-seed) as a faster version of the DX generator.

See [What is New](what_is_new.md) for more details.

## Background and Motivation

This section provides needed background information about RNGs to be used 
and explains the motivation behind both the package and the proposed RNGs.


### Multiple Recursive Generators

**Multiple recursive generators (MRGs)** have become one of the most commonly 
used random number generators in computer simulation. 
An MRG is defined by a \( k \)-th order linear recurrence relation:


$$
X_i = (\alpha_1 X_{i-1} + \alpha_2 X_{i-2} + \dots + \alpha_k X_{i-k}) \mod p, \quad i \geq k \tag{1}
$$

where the modulus \( p \) is a large prime number, 
and the initial seeds \( X_0, \dots, X_{k-1} \) are integers in 
\( \mathbb{Z}_p = \{0, 1, \dots, p-1\} \), 
not all of which are zero.

A common way to obtain variates \( U_i \) 
between 0 and 1 is to apply the transformation

$$
U_i = \frac{X_i}{p}.
$$

To improve statistical and numerical properties, 
Deng and Xu [[2]](#references) recommended the following modification:

$$
U_i = \frac{X_i + 0.5}{p}.
$$

This modification can offer several advantages: 
(i) it prevents the generation of exact values of 0 or 1, 
thus avoiding issues in applications like generating a random variable 
with a standard exponential distribution using \( X = -\ln(U) \) 
or a logistic distribution using \( X = -\ln(U/(1-U)) \);
(ii) the average value of \( U_i \) is closer to \( \frac{1}{2} \) 
because the output range is symmetric around \( \frac{1}{2} \). See, the paper by
Deng and Xu [[2]](#references). To produce a 32-bit integer variate, say, we can simply 
scale \( U_i \) by \(2^{32}\) 
using the floor function \( Y_i = \lfloor U_i \cdot 2^{32} \rfloor \). 

The **period length** of an RNG
refers to the number of iterations (or random numbers generated) 
before the sequence repeats itself. Every RNG eventually enters a cycle, 
starting to produce the same sequence of numbers again after a certain number of steps. 
For the MRG, the maximum period is given by \( p^k - 1 \), 
which is achieved if and only if its characteristic polynomial 

$$
f(x) = x^k - \alpha_1 x^{k-1} - \alpha_2 x^{k-2} - \cdots - \alpha_k 
$$


is a primitive polynomial which can be checked using proposed algorithms in [[3, 4, 7]](#references).

A maximal period MRG has a nice property of  **equidistribution** 
in spaces up to \( k \)-dimensions, 
Specifically, according to 
Lidl and Niederreiter [1994, Theorem 7.43]  [[8]](#references), 
for $1 \leq d \leq k$, 

- every non-zero $d$-tuple $(a_1, a_2, \cdots, a_d)$ appears the 
*same number* of times ($p^{k-d}$) over its entire period $p^k-1$.

- all-zero $d$-tuple $(0, 0, \cdots, 0)$ 
appears *one times less* ($p^{k-d}-1$).

This would imply the random numbers are uniformly distributed across dimensions $d\leq k$. 
This uniformity helps reducing correlation artifacts, 
which can improve the accuracy of simulations, 
especially in high-dimensional spaces. 
**Empirical tests** have been tested on several maximal period MRGs with great results. 
In summary, a large order MRG will yield an extremely long period by modern standards, 
it has a nice equidistribution property over high dimensional space, 
and it can pass stringent extensive empirical tests.



### Linear Congruential Generators

When \( k = 1 \) in Eq. (1), the MRG reduces to a **Linear Congruential Generator (LCG)**.
The sequence is given by:

$$
X_i = (B X_{i-1} + A) \mod p, \quad i \geq 1 \tag{2}
$$

where \( X_i \), \( A \), \( B \), and \( p \) are nonnegative integers, 
and \( X_0 \neq 0 \) is chosen from \( \mathbb{Z}_p \) as a seed. 
If \( A \neq 0 \), it is possible to achieve a full period of \( p \).

It is common to use \( A = 0 \) because it offers faster computation and 
clear properties. In this case, the sequence is described by:

$$
X_i = B X_{i-1} \mod p, \quad i \geq 1 \tag{3}
$$

where \( X_0 \neq 0 \). 
When \( p \) is a prime number and \( B \) is a primitive root modulo \( p \), 
the LCG in Eq. (3) has a period of \( p-1 \).

Until recently, LCGs enjoyed popularity for their simplicity, 
efficiency, and well-known theoretical properties. 
However, they are now considered less ideal due to their relatively short periods by modern standards, 
as well as their inability to achieve equidistribution in dimensions greater than one. 
Furthermore, LCGs also show poor empirical performance, 
failing to pass rigorous statistical tests.


### PCG64: Permuted Congruential Generator

LCG is the baseline RNG used in the popular
[PCG64](https://numpy.org/doc/stable/reference/random/bit_generators/pcg64.html)
which is designed to address some of the inherent shortcomings of LCGs. Specifically, 
PCG64 uses a 128-bit LCG with \( p = 2^{128} \) and \( A \neq 0 \) in Eq. (2), 
dividing 128-bit output into two 64-bit outputs,
appling permutation and combination transformation to produce 64-bit (or two 32-bit) generated values. 
This permutation and combination, along with the high-bit modulus, 
helps improve the generator’s empirical performance. It was shown that 
PCG64 can pass stringent statistical tests whereas traditional LCGs often fail.
However, since its baseline structure is still based on an LCG, 
it is expected to inherit the same limitations of LCG. 
In particular, it can not achieve equidistribution in higher dimensions, 
and its period, with an upper limit of \( 2^{128} \), is relatively short for 
modern applications that demand longer sequences. 
Furthermore, its reliance on 128-bit unsigned integers introduces 
portability concerns, as not all platforms support such high-bit operations.

We should note that the modulus used by PCG64 is \( p = 2^{128} \) in Eq. (2) 
is not a prime number whereas the modulus $p$ used
for LCG or MRG is a prime number which can be of size with 32-bit or 64-bit outputs. 
Large order MRGs in Eq. (1) do not require 
additional generation time for permuation and/or 
combination transformation as required by PCG64. 
Comparing with PCG64, however, the MRGs 
required expensive modulus operation. 
Next, we will consider an efficient class of MRG to speed up its generating time.

### DX Generators: A class of efficient MRGs

The MRG achieves good theoretical properties, 
does not require any output transformations, 
and avoids reliance on high-bit arithmetic. 
However, as the order \( k \) in Eq. (1) increases, 
two challenges emerge: 
(1) a loss of efficiency due to the increasing number of multiplications, 
and (2) the difficulty of selecting parameters that yield the maximum period length.

The **DX-k-s** class of generators is an efficient subclass of the MRG, 
in which the number of nonzero coefficients is restricted to \( s \), 
and all nonzero terms share the same multiplier \( B \).
The \( k \)-th order linear recurrences for \( s = 1, 2 \) are given by:

When \( s = 1 \):

  $$
  X_i = (X_{i-1} + B X_{i-k}) \mod p, \quad i \geq k
  $$

When \( s = 2 \):

  $$
  X_i = B(X_{i-1} + X_{i-k}) \mod p, \quad i \geq k
  $$

where 
\( k \) represents the order of the recurrence relation, 
\( s \) specifies the recurrence structure, 
\( B \) is the multiplier, 
and \( p \) is the prime modulus.


With appropriate parameter choices, 
the DX generators satisfy the **HELP** properties proposed 
by Deng [[2, 3]](#references), 
making them suitable for a wide range of applications:

- **H**igh-dimensional equidistribution: 
The maximal period DX generators ensure high-dimensional equidistribution up to \( k \) dimensions. 
Specifically, every \( d \)-tuple (where \( 1 \leq d \leq k \)) of integers 
between 0 and \( p-1 \) appears exactly \( p^{k-d} \) 
times across the entire period \( p^k - 1 \), 
except for the all-zero tuple, 
which appears one less time, i.e., \( p^{k-d} - 1 \). 

- **E**fficiency: 
By limiting the number of nonzero coefficients and using a shared multiplier, 
DX generators reduce the computational cost while maintaining high-quality outputs.

- **L**ong period length: 
With appropriate parameters, 
DX generators can achieve the maximum period \( p^k - 1 \), 
which is more than sufficient for most simulation scenarios even with moderate order \(k\).

- **P**ortability: 
DX generators avoid high-bit arithmetic and output transformations, 
making them easy to implement across various platforms 
without compromising performance or statistical quality.


Additionally, Deng [[4]](#references) proposed an improved efficient search algorithm called GMP 
for finding maximal period MRGs of large order. 
With the Algorithm GMP, the maximum period parameters for DX generators can be found, 
achieving a period length of \( p^k - 1 \), 
\( k \)-dimensional equidistribution, 
and great empirical test results.

Deng et. al. [[5]](#references) also proposed a method for automatically constructing maximum-period MRGs 
from a single DX generator. 
Using this method, multiple distinct maximal-period MRGs 
can be found and then assigned to different threads or processors for parallel simulations. 
This approach is more effective than traditional methods, 
such as "jump-ahead parallelization."


For more details on the DX generator, 
refer to [Chapter 3](https://link.springer.com/chapter/10.1007/978-3-031-76722-7_3)
of the RNG book [[1]](#references). 
**Section 3.1** discusses the advantage and challenge of large order MRGs, 
and **Section 3.2** provides an explanation of the DX generator. 
Parallelization of the DX generator was introduced in 
[Chapter 8](https://link.springer.com/chapter/10.1007/978-3-031-76722-7_8), 
with the classical method covered in **Section 8.1** 
and the advantage of the proposed method in **Section 8.2.2**.



### DL/DS/DT/DW Generators

The **DX generator** is an efficient MRG 
with its generating speed and nice statistical properties. 
However, it has two potential limitations: 
(a) bad initialization effect, 
where a near-zero state may result in a prolonged sequence of zero values, 
and (b) suboptimal spectral test results in dimensions higher than \( k \). 
These limitations arise from the generator's design, 
which prioritizes efficiency by using a minimal number of non-zero terms 
in Eq. (1). 
This so-called bad initialization effect is rarely encountered in practice. 
Unless the initial state is deliberately chosen to be nearly zero, 
it is extremely unlikely for the generator to enter such 
problematic states during typical use. 
Moreover, DX generators have passed stringent empirical tests, 
indicating that their overall statistical quality remains strong in practice.


To address these potential limitations while ensuring efficiency, 
the **DL**, **DS**, and **DT generators** 
were developed by incorporating additional non-zero terms in Eq. (1). 
While the DL generator improves initialization behavior, 
its spectral performance in dimensions higher than \( k \) remains somewhat limited. 
The DS and DT generators enhance both initialization behavior 
and spectral properties, offering a more balanced and effective solution. 
Like the DX generator, all three maintain desirable statistical properties. 
For more details on these generators, 
refer to [Chapter 3](https://link.springer.com/chapter/10.1007/978-3-031-76722-7_3)
of the RNG book [[1]](#references), 
where **Section 3.2.5** provides the motivation behind the efficient generators.

The **DW generator** 
was developed to tackle two significant challenges 
faced by MRGs with numerous non-zero terms: (1) computational inefficiency 
due to the large number of multiplications required, 
and (2) difficulties in parallelization, 
particularly with traditional methods such as "jump-ahead parallelization." 
The DW generator addresses these challenges by utilizing a 
Matrix Congruential Generator to efficiently implement 
maximum-period MRGs with a large number of non-zero terms. 
This approach ensures both strong statistical properties 
and efficient parallel execution, 
providing a practical solution for high-order MRGs with numerous non-zero terms.
For more details on the DW generator and its motivation, 
refer to **Section 3.3** of 
[Chapter 3](https://link.springer.com/chapter/10.1007/978-3-031-76722-7_3) 
and [Chapter 9](https://link.springer.com/chapter/10.1007/978-3-031-76722-7_9) 
for a more detailed description.


### Security Consideration

In cryptographic applications, 
the security of a stream cipher depends entirely on the quality of its key stream. 
A truly random key stream would result in ciphertext that
behaves like a random sequence of variates, 
making it extremely difficult for attackers to decrypt 
without knowing the key stream. 
However, truly random sequences cannot be generated by deterministic algorithms, 
the best that we can hope is to contruct some well-designed **secure RNGs**.

A secure RNG should have a long period, 
strong unpredictability (in both forward and backward directions), 
excellent statistical properties, 
high efficiency, 
and a simple, flexible design. 
While many linear generators (such as MRGs) 
perform well in statistical simulations, 
they are not considered as secure. 
Their linearity allows attackers to predict future values by solving recurrence relations 
from a few observed outputs. To address this,  **SAFE** (Secure And Fast Encryption), 
Deng et al. [[6]](#references) proposed to use two shuffle tables 
with injection of two good RNGs with nonlinearity transformation and 
mutual shuffling technique to resist attacks.

There are several other popular secure RNGs/ciphers proposed in the literature. 
For example, **RC4** is a popular 8-bit RNG
and **HC-256**, **ChaCha/Salsa** and **Rabbit** are popular secure ciphers 
which are among the finalists in eStream Project.
Most of the proposed RNGs applied ARX (Addition, Rotation, and XOR) operations 
to produce ''randomness'' and ''unpredictability''.
Consequently, one major weakness of these secure RNGs is lack of 
theoretical support for statistical properties. 

To address this, in the RNG Book, 
we propose to inject a good RNG to the existing popular secure ciphers 
which incorporate 
nonlinearity transformation and additional techniques to resist attacks. 
For example,  **eRC** is an enhancement to **RC4** 
with 32-bit or 64-bit variates in its shuffle table.
Similar idea can be used to enhance **HC** with **eHC** 
by injecting two good RNGs to the two shuffle tables.
For more details, refer to **Part IV** of the RNG book [[1]](#references).


## Current Features of NextRNGBook

In its current version, the package features the **32-bit DX generator** and 
provides parallelization capabilities. 
Specifically, the package offers over **4,000 distinct DX generators** 
with desirable properties, allowing users to assign different generators to different threads 
or processors for parallel simulations. This approach is more effective than those used in 
[NumPy](https://numpy.org/doc/stable/reference/random/parallel.html), 
such as `jumped` or `spawn`, 
where a single RNG with different starting seeds may lead to overlaps and high correlations. 
Different combinations of \( B \), \( p \), \( k \), and \( s \) in the DX generator 
effectively mitigate these issues, enabling better parallelization.

There are wide range of DX generators can be selected with $k$ 
(from $k=2$, $k=3$, $\cdots$, up to  $k = 50,873$) and $s$ ($s=1$ or $s=2$). 
There are several selections of prime modulus $p$ which can be of size 
$31$-bit or $32$-bit. 
The period length ranges from approximately $10^{18.7}$ to $10^{474729.3}$. 
There are many more parameters $B$'s can be found for a given DX-$k$-$s$. 
In the future, we will also ''extend'' the proposed RNGs in several directions, 
with an even larger order $k$ and/or  increase the size of $p$ 
from 32-bit to 64-bit for various RNGs later (e.g. DX-64).

## NextRNGBook Expansion Plans

**Secure RNGs** will be introduced, 
designed for cryptographic and security-critical applications, such as:

- **SAFE (Secure And Fast Encryption)**: with mutual shuffle on two RNGs.
- **eRC**: enhancement on RC4  8bit stream cipher.
- **eHC**: enhancement on HC-256 and HC128 stream ciphers.
- **eChaCha**: enhancement on ChaCha/Salsa stream ciphers.
- **eRabbit**: enhancement on Rabbit stream ciphers.

NextRNGBook will also include the **64-bit** RNGs version of various
32-bit RNGs as previously discussed.


## Learn More

- **[Quick Start](dx32_quick_start.md)** – Learn how to install and use NextRNGBook.
- **[API Reference](reference.md)** – API documentation.
- **[Explanation](team_and_contributor.md)** – Background, design principles, and team members. 
  *Under construction. Currently lists team members only.*


## References

[1] Deng, L.-Y., Kumar, N., Lu, H. H.-S., & Yang, C.-C. (2025). 
*Random Number Generators for Computer Simulation and Cyber Security:
Design, Search, Theory, and Application* (1st ed.). Springer. 
[https://doi.org/10.1007/978-3-031-76722-7](https://doi.org/10.1007/978-3-031-76722-7)
 
[2] Deng, L. Y., & Xu, H. (2003). 
*A system of high-dimensional, efficient, long-cycle and portable uniform random number generators*. 
ACM Transactions on Modeling and Computer Simulation (TOMACS), 13(4), 299-309.
 
[3] Deng, L.-Y. (2005). 
*Efficient and portable multiple recursive generators of large order*. 
ACM Transactions on Modeling and Computer Simulation, 15(1), 1–13. 
[https://doi.org/10.1145/1044322.1044323](https://doi.org/10.1145/1044322.1044323)

[4] Deng, L. Y. (2004). 
*Generalized Mersenne prime number and its application to random number generation*. 
In Monte Carlo and Quasi-Monte Carlo Methods 2002: 
Proceedings of a Conference held at the National University of Singapore, 
Republic of Singapore, November 25–28, 2002 (pp. 167-180). Springer Berlin Heidelberg.
[https://doi.org/10.1007/978-3-642-18743-8_9](https://doi.org/10.1007/978-3-642-18743-8_9)

[5] Deng, L. Y., Winter, B. R., Shiau, J. J. H., Lu, H. H. S., Kumar, N., 
& Yang, C. C. (2023). 
*Parallelizable efficient large order multiple recursive generators*. 
Parallel Computing, 117, 103036.

[6] Deng, L. Y., Shiau, J. J. H., Lu, H. H. S., & Bowman, D. (2018). 
*Secure and fast encryption (SAFE) with classical random number generators*. 
ACM Transactions on Mathematical Software (TOMS), 44(4), 1-17.

[7] Knuth, D. E. (1998). 
*The art of computer programming, vol 2, seminumerical algorithms, 3rd edition*. 
Addison-Wesley.

[8] Lidl, R., and Niederreiter, H. (1994). 
*Introduction to Finite Fields and Their Applications  . Revised Edition*. 
Cambridge University Press, Cambridge, MA.

[9] L’Ecuyer, P., & Simard, R. (2007). 
*TestU01: A C library for empirical testing of random number generators*. 
ACM Transactions on Mathematical Software (TOMS), 33(4), 1–40.

[10] Crandall, R. E. (1992). 
*Method and apparatus for fast modular multiplication and division*. 
U.S. Patent No. 5,159,632.

[11] O’Neill, M. E. (2014). 
*PCG: A family of simple fast space-efficient statistically good algorithms for random number generation*. 
ACM Transactions on Mathematical Software.

[12] L’Ecuyer, P. (1999). 
*Tables of linear congruential generators of different sizes and good lattice structure*. 
Mathematics of Computation, 68(225), 249–260.

[13] Matsumoto, M., & Nishimura, T. (1998). 
*Mersenne Twister: A 623-dimensionally equidistributed uniform pseudorandom number generator*. 
ACM Transactions on Modeling and Computer Simulation (TOMACS), 8(1), 3–30.

[14] Nishimura, T. (2000). 
*Tables of 64-bit Mersenne Twisters*. 
ACM Transactions on Modeling and Computer Simulation (TOMACS), 10(4), 348–357.

[15] O'Neill, M. E. *Response to Vigna's critique of PCG streams*.  
[https://www.pcg-random.org/posts/on-vignas-pcg-critique.html](https://www.pcg-random.org/posts/on-vignas-pcg-critique.html)

[16] Deng, L. Y., Lu, H. H. S., & Chen, T. B. (2010). 
64-Bit and 128-bit DX random number generators. Computing, 89(1), 27-43.

[17] O'Neill, M. E. *Critiquing PCG's streams (and SplitMix's too)*.
[https://www.pcg-random.org/posts/critiquing-pcg-streams.html](https://www.pcg-random.org/posts/critiquing-pcg-streams.html)

[18] Henderson, P., Islam, R., Bachman, P., Pineau, J., Precup, D., & Meger, D. (2018, April). 
*Deep reinforcement learning that matters*. In Proceedings of the AAAI conference on artificial intelligence (Vol. 32, No. 1).

[19] Islam, R., Henderson, P., Gomrokchi, M., & Precup, D. (2017). 
*Reproducibility of benchmarked deep reinforcement learning tasks for continuous control.* arXiv preprint arXiv:1708.04133.

[20] Fortunato, M., Azar, M. G., Piot, B., Menick, J., Osband, I., Graves, A., ... & Legg, S. (2017). 
*Noisy networks for exploration*. arXiv 2017. arXiv preprint arXiv:1706.10295.