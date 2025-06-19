import os
import subprocess
from tqdm import tqdm
from generate_data import run_simulation
from compute_tests import execute_tests
from analyze_results import plot_results

if __name__ == "__main__":
    # Ensure the NIST C code is compiled
    subprocess.run(["make", "-f", "makefile"], cwd="src/experiments/sts-2.1.2")

    data_directory = 'src/experiments/data/'

    for _ in tqdm(range(10), ascii="░▒█", desc='Run simulation n°'):
        test_directory = run_simulation(100, data_directory)
        execute_tests(os.path.join(os.getcwd(), test_directory))

    # plot_results(data_directory)

    # >>> 1792*4
    # 7168
    # >>> 1635*6
    # 9804

    # >>> 103*9804
    # 1010430
    # >>> 141*7168
    # 1010688








