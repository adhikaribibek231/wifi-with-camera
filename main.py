import cv2


def main() -> None:
    window_name = "WiFi QR Scanner"

    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    cv2.namedWindow(window_name)

    detected_data: str | None = None

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame from webcam.")
            break

        frame = cv2.flip(frame, 1)

        data, points, _ = detector.detectAndDecode(frame)

        if data:
            detected_data = data
            print(f"QR Code Detected: {detected_data}")

            if points is not None:
                points = points[0].astype(int)

                for i in range(len(points)):
                    pt1 = tuple(points[i])
                    pt2 = tuple(points[(i + 1) % len(points)])
                    cv2.line(frame, pt1, pt2, (0, 255, 0), 3)

            cv2.putText(
                frame,
                "QR detected. Closing...",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow(window_name, frame)
            cv2.waitKey(1200)
            break

        cv2.imshow(window_name, frame)

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

    cap.release()
    cv2.destroyAllWindows()

    if detected_data:
        print("\nFinal detected QR content:")
        print(detected_data)


if __name__ == "__main__":
    main()
