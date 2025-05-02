from sympy.ntheory.residue_ntheory import sqrt_mod

from utils import track_operation # decorator
from ecc import  A, Z, p, G, curve, ECCPoint, Point, is_negative
from utils import rnd_padding

def legendre(n: int) -> int:
    """Legendre symbol:

    returns  0 if n ≡ 0 mod p
    returns  1 if n is a quadratic residue mod p (i.e. non-zero square)
    returns -1 if n is a non-residue mod p (i.e. not a square)
    """
    e = pow(n, (p - 1) // 2, p)
    return -1 if e == p - 1 else e

def is_square(n: int) -> bool:
    """
    Checks whether n is a quadratic residue modulo p (i.e. non-zero square)
    """
    return legendre(n) != -1

@track_operation
def hash_to_point(r: int) -> Point:
    """
    Maps an integer to an elliptic curve point using a modified Elligator2 method.
    NOTE: Used only for mapping IP addresses (i.e. n1, n2, n3, dest) in a reversible way

    Args:
        r (int): Integer to map to a Point on the curve (e.g. n1, n2, n3, dest)

    Returns:
        Point: A valid elliptic curve point on the curve.
    """
    r = rnd_padding(r)  # NOTE: Tweak for our use case (not in the original 'Elligator2' algorithm)

    w = (-A * pow((1 + Z*pow(r,2,p)), -1, p)) % p
    e = legendre(w**3 + A*w**2 + w)
    u = (e*w - (1-e)*(A//2)) % p
    v = (-e * sqrt_mod(u**3 + A*u**2 + u, p)) % p

    return Point(ECCPoint(u, v, curve))

@track_operation
def point_to_hash(P: Point) -> int:
    """
    Maps a curve point to an integer representation.
    
    NOTE:point-to-hash is used for:
    - shared_secrets (s_i)            => Can be 'one-way' (because never use the inverse mapping with shared secrets)
    - IP addresses (n1, n2, n3, dest) => Must be 'bidirectionnal' (because should be able to get back the original IP value) 
    ===> With our tweak, it is 'bidirectionnal' iff P is a valid point for the mapping. 
    ===> It will always be the case for IP addresses since we first apply the hash_to_point(ip) (so we work with a valid point)

    Args:
        P (Point): A valid elliptic curve point.

    Returns:
        int: An integer derived from the point.
    """
    # NOTE: (while loop) Tweak for our use case (not in the original 'Elligator2' algorithm)
    while P.x() == -A or not is_square(-Z * P.x() * (P.x() + A)): 
        P = P + G # normally only for shared_secret (see. ) -> half percent chance to enter in a loop iteration
    
    if P.x() == -A or not is_square(-Z * P.x() * (P.x() + A)):
        raise "no inverse mapping"
    if is_negative(P.y()):
        rep = sqrt_mod(-(P.x() + A) * pow(Z * P.x(), -1, p), p)
    else:
        rep = sqrt_mod(-P.x() * pow(Z * (P.x() + A), -1, p), p)

    return rep

def test_elligator(it: int = 100) -> None:
    """
    Run tests to verify the consistency of our Elligator2 specific implementation (hash_to_point and point_to_hash functions).
    """
    import random
    from tqdm import tqdm
    def find_valid_mapping_point(P: Point) -> Point:
        """
        Ensures that the point P satisfies the conditions for a valid mapping.
        Specifically, it checks that:
        1. P.x is not equal to -A (which would make the mapping invalid).
        2. The quantity `-Z * P.x * (P.x + A)` is a perfect square.

        If either condition is violated, it increments the point by the generator G
        and checks again, repeating the process until a valid point is found.
        In average: 1 miss (i.e. enters once in the loop)


        Args:
            P (Point): An elliptic curve point

        Returns:
            Point: A valid elliptic point that satisfies the inverse mapping conditions (i.e. point_to_hash)
        """
        while P.x == -A or not is_square(-Z * P.x * (P.x + A)):
            P = P + G
        return P

    for _ in tqdm(range(it)):
        r = random.randint(1,p)
        assert point_to_hash(hash_to_point(r)) == r
        P = r*G
        assert hash_to_point(point_to_hash(hash_to_point(point_to_hash(P)))) == hash_to_point(point_to_hash(P))
        Q = find_valid_mapping_point(P)
        assert hash_to_point(point_to_hash(Q)) == Q
