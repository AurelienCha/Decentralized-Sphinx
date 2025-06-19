from tqdm import tqdm
from datetime import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import random_ip
from setup import mixnet, TTPs
from client import Client
from mixnode import Mixnode
from run_original import run_original_sphinx

NIST_LENGTH = pow(10,6)

def create_test_folder(data_directory):
    # Create the new folder
    new_folder = datetime.now().strftime("%Y-%m-%d__%H:%M:%S")  # more precise: "%Y-%m-%d__%H:%M:%S__%f"
    new_folder_path = os.path.join(data_directory, new_folder)
    os.mkdir(new_folder_path)
    return new_folder_path

def save(header, data_directory, file):
    def binarize(header):
        return f"{header.alpha:0256b}{header.gamma:0256b}{header.beta[0]:0256b}{header.beta[1]:0256b}{header.beta[2]:0256b}{header.beta[3]:0256b}{header.beta[4]:0256b}"
    
    with open(f"{data_directory}/{file}.data",'a') as f:
        f.write(binarize(header))

def run_simulation(iterations=100, data_directory='src/experiments/data/'):
    # Create new folder to store test's data and result
    data_directory = create_test_folder(data_directory)

    # Need 100 times 10^6 bits for NIST testing
    # One iteration of original Sphinx code produces: 9 804 bits
    # One iteration of Decentralized Sphinx code produces: 7 168 bits
    nbr_original_it = (iterations * NIST_LENGTH // 9804) + 1
    nbr_decentralized_it = (iterations * NIST_LENGTH // 7168) + 1

    # Generate system (default mixnodes and TTPs) -> normal_case
    client = Client(mixnet, TTPs)
    for it in tqdm(range(nbr_decentralized_it)):
        # Generate and process header (destination is a nounce)
        destination = random_ip()
        header = client.send_packet(destination)
        save(header, data_directory, 'decentralized')
        
        for layer in range(1,4):
            mixnode = mixnet[header.n]
            header = mixnode.process_packet(header)
            save(header, data_directory, 'decentralized')
        # Correctness check
        assert header.n == destination

    run_original_sphinx(nbr_original_it, data_directory)

    return data_directory


if __name__ == "__main__":
    run_simulation(iterations=100)
