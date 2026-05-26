from wifi_with_camera.parser.wifi_qr_parser import WifiCredentials


def display_credentials(credentials: WifiCredentials) -> None:
    print("\nWiFi QR Result")
    print("-" * 30)
    print(f"SSID:     {credentials.ssid}")
    print(f"Security: {credentials.security}")

    if credentials.password is None:
        print("Password: <none>")
    else:
        print(f"Password: {credentials.password}")

    print("-" * 30)
    print("\nCopy-friendly output:")
    print(f"SSID={credentials.ssid}")
    print(f"SECURITY={credentials.security}")
    print(f"PASSWORD={credentials.password or ''}")


def display_error(message: str) -> None:
    print("\nCould not parse WiFi QR code")
    print("-" * 30)
    print(message)
