from mclbn256 import G1, Fr
from random import randint, sample
from time import time
from math import prod 

from crypto import *


class Mixnode:
    def __init__(self, ip):
        self.k = Fr().randomize()          # secret key
        self.N = encode_ip(ip)             # IP encoding
        self.r = randint(1, pow(2,32))     # Identifier

        # Random polynomials with constraint at 0
        self.f = Polynomial([Fr(self.k)] + [Fr().randomize() for _ in range(d - 1)]) # polynome Fr() of degree d-1 : f(0)=k
        self.g = Polynomial([self.N] + [G1().randomize() for _ in range(d - 1)])     # polynome G1() of degree d-1 : g(0)=N

    def send_share(self, t):

        # Shares (i.e. evaluate polynomials at t)
        k_t = self.f(t)
        N_t = self.g(t)

        return (self.r, k_t, N_t)


class STTP:
    def __init__(self):
        self.t = Fr(hash(get_rnd_ip()))
        self.table = []
    
    def get_shares(self):
        self.table = [node.send_share(self.t) for node in MIXNODES.values()]
        self.table.sort()
        
    def compute_route(self, w):
        Alpha = hash_to_point(w)

         # every sec (may truncate to timestamp to get every 10 sec)
        seed = f"{w}{int(time())}" 
        n = len(self.table)

        path_materials = []
        for i in range(PATH_LENGTH):
            h = hash(seed + str(i))
            _, k_it, N_it = self.table[h % n]  # take mixnode at index h (modulo table size)
            path_materials.append((N_it,  Alpha * k_it))

        return self.t, path_materials  # (t, [N_i, S_i]_{for i in range(PATH_LENGTH)})


class Client:
    
    def get_rnd_route(self):
        w = Fr().randomize()
        Alpha = hash_to_point(w)
        
        all_shares = []
        for sttp in sample(STTPS, k=d):
            sttp_shares = []
            t, path_materials = sttp.compute_route(w) # (t, [N_i, S_i]_{for i in range(PATH_LENGTH)})
            for (N_it, S_it) in path_materials:
                sttp_shares.append((t, N_it))
                sttp_shares.append((t, S_it))
            all_shares.append(sttp_shares)

        all_shares = [lagrange_interpolation(points) for points in zip(*all_shares)]
        N_list, S_list = all_shares[::2], all_shares[1::2]

        # Rerandomization
        r = Fr().randomize()
        Alpha = Alpha * r
        S_list = [S * r for S in S_list]

        # Cascade
        s_list = []
        for S in S_list:
            s_list.append(point_to_hash(S * prod(s_list, start=Fr(1))))

        return (Alpha, N_list, s_list)


##########
## MAIN ##
##########

if __name__ == "__main__":

    ## PARAMETERS ------------------------------------------
    NBR_MIXNODES = 10
    NBR_STTPS = 5
    PATH_LENGTH = 3
    d = 5


    ## INIT ------------------------------------------------
    STTPS = [STTP() for _ in range(NBR_STTPS)]
    MIXNODES = {}
    for _ in range(NBR_MIXNODES):
        ip = get_rnd_ip()
        MIXNODES[ip] = Mixnode(ip)

    ## SETUP ------------------------------------------------
    for sttp in STTPS:
        sttp.get_shares()

    ## ROUTE SAMPLING ---------------------------------------
    Alpha_0, N_list, s_list = Client().get_rnd_route()


    # VERIFICATION that it works ----------------------------
    Alpha = Alpha_0
    for N, s in zip(N_list, s_list):
        ip = decode_ip(N)
        print(ip)
        node = MIXNODES.get(ip)
        assert s == point_to_hash(Alpha * node.k)   # Verify correct shared secret derivation
        Alpha *= s                                  # Update alpha