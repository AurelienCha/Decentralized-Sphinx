from sympy.ntheory.residue_ntheory import sqrt_mod
from setup import *
from header import *

def legendre(n):
    """Legendre symbol:

    returns  0 if n is zero
    returns  1 if n is a non-zero square
    returns -1 if n is not a square
    """
    e = pow(n, (p - 1) // 2, p)
    return -1 if e == p - 1 else e
    
def is_negative(v, p):
    return v > (p - 1) // 2


def is_square(n):
    return legendre(n) != -1

def hash_to_point(r):
    w = (-A * pow((1 + Z*pow(r,2,p)), -1, p)) % p
    e = legendre(w**3 + A*w**2 + w)
    u = (e*w - (1-e)*(A//2)) % p
    v = (-e * sqrt_mod(u**3 + A*u**2 + u, p)) % p

    return Block(is_negative(r,p), Point(u, v, curve)) 

def point_to_hash(block):

    P = block.point

    while P.x == -A or not is_square(-Z * P.x * (P.x + A)): 
        # Instead of raise "no inverse mapping" => increment the point until we get a valid mapping (i.e. apply "_find_valid_mapping_point()")
        P = P + G
        # TODO TOTEST: inverte sign if not mapping
        # block.sign ^= 1 # XOR 1 == inverse bit
    if P.x == -A or not is_square(-Z * P.x * (P.x + A)):
        raise "no inverse mapping"
    if is_negative(P.y, p):
        rep = sqrt_mod(-(P.x + A) * pow(Z * P.x, -1, p), p)
    else:
        rep = sqrt_mod(-P.x * pow(Z * (P.x + A), -1, p), p)
        
    if block.sign:
        return -rep % p
    else:
        return rep


def _find_valid_mapping_point(P): # Should not be used in the code
    """
    Ensures that the point P satisfies the conditions for a valid mapping.
    Specifically, it checks that:
    1. P.x is not equal to -A (which would make the mapping invalid).
    2. The quantity `-Z * P.x * (P.x + A)` is a perfect square.

    If either condition is violated, it increments the point by the generator G
    and checks again, repeating the process until a valid point is found.
    In average: 1 miss (i.e. enters once in the loop)

    Args:
    - P: An elliptic curve point.

    Returns:
    - A valid elliptic curve point P that satisfies the mapping conditions.
    """
    while P.x == -A or not is_square(-Z * P.x * (P.x + A)):
        P = P + G
        # TODO TOTEST by default Block(0, P) => Only 50% of points
        # We could if P failed (i.e. enter the loops) put sign=1 => Block(1, P) => Cover 75% of points (fewer collusions)
    return P


def TEST_ELLIGATOR(it=100):
    from tqdm import tqdm
    for _ in tqdm(range(it)):
        r = randint(1,p)
        assert point_to_hash(hash_to_point(point_to_hash(hash_to_point(r)))) == r
        sign = randint(0,1)
        P = r*G
        block = Block(sign, P)
        assert hash_to_point(point_to_hash(hash_to_point(point_to_hash(block)))) == hash_to_point(point_to_hash(block))
        assert hash_to_point(point_to_hash(hash_to_point(point_to_hash(block)))) == Block(sign, _find_valid_mapping_point(P))
