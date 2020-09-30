#!/usr/bin/env python

import asyncio
import websockets
import json
import uuid

async def handle_message():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:

        some_data = { 'action': 'enter', 'name': str(uuid.uuid4())[:8]}
        await websocket.send(json.dumps(some_data))
        print(f"Sent: {some_data}")

        while True:
            got_back = await websocket.recv()
            print(f"Got: {got_back}")

asyncio.get_event_loop().run_until_complete(handle_message())
