from setup import *
from header import Header

print("????", G_i)
class TTP:

    def __init__(self):
        pass # TODO

    def generate_header(self, alpha, dest, N, s):
        # TODO verify if 'alpha' is the entire value (or a piece)
        """
        N = list of piece of mixnode IP (Point) and destionation
        s = list of piece of shared secrets (Scalar)
        """
        def _compute_initial_layer(dest, s):
            beta = [
                dest + s[2] * G_i[0],
                - (s[1] * G_i[-4] + s[0] * G_i[-2]),
                - (s[1] * G_i[-3] + s[0] * G_i[-1]),
                -  s[1] * G_i[-2],
                -  s[1] * G_i[-1]
            ]
            gamma = sum(beta) + s[2] * G
            return beta, gamma


        def _compute_single_layer(N, s, beta, gamma):
            next_beta = [
                N + s * G_i[0],
                gamma + s * G_i[1],
                beta[0] + s * G_i[2],
                beta[1] + s * G_i[3],
                beta[2] + s * G_i[4]
            ]
            next_gamma = sum(next_beta) + s * G
            return (next_beta, next_gamma)

        # Layer 3
        beta, gamma = _compute_initial_layer(dest, s)
        # Layer 2
        beta, gamma = _compute_single_layer(N[2], s[1], beta, gamma)
        # Layer 1
        beta, gamma = _compute_single_layer(N[1], s[0], beta, gamma)

        return Header(n=N[0], alpha=alpha, beta=beta, gamma=gamma)