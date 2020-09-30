#!/usr/bin/env python
import asyncio
import json
import time

from tools import get_logger, make_fake_tick
logger = get_logger(__name__)

import asyncio_redis

TICKER_SUBJECT_NAME = 'ticker'

async def main():
    connection = await asyncio_redis.Connection.create('localhost', 6379)

    loop = asyncio.get_event_loop()
    try:
        while True:
            # Get input (always use executor for blocking calls)
            # text = await loop.run_in_executor(None, input, 'Enter message: ')
            data = json.dumps(make_fake_tick())
            try:
                await connection.publish(TICKER_SUBJECT_NAME, data)
                logger.info(f'Publishing [{data}]')
            except asyncio_redis.Error as e:
                logger.info(f'Published failed: {e}')
            time.sleep(2)
    except Exception as e:
        logger.error(e, stack_info=True)
    finally:
        connection.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
