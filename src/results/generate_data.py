from tqdm import tqdm
import pandas as pd
import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from setup import *
from client import Client

ITERATIONS = pow(10,4)

def test():
    iterations = pow(10,2)
    # worst_case(iterations, 'txt')
    normal_case(iterations, 'txt')
    # ideal_case(iterations, 'txt')
    # worst_case(iterations, 'csv')
    # normal_case(iterations, 'csv')
    # ideal_case(iterations, 'csv')


def worst_case(iterations, format='txt'):
    """
    A single mixnode
    A single destination
    Only 2 TTPs
    """

    ip = randint(1, pow(2,128))
    mixnet = {ip: Mixnode(ip=ip)}
    destination = randint(1,N)
    TTPs = [TTP() for _ in range(2)] 

    client = Client(mixnet, TTPs)
    file_name = f"{datetime.datetime.now().strftime("%y-%m-%d-%X")}_it={iterations}"

    for _ in tqdm(range(iterations)):
        header = client.send_packet(destination)

        for _ in range(3):
            mixnode = mixnet[header.n]
            header = mixnode.process_packet(header)
        assert destination == header.n

        save(header, f"{file_name}_worst", format)

def normal_case(iterations, format='txt'):
    """
    See config.py for number of Mixnodes and TTPs
    Random destination
    """
    client = Client(mixnet, TTPs)
    file_name = f"{datetime.datetime.now().strftime("%d-%m-%y-%X")}_it={iterations}_setup={len(mixnet)}-{len(TTPs)}"
    for _ in tqdm(range(iterations)):

        destination = randint(1,N)
        header = client.send_packet(destination)

        for _ in range(3):
            mixnode = mixnet[header.n]
            header = mixnode.process_packet(header)
        assert destination == header.n

        save(header, file_name, format)

def ideal_case(iterations, format='txt'):
    """
    Mixnode on the fly
    See config for number of TTPs
    Random destination
    """
    file_name = f"{datetime.datetime.now().strftime("%d-%m-%y-%X")}_it={iterations}"
    for _ in tqdm(range(iterations)):

        mixnet = {}
        for _ in range(3):
            ip = randint(1, pow(2,128))
            mixnet[ip] = Mixnode(ip=ip)
        destination = randint(1,N)
        header = Client(mixnet, TTPs).send_packet(destination)

        for _ in range(3):
            mixnode = mixnet[header.n]
            header = mixnode.process_packet(header)
        assert destination == header.n

        save(header, f"{file_name}_ideal", format)

def save(header, file, format):
    if format == 'csv': 
        data = {
            'n': header.n,
            'alpha': header.alpha.x,
            'beta0': header.beta[0].x,
            'beta1': header.beta[1].x,
            'beta2': header.beta[2].x,
            'beta3': header.beta[3].x,
            'beta4': header.beta[4].x,
            'gamma': header.gamma.x,
        }
        # Make data frame of above data
        df = pd.DataFrame([data])
        df.to_csv(f"src/results/{file}.{format}", mode='a', index=False, header=False)
    if format == 'txt':
        with open(f"src/results/{file}.{format}", "a") as f:
            f.write(f"{header.alpha.x:0256b}{header.gamma.x:0256b}{header.beta[0].x:0256b}{header.beta[1].x:0256b}{header.beta[2].x:0256b}{header.beta[3].x:0256b}{header.beta[4].x:0256b}\n")


test()