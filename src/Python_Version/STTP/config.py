# ============================================================
# CONFIG LOADER
# ============================================================

from dataclasses import dataclass
import json

from ECC import *


@dataclass(slots=True)
class PublicConfig:
    path_length: int
    generators: list[G1]
    nbr_mixnodes: int
    nbr_sttps: int
    threshold: int

def load_public_config() -> PublicConfig:
    with open(".config.json", encoding="utf-8") as file:
        raw = json.load(file)

        return PublicConfig(
            path_length=raw["path_length"],
            generators=[G1().fromstr(value.encode()) for value in raw["generators"]],
            nbr_mixnodes=raw["nbr_mixnodes"],
            nbr_sttps=raw["nbr_sttps"],
            threshold=raw["threshold"],
        )


config = load_public_config()

PATH_LENGTH = config.path_length
BETA_SIZE = 2 * PATH_LENGTH - 1

GENERATORS = config.generators
NBR_MIXNODES = config.nbr_mixnodes
NBR_STTPS = config.nbr_sttps
THRESHOLD = config.threshold
