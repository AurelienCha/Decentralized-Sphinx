from datetime import date
from math import log
from utils import hash
from random import randint

##############################
# 7 'independant' Generators # => needed otherwise 'unlinkability' is not respected (see notebook notes)
##############################
from curve_config import *
seed = date.today().isoformat().encode('utf-8')
size_N = int(log(N,2))
G_i = [hash(seed, it=i, bits=size_N)*G for i in range(1,8)]

#####################
# MIXNET GENERATION #
#####################
from mixnode import *
ip_pool = set()
while len(ip_pool) < NBR_MIXNODES:
    ip_pool.add(randint(1, pow(2,128)) )# IPv6 are 128-bits addresses
mixnet = {}
for ip in ip_pool:
    mixnet[ip] = Mixnode(ip=ip) 

###################
# TTPs GENERATION #
###################
from ttp import *
TTPs = [TTP() for _ in range(NBR_TTP)]

