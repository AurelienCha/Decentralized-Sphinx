from typing import List, Optional
from tqdm import tqdm
import pandas as pd

from nist80022 import run_tests


def extract_data(data_directory):
    CSV_FILE  = f"{data_directory}/data.csv"
    DTYPES = {
        "algo": str,
        "iteration": int,
        "header": str
    }
    return pd.read_csv(CSV_FILE, dtype=DTYPES)

def headerwise_tests(df, data_directory): 
    results = []
    for _, row in tqdm(list(df.iterrows()), ascii="░▒█", dynamic_ncols=True, desc=f"Headerwise"):
        for i, pvalue in enumerate(run_tests(row["header"])):
            results.append({'algo':row['algo'], 'iteration':row['iteration'], 'test': i+1, 'p-value': pvalue})
    pd.DataFrame(results).to_csv(f"{data_directory}/pvalues_headerwise.csv", mode='w', index=False)

def bitwise_tests(df, data_directory):
    def tests(df, algo):
        def transpose(matrix):
            """
            Return the transpose of a list of list
            """
            return list(zip(*matrix))
        # Extract matrix of headers 
        headerwise = list(df[df['algo']==algo]['header'])
        # Transpose matrix (headerwise -> bitwise)                  
        bitwise = [''.join(b) for b in transpose(headerwise)]
        # Run tests (i.e. p-values)
        results = []
        for bit, row in tqdm(enumerate(bitwise), ascii="░▒█", dynamic_ncols=True, desc=f"Bitwise ({algo})", position=1, leave=False):
            for i, pvalue in enumerate(run_tests(row)):
                results.append({'algo':algo, 'iteration':bit, 'test': i+1, 'p-value': pvalue})
        return pd.DataFrame(results)

    pd.concat([tests(df, 'Original'), tests(df, 'Decentralized')]).to_csv(f"{data_directory}/pvalues_bitwise.csv", mode='w', index=False)

def execute_tests(data_directory = 'src/results/data'):
    data = extract_data(data_directory)
    # Headerwise p-values
    headerwise_tests(data, data_directory)
    # Bitwise p-values
    bitwise_tests(data, data_directory)

if __name__ == "__main__":
    execute_tests()
    
