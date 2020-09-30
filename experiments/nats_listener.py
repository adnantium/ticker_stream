import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout

async def go(loop):
    nc = NATS()

    try:
        await nc.connect(servers=["nats://127.0.0.1:4222"], loop=loop)
    except:
        pass

    async def message_handler(msg):
        print(f"[Received on '{msg.subject}']: {msg.data.decode()}")



    async def request_handler(msg):
        print("[Request on '{} {}']: {}".format(msg.subject, msg.reply,
                                                msg.data.decode()))


        # await nc.publish(msg.reply, b'OK')

    if nc.is_connected:

        # Subscription using a 'workers' queue so that only a single subscriber
        # gets a request at a time.
        await nc.subscribe("foo", "workers", cb=request_handler)

        # try:
        #     # Make a request expecting a single response within 500 ms,
        #     # otherwise raising a timeout error.
        #     msg = await nc.timed_request("help", b'help please', 0.500)
        #     print(f"[Response]: {msg.data}")

        #     # Make a roundtrip to the server to ensure messages
        #     # that sent messages have been processed already.
        #     await nc.flush(0.500)
        # except ErrTimeout:
        #     print("[Error] Timeout!")

        # Wait a bit for message to be dispatched...
        await asyncio.sleep(1, loop=loop)

        # Detach from the server.
        await nc.close()

    if nc.last_error is not None:
        print(f"Last Error: {nc.last_error}")

    if nc.is_closed:
        print("Disconnected.")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(go(loop))
    loop.close()
