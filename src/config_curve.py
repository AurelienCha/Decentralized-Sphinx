from ecpy.curves import Curve, Point

##############
# LOAD CURVE #
##############
curve = Curve.get_curve('Curve25519') # Montgomery Curve25519
G = curve.generator
p = curve.field
N = curve.order
Z = 2  # Parameter for Elligator for Curve25519
A = curve.a

def print_curve():
    print((32-4)*'#' + ' SETUP ' + (32-4)*'#')
    print(f"CURVE           : x25519")
    print(f"TYPE            : Montgomery curve")
    print(f"EQUATION        : y² = x³ + {curve.a}x² + x")
    print(f"Field (prime p) : {p}")
    print(f"Order (N)       : {N}")
    print(f"Cofactor        : {int(p/N)}")
    print(f"Z (Elligator)   : {Z}")
    print(f"Generator       : ({G.x}, {G.y})")
    print(64*'#', '\n')