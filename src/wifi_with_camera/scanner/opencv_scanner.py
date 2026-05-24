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
