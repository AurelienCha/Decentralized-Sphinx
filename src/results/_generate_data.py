from tqdm import tqdm
import pandas as pd
import datetime

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import random_ip
from setup import mixnet, TTPs
from client import Client
from mixnode import Mixnode
from run_original import run_original_sphinx

def binarize(header):
    return f"{header.alpha:0256b}{header.gamma:0256b}{header.beta[0]:0256b}{header.beta[1]:0256b}{header.beta[2]:0256b}{header.beta[3]:0256b}{header.beta[4]:0256b}"

def row(header, layer, it, params):
    return {
        'algo': 'Decentralized',
        'date': params['date'],
        'nbr_ttp': params['# TTPs'],
        'nbr_mixnode': params['# Nodes'],
        'iteration': it,
        'layer': layer,
        'header': binarize(header),
    }

def prepare_data(df):
    df = df.drop(columns=["date","nbr_mixnode","nbr_ttp"])
    df = df.drop(df[(df['layer']==3) & (df['algo']=='Original')].index)
    df = df.sort_values('layer', ascending=False).groupby(["algo", "iteration"])["header"].agg(lambda x: ''.join(x)[:7168]).reset_index()
    return df

def run_simulation(iterations, data_directory='src/results/data'):
    results = []

    # Generate system (default mixnodes and TTPs) -> normal_case
    client = Client(mixnet, TTPs)
    params = {'# Nodes': len(client.mixnet), '# TTPs': len(client.TTPs), 'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    for it in tqdm(range(iterations)):
        # Generate and process header (destination is a nounce)
        destination = random_ip()
        header = client.send_packet(destination)
        results.append(row(header, 0, it, params))
        
        for layer in range(1,4):
            mixnode = mixnet[header.n]
            header = mixnode.process_packet(header)
            results.append(row(header, layer, it, params))
        # Correctness check
        assert header.n == destination

    df = pd.DataFrame(results + run_original_sphinx(iterations, data_directory))
    df.to_csv(f"{data_directory}/raw_data.csv", mode='w', index=False)
    prepare_data(df).to_csv(f"{data_directory}/data.csv", mode='w', index=False)


if __name__ == "__main__":
    run_simulation(iterations=10) # 7168

# def normal_case(iterations: int, ext: str = 'txt') -> None:
#     """
#     - MIXNODE:      Fixed -> see setup.py
#     - TTP:          Fixed -> See setup.py
#     - DESTINATION:  Generated on the fly
#     """
# def worst_case(iterations: int, ext: str = 'txt') -> None:
#     """
#     - MIXNODE:      Unique (i.e. simulate system in which all mixnodes have the same keys)
#     - TTP:          Smallest number of TTP
#     - DESTINATION:  Unique (i.e. simulate system in which all the communications are for the same recipient
#     """
#
# def ideal_case(iterations: int, ext: str = 'txt') -> None:
#     """
#     - MIXNODE:      Generated on the fly
#     - TTP:          Fixed -> See setup.py
#     - DESTINATION:  Generated on the fly
#     """
