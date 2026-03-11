from pypylon import pylon
import cv2
import threading
import time
import logging
from logging.handlers import RotatingFileHandler
import os

class BaslerFrameReceiver:
    def __init__(self):
        # Log directory
        log_dir = r"D:\Bajaj_Plp\Basler_Camera\Logs"
        os.makedirs(log_dir, exist_ok=True)
        self.logger = logging.getLogger("basler_camera")
        self.logger.setLevel(logging.ERROR)
        handler = RotatingFileHandler(os.path.join(log_dir, "basler_camera.log"),maxBytes=5*1024*1024,backupCount=5)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        # Camera setup
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.Open()
        print("Using device:", self.camera.GetDeviceInfo().GetModelName())
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        # Converter
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        self.frame = None
        self.running = True
        # Start capture thread
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
    
    

    def _capture_loop(self):
        while self.running: #and self.camera.IsGrabbing():
            try:
                grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_Return)
                if grabResult is None:
                    continue
                if grabResult.GrabSucceeded():
                    image = self.converter.Convert(grabResult)
                    self.frame = image.GetArray()
                grabResult.Release()
            except Exception as e:
                if isinstance(e, RuntimeError) or "RuntimeException" in str(e):
                    self.logger.error("Basler Runtime Error: %s", e)
                print("Camera disconnected:", e)
                try:
                    if self.camera.IsGrabbing():
                        self.camera.StopGrabbing()
                    if self.camera.IsOpen():
                        self.camera.Close()
                except:
                    pass
                print("Waiting for camera reconnect...")
                # try reconnecting
                while self.running:
                    try:
                        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
                        self.camera.Open()
                        print("Reconnected:", self.camera.GetDeviceInfo().GetModelName())
                        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
                        break
                    except Exception as e:
                        self.logger.error("Camera reconnected")
                        time.sleep(2)

    def get_frame(self):
        """
        Returns latest frame
        """
        return self.frame

    def stop(self):
        print("Stopping camera...")
        self.running = False
        # wait for capture thread to finish
        if self.thread.is_alive():
            self.thread.join()
        if self.camera.IsGrabbing():
            self.camera.StopGrabbing()
        if self.camera.IsOpen():
            self.camera.Close()
        print("Camera stopped")