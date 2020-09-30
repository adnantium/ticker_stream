#!/usr/bin/env python

import asyncio
import json
import logging
import websockets

logging.basicConfig()


clients = {}

async def notify_clients(message, connections=None):
    connections = connections or clients.keys()
    # message = json.dumps({"type": "users", "count": len(connections)})
    for c in connections:
        await c.send(message)
    # await asyncio.wait([c.send(message) for c in connections])


async def register_client(websocket):
    print(f'Enter [{websocket}] ({len(clients)} existing clients)')
    # await notify_users()


async def unregister_client(websocket):
    print(f'Exit: {websocket}')
    del clients[websocket]




async def handle_message(websocket, path):

    print('New client', websocket)
    print('New client [{}] ({} existing clients)'.format(websocket, len(clients)))

    await websocket.send('hi')

    try:
        async for raw_message in websocket:
            print(f'Got: [{raw_message}]')
    finally:
        await unregister_client(websocket)


start_server = websockets.serve(handle_message, "localhost", 6789)
print(f'Starting: {start_server}')


loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
try:
    loop.run_forever()
except KeyboardInterrupt as ki:
    print(ki)
    # raise ki
loop.close()
print(f'Shutting down: {start_server}')
