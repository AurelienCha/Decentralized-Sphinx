from typing import List, Optional
from tqdm import tqdm
import pandas as pd

from nist80022 import run_tests

data_directory = 'src/results/data'

def extract_data():
    CSV_FILE  = f"{data_directory}/data.csv"
    COLUMN_NAMES = ["algo", "date", "nbr_ttp", "nbr_mixnode", "iteration", "layer", "header"]
    DTYPES = {
        "algo": str,
        "date": str,
        "nbr_ttp": int,
        "nbr_mixnode": int,
        "iteration": int,
        "layer": int,
        "header": str
    }
    return pd.read_csv(CSV_FILE, names=COLUMN_NAMES, dtype=DTYPES, header=0)

def filter_data(df):
    return df[
        ((df["algo"] == "Decentralized") &
        (df["nbr_mixnode"] == 20) &
        (df["nbr_ttp"] == 3)
        |
        (df["algo"] == "Original") &
        (df["nbr_mixnode"] == 20) &
        (df["nbr_ttp"] == 0)
        )
    ]

def headerwise_tests(df): 
    results = []
    for _, row in tqdm(list(df.iterrows()), ascii="░▒█", dynamic_ncols=True, desc=f"Headerwise"):
        for i, pvalue in enumerate(run_tests(row["header"])):
            results.append({'algo':row['algo'], 'date':row['date'], 'iteration':row['iteration'], 'layer':row['layer'], 'test': i+1, 'p-value': pvalue})
    pd.DataFrame(results).to_csv(f"{data_directory}/pvalues_headerwise.csv", mode='w', index=False)

def bitwise_tests(df):
    def tests(df, algo):
        def transpose(matrix):
            """
            Return the transpose of a list of list
            """
            return list(zip(*matrix))
        # Extract matrix of headers 
        headerwise = list(df[df['algo']==algo]['header'])
        # Transpose matrix (headerwise -> bitwise)                  
        # NOTE: Should put a limit ~1700 to have same size as headerwise tests -> e.g. ''.join(b[:1700])
        bitwise = [''.join(b) for b in transpose(headerwise)]
        # Run tests (i.e. p-values)
        results = []
        for bit, row in tqdm(enumerate(bitwise), ascii="░▒█", dynamic_ncols=True, desc=f"Bitwise ({algo})", position=1, leave=False):
            for i, pvalue in enumerate(run_tests(row)):
                results.append({'algo':algo, 'bit':bit, 'test': i+1, 'p-value': pvalue})
        return pd.DataFrame(results)
    
    pd.concat([tests(df, 'Original'), tests(df, 'Decentralized')]).to_csv(f"{data_directory}/pvalues_bitwise.csv", mode='w', index=False)

if __name__ == "__main__":
    
    data = filter_data(extract_data())
    # Headerwise p-values
    headerwise_tests(data)
    # Bitwise p-values
    bitwise_tests(data)
