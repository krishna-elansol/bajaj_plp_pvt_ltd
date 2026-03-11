from pypylon import pylon
import cv2
import time

start_total = time.time()

# -------- Camera Creation --------
t0 = time.time()
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()
t1 = time.time()

print("Using device:", camera.GetDeviceInfo().GetModelName())
print("Camera open time:", round(t1 - t0, 4), "seconds")

# -------- Start Grabbing --------
t2 = time.time()
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
t3 = time.time()

print("Start grabbing time:", round(t3 - t2, 4), "seconds")

# -------- Converter --------
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

# -------- First Frame Time --------
t4 = time.time()
grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

if grabResult.GrabSucceeded():
    image = converter.Convert(grabResult)
    img = image.GetArray()
    t5 = time.time()

    print("First frame capture time:", round(t5 - t4, 4), "seconds")
    print("Total startup time:", round(t5 - start_total, 4), "seconds")

grabResult.Release()

camera.StopGrabbing()
camera.Close()