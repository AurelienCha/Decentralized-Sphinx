from __future__ import annotations
from typing import Union
from sympy.ntheory.residue_ntheory import sqrt_mod


from utils import track_operation # decorator
from ecpy.curves import Curve
from ecpy.curves import Point as ECCPoint

class Point:
    """
    A wrapper for elliptic curve point (from ECPy library) that supports compressed initialization
    from a 256-bit integer where the first bit indicates the sign of the y-coordinate.
    """

    def __init__(self, arg: Union[int, ECCPoint]):
        """
        Initializes a Point instance from either:
        - an ECCPoint object, or
        - a 256-bit integer (first bit is the sign of y, remaining 255 bits are x coordinates)
        """
        if isinstance(arg, int):  # 256-bit integer with first bit for y-sign
            sign = arg >> 255
            x = arg & ((1 << 255) - 1)
            y = sqrt_mod((pow(x,3,p) + A*pow(x,2,p) + x) % p, p, all_roots=True)[sign]
            self.point = ECCPoint(x, y, curve)
        elif isinstance(arg, ECCPoint):  # ECPy Point
            self.point = arg
        else:
            raise TypeError(f"{type(arg)} 'arg' must be an ECCPoint or integer (1-bit sign | 255-bit x-coord)")

    def zip(self) -> int:
        """
        Compresses the point into a 256-bit integer with the sign bit as the MSB.

        Returns:
            int: A 256-bit integer with sign of y as the highest bit and x-coordinate in the lower 255 bits.
        """
        return (is_negative(self.y()) << 255) + self.x()

    def x(self) -> int:
        """
        Returns the x-coordinate of the point
        """
        return self.point.x

    def y(self) -> int:
        """
        Returns the y-coordinate of the point
        """
        return self.point.y

    @track_operation
    def __add__(self, Q: Point) -> Point:
        """
        Left-side addition between two elliptic curve points (P + Q)
        """
        if not isinstance(Q, Point):
            raise TypeError(f"unsupported operand type(s) for +: 'Point' and '{type(Q)}'")
        return Point(self.point + Q.point)

    def __radd__(self, Q: List[Point]) -> Point:
        """
        Right-side addition to enables sum()
        """
        if Q == 0:
            return self
        return self.__add__(Q)
    
    @track_operation
    def __sub__(self, Q: Point) -> Point:
        """
        Subtraction between two elliptic curve points (P - Q)
        """
        if not isinstance(Q, Point):
            raise TypeError(f"unsupported operand type(s) for -: 'Point' and '{type(Q)}'")
        return Point(self.point - Q.point)

    @track_operation
    def __mul__(self, n: int) -> Point:
        """
        Left-side scalar multiplication of a point (P * n)
        """
        if not isinstance(n, int):
            raise TypeError(f"unsupported operand type(s) for *: 'Point' and '{type(n)}'")
        return Point(n * self.point)

    def __rmul__(self, n: int) -> Point:
        """
        Right-side scalar multiplication of a point (n * P)
        """
        return self.__mul__(n)

    def __neg__(self) -> Point:
        """
        Negates the point (x,y) => (x, -y mod p)
        """
        return Point(-self.point)

    def __eq__(self, Q: Point) -> bool:
        """
        Checks equality between two points (P == Q)
        """
        if not isinstance(Q, Point):
            raise TypeError(f"unsupported operand type(s) for ==: 'Point' and '{type(Q)}'")
        return self.point == Q.point


##############
# LOAD CURVE #
##############

curve = Curve.get_curve('Curve25519')   # Montgomery Curve25519
G = Point(curve.generator)              # A point able to generate all the other points on the curve
p = curve.field                         # (x,y) coords are in [0,p[
N = curve.order                         # nbr points on the curve (i.e. N*G = O, (N+1)*G = G)
A = curve.a                             # Parameter of the curve used in Elligator
Z = 2                                   # Parameter of Elligator for Curve25519

def is_negative(v):
    return v > (p - 1) // 2

def print_curve():
    print()
    print((50-4)*'#' + ' CURVE ' + (50-4)*'#')
    print(f"NAME            : x25519")
    print(f"TYPE            : Montgomery curve")
    print(f"EQUATION        : y² = x³ + {curve.a}x² + x")
    print(f"Field (prime p) : {p}")
    print(f"Order (N)       : {N}")
    print(f"Cofactor        : {int(p/N)}")
    print(f"Z (Elligator)   : {Z}")
    print(f"Generator       : ({G.x()}, {G.y()})")
    print(100*'#', '\n')

print_curve()