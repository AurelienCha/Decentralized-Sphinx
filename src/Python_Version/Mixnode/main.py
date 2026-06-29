import asyncio, argparse

from config import NBR_MIXNODES
from mixnode import Mixnode
from log import create_logger
from ECC import *


# ============================================================
# MAIN
# ============================================================ 

async def main(node_id: int) -> None:

    create_logger("MIX", node_id)
    node = Mixnode(node_id=node_id)

    # == START ==
    await node.start()

    # == SETUP: Send shares to STTPs ==
    await node.setup() 

    # == WAIT TO PROCESS PACKET ==
    await asyncio.Event().wait()  # <- keeps alive

# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", type=int, required=True, help="Mixnode identifier")
    arguments = parser.parse_args()

    asyncio.run(main(arguments.id))