import cv2
from Basler import BaslerFrameReceiver

camera = BaslerFrameReceiver()


def main():

    while True:
        frame = camera.get_frame()
        if frame is not None:
            frame = cv2.resize(frame, (1920, 1080))
            cv2.imshow("Basler Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Exiting...")
            break
    camera.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()