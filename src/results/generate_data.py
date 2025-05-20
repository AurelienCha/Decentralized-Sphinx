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
from ttp import TTP
from header import Header

data_directory = 'src/results/data'

def test():
    iterations = 49221 # pow(10,5)
    # worst_case(iterations, 'csv')
    # ideal_case(iterations, 'csv')
    # normal_case(iterations, 'csv')
    # worst_case(iterations, 'txt')
    # ideal_case(iterations, 'txt')
    normal_case(iterations, 'txt')

def process_and_save_header(mixnet: dict[int: Mixnode], header: Header, file_name: str, ext: str):
    """
    Process the header by the 3 mixnodes in the path and save the results in 5 files:
    - file_name     : header send by the client
    - file_name_1   : header after first mixnode
    - file_name_2   : header after second mixnode
    - file_name_3   : header after thid mixnode
    - file_name_all : headers at all steps (client, first node, second node, third node)
    """
    save(header, f"{file_name}_0", ext)
    save(header, f"{file_name}_all", ext)

    for i in range(1,4):
        mixnode = mixnet[header.n]
        header = mixnode.process_packet(header)
        save(header, f"{file_name}_{i}", ext)
        save(header, f"{file_name}_all", ext)
    return header.n

def worst_case(iterations: int, ext: str = 'txt') -> None:
    """
    - MIXNODE:      Unique (i.e. simulate system in which all mixnodes have the same keys)
    - TTP:          Smallest number of TTP
    - DESTINATION:  Unique (i.e. simulate system in which all the communications are for the same recipient
    """
    file_name = f"{datetime.datetime.now().strftime("%y-%m-%d-%X")}_it={iterations}_worst"

    # Generate system (unique destination, unique mixnode and 3 TTPs)
    ip = random_ip()
    mixnet = {ip: Mixnode(ip=ip)}
    TTPs = [TTP() for _ in range(3)]  # FIXME: not working with less than 3 TTP (why ?)

    client = Client(mixnet, TTPs)
    destination = random_ip()

    for _ in tqdm(range(iterations)):
        # Generate and process header
        header = client.send_packet(destination)
        last_node = process_and_save_header(mixnet, header, file_name, ext)
        # Correctness check
        assert last_node == destination

def normal_case(iterations: int, ext: str = 'txt') -> None:
    """
    - MIXNODE:      Fixed -> see setup.py
    - TTP:          Fixed -> See setup.py
    - DESTINATION:  Generated on the fly
    """
    file_name = f"{datetime.datetime.now().strftime("%y-%m-%d-%X")}_it={iterations}_setup={len(mixnet)}-{len(TTPs)}"

    # Generate system (default mixnodes and TTPs)
    client = Client(mixnet, TTPs)

    for _ in tqdm(range(iterations)):
        # Generate and process header (destination is a nounce)
        destination = random_ip()
        header = client.send_packet(destination)
        last_node = process_and_save_header(mixnet, header, file_name, ext)
        # Correctness check
        assert last_node == destination
    
def ideal_case(iterations: int, ext: str = 'txt') -> None:
    """
    - MIXNODE:      Generated on the fly
    - TTP:          Fixed -> See setup.py
    - DESTINATION:  Generated on the fly
    """
    file_name = f"{datetime.datetime.now().strftime("%y-%m-%d-%X")}_it={iterations}_ideal"

    for _ in tqdm(range(iterations)):

        # Generate system (mixnodes on the fly)
        mixnet = {}
        for _ in range(3):
            ip = random_ip()
            mixnet[ip] = Mixnode(ip=ip)

        # Generate and process header (destination is a nounce)
        destination = random_ip()
        header = Client(mixnet, TTPs).send_packet(destination)
        last_node = process_and_save_header(mixnet, header, file_name, ext)
        # Correctness check
        assert last_node == destination

def save(header: Header, file: str, ext: str) -> None:
    """
    Save header in file.ext (in binary format for .txt file)
    """
    if ext == 'csv': 
        data = {
            'n': header.n,
            'alpha': header.alpha,
            'beta0': header.beta[0],
            'beta1': header.beta[1],
            'beta2': header.beta[2],
            'beta3': header.beta[3],
            'beta4': header.beta[4],
            'gamma': header.gamma,
        }
        df = pd.DataFrame([data])
        df.to_csv(f"{data_directory}/{file}.{ext}", mode='a', index=False, header=False)

    if ext == 'txt':
        with open(f"{data_directory}/{file}.{ext}", "a") as f:
            f.write(f"{header.alpha:0256b}{header.gamma:0256b}{header.beta[0]:0256b}{header.beta[1]:0256b}{header.beta[2]:0256b}{header.beta[3]:0256b}{header.beta[4]:0256b}\n")

if __name__ == "__main__":
    test()



