"""
Main entry point for the WiFi QR Scanner application.

This module orchestrates the workflow:
  1. Capture video frame from camera using OpenCVScanner
  2. Detect QR code in frame
  3. Parse QR text to extract WiFi credentials
  4. Connect to WiFi network using the connector

The flow should be: main() -> scanner.scan() -> parser.parse() -> network.connect()
At this stage, just print the parsed result. GUI comes later.
"""

from wifi_with_camera.parser.wifi_qr_parser import parse
from wifi_with_camera.scanner.opencv_scanner import scan


def main() -> None:
    qr_text = scan()
    if qr_text is None:
        print("No QR code detected.")
        return
    print("\nFinal detected QR content: ")
    print(qr_text)
    result = parse(qr_text)
    print("")
    print("")
    print(result)


if __name__ == "__main__":
    main()
