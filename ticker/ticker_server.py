

import os
import json
# import websockets
import signal
import asyncio
import asyncio_redis

from nats.aio.client import Client as NATS

from tools import get_logger
logger = get_logger(__name__)

"""Core component that brings together ticker stream and NATS integration

Environments variables expected:
* NATS_HOSTNAME (default: localhost)
* REDIS_HOSTNAME (default: localhost)
* SOCKET_SERVER_HOSTAME (default: localhost)
"""

SOCKET_SERVER_HOSTAME = os.environ.get('SOCKET_SERVER_HOSTAME', '0.0.0.0')
SOCKET_SERVER_PORT = 6789

NATS_HOSTNAME = os.environ.get('NATS_HOSTNAME', 'localhost')
NATS_SERVERS = [f'nats://{NATS_HOSTNAME}:4222']

TICKER_SUBJECT_NAME = 'ticker'

async def nats_listener(loop):
    """Core NATS integration component."""
    nats_client = NATS()

    async def closed_cb():
        logger.info("Connection to NATS is closed.")
        loop.create_task(nats_client.close())

    options = {
        "servers": NATS_SERVERS,
        "loop": loop,
        "closed_cb": closed_cb
    }

    await nats_client.connect(**options)
    logger.info(f"Connected to NATS at {nats_client.connected_url.netloc}...")

    async def ticker_handler(msg):
        subject, reply, data = msg.subject, msg.reply, msg.data
        # logger.debug(f"Got: [{subject}] [{reply if reply else '--' }]: [{data}]")
        logger.debug(f"Got NATS : [{subject}]: [{data.decode()}]")
        for client in websocket_clients:
            logger.debug(f'Sending {data} to {client}')
            await client.send(msg)

    await nats_client.subscribe(TICKER_SUBJECT_NAME, cb=ticker_handler)

    def signal_handler():
        if nats_client.is_closed:
            return
        logger.info("Disconnecting...")
        loop.create_task(nats_client.close())


async def redis_listener(loop):
    connection = await asyncio_redis.Connection.create("localhost", 6379)
    logger.info(f'Connected: [{connection}]')
    try:
        # Subscribe to a channel.
        subscriber = await connection.start_subscribe()
        logger.debug(f'Subscribing to [{TICKER_SUBJECT_NAME}]')
        await subscriber.subscribe([TICKER_SUBJECT_NAME])
        while True:
            reply = await subscriber.next_published()
            logger.debug(f'Got Redis: [{reply.channel}]: [{reply.value}]')
    except Exception as e:
        logger.error(e, stack_info=True)
    finally:
        logger.info(f'Disconnecting: [{connection}] ...')
        connection.close()


def handle_exception(loop, context):
    """logs any exception events and initaites the shutdown process"""
    msg = context.get("exception", context["message"])
    logger.error(f"Caught exception: {msg}")
    logger.info("Shutting down...")
    asyncio.create_task(shutdown(loop))

async def shutdown(loop, signal=None):
    """Wraps up, closes open connects and initates task cancels"""
    if signal:
        logger.info(f"Received exit signal {signal.name}...")
    logger.info("Closing database connections...")
    # TODO: close nats connections
    # TODO: close redis connections

    logger.info("Cancelling active tasks...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)

    loop.stop()

def main():
    loop = asyncio.get_event_loop()

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(loop, signal=s))
        )
    loop.set_exception_handler(handle_exception)

    try:
        loop.run_until_complete(nats_listener(loop))
        loop.run_until_complete(redis_listener(loop))

        loop.run_forever()
    finally:
        loop.close()
        logger.info(f"Successfully shutdown [{loop}].")

if __name__ == "__main__":
    main()

