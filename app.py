import struct

from flask import Flask, request, Response
import asyncio
import websockets
import threading
import json
import base64

app = Flask(__name__)

# In-memory set of connected Raspberry Pi clients
pi_clients = set()

@app.route("/twiml", methods=["POST"])
def twiml():
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Start>
        <Stream url="wss://carcall.canora.us/ws2" />
    </Start>
    <Say>Connecting you now.</Say>
    <Dial>
        <Conference>ForeverCall</Conference>
    </Dial>
</Response>"""
    return Response(twiml_response, mimetype="text/xml")

# -------- WebSocket Server Stuff -------- #

async def handle_pi(websocket, path=""):
    print("Pi connected")
    pi_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        print("Pi disconnected")
        pi_clients.remove(websocket)

async def handle_twilio(websocket, path=""):
    print("Twilio stream connected")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("event") == "media":
                    payload = data["media"]["payload"]
                    audio = base64.b64decode(payload)

                    # Ensure the audio data is in the correct format
                    # Twilio sends 16-bit PCM at 8kHz mono
                    # Convert bytes to 16-bit integers if needed
                    audio_samples = struct.unpack('<%dh' % (len(audio) // 2), audio)
                    audio_bytes = struct.pack('<%dh' % len(audio_samples), *audio_samples)

                for pi_ws in pi_clients:
                        await pi_ws.send(audio_bytes)
            except Exception as e:
                print(f"Decode error: {e}")
    except Exception as e:
        print(f"Twilio connection error: {e}")
    finally:
        print("Twilio stream disconnected")

# Start both WebSocket servers
async def start_websocket_servers():
    server = await websockets.serve(handle_twilio, "0.0.0.0", 9902)
    pi_server = await websockets.serve(handle_pi, "0.0.0.0", 9901)
    await asyncio.gather(server.wait_closed(), pi_server.wait_closed())

def run_websocket_servers():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_websocket_servers())
    loop.run_forever()

if __name__ == "__main__":
    threading.Thread(target=run_websocket_servers, daemon=True).start()
    app.run(host="0.0.0.0", port=80)