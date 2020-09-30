import asyncio
import os
import time
import json

from nats.aio.client import Client

from tools import get_logger, make_fake_tick
logger = get_logger(__name__)

NATS_HOSTNAME = os.environ.get('NATS_HOSTNAME', 'localhost')
NATS_SERVERS = [f'nats://{NATS_HOSTNAME}:4222']

TICKER_SUBJECT_NAME = 'ticker'

async def main(event_loop):
    nats_client = Client()
    await nats_client.connect(NATS_SERVERS, loop=event_loop)
    logger.info(f"Connected to NATS at {nats_client.connected_url.netloc}...")
    logger.info(f'Publishing ticks to [{TICKER_SUBJECT_NAME}]')

    while True:
        tick = make_fake_tick()
        await nats_client.publish(TICKER_SUBJECT_NAME, json.dumps(tick).encode())
        await nats_client.flush(timeout=1)
        logger.info(f'Published: {tick}')
        time.sleep(3)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()