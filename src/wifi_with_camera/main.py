"""
Main entry point for the Wi-Fi QR Scanner application.

This module orchestrates the workflow:
  1. Capture video frame from camera using OpenCVScanner
  2. Detect a QR code in the frame
  3. Parse QR text to extract Wi-Fi credentials
  4. Display the parsed result
  5. Optionally connect to the Wi-Fi network using the Linux nmcli backend
"""

from wifi_with_camera.display.result_display import display_credentials, display_error
from wifi_with_camera.network.base import NetworkConnectionError
from wifi_with_camera.network.linux_nmcli import connect_to_wifi
from wifi_with_camera.parser.wifi_qr_parser import parse
from wifi_with_camera.scanner.opencv_scanner import scan


def main() -> None:
    qr_text = scan()

    if qr_text is None:
        display_error("No QR code detected.")
        return

    try:
        credentials = parse(qr_text)
    except ValueError as error:
        display_error(str(error))
        return

    display_credentials(credentials)
    should_connect = input("\nConnect to this Wi-Fi network? [y/N]: ").strip().lower()

    if should_connect != "y":
        print("Connection cancelled.")
        return
    try:
        connection_result = connect_to_wifi(credentials)
    except NetworkConnectionError as error:
        print("\nCould not connect to Wi-Fi")
        print("-" * 30)
        print(error)
        return
    print(connection_result.message)


if __name__ == "__main__":
    main()
