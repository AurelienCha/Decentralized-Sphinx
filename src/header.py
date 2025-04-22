from ecpy.curves import Point
from setup import *

class Block:

        def __init__(self, sign, point):
            self.sign = sign
            self.point = point

        def __str__(self):
            return f"{"-" if self.sign else "+"}{self.point.x}"

        def to_bin(self):
            # Format as a 256-bit binary string
            return f"{((self.sign << 255) | self.point.x):0256b}"

        def __add__(self, other):
            if isinstance(other, Point):
                return Block(self.sign, self.point + other) 
            elif not isinstance(other, Block):
                raise TypeError(f"unsupported operand type(s) for +: 'Block' and '{type(other)}'")
            return Block(self.sign ^ other.sign, self.point + other.point)

        def __sub__(self, other):
            if isinstance(other, Point):
                return Block(self.sign, self.point - other) 
            elif not isinstance(other, Block):
                raise TypeError(f"unsupported operand type(s) for -: 'Block' and '{type(other)}'")
            return Block(self.sign ^ other.sign, self.point - other.point)

        def __radd__(self, other):
            if other == 0:
                return self
            if not isinstance(other, Block):
                raise TypeError(f"unsupported operand type(s) for -: 'Block' and '{type(other)}'")
            return self.__add__(other)

        def __eq__(self, other):
            return self.sign==other.sign and self.point==other.point


class Header:
    
    def __init__(self, n=None, alpha=None, beta=5*[None], gamma=None):
        self.n = n
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def __str__(self):
        return f"""
        n     : {self.n}
        alpha : {self.alpha}
        beta  :     {self.beta[0]}
                    {self.beta[1]}
                    {self.beta[2]}
                    {self.beta[3]}
                    {self.beta[4]}
        gamma : {self.gamma}
        """

    def to_bin(self):return f"""
        n     : {self.n.to_bin()}
        alpha : {self.alpha.to_bin()}
        beta  : {self.beta[0].to_bin()}
                {self.beta[1].to_bin()}
                {self.beta[2].to_bin()}
                {self.beta[3].to_bin()}
                {self.beta[4].to_bin()}
        gamma : {self.gamma.to_bin()}
        """

    def __add__(self, other):
        if not isinstance(other, Header):
            raise TypeError(f"unsupported operand type(s) for +: 'Header' and '{type(other)}'")
        n = (self.n + other.n) % N
        a = self.alpha + other.alpha
        g = self.gamma + other.gamma
        b = [bs + bo for (bs, bo) in zip(self.beta, other.beta)]
        return Header(n=n, alpha=a, beta=b, gamma=g)

    def __radd__(self, other):
        if other == 0:
            return self
        if not isinstance(other, Header):
            raise TypeError(f"unsupported operand type(s) for -: 'Header' and '{type(other)}'")
        return self.__add__(other)

    def __eq__(self, other):
        return self.n==other.n and self.alpha==other.alpha and self.gamma==other.gamma and all([bs==bo for (bs, bo) in zip(self.beta, other.beta)])

    def set_alpha(self, alpha):
        self.alpha = alpha
    
    def get_content(self):
        return self.n, self.alpha, self.beta, self.gamma