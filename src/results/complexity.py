import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from tqdm import tqdm
from collections import Counter
import time
import random

from param import NBR_TTP
from utils import random_ip, extract_operation_log
from setup import mixnet, TTPs
from client import Client
from ecc import N, G
from elligator import hash_to_point, point_to_hash

def get_log(it):
    return pd.DataFrame([
        {
            'run': it,
            'operation': op.strip('_').replace('sub', 'add'),
            'entity': entity.replace('.py', ''),
            'function': func,
            'occurrence': count if entity!='ttp.py' else count // NBR_TTP
        }
        for ((op, entity, func), count) in Counter([log for log in extract_operation_log()]).items()
    ])

def operation_timing():
    """
    NOTE: Time comparison in seconds (absolu and relatif)
    EC multiplication (ecpy):       0.0021968028545379637       (1)
    point_to_hash:                  0.001901822566986084        (0.8657229132133841)
    point_to_hash (ideal):          0.0010171916484832764       (0.46303274159629326)
    hash_to_point:                  0.0008252565860748291       (0.37566256087572264)
    EC add (ecpy):                  0.0006737375259399414       (0.3066900266212752)
    """
    time_mult = []
    time_hash = []
    time_hash_r = []
    time_hash_r2 = []
    time_add = []
    for _ in range(1000):
        r = random.randint(N//100,N)

        start = time.time()
        r * G 
        time_mult.append(time.time()-start)
        
        start = time.time()
        hash_to_point(r) 
        time_hash.append(time.time()-start)

        P = hash_to_point(r)
        start = time.time()
        point_to_hash(P) 
        time_hash_r.append(time.time()-start)

        P = r*G
        start = time.time()
        point_to_hash(P) 
        time_hash_r2.append(time.time()-start)

        P2 = random.randint(N//100,N) * G
        start = time.time()
        P + P2
        time_add.append(time.time()-start)
        
    print(sum(time_mult)/len(time_mult))
    print(sum(time_hash)/len(time_hash))
    print(sum(time_hash_r)/len(time_hash_r))
    print(sum(time_hash_r2)/len(time_hash_r2))
    print(sum(time_add)/len(time_add))

if __name__ == '__main__':
    """
    NOTE: When running this script, the COUNT_OPERATIONS bool (in param.py) is set to True.
    Therefore the decorator to track the number of operations is enable.
    """

    logs = []
    client = Client(mixnet, TTPs)

    for it in tqdm(range(100)):
        header = client.send_packet(random_ip())
        header = mixnet[header.n].process_packet(header)    # NOTE: only once to get the number of operations per mixnode
        logs.append(get_log(it))
    
    logs = pd.concat(logs, ignore_index=True).sort_values(by=['run', 'entity', 'operation']).reset_index(drop=True)
    print(logs)