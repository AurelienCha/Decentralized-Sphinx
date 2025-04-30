from typing import List, Union, Tuple
import pandas as pd
import os

data_directory = 'src/results/data'

def get_files() -> List[str]:
    """
    Return a sorted list of filenames with data (.txt or .csv) in data directory 
    """
    def is_data_file(file):
        ext = file.split('.')[-1]
        return ext == 'txt' or ext == 'csv'

    return sorted([file for file in os.listdir(data_directory) if is_data_file(file)])

def get_file(arg: Union[None, int, str]) -> str:
    """
    Return a data filename based on the argument:
    - None: return the most recent data file
    - int: return data file at that index
    - str: return data file containing the string.
    """
    list_files = get_files()

    if arg is None:
        return list_files[-1]

    if isinstance(arg, int):
        return list_files[arg]

    if isinstance(arg, str):
        files = [f for f in list_files if f.find(arg)>=0]
        if len(files)==1:
            return files[0]
        elif len(files)==0:
            raise Error(f"No file found related to: {arg}")
        else:
            raise Error(f"Several files found related to: {arg}")

def read_csv(file: str) -> pd.DataFrame:
    """
    Read file.csv and return the corresponding dataframe (not in binary format)
    """
    columns = ['n', 'alpha', 'gamma', 'beta0', 'beta1', 'beta2', 'beta3', 'beta4']
    return pd.read_csv(f"{data_directory}/{file}", header=None, names=columns)

def read_txt(file: str) -> List[str]:
    """
    Read file.txt and return all the line in a list
    Each line in file.txt is an header in binary format
    """
    with open(f"{data_directory}/{file}", "r+") as file:
        data = file.read()
    return data.split()

def get_data(arg: Union[None, int, str] = None) -> Tuple[str, Union[pd.DataFrame, List[str]]]:
    """
    Gets data from the latest or specified file, depending on the argument
    
    Returns:
        A tuple: (filename, content) 
            file.txt: content is a binary list
            file.csv: content is pd.DataFrame
    """
    file = get_file(arg)
    ext = file.split('.')[-1]
    if ext == 'csv':
        return file, read_csv(file)
    elif ext == 'txt':
        return file, read_txt(file)
    else:
        raise Error(f"Support only .csv and .txt")
