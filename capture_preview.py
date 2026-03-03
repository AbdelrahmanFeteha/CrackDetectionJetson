
import argparse
import os
import time
import cv2

def gstreamer_pipeline(sensor_id=0, width=1280, height=720, framerate=30, flip=0):
    return (
        f"nvarguscamerasrc sensor_id={sensor_id} ! "
        f"video/x-raw(memory:NVMM), width=(int){width}, height=(int){height}, "
        f"format=(string)NV12, framerate=(fraction){framerate}/1 ! "
        f"nvvidconv flip-method={flip} ! "
        f"video/x-raw, format=(string)BGRx ! "
        f"videoconvert ! "
        f"video/x-raw, format=(string)BGR ! "
        f"appsink max-buffers=1 drop=true sync=false"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sensor-id", type=int, default=0)
    ap.add_argument("--out", default="captures/cam.jpg")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--fr", type=int, default=30)
    ap.add_argument("--warmup", type=float, default=2.0, help="seconds")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    cap = cv2.VideoCapture(gstreamer_pipeline(args.sensor_id, args.width, args.height, args.fr), cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        raise SystemExit("Could not open camera. Check sensor_id and GStreamer.")

    t0 = time.time()
    print(f"Warming up for {args.warmup}s... then press SPACE to capture, q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # overlay instructions
        msg = "SPACE=capture   q=quit"
        cv2.putText(frame, msg, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        cv2.imshow("CrackWatch Preview", frame)

        k = cv2.waitKey(1) & 0xFF

        # ignore capture during warmup
        if time.time() - t0 < args.warmup:
            continue

        if k == ord('q'):
            break
        if k == 32:  # SPACE
            cv2.imwrite(args.out, frame)
            print(f"Saved {args.out}")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
