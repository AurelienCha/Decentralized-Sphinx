import asyncio, argparse, json
from hashlib import sha256
from enum import StrEnum
from pathlib import Path

from config import PATH_LENGTH, NBR_MIXNODES
from log import create_logger, timing
from network import Network

from ECC import *

class Stage(StrEnum):
    SETUP = "SETUP"
    ROUTE = "ROUTE"

class STTP:
    def __init__(self, ip):
        # Other
        self.shares = []
        
        # Network
        self.ip = ip
        self.id = hash_to_Fr(ip.encode())
        self.network = Network(ip, self.handle_message)

    async def send(self, ip, msg_type, message):
        await self.network.send(ip, msg_type, message)

    async def handle_message(self, ip, msg_type, message):
        match msg_type:
            case Stage.SETUP: 
                await self.store_share(message)
            case Stage.ROUTE:
                await self.send_share(message, ip)
    
    @timing
    async def store_share(self, message):
        self.shares.append(message)
        if len(self.shares) >= NBR_MIXNODES:
            self.shares.sort()
    
    @timing
    async def send_share(self, message, ip):
        nonce, timestamp = message
        Alpha = G1().hash(nonce)

        path_materials = [self.id]
        for i in range(PATH_LENGTH):
            idx = int(sha256(f"{Alpha}{timestamp}{i}".encode()).hexdigest(), 16) % NBR_MIXNODES
            _, k_i, N_i = self.shares[idx]
            path_materials.append(N_i)
            path_materials.append(Alpha * k_i)

        await self.send(ip, Stage.ROUTE, path_materials) # (t, [N_i, S_i]_{for i in range(PATH_LENGTH)})
  
    async def start(self):
        await self.network.start()

# ===================== MAIN =====================
async def main(ID):
    with open(".config.json") as f:
        config = json.load(f)


    create_logger("STTP", ID)
    node = STTP(ip = f"127.0.1.{ID}")

    # == START ==
    await node.start()
    
    # flag file to signal ready
    Path(".tmp").mkdir(exist_ok=True)
    Path(f".tmp/sttp_{ID}.flag").touch()

    await asyncio.Event().wait()  # <- keeps program alive

# ===================== CLI =====================
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", type=int, required=True)
    args = parser.parse_args()

    asyncio.run(main(args.id))
