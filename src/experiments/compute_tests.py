import subprocess
import time
import shutil

NIST_LENGTH = pow(10,6)

def display():
    print("""\n
                   N I S T   S P   8 0 0 - 2 2
                S T A T I S T I C A L   T E S T S
                _________________________________

        [01] Frequency                       [02] Block Frequency
        [03] Cumulative Sums                 [04] Runs
        [05] Longest Run of Ones             [06] Rank
        [07] Discrete Fourier Transform      [08] Nonperiodic Template Matchings
        [09] Overlapping Template Matchings  [10] Universal Statistical
        [11] Approximate Entropy             [12] Random Excursions
        [13] Random Excursions Variant       [14] Serial
        [15] Linear Complexity
    """)

def copy_result_summary(data_directory, file):
    src_path = 'src/experiments/sts-2.1.2/experiments/AlgorithmTesting/finalAnalysisReport.txt'
    shutil.copy2(src_path, f"{data_directory}/{file}.result")

def run_nist_tests(data_directory, file, size_seq=str(NIST_LENGTH)):
    # Determine number of sequence
    with open(f"{data_directory}/{file}.data", 'r') as f:
        nbr_seq = str(len(f.read()) // NIST_LENGTH)
    inputs = ["0", f"{data_directory}/{file}.data", "1", "0", nbr_seq, "0"]  # [file_option, file_name, all_test, modify_param, nbr_seq, '0=ASCII']
    
    # Run NIST test suite (with stdbuf to force unbuffered output)
    print(f"     F I L E :   {data_directory}/{file}.data")
    process = subprocess.Popen(
		["stdbuf", "-oL", "./assess", size_seq],
        cwd="src/experiments/sts-2.1.2",
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		text=True,
		bufsize=1
	)

	# Run NIST test suite with the following user's inputs
    for user_input in inputs:
        process.stdin.write(user_input + '\n')
        process.stdin.flush()
    print("     Statistical Testing In Progress.........")
    for i, line in enumerate(process.stdout):
        pass
    print("     Statistical Testing Complete!!!!!!!!!!!!\n")

    # Keep a save of the summary result
    copy_result_summary(data_directory, file)


def execute_tests(data_directory):
    display()
    run_nist_tests(data_directory, "decentralized")
    run_nist_tests(data_directory, "original")


if __name__ == "__main__":
    execute_tests('/home/garuda/Documents/PhD/Code/Decentralized-Sphinx/src/experiments/data/.../')