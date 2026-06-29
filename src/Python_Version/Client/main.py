import argparse, asyncio

from client import Client
from log import create_logger
from ECC import *

# ============================================================
# MAIN
# ============================================================

async def main(node_id: int) -> None:

    create_logger("CLIENT", node_id)
    client = Client(node_id=node_id)

    # == START Network ==
    await client.start()
    await asyncio.sleep(1)

    # == SEND packet == 
    # while True:
    #     await client.send_packet(client.network.ip) # TODO: send to self just for testing, change to real destination later
    for _ in range(1):
        await client.send_packet(client.network.ip)

    # print(OP_COUNT) 

    await asyncio.Event().wait()  # <- keeps program alive


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", type=int, required=True, help="Client identifier")
    arguments = parser.parse_args()

    asyncio.run(main(arguments.id))
