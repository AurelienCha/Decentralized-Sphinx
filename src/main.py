from setup import *
from elligator import *
from client import *

# TEST_ELLIGATOR(10)
# print(mixnet)
# print(G_i)

from tqdm import tqdm
for _ in tqdm(range(100)):
    DESTINATION = randint(1,N)
    header = Client().send_packet(DESTINATION)

    for _ in range(3): # path of length 3
        # print(_ , header)
        mixnode = mixnet[header.n]
        header = mixnode.process_packet(header)
    # print(header)
    assert DESTINATION == header.n