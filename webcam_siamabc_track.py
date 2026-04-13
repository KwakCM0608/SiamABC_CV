import time
import cv2
import numpy as np

from realtime_test import get_tracker
from core.utils.hydra import load_hydra_config_from_path


REPO_ROOT = "/workspace/SiamABC"
CONFIG_PATH = "./core/config"
CONFIG_NAME = "SiamABC_tracker"
MODEL_SIZE = "S_Tiny"
WEIGHTS_PATH = f"{REPO_ROOT}/assets/S_Tiny/model_S_Tiny_v1.pt"
DEVICE_PATH = "/dev/video0"


def build_tracker(
    config_path=CONFIG_PATH,
    config_name=CONFIG_NAME,
    model_size=MODEL_SIZE,
    weights_path=WEIGHTS_PATH,
):
    config = load_hydra_config_from_path(
        config_path=config_path,
        config_name=config_name,
    )
    config["model"]["model_size"] = "S" if model_size == "S_Tiny" else "M"
    tracker = get_tracker(config=config, weights_path=weights_path)
    return tracker


def select_roi(frame_bgr):
    print("[INFO] Drag your face ROI, then press ENTER or SPACE.")
    print("[INFO] Press C to cancel.")
    bbox = cv2.selectROI(
        "Select Face ROI",
        frame_bgr,
        fromCenter=False,
        showCrosshair=True,
    )
    cv2.destroyWindow("Select Face ROI")

    x, y, w, h = map(int, bbox)
    if w <= 0 or h <= 0:
        return None
    return np.array([x, y, w, h], dtype=np.int32)


def draw_tracking_box(frame_bgr, bbox, score=None, fps=None):
    vis = frame_bgr.copy()
    x, y, w, h = map(int, bbox)

    cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)

    info1 = f"bbox: x={x}, y={y}, w={w}, h={h}"
    cv2.putText(
        vis, info1, (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
    )

    if score is not None:
        info2 = f"score: {float(score):.4f}"
        cv2.putText(
            vis, info2, (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )

    if fps is not None:
        info3 = f"fps: {fps:.1f}"
        cv2.putText(
            vis, info3, (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )

    cv2.putText(
        vis,
        "q: quit | r: reselect ROI",
        (10, vis.shape[0] - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
    )
    return vis


def main():
    cap = cv2.VideoCapture(DEVICE_PATH)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open webcam: {DEVICE_PATH}")

    tracker = build_tracker()

    ret, first_frame_bgr = cap.read()
    if not ret or first_frame_bgr is None:
        cap.release()
        raise RuntimeError("Failed to read first webcam frame.")

    init_bbox = select_roi(first_frame_bgr)
    if init_bbox is None:
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] ROI selection cancelled.")
        return

    first_frame_rgb = cv2.cvtColor(first_frame_bgr, cv2.COLOR_BGR2RGB)
    tracker.initialize(first_frame_rgb, init_bbox)

    prev_time = time.time()
    fps = 0.0

    while True:
        ret, frame_bgr = cap.read()
        if not ret or frame_bgr is None:
            print("[WARN] Failed to read webcam frame. Exiting.")
            break

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        pred_bbox, pred_score = tracker.update(frame_rgb)
        pred_bbox = np.array(pred_bbox).astype(np.int32)

        now = time.time()
        dt = now - prev_time
        if dt > 0:
            fps = 1.0 / dt
        prev_time = now

        vis = draw_tracking_box(frame_bgr, pred_bbox, score=pred_score, fps=fps)
        cv2.imshow("SiamABC Webcam Face Tracking", vis)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("r"):
            ret, reinit_frame_bgr = cap.read()
            if not ret or reinit_frame_bgr is None:
                print("[WARN] Failed to read frame for reinitialization.")
                continue

            new_bbox = select_roi(reinit_frame_bgr)
            if new_bbox is None:
                print("[INFO] Re-selection cancelled. Continue tracking.")
                continue

            reinit_frame_rgb = cv2.cvtColor(reinit_frame_bgr, cv2.COLOR_BGR2RGB)
            tracker.initialize(reinit_frame_rgb, new_bbox)
            print(f"[INFO] Reinitialized with bbox={new_bbox.tolist()}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
