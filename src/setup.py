import datetime
import random
import math

from utils import random_ip

NBR_MIXNODES = 20
NBR_TTP = 3

##############################
# 7 'independant' Generators # 
##############################
from ecc import N, G
from utils import truncated_hash
"""
Generate random and independent curve generators G_i based on a seed (updated every day)
NOTE: Need 7 different G_i, one for each 'block' (i.e. Point) in the header (to preserve 'unlinkability' property)
"""
seed = datetime.date.today().isoformat().encode('utf-8')
size_N = int(math.log(N,2))
G_i = [truncated_hash(seed, it=i, bits=size_N) * G for i in range(1,8)]

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
