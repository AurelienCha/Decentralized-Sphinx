import secrets

from setup import G_i
from ecc import N, G, Point, curve, p
from elligator import point_to_hash
from utils import truncated_hash, my_hash
from header import Header

class Mixnode:
    """
    Represents a mixnet node with elliptic curve asymmetric keys

    Attributes:
        ip (int): The mixnode's IP address
        sk (int): The mixnode's private key
        pk (Point): The mixnode's public key
    """

    def __init__(self, ip: int):
        """
        Initialize a Mixnode with a unique IP address and ECC key pair
        """
        self.ip = ip
        # NOTE: N is the curve order (i.e. nbr points on the curve)
        self.sk = secrets.randbelow(N)          # secret key (int)
        self.PK =  self.sk * G                  # Public Key (Point)

    def process_packet(self, header: Header) -> Header:
        """
        Process an incoming packet (header) and return the updated outgoing packet (header)
        1) Extract information from the header
        2) Recompute shared secret
        3) Integrity check
        4) Update encrypted information (β)
        5) Update cryptographic element (α)

        Args:
            header (Header): The incoming packet header

        Returns:
            Header: The transformed outgoing packet header 
        """
        # 1) Extract information from the header
        n, alpha, beta, gamma = header.unzip()
        if n != self.ip:
            raise ValueError(f"Packet reaching the wrong mixnode (IP={self.ip}), it should have reached {n}")

        # 2) Recompute shared secret
        S = self.sk * alpha                 # Shared secret in Point version
        s = point_to_hash(S)                # Shared secret in integer version

        # 3) Integrity check
        h = s
        h = [h:=my_hash(h) for i in range(5)]
        assert gamma == s*G + sum([h[i] * beta[i] for i in range(5)])

        # 4) Update encrypted information (β)
        beta += [Point(curve.infinity), Point(curve.infinity)]  # Padding
        for i in range(len(beta)):                              # Block-wise 'XOR' operations
            beta[i] = beta[i] - s * G_i[i]

        # 5) Update cryptographic element (α)
        alpha = truncated_hash((alpha.y() + S.y()).to_bytes(32)) * alpha

        return Header(
            n = point_to_hash(beta[0]) % pow(2,128), 
            alpha = alpha.zip(), 
            beta = [b.zip() for b in beta[2:]], 
            gamma = beta[1].zip())

    def get_key(self) -> Point:
        """Returns the public key of the mixnode (Point)"""
        return self.PK

    def get_ip(self) -> int:
        """Returns the IP address of the mixnode (int)"""
        return self.ip
