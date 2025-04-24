import pandas as pd

from setup import *
from client import Client

from tqdm import tqdm
for _ in tqdm(range(pow(10,4))):
    DESTINATION = randint(1,N)
    header = Client().send_packet(DESTINATION)

    for _ in range(3): # path of length 3
        # print(_ , header)
        mixnode = mixnet[header.n]
        header = mixnode.process_packet(header)
    # print(header)
    assert DESTINATION == header.n

    # data of Player and their performance
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
    df.to_csv('src/results/output.csv', mode='a', index=False, header=False)