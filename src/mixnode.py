from setup import *
from header import *
from elligator import *
import secrets


class Mixnode:

    def __init__(self, ip):
        self.ip = ip
        # Secret key
        self._sk = secrets.randbelow(N)  # N is the curve order (i.e. nbr points on the curve)
        # Public key
        self.pk =  self._sk * G

    def process_packet(self, header):
        n, alpha, beta, gamma = header.get_content()

        if n != self.ip:
            raise ValueError(f"Packet reaching the wrong mixnode (IP={self.ip}), it should have reached {n}")

        # recompute share secret s
        S = self._sk * alpha
        s = point_to_hash(Block(0,S)) # TODO variety of sign (/!\ need modification in Client as well)
        # check integrity
        assert gamma == sum(beta) + s * G

        # beta padding
        beta += [curve.infinity, curve.infinity]

        # XOR
        for i in range(len(beta)):
            beta[i] = beta[i] - s * G_i[i]

        # update alpha
        alpha = hash((alpha.y + S.y).to_bytes(32)) * alpha
        return Header(n=point_to_hash(beta[0]), alpha=alpha, beta=beta[2:], gamma=beta[1])

    def get_key(self):
        return self.pk

    def get_ip(self):
        return self.ip
