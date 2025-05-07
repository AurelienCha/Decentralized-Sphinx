from typing import List, Tuple, Optional
import random

from param import NBR_TTP
from ecc import p, N, G, Point
from utils import truncated_hash
from elligator import hash_to_point, point_to_hash
from mixnode import Mixnode
from ttp import TTP
from setup import mixnet, TTPs

class Client:
    """
    Represents a mixnet client that build a decentralized Sphinx header (through the use of TTPs)
    """

    def __init__(self, mixnet: dict[int, Mixnode] = mixnet, TTPs: List[TTP] = TTPs) -> None:
        """
        Initializes a Client instance with the system information

        Args:
            mixnet (dict[int, Mixnode]): A dictionary mapping IP addresses to mixnode 
            TTPs (List[TTP]): List of trusted third parties (TTPs) in the system
        """
        self.mixnet = mixnet
        self.TTPs = TTPs

    def send_packet(self, dest: int, path: Optional[List[int]] = None, x: Optional[int] = None):
        """
        Constructs a sphinx packet for the desired destination (by default: random path of size 3)

        Args:
            dest (int): Destination IP
            path (Optional[List[int]]): List of 3 mixnode's IP (optional).
            x (Optional[int]): Client's nonce (optional).

        Returns:
            Header object: The final sphinx header
        """
        if len(self.mixnet) >= 3: # Path of 3 mixnodes
            path = path if path else random.sample(sorted(self.mixnet), 3) # without replacement
        else: # NOTE: only for the testing worst case scenario
            path = path if path else random.choices(sorted(self.mixnet), k=3) # with replacement
        x = x if x else random.randint(1, N) # N = nbr pts on curve # x * G
        return self.build_header(x, dest, path)

    def split_point(self, point: Point, m: int) -> List[Point]:
        """
        Splits an elleptic curve point into m additive shares

        Args:
            point (Point): Point to split
            m (int): Number of shares

        Returns:
            List[Point]: A list of m Points summing to the input point.
        """
        shares = [random.randint(1,N-1) * G for _ in range(m-1)]  # NOTE: Need a random Point, so we could use hash_to_point() (elligator): for the moment EC multiplication is ~2.5 time slower than hash_to_point() because ecpy lib is not efficient...
        shares.append(point - sum(shares))
        return shares

    def split_int(self, integer: int, m: int) -> List[int]:
        """
        Splits an integer into m additive shares modulo N

        Args:
            integer (int): Integer to split
            m (int): Number of shares 

        Returns:
            List[int]: A list of m integers summing to the input modulo N.
        """
        shares = [random.randint(1, p) for _ in range(m-1)]    # NOTE (mod p) because numbers are in mod p (i.e. shared secrets)
        last_share = (integer - sum(shares)) % N        # NOTE (mod N) because numbers are used to aggregate point multiplication (i.e. sum(s*G))
        shares.append(last_share)
        return shares

    def build_header(self, x: int, dest: int, path: List[str]):
        """
        Constructs a Sphinx header:
        1) Generate the chain of shared secrets (Points)
        2) Splitting information in pieces to get partial information: IPs (int -> Point) and share secrets (Point -> int)
        3) Send to TTP partial information (dest, nodes, secrets) to generate partial header 
        4) Aggregate partial headers, and set the first mixnode's IP (int) and Alpha (Point)

        Args:
            x (int): Client's Nonce
            dest (int): Destination IP
            path (List[int]): List of 3 mixnode's IP

        Returns:
            Header: The Sphinx header
        """
        # 1) Generate the chain of shared secrets 
        shared_secrets = self.generate_shared_secrets(x, path) 
        n0, *path = path # first node don't need further processing since it is send in 'cleartext' (first hop)

        # 2) Spliting information (Destination IPs, Node's IPs, Shared secret)
        partial_dest = self.split_point(hash_to_point(dest), NBR_TTP)
        partial_nodes = list(zip(*[self.split_point(hash_to_point(n), NBR_TTP) for n in path]))  # zip(*matrix) := transpose
        partial_secrets = list(zip(*[self.split_int(point_to_hash(S), NBR_TTP) for S in shared_secrets]))
        
        # 3) Send to TTP partial information (dest, nodes, secrets) to generate partial header 
        split_headers = [ttp.generate_header(partial_dest[i], partial_nodes[i], partial_secrets[i]) for (i, ttp) in enumerate(self.TTPs)]
        
        # 4) Aggregate partial headers, and set the first mixnode's IP (int) and Alpha (Point) 
        header = sum(split_headers)
        header.set_n(n0)
        header.set_alpha(x * G)

        return header
    
    def generate_shared_secrets(self, x: int, path: List[int]) -> Tuple[Point, Point, Point]:
        """
        Generates the chain of shared secrets for the given path

        Args:
            x (int): Client's Nonce
            path (List[int]): List of 3 mixnode's IPs

        Returns:
            Tuple[Point, Point, Point]: Shared secrets (S1, S2, S3)
        """

        def _compute_secret(x, PK):
            alpha = x * G 
            S = x * PK  
            b = truncated_hash((alpha.y() + S.y()).to_bytes(32)) # TODO better randomization ?
            return (x * b, S)
        
        PK = [self.mixnet[ip].get_key() for ip in path]

        x1, S1 = _compute_secret(x, PK[0])
        x2, S2 = _compute_secret(x1, PK[1])
        _, S3 = _compute_secret(x2, PK[2])

        return S1, S2, S3