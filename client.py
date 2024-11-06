# websocket_client.py

import asyncio
import websockets
import aioconsole

async def main():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        async def receive_message():
            async for message in websocket:
                print(f"Server: {message}")

        async def send_message():
            while True:
                message = await aioconsole.ainput("You (Client): ")
                await websocket.send(message)

        await asyncio.gather(receive_message(), send_message())

asyncio.run(main())
