from typing import List, Optional
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import os

from read_data import get_data, get_files, get_file
from nist80022 import run_tests

data_directory = 'src/results/data'

NIST_TEST_NAME = [
    "Monobit Frequency",                        #  1
    "Monobit Frequency per Block",              #  2
    "Runs Test",                                #  3
    "Longest-Run-of-Ones in a Block",           #  4
    "Binary Matrix Rank",                       #  5
    "Discrete Fourier Transform (Spectral)",    #  6
    "Non-overlapping Template Matching",        #  7
    "Overlapping Template Matching",            #  8
    "Maurer's Universal Statistical Test,",     #  9
    "Linear Complexity Test",                   # 10
    "Serial Test",                              # 11
    "Approximate Entropy Test",                 # 12
    "Cumulative Sums Test",                     # 13
    "Random Excursions Test",                   # 14
    "Random Excursions Variant Test"]           # 15

def plotting(results, file_name):
    """
    Plot the test results in histograms
    """
    fig, axs = plt.subplots(2, (1+len(results))//2, figsize=(10, 8))

    # Loop over each subplot (axis) and the corresponding data
    for i, ax in enumerate(axs.flatten()): 
        # Histogram
        color = 'steelblue' # NOTE: nice colors are: steelblue, darkorange and seagreen
        ax.hist(results[i], bins=100, range=(0, 1), histtype='stepfilled', alpha=0.3, color=color, density=True, stacked=True, label="Ours (100 bins)")
        ax.hist(results[i], bins=15, range=(0, 1), histtype='step', alpha=1, color=color, density=True, stacked=True, label="Ours (15 bins)")
        
        # Set titles and labels
        ax.set_xlabel('P-value')
        ax.set_ylabel('Frequency')
        ax.set_title(NIST_TEST_NAME[i])
        ax.label_outer()  # Only show labels on the outer axes (bottom row and leftmost column)
        ax.legend()
    
    plt.suptitle("NIST Statistical Test Results", fontweight="bold")
    plt.tight_layout()
    plt.savefig(file_name)
    plt.close()

def transpose(matrix):
    """
    Return the transpose of a list of list
    """
    return list(zip(*matrix))

def analyze_data(data: List[List[str]], mode: str, file_name: str) -> None:
    """
    Applying nist-sp-800.22 randomness tests on the data.
    Those tests return p-values that are plot in a histogram.
    NOTE: For random samples, the p-value histogram should be uniform

    Args:
        data (List[List[str]]): Matrix of the data (either run-wise or bit-wise)
        mode (str): To distinguish if data visualized by 'run' or by 'bit' (for saving purpose)
        file_name (str): Name of the data file (for saving purpose)
    """
    results = run_tests(data, mode)         # results := [data_1, data_2, ..., data_n]
    test_results = transpose(results)       # test_results := [test_1, test_2, ..., test_m]
    plotting(test_results, f"{data_directory}/{file_name.split('.')[0]}_histogram_by_{mode}.png")

def analyze_file(data_file: Optional[str] = None):
    """
    Analyse a data_file both:
    - Run-wise analysis
    - Bit-wise analysis
    """
    # Fetch data
    if data_file is None:
        file_name, data = get_data()    # by default, the last data_file
    else:
        file_name, data = get_data(data_file)
    
    # --- Run-wise analysis ---
    analyze_data(data, 'run', file_name)

    # --- Bit-wise analysis ---
    bitwise_data = [''.join(l) for l in transpose(data)]
    analyze_data(bitwise_data, 'bit', file_name)

if __name__ == "__main__":
    os.system('clear')  # Clearing the shell
    
    file = 'ALL'

    if file is None:
        analyze_file()
    elif file == 'ALL':
        for f in tqdm(get_files(), ascii="░▒█", dynamic_ncols=True, desc="Analysing data files", position=0, leave=True):
            tqdm.write(f"File: {f[:50]}")
            analyze_file(f)
    else:
        analyze_file(file)
