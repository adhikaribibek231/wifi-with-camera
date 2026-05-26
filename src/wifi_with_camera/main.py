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

    print("\nFinal detected QR content:")
    print(qr_text)

    try:
        credentials = parse(qr_text)
    except ValueError as error:
        print("\nInvalid WiFi QR code:")
        print(error)
        return

    print("\nParsed WiFi credentials:")
    print(f"SSID: {credentials.ssid}")
    print(f"Security: {credentials.security}")

    if credentials.password is None:
        print("Password: None")
    else:
        print(f"Password: {credentials.password}")


if __name__ == "__main__":
    main()
