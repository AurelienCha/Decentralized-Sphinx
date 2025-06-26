import os
import subprocess
from tqdm import tqdm
from generate_data import run_simulation
from compute_tests import execute_tests
from analyze_results import plot_results

if __name__ == "__main__":
    # Ensure the NIST C code is compiled
    subprocess.run(["make", "-f", "makefile"], cwd="src/experiments/sts-2.1.2")

    data_directory = os.path.join(os.getcwd(), 'src/experiments/data')

    for _ in tqdm(range(1), ascii="░▒█", desc='Run simulation n°'):
        test_directory = run_simulation(100, data_directory)
        execute_tests(os.path.join(os.getcwd(), test_directory))
