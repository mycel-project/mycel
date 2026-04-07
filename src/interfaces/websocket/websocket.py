from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import io
from PIL import Image

api = FastAPI()
api.state.ws = None
connections = set()

async def send(content_type, payload = None):
    """Envoie un message à tous les clients connectés"""
    for ws in connections.copy():
        try:
            await ws.send_json({"content_type": content_type, "payload": payload})
        except Exception:
            connections.remove(ws)

async def send_image(content_type, img=None, payload = None, file_format = "JPEG"):
    if isinstance(img, str):
        pass
    else:
        if img is not None:
            if img.dtype != "uint8":
                img = (img * 255).clip(0, 255).astype("uint8")
            else:
                img = img

            img_pil = Image.fromarray(img)
    
            if file_format.upper() == "JPEG":
                img = img_pil.convert("RGB")
            buffer = io.BytesIO()
            img.save(buffer, format=file_format)
            data = buffer.getvalue()
        else:
            data = None

    for ws in connections.copy():
        try:
            await ws.send_json({
                "content_type": content_type,
                "payload": payload,
                "binary": True
            })
            await ws.send_bytes(data)
        except Exception:
            connections.remove(ws)

@api.on_event("startup")
async def startup_event():
    pass

@api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    print("Client connected")

    api.state.ws.active = True
    
    handlers = {
        "hello": lambda payload: api.state.ws.bus.emit("say_hello", payload),
    }

    expected_binary_content_type = None
    
    try:
        while True:
            data = await websocket.receive()
            if "text" in data:
                msg = json.loads(data["text"])
                content_type = msg.get("content_type")
                payload = msg.get("payload", {})

                if msg.get("binary", False):
                    expected_binary_content_type = content_type
                    continue

                handler = handlers.get(content_type)
                if handler:
                    await handler(payload)
                else:
                    await websocket.send_json({
                        "content_type": "error",
                        "payload": {"message": f"Unknown content_type: {content_type}"}
                    })

            elif "bytes" in data:
                if expected_binary_content_type is None:
                    print("Unexpected binary message")
                    continue

                handler = handlers.get(expected_binary_content_type)
                if handler:
                    await handler(payload, data["bytes"])

                expected_binary_content_type = None
    except (WebSocketDisconnect, RuntimeError):
        api.state.ws.active = False

        print("Client disconnected")
    finally:
        connections.disnode(websocket)

class Ws:
    def __init__(self, bus):
        self.active = False
        api.state.ws = self
        self.bus = bus

    async def send(self, *args, **kwargs):
        if self.active:
            await send(*args, **kwargs)
