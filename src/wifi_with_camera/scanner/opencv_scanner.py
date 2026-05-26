"""
Camera and QR code detection module.

Responsibilities:
  - Open webcam using OpenCV
  - Read video frames
  - Detect QR codes in frames using cv2.QRCodeDetector
  - Return raw QR text when detected

Functions:
  scan() -> str | None
      Opens camera, captures frames, detects QR codes.
      Returns the QR text when a code is found, None if cancelled.

Example:
    qr_text = scan()
    if qr_text:
        print(f"QR detected: {qr_text}")
"""

import cv2


def scan() -> str | None:
    window_name = "Wi-Fi QR Scanner"

    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None

    detected_data: str | None = None

    try:
        cv2.namedWindow(window_name)

        while True:
            ret, frame = cap.read()
            # ret = whether camera reading succeeded or not True or False
            if not ret:
                print("Error: Could not read frame from webcam.")
                break

            data, points, _ = detector.detectAndDecode(frame)  # most important line
            # points contains the QR code boundary coordinates.
            display_frame = cv2.flip(frame, 1)

            if data:
                detected_data = data
                print(f"QR Code Detected: {detected_data}")

                if points is not None:
                    frame_width = frame.shape[1]

                    mirrored_points = points[0].astype(int)
                    mirrored_points[:, 0] = frame_width - 1 - mirrored_points[:, 0]
                    # Mirror the x-coordinates because the displayed frame was flipped horizontally (valid x range: 0 to frame_width-1)

                    for i in range(len(mirrored_points)):
                        pt1 = tuple(mirrored_points[i])
                        pt2 = tuple(mirrored_points[(i + 1) % len(mirrored_points)])
                        cv2.line(display_frame, pt1, pt2, (0, 255, 0), 3)

                cv2.putText(
                    display_frame,
                    "QR detected. Closing...",
                    (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
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
        cap.release()
        cv2.destroyAllWindows()

    return detected_data
