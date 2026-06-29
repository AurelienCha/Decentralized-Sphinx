import argparse, json
from random import randint,seed

from mclbn256 import G1, G2, GT, Fr

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path_length", type=int, required=True)
parser.add_argument("-m", "--mixnodes", type=int, required=True)
parser.add_argument("-s", "--sttps", type=int, required=True)
parser.add_argument("-t", "--threshold", type=int, required=True)
args = parser.parse_args()

data = {
    "path_length": args.path_length,
    "nbr_mixnodes": args.mixnodes,
    "nbr_sttps": args.sttps,
    "threshold": args.threshold,
    "generators": [str(G1().randomize()) for _ in range(2 * args.path_length + 1)],
}

with open(".config.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)