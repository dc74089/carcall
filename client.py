import asyncio
import websockets
import pyaudio
import audioop

async def play_audio():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=8000,
        output=True,
        frames_per_buffer=1024
    )

    async with websockets.connect("wss://carcall.canora.us/ws1") as websocket:
        print("Connected to server")
        try:
            async for message in websocket:
                # Convert mu-law to linear PCM
                pcm_data = audioop.ulaw2lin(message, 2)  # 2 for 16-bit output
                stream.write(pcm_data)
        except Exception as e:
            print(f"Error playing audio: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

asyncio.run(play_audio())