from random import randint, sample, choices

from setup import *
from elligator import hash_to_point, point_to_hash
from header import Block#, Header


class Client:

    def __init__(self, mixnet=mixnet, TTPs=TTPs):
        self.mixnet = mixnet
        self.TTPs = TTPs

    def send_packet(self, dest, path=None, x=None):
        if len(self.mixnet) >= 3: # Path of 3 mixnodes
            path = path if path else sample(sorted(self.mixnet), 3) # without replacement
        else: # NOTE: only for the testing part
            path = path if path else choices(sorted(self.mixnet), k=3) # with replacement
        x = x if x else randint(1, N) # N = curve order (i.e. nbr pts on curve)
        return self.build_header(x, dest, path)

    def split(self, value, nbr_pieces):
        if isinstance(value, int):
            res = self._split_integer(value, nbr_pieces)
        elif isinstance(value, Block):
            res = self._split_block(value, nbr_pieces)
        else:
            raise TypeError("split() takes either an integer or a 'Block' (i.e. EC Point with sign) as input")
        return res

    def _split_point(self, point, m):
        def sum_points(points):
            from functools import reduce
            return reduce(lambda x,y: (x+y), points)
        # Create a list of 'm-1' random Block
        shares = [randint(1,N-1) * G for _ in range(m-1)]
        # Compute and add the last Block such that the sum equals the original value
        shares.append(point - sum_points(shares))
        return shares

    def _split_block(self, block, m):
        # Create a list of 'm-1' random Block
        shares = [Block(randint(0,1), randint(1,N-1) * G) for _ in range(m-1)]
        # Compute and add the last Block such that the sum equals the original value
        shares.append(block - sum(shares))
        return shares

    def _split_integer(self, integer, m, max_range=N):
        # Create a list of 'm-1' random integer
        shares = [randint(1,max_range) for _ in range(m-1)]
        # Compute and add the last integer such that the sum equals the original value
        last_share = (integer - sum(shares)) % max_range
        shares.append(last_share)
        return shares

    def build_header(self, x, dest, path):
        # Compute shared secrets
        shared_secrets = self.generate_shared_secrets(x, path) 

        split_alpha = self._split_point(x * G, NBR_TTP) #
        split_dest = self.split(hash_to_point(dest), NBR_TTP)
        path = [path[0]] + [hash_to_point(n) for n in path[1:]]  # first node in path is 'ip' not block
        split_nodes = list(zip(*[self.split(n, NBR_TTP) for n in path])) # zip(*matrix) = transpose
        split_secrets = list(zip(*[self.split(point_to_hash(S), NBR_TTP) for S in shared_secrets]))
        
        split_headers = [ttp.generate_header(split_alpha[i], split_dest[i], split_nodes[i], split_secrets[i]) for (i, ttp) in enumerate(self.TTPs)]
        header = sum(split_headers)

        return header
            
    def generate_shared_secrets(self, x, path):
        def _compute_single_secret(x, PK):
            alpha = x * G  # = b1 * ALPHA_1
            S = x * PK  # TODO ensure_mapping (handle in Elligator.py point_to_hash())
            b = hash((alpha.y + S.y).to_bytes(32)) # TODO CHECK
            return (x * b, S)
        
        PK = [self.mixnet[ip].get_key() for ip in path]

        x1, S1 = _compute_single_secret(x, PK[0])
        x2, S2 = _compute_single_secret(x1, PK[1])
        _, S3 = _compute_single_secret(x2, PK[2])

        return (Block(0,S1), Block(0,S2), Block(0,S3)) # TODO sign must be random sometimes '0', sometimes '1' # check with ensure_mapping 


    # def _build_header_alone(self, alpha, dest, N, s):
    #     """
    #     N = list of piece of mixnode IP (Point) and destionation
    #     s = list of piece of shared secrets (Scalar)
    #     """
    #     def _compute_initial_layer(dest, s):
    #         beta = [
    #             dest + s[2] * G_i[0],
    #             - (s[1] * G_i[-4] + s[0] * G_i[-2]),
    #             - (s[1] * G_i[-3] + s[0] * G_i[-1]),
    #             -  s[1] * G_i[-2],
    #             -  s[1] * G_i[-1]
    #         ]
    #         gamma = sum(beta) + s[2] * G
    #         return beta, gamma


    #     def _compute_single_layer(N, s, beta, gamma):
    #         next_beta = [
    #             N + s * G_i[0],
    #             gamma + s * G_i[1],
    #             beta[0] + s * G_i[2],
    #             beta[1] + s * G_i[3],
    #             beta[2] + s * G_i[4]
    #         ]
    #         next_gamma = sum(next_beta) + s * G
    #         return (next_beta, next_gamma)

    #     # Layer 3
    #     beta, gamma = _compute_initial_layer(dest, s)
    #     # Layer 2
    #     beta, gamma = _compute_single_layer(N[2], s[1], beta, gamma)
    #     # Layer 1
    #     beta, gamma = _compute_single_layer(N[1], s[0], beta, gamma)

    #     return Header(n=N[0], alpha=alpha, beta=beta, gamma=gamma)