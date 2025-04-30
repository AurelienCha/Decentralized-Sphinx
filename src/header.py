from __future__ import annotations
from typing import List, Tuple, Optional

from ecc import Point

class Header:
    """
    Represents a cryptographic Sphinx header (n, alpha, beta, gamma) 
    """
    
    def __init__(self, beta: List[int], gamma: int, n: Optional[int] = None, alpha: Optional[int] = None):
        """
        Initialize a Header 
        NOTE: Points are used in their compressed form (i.e. 256-bit integer)

        Args:
            n (Optional[int]): IP of the next hop
            alpha (Optional[int]): A compressed Point to recompute shared secrets   =>  i.e. Cryptographic group element    (α)
            beta (List[int]]): A list of compressed Points (256-bit int)            =>  i.e. Encrypted routing information  (β)
            gamma (int): A compressed point for integrity check                     =>  i.e. Integrity tag                  (γ)
        """
        self.n = n
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def __add__(self, other: Header) -> Header:
        """
        Left-side addition between two headers:
        - beta: Point-wise addition
        - gamma: Point addition
        """
        if not isinstance(other, Header):
            raise TypeError(f"unsupported operand type(s) for +: 'Header' and '{type(other)}'")
        g = (Point(self.gamma) + Point(other.gamma)).zip()
        b = [(Point(bs) + Point(bo)).zip() for (bs, bo) in zip(self.beta, other.beta)]
        return Header(beta=b, gamma=g)

    def __radd__(self, other: List[Header]) -> Header:
        """
        Right-side addition to enables sum()
        """
        if other == 0:
            return self
        if not isinstance(other, Header):
            raise TypeError(f"unsupported operand type(s) for -: 'Header' and '{type(other)}'")
        return self.__add__(other)

    def __eq__(self, other: Header) -> bool:
        """
        Check equality between two headers.
        """
        return (
            self.n==other.n and 
            self.alpha==other.alpha and 
            self.gamma==other.gamma and 
            all([bs==bo for (bs, bo) in zip(self.beta, other.beta)])
        )

    def set_alpha(self, alpha: Point) -> None:
        """
        Set the alpha field from a Point (that will be compressed)
        """
        self.alpha = alpha.zip()
    
    def set_n(self, n: int) -> None:
        """
        Set the n field (next hop) with an IP address (128-bit int)
        """
        self.n = n
    
    def unzip(self) -> Tuple[int, Point, List[Point], Point]:
        """
        Extract information form header (i.e. uncompressed Points)
        """
        return self.n, Point(self.alpha), [Point(b) for b in self.beta], Point(self.gamma)

    # NOTE: Print / Debug purpose (not used)
    #
    # def __str__(self):
    #     return f"""
    #     n     : {self.n}
    #     alpha : {self.alpha}
    #     beta  :     {self.beta[0]}
    #                 {self.beta[1]}
    #                 {self.beta[2]}
    #                 {self.beta[3]}
    #                 {self.beta[4]}
    #     gamma : {self.gamma}
    #     """
    #
    # def to_bin(self):return f"""
    #     n     : {self.n}
    #     alpha : {self.alpha:0256b}
    #     beta  : {self.beta[0]:0256b}
    #             {self.beta[1]:0256b}
    #             {self.beta[2]:0256b}
    #             {self.beta[3]:0256b}
    #             {self.beta[4]:0256b}
    #     gamma : {self.gamma:0256b}
    #     """