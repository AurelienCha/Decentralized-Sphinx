import pandas as pd
import matplotlib.pyplot as plt
import os


def get_files():

    def is_data(file):
        ext = file.split('.')[-1]
        return ext == 'txt' or ext == 'csv'

    return sorted([file for file in os.listdir('src/results') if is_data(file)])
    print(f)

def _get_file(arg):
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

def read_csv(file):
    columns = ['n', 'alpha', 'gamma', 'beta0', 'beta1', 'beta2', 'beta3', 'beta4']
    return pd.read_csv(f"src/results/{file}", header=None, names=columns)

def read_txt(file):
    with open(f"src/results/{file}", "r+") as file:
        data = file.read()
    return data.split()

def get_data(arg=None):
    file = _get_file(arg)
    print(f"Reading file: {file}")
    ext = file.split('.')[-1]
    if ext == 'csv':
        return read_csv(file)
    elif ext == 'txt':
        return read_txt(file)
    else:
        raise Error(f"Support only .csv and .txt")