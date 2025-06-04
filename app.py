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
    # You can customize the TwiML here dynamically if needed
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Start>
        <Stream url="wss://yourdomain.com:8765/twilio" />
    </Start>
    <Say>Connecting you now.</Say>
    <Dial>
        <Conference>ForeverCall</Conference>
    </Dial>
</Response>"""
    return Response(twiml_response, mimetype="text/xml")

# -------- WebSocket Server Stuff -------- #

# Handle connections from Raspberry Pi clients
async def handle_pi(websocket, path):
    print("Pi connected")
    pi_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        print("Pi disconnected")
        pi_clients.remove(websocket)

# Handle incoming Twilio media stream
async def handle_twilio(websocket, path):
    print("Twilio stream connected")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("event") == "media":
                    payload = data["media"]["payload"]
                    audio = base64.b64decode(payload)
                    for pi_ws in pi_clients:
                        await pi_ws.send(audio)
            except Exception as e:
                print(f"Decode error: {e}")
    except Exception as e:
        print(f"Twilio connection error: {e}")
    finally:
        print("Twilio stream disconnected")

# Start both WebSocket servers
def start_websocket_servers():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server = websockets.serve(handle_twilio, "0.0.0.0", 9002, ssl=None, create_protocol=None, ping_interval=None, subprotocols=None)
    pi_server = websockets.serve(handle_pi, "0.0.0.0", 9001, ssl=None, create_protocol=None, ping_interval=None)
    loop.run_until_complete(asyncio.gather(server, pi_server))
    loop.run_forever()

# Start Flask and WebSocket server in parallel
if __name__ == "__main__":
    threading.Thread(target=start_websocket_servers, daemon=True).start()
    app.run(host="0.0.0.0", port=80)
