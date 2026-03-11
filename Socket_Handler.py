import socketio
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────

SERVER_URL = "http://192.168.0.14:3001"

EVENT_FOLDER = r"D:\Bajaj_Plp\events"
IMAGE_PATH = r"D:\Codes\Inspecting_Image\Inspection_Image.jpg"

# ─────────────────────────────────────────
# SOCKET CLIENT
# ─────────────────────────────────────────

sio = socketio.Client(
    logger=True,
    engineio_logger=True,
    reconnection=True
)

@sio.event
def connect():
    print("\n[CONNECTED]")
    print("Server :", SERVER_URL)
    print("Socket :", sio.sid)

@sio.event
def disconnect():
    print("\n[DISCONNECTED]")

@sio.event
def connect_error(data):
    print("\n[CONNECTION FAILED]", data)


# ─────────────────────────────────────────
# EVENT MAP
# ─────────────────────────────────────────

EVENT_MAP = {
    "Bin_Present.txt": "BIN_PRESENT",
    "Image_Capture.txt": "IMAGE_CAPTURE",
    "Bin_Pocket.txt": "BIN_VERIFICATION",
    "Part_Verification.txt": "PART_VERIFICATION",
    "Variant_Verification.txt": "VARIANT_VERIFICATION",
    "Result.txt": "RESULT"
}


# ─────────────────────────────────────────
# PAYLOAD BUILDER
# ─────────────────────────────────────────

def build_payload(event_name):

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if event_name == "IMAGE_CAPTURE":

        return {
            "step": event_name,
            "status": "OK",
            "timestamp": timestamp,
            "imageUrl": IMAGE_PATH
        }

    elif event_name == "RESULT":

        return {
            "step": event_name,
            "status": "OK",
            "timestamp": timestamp,
            "inspectionStatus": "OK",
            "totalParts": 10,
            "okParts": 10,
            "nokParts": 0,
            "emptyPockets": 0
        }

    else:

        return {
            "step": event_name,
            "status": "OK",
            "timestamp": timestamp,
            "imageUrl": IMAGE_PATH
        }


# ─────────────────────────────────────────
# SEND EVENT
# ─────────────────────────────────────────

def send_event(file_name):

    if file_name not in EVENT_MAP:
        return

    event_name = EVENT_MAP[file_name]

    payload = build_payload(event_name)

    try:
        sio.emit(event_name, payload)
        print(f"[SENT] {event_name}")

    except Exception as e:
        print("Send failed:", e)


# ─────────────────────────────────────────
# FILE WATCHER
# ─────────────────────────────────────────

class EventHandler(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        file_name = os.path.basename(event.src_path)

        if file_name in EVENT_MAP:

            print("\n[EVENT FILE DETECTED]", file_name)

            time.sleep(0.2)

            send_event(file_name)

            try:
                os.remove(event.src_path)
            except:
                pass


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

if __name__ == "__main__":

    print("\n[VISION SOCKET SENDER STARTING]")
    print("Connecting to:", SERVER_URL)

    sio.connect(
        SERVER_URL,
        transports=["websocket"]
    )

    event_handler = EventHandler()
    observer = Observer()

    observer.schedule(
        event_handler,
        EVENT_FOLDER,
        recursive=False
    )

    observer.start()

    print("\nWatching folder:", EVENT_FOLDER)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()