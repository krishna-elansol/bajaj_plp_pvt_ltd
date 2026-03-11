import socketio
import eventlet

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)


@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.on("work-order-updated")
def vision_event(sid, data):
    print("\n===== EVENT RECEIVED =====")
    print("Event      :", data.get("Event"))
    print("Message    :", data.get("Message"))
    # print("Image Path :", data.get("Image_Path"))
    # print("==========================\n")


@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 3001)), app)