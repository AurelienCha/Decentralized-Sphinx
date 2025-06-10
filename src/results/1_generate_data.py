from tqdm import tqdm
import pandas as pd
import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import random_ip
from setup import mixnet, TTPs
from client import Client
from mixnode import Mixnode

data_directory = 'src/results/data'

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

def run_simulation(iterations):
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

    df = pd.DataFrame(results)

    file_name = f"{data_directory}/data.csv"
    file_exists = os.path.exists(file_name)
    df.to_csv(file_name, mode='a', index=False, header=not file_exists)

if __name__ == "__main__":
    run_simulation(iterations=pow(10,5))

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
