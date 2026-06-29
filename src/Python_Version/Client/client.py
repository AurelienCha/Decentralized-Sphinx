from __future__ import annotations
from enum import StrEnum
from random import sample
from time import time
from math import prod
import asyncio

from log import timing
from network import Network
from crypto import Crypto
from header import Header
from ECC import *

from config import GENERATORS, PATH_LENGTH, NBR_MIXNODES, NBR_STTPS, THRESHOLD


class Stage(StrEnum):
    ROUTE = "ROUTE"
    RUN = "RUN"


class Client:

    def __init__(self, node_id: int):
        self.network = Network(f"127.0.100.{node_id}", self.handle_message)
        self.route_sampling_queue = asyncio.Queue()
    
    # ========================================================
    # NETWORK
    # ========================================================

    async def start(self) -> None:
        await self.network.start()

    async def send(self, ip: str, message_type: Stage, message) -> None:
        await self.network.send(ip, message_type, message)

    async def handle_message(self, ip: str, message_type: Stage, message) -> None:
        match message_type:
            case Stage.ROUTE:
                await self.route_sampling_queue.put(message)
            case Stage.RUN:
                pass 

    # ========================================================
    # QUERY ROUTE
    # ========================================================

    @timing
    async def query_route(self, nonce):
        """Query shares to a THRESHOLD number of STTP"""

        timestamp = int(time())

        for sttp in sample(range(NBR_STTPS), k=THRESHOLD): 
            await self.send(f"127.0.1.{sttp}", Stage.ROUTE, [nonce, timestamp])
    
        # Getting shares
        all_shares = [await self.route_sampling_queue.get() for _ in range(THRESHOLD)]
        all_shares = [[(t, share) for share in shares] for t, *shares in all_shares]
        
        # Lagrange interpolation (reconstitution)
        all_shares = [Crypto.lagrange_interpolation(points) for points in zip(*all_shares)]
        route, shared_secret_points = all_shares[::2], all_shares[1::2]
        return route, shared_secret_points
    
    @timing
    def shared_secret_rerandomization(self, nonce, shared_secret_points):
        # Rerandomization
        r = Fr().randomize()
        Alpha = G1().hash(nonce) * r # Alpha * r
        shared_secret_points = [S * r for S in shared_secret_points]

        # Cascade
        shared_secrets = []
        for S in shared_secret_points:
            shared_secrets.append((S * prod(shared_secrets, start=Fr(1))) >> Fr())

        return (Alpha, shared_secrets)


    # ========================================================
    # SEND PACKET
    # ========================================================

    async def send_packet(self, destination_ip: str) -> None:
        first_hop, header = await self.build_packet(destination_ip)
        await self.send(decode_ip(first_hop), Stage.RUN, header)


    @timing
    async def build_packet(self, destination_ip: str) -> None:

        delta = encode_ip(destination_ip) 

        # Decentralized Route Sampling (STTPs)
        nonce = Fr().randomize()  
        route, shared_secret_points = await self.query_route(nonce)
        alpha, shared_secrets = self.shared_secret_rerandomization(nonce, shared_secret_points)

        header = Header.build(
            destination= delta,
            route=route,
            shared_secrets=shared_secrets,
            alpha=alpha,
        )

        return (route[0], header)