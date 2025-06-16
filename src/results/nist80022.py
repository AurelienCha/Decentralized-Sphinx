"""
The file implement the NIST SP 800-22: Statistical evaluation of binary strings randomness
In short: https://csrc.nist.gov/Projects/random-bit-generation/Documentation-and-Software/Guide-to-the-Statistical-Tests
PDF: https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-22r1a.pdf

NIST SP 800-22 evaluates:
- Uniformity (equal number of 0s and 1s)
- Independence (no predictable patterns)
- Complexity (random structure, not compressible)

It contains 15 tests such as:
1. The Frequency (Monobit) Test,                                (done)
2. Frequency Test within a Block,                               (done)
3. The Runs Test,                                               (done)
4. Tests for the Longest-Run-of-Ones in a Block,                (done)
5. The Binary Matrix Rank Test,                                 ()
6. The Discrete Fourier Transform (Spectral) Test,              ()
7. The Non-overlapping Template Matching Test,                  ()
8. The Overlapping Template Matching Test,                      ()
9. Maurer's "Universal Statistical" Test,                       ()
10. The Linear Complexity Test,                                 ()
11. The Serial Test,                                            ()
12. The Approximate Entropy Test,                               ()
13. The Cumulative Sums (Cusums) Test,                         ('done') -> small modification
14. The Random Excursions Test, and                             ()
15. The Random Excursions Variant Test.                         ()

Note: All the tests output the p-value (p): if p < 0.01, then test FAILED (i.e. not random)
"""

import math
import scipy
import sys

def run_tests(bits: str) -> float:
    return (monobit_test(bits),
            block_frequency_test(bits), 
            runs_test(bits),
            longest_run_of_ones_test(bits))

def monobit_test(bits: str) -> float:
    """
    Monobit (Frequency) Test – NIST 800-22, Section 2.1
    Tests whether the number of ones and zeros are approximately the same

    NOTE: small P-value would be caused by 's_n' being large.
        Large positive values of 's_n' are indicative of too many ones, 
        and large negative values of 's_n' are indicative of too many zeros
    """
    n = len(bits) # recommended n >= 100
    s_n = sum(1 if b == '1' else -1 for b in bits)
    s_obs = abs(s_n) / math.sqrt(n)
    p_value = math.erfc(s_obs / math.sqrt(2))
    return p_value #, s_n

def block_frequency_test(bits: str, block_size: int = 32) -> float:
    """
    Frequency Test within a Block – NIST 800-22, Section 2.2
    Divides sequence into M-bit blocks and checks the balance of ones in each block.

    NOTE: small P-values indicates a large deviation from the equal proportion of ones and zeros in at least one of the blocks
    
    """ 
    N = len(bits) // block_size
    # M >= 20 and M > n/100 where M is the block_size and n the input_size
    # N < 100

    chi_sq = 0.0
    for i in range(N):
        block = bits[i*block_size:(i+1)*block_size]
        pi = sum(1 if b == '1' else 0 for b in block) / block_size
        chi_sq += pow((pi - 0.5), 2)

    p_value = scipy.stats.chi2.sf(4 * block_size * chi_sq, df=N)
    return p_value

def runs_test(bits: str) -> float:
    """
    Runs Test – NIST 800-22, Section 2.3
    Tests the total number of runs (consecutive sequences of identical bits), 
    where a 'run' is an uninterrupted sequence of identical bits

    NOTE: a large value for 'v_obs' indicates an oscillation in the string which is too fast; 
          a small value would have indicated that the oscillation is too slow.
    """
    n = len(bits)
    pi = sum(1 if b == '1' else 0 for b in bits) / n
    if pi == 0.0:
        pi = sys.float_info.epsilon
    elif pi == 1.0:
        pi = 1.0 - sys.float_info.epsilon
    if abs(pi - 0.5) >= (2 / math.sqrt(n)):
        return 0.0  # Runs test need not be performed (i.e., the test should not have been run because of a failure to pass test 1, the Frequency (Monobit) test). 
    v_obs = 1 + sum(bits[i] != bits[i+1] for i in range(n - 1))
    p_value = math.erfc(abs(v_obs - 2 * n * pi * (1 - pi)) / (2 * math.sqrt(2 * n) * (pi) * (1 - pi)))
    return p_value #, v_obs

def longest_run_of_ones_test(bits: str, block_size: int = 8) -> float:
    """
    Longest Run of Ones in a Block Test – NIST 800-22, Section 2.4
    Tests for the longest sequence of ones in fixed-size blocks.

    NOTE: large value of 'chi_sq' indicates presence of clusters of ones
    """
    n = len(bits)
    N = n // 8 # block_size = 8 # hardcode since small bits_size (< 6272)

    blocks = [bits[i*block_size:(i+1)*block_size] for i in range(N)]
    max_run_lengths = [max(len(run) for run in block.split('0')) for block in blocks]

    freq = [0] * 4
    for run_length in max_run_lengths:
        if run_length <= 1:
            freq[0] += 1
        elif run_length == 2:
            freq[1] += 1
        elif run_length == 3:
            freq[2] += 1
        else:
            freq[3] += 1

    pi = [0.2148, 0.3672, 0.2305, 0.1875] # pre-computed table (see NIST SP 800-22)
    chi_sq = sum(((f - N * p) ** 2) / (N * p) for f, p in zip(freq, pi))
    p_value = scipy.stats.chi2.sf(chi_sq, df=3)
    return p_value #, chi_sq

# def cumulative_sums_test(bits: str) -> float:
#     """
#     Cumulative Sums (Cusum) Test – NIST 800-22, Section 2.13
#     Tests the maximal excursion of the random walk defined by the bits.
#     """
#     n = len(bits)
#     s = 0
#     S = []
#     for b in bits:
#         s += 1 if b == '1' else -1
#         S.append(abs(s))

#     z = max(S) 
#     p_value = 2 * math.erfc(z / math.sqrt(2*n))  # NOTE: not the exact formula as NIST but good approx
#     return p_value
