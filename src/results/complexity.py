import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from tqdm import tqdm
from collections import Counter

from param import NBR_TTP
from utils import random_ip, extract_operation_log
from setup import mixnet, TTPs
from client import Client

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