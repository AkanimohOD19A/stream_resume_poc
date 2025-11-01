# signaling_server.py
from fastapi import FastAPI, WebSocket
import json

app = FastAPI()
rooms = {}  # room_id: [websocket1, websocket2]

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    room = None
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg["type"] == "join":
                room = msg["room"]
                rooms.setdefault(room, []).append(ws)
                print(f"{ws.client} joined room {room}")
                # Confirm join
                await ws.send_text(json.dumps({"type": "joined", "room": room}))
            else:
                # Relay to all other peers in same room
                peers = rooms.get(room, [])
                for peer in peers:
                    if peer != ws:
                        await peer.send_text(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if room and ws in rooms.get(room, []):
            rooms[room].remove(ws)