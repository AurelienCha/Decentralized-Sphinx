from typing import List, Tuple

from setup import G_i
from ecc import G, Point
from header import Header

class TTP:
    """
    Trusted Third Party (TTP) responsible for generating (partial) Sphinx headers
    """

    def __init__(self):
        pass  # Reserved for future use

    def generate_header(self, dest: Point, nodes: List[Point], s: List[int]) -> Header:
        """
        Generate a Sphinx header (multi-layer onion-style Header) using mixnodes and destination shares.

        Args:
            dest (Point): (partial) destination address 
            nodes (List[Point]): List of (partial) mixnode IPs (2nd and 3rd hop)
            s (List[int]): List of (partial) shared secrets (1st, 2nd and 3rd hop)

        Returns:
            Header: The computed encrypted (partial) Header

        NOTE: Processing in reverse order (from destination to first hop)
        """
        
        def _compute_initial_layer(dest: Point, s: List[int]) -> Tuple[List[Point], Point]:
            """
            Preprocessing of the header (Phi in the article (Φ)) and compute the first layer (which is slightly different)

            Args:
                dest (Point): (partial) destination address 
                s (List[int]): List of (partial) shared secrets (1st, 2nd and 3rd hop)
            
            Returns:
                beta (List[Point]): (partial) Encrypted routing information (β) on the first layer
                gamma (Point): (partial) Integrity tag (γ) on the first layer
            """
            beta = [
                dest + s[2] * G_i[0],
                - (s[1] * G_i[-4] + s[0] * G_i[-2]),
                - (s[1] * G_i[-3] + s[0] * G_i[-1]),
                -  s[1] * G_i[-2],
                -  s[1] * G_i[-1]
            ]

            gamma = sum(beta) + s[2] * G

            return beta, gamma


        def _compute_single_layer(IP: Point, beta: List[Point], gamma: Point, s: int) -> Tuple[List[Point], Point]:
            """
            Compute a single layer of the header

            Args:
                IP (Point): (partial) IP address of the 'previous' mixnode
                beta (List[Point]): (partial) Encrypted routing information (β) from the 'previous' layer
                gamma (Point): (partial) Integrity tag (γ) of 'previous' layer
                s (int): (partial) shared secrets of the 'NEXT' mixnode
            
            Returns:
                next_beta (List[Point]): (partial) Encrypted routing information (β) for the next layer
                next_gamma (Point): (partial) Integrity tag (γ) for the next layer
            """
            next_beta = [
                IP + s * G_i[0],
                gamma + s * G_i[1],
                beta[0] + s * G_i[2],
                beta[1] + s * G_i[3],
                beta[2] + s * G_i[4] 
            ]

            next_gamma = sum(next_beta) + s * G

            return (next_beta, next_gamma)

        # Layer 3 (destination -> third mixnode)
        beta, gamma = _compute_initial_layer(dest, s)
        # Layer 2 (third -> second mixnode)
        beta, gamma = _compute_single_layer(nodes[1], beta, gamma, s[1])  # NOTE: nodes[i] := IP of PREVIOUS layer
        # Layer 1 (second -> first mixnode)
        beta, gamma = _compute_single_layer(nodes[0], beta, gamma, s[0])  # NOTE: s[i] := shared secret of NEXT layer

        return Header(
            beta = [b.zip() for b in beta],  # NOTE: zip() return the compressed version of the point (256-bit)
            gamma = gamma.zip())