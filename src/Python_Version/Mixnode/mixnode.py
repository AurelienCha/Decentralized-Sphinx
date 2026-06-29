from __future__ import annotations
from typing import Any
from enum import StrEnum
from random import randint, sample
import asyncio

from log import timing
from network import Network
from crypto import Crypto, Polynomial
from header import Header
from ECC import *

from config import GENERATORS, NBR_STTPS, THRESHOLD

class Stage(StrEnum):
    SETUP = "SETUP"
    RUN = "RUN"


class Mixnode:
    def __init__(self, node_id: int):
        # Network
        self.ip = f"127.0.10.{node_id}"
        self.network = Network(self.ip, self.handle_message)

        # Keys (private and public)
        self.secret_key = Fr().randomize()
        self.public_key = G1().base_point() * self.secret_key

        # Polynomial (secret sharing)
        self.r = randint(1, pow(2,32))     # Tmp Pseudonyme
        self.f = Polynomial([self.secret_key] + [Fr().randomize() for _ in range(THRESHOLD - 1)])    # polynome Fr() of degree d-1 : f(0)=k
        self.g = Polynomial([encode_ip(self.ip)] + [G1().randomize() for _ in range(THRESHOLD - 1)]) # polynome G1() of degree d-1 : g(0)=N

    async def start(self) -> None:
        await self.network.start()

    async def send(self, ip: str, message_type: str, message: Any) -> None:
        await self.network.send(ip, message_type, message)

    async def handle_message(self, ip: str, message_type: str, message: Any) -> None:
        match message_type:
            case Stage.SETUP:
                pass
            case Stage.RUN:
                header: Header = message
                next_ip, processed_header = header.process_header(self.secret_key)

                await self.send(next_ip, Stage.RUN, processed_header) 

    @timing
    async def setup(self) -> G1:
        # Send share to all STTPs
        for sttp in range(1, NBR_STTPS+1): 
            sttp_ip = f"127.0.1.{sttp}"
            t = hash_to_Fr(sttp_ip.encode())

            # Shares (i.e. evaluate polynomials at t)
            k_t = self.f(t)
            N_t = self.g(t)
            
            await self.send(sttp_ip, Stage.SETUP, [self.r, k_t, N_t])
