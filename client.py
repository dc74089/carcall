import asyncio
import websockets
import pyaudio

async def play_audio():
    p = pyaudio.PyAudio()
    # Explicitly set format to match Twilio's stream:
    # - 16-bit PCM (paInt16)
    # - 8kHz sample rate
    # - 1 channel (mono)
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
                stream.write(message)
        except Exception as e:
            print(f"Error playing audio: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

asyncio.run(play_audio())