"""Camera frame capture and QR code detection helpers."""

import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from wifi_with_camera.scanner.decoder import ZXingQRDecoder

os.environ.setdefault("OPENCV_LOG_LEVEL", "SILENT")

import cv2
import numpy as np
from numpy.typing import NDArray

Frame = NDArray[np.uint8]
QRPoints = NDArray[np.float32]
OPENCV_LOG_LEVEL_SILENT = 0


def silence_opencv_logs() -> None:
    set_log_level = getattr(cv2, "setLogLevel", None)
    if set_log_level is None:
        return

    cast(Callable[[int], None], set_log_level)(OPENCV_LOG_LEVEL_SILENT)


@dataclass(frozen=True)
class QRDetection:
    text: str
    points: QRPoints | None


class OpenCVScanner:
    """Small reusable wrapper around OpenCV webcam capture and QR detection."""

    def __init__(self, camera_index: int = 0) -> None:
        silence_opencv_logs()
        self.capture = cv2.VideoCapture(camera_index)
        self.detector = ZXingQRDecoder()

    def is_opened(self) -> bool:
        return self.capture.isOpened()

    def read_frame(self) -> Frame | None:
        success, frame = self.capture.read()
        if not success:
            return None

        return cast(Frame, frame)

    def detect_qr_code(self, frame: Frame) -> QRDetection | None:
        result = self.detector.decode(frame)

        if result is None:
            return None

        return QRDetection(
            text=result.text,
            points=None,
        )

    def detect_qr(self, frame: Frame) -> str | None:
        detection = self.detect_qr_code(frame)
        if detection is None:
            return None

        return detection.text

    def release(self) -> None:
        self.capture.release()


def draw_qr_overlay(
    frame: Frame,
    points: QRPoints | None,
    message: str = "QR detected",
) -> None:
    if points is not None:
        outline = points[0].astype(int)

        for index in range(len(outline)):
            start = tuple(int(value) for value in outline[index])
            end = tuple(int(value) for value in outline[(index + 1) % len(outline)])
            cv2.line(frame, start, end, (0, 255, 0), 3)

    cv2.putText(
        frame,
        message,
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )


def mirror_qr_points(points: QRPoints | None, frame_width: int) -> QRPoints | None:
    if points is None:
        return None

    mirrored_points = points.copy()
    mirrored_points[:, :, 0] = frame_width - 1 - mirrored_points[:, :, 0]
    return mirrored_points


def scan() -> str | None:
    window_name = "Wi-Fi QR Scanner"

    scanner = OpenCVScanner()

    if not scanner.is_opened():
        print("Error: Could not open webcam.")
        return None

    detected_data: str | None = None

    try:
        cv2.namedWindow(window_name)

        while True:
            frame = scanner.read_frame()
            if frame is None:
                print("Error: Could not read frame from webcam.")
                break

            display_frame = cast(Frame, cv2.flip(frame, 1))
            detection = scanner.detect_qr_code(frame)

            if detection is not None:
                detected_data = detection.text
                print(f"QR Code Detected: {detected_data}")

                mirrored_points = mirror_qr_points(
                    detection.points,
                    frame_width=frame.shape[1],
                )
                draw_qr_overlay(
                    display_frame, mirrored_points, "QR detected. Closing..."
                )

                cv2.imshow(window_name, display_frame)
                cv2.waitKey(2000)
                break

            cv2.imshow(window_name, display_frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                print("Scanner closed by user.")
                break

            try:
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    print("Scanner window closed.")
                    break
            except cv2.error:
                print("Scanner window closed.")
                break

    finally:
        scanner.release()
        cv2.destroyAllWindows()

    return detected_data
