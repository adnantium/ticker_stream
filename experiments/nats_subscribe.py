import asyncio
import os
import signal
import sys

from nats.aio.client import Client as NATS

from tools import get_logger
logger = get_logger(__name__)

TICKER_SUBJECT_NAME = 'ticker'
WORKERS_NAME = 'works'

async def run(loop):
    nc = NATS()

    async def closed_cb():
        print("Connection to NATS is closed.")
        await asyncio.sleep(0.1, loop=loop)
        loop.stop()

    options = {
        "servers": ["nats://127.0.0.1:4222"],
        "loop": loop,
        "closed_cb": closed_cb
    }

    await nc.connect(**options)
    print(f"Connected to NATS at {nc.connected_url.netloc}...")

    async def ticker_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data
        print(f"Received: [{subject}]: [{data}]\n")

    await nc.subscribe(TICKER_SUBJECT_NAME, WORKERS_NAME, ticker_handler)

    # when it ends
    def signal_handler():
        if nc.is_closed:
            return
        print("Disconnecting...")
        loop.create_task(nc.close())

    for sig in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, sig), signal_handler)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    try:
        loop.run_forever()
    finally:
        loop.close()
