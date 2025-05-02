from tqdm import tqdm

from utils import random_ip
from setup import mixnet
from client import Client
from ecc import Point

for it in tqdm(range(pow(10,3)), ascii="░▒█", dynamic_ncols=True, position=0, leave=True):

    # ---  Client / TTP Side  (aka. encryption)  ---
    destination = random_ip()                      # 1) Generate a random IP destination
    header = Client().send_packet(destination)      # 2) Simulate a Client sending a packet (by default with random path and nounce)
    
    # ---  Mixnode Side  (aka. decryption)  ---
    for _ in range(3):                              
        mixnode = mixnet[header.n]                  # 3) Extract the next mixnode IP from the header
        header = mixnode.process_packet(header)     # 4) Simulate the reception and processing of the header by the mixnode

    # ---  Verification / Corectness  ---
    assert destination == header.n
