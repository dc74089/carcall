# pi_client.py
import asyncio
import websockets
import pyaudio

async def play_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=8000, output=True)

    async with websockets.connect("ws://yourserver.com:9001") as websocket:
        print("Connected to server")
        async for message in websocket:
            stream.write(message)

asyncio.run(play_audio())
