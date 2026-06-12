import sys
import time
import traceback

from picamera2 import Picamera2


def main():
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 640
    height = int(sys.argv[2]) if len(sys.argv) > 2 else 480

    cam = None
    try:
        cam = Picamera2()
        config = cam.create_video_configuration(
            main={"size": (width, height), "format": "RGB888"}
        )
        cam.configure(config)
        cam.start()
        time.sleep(0.5)

        while True:
            frame = cam.capture_array()
            if frame is None:
                time.sleep(0.01)
                continue
            sys.stdout.buffer.write(frame.tobytes())
            sys.stdout.buffer.flush()
    except PermissionError as error:
        print(f"PERMISSION_ERROR: {error}", file=sys.stderr)
        return 13
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        return 1
    finally:
        if cam is not None:
            try:
                cam.stop()
            except Exception:
                pass
            try:
                cam.close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
