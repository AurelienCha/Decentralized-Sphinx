from mclbn256 import G1, Fr
from hashlib import sha256
from random import randint

###############
## ELLIGATOR ##
###############

# Replaced by an ersatz of Elligator for encoding/decoding IPv4

def encode_ip(ip: str) -> G1: 
    a, b, c, d = map(int, ip.split('.'))
    ip = (a << 24) | (b << 16) | (c << 8) | d
    return G1().mapfrom(Fr(ip << (221)))
    
def decode_ip(point: G1) -> str: # IP-Point to IPv4
    value = int(point.tostr().split()[1].decode(), 16) >> 221
    return f"{(value >> 24) & 255}.{(value >> 16) & 255}.{(value >> 8) & 255}.{value & 255}"

def get_rnd_ip() -> str:
    return f"{randint(0,255)}.{randint(0,255)}.{randint(0,255)}.{randint(0,255)}"
    
##########
## Hash ##
##########

def point_to_hash(Point):  # Point G1() -> Integer Fr()
    return Fr(int(sha256(Point.serialize()).hexdigest(), 16) >> 3) # shift of 3 bits because hash is 256 bits, curve is 253 bits

def hash_to_point(integer):  # Integer Fr() -> Point G1()
    return G1().mapfrom(integer)

# Hash anything to 253-bits integer
def hash(values) -> int:
    h = sha256()
    if not isinstance(values, (list, tuple)):
        values = [values]

    for v in values:
        h.update(str(v).encode())
        h.update(b"|")

    return int(h.hexdigest(), 16) >> 3  # From sha256 to 253-bits Fr()

################################
## ECC LAGRANGE INTERPOLATION ##
################################

# Lagrange interpolation at x=0
def lagrange_interpolation(points: list[tuple[Fr, G1]]) -> G1:
    result = points[0][1] * Fr(0)  # init to zero point

    for k, (xk, yk) in enumerate(points):
        numerator = Fr(1)
        denominator = Fr(1)

        for i, (xi, _) in enumerate(points):
            if i != k:
                numerator *= -xi
                denominator *= (xk - xi)

        result += yk * (numerator * ~denominator)

    return result

###########################
## POLYNOMIAL EVALUATION ##
###########################

class Polynomial:
    def __init__(self, coeffs):
        self.coeffs = coeffs  # [a0, a1, ...]

    def __call__(self, x):
        # Horner's method (fast polynomial evaluation)
        acc = self.coeffs[-1]
        for c in reversed(self.coeffs[:-1]):
            acc = acc * x + c
        return acc
