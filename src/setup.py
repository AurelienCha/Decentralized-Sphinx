import datetime
import random
import math

from param import NBR_MIXNODES, NBR_TTP
from utils import random_ip

##############################
# 7 'independant' Generators # 
##############################
from ecc import N, G, curve
from utils import truncated_hash
from elligator import hash_to_point
"""
Generate random and independent curve generators G_i based on a seed (updated every day)
NOTE: Need 7 different G_i, one for each 'block' (i.e. Point) in the header (to preserve 'unlinkability' property)
"""
seed = datetime.date.today().isoformat().encode('utf-8')
size_N = int(math.log(N,2))
G_i = [8 * hash_to_point(truncated_hash(seed, it=i, bits=size_N)) for i in range(1,8)]  # NOTE: multiply by 8 to stay in the same subfield (see 'clean cofactor' in Elligator 2)

#####################
# MIXNET GENERATION #
#####################
from mixnode import Mixnode
"""
Generate a dictionary of mixnodes with unique IPv6 addresses (i.e. random 128 bits) => dict[IP, mixnode]
"""
ip_pool = set()
while len(ip_pool) < NBR_MIXNODES:
    ip_pool.add(random_ip())
mixnet = {ip: Mixnode(ip=ip) for ip in ip_pool}

###################
# TTPs GENERATION #
###################
from ttp import TTP
"""
Generate a list of TTPs
"""
TTPs = [TTP() for _ in range(NBR_TTP)] 
