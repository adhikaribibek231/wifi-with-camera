"""
Linux NetworkManager CLI (nmcli) connector for Wi-Fi connections.

Responsibilities:
  - Implement Wi-Fi connection using the nmcli command-line tool
  - Handle Linux-specific connection logic
  - Execute shell commands to manage Wi-Fi networks

Functions:
  is_nmcli_available() -> bool
      Checks whether nmcli is available on the current system.

  build_nmcli_connect_command(credentials: WifiCredentials) -> list[str]
      Builds the nmcli command without executing it.

  connect_to_wifi(credentials: WifiCredentials) -> ConnectionResult
      Attempts to connect to the Wi-Fi network and returns a result.

Example:
    credentials = WifiCredentials(
        ssid="HomeWifi",
        password="secret123",
        security="WPA",
    )
    result = connect_to_wifi(credentials)
    print(result.message)

Note:
  Requires nmcli to be installed on the system.
"""

import shutil
import subprocess
from typing import List

from wifi_with_camera.network.base import ConnectionResult, NetworkConnectionError
from wifi_with_camera.parser.wifi_qr_parser import WifiCredentials


def is_nmcli_available() -> bool:
    return shutil.which("nmcli") is not None


def build_nmcli_connect_command(credentials: WifiCredentials) -> List[str]:
    command = [
        "nmcli",
        "device",
        "wifi",
        "connect",
        credentials.ssid,
    ]
    if credentials.password is not None:
        command.extend(["password", credentials.password])

    return command


def connect_to_wifi(credentials: WifiCredentials) -> ConnectionResult:
    if not is_nmcli_available():
        raise NetworkConnectionError("nmcli is not installed or not available")
    command = build_nmcli_connect_command(credentials)
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return ConnectionResult(
            success=True, message=f"Successfully connected to {credentials.ssid}"
        )

    error_output = result.stderr.strip() or result.stdout.strip()

    if "No network with SSID" in error_output:
        raise NetworkConnectionError(f"Wi-Fi network not found: {credentials.ssid}")

    if "Secrets were required" in error_output or "password" in error_output.lower():
        raise NetworkConnectionError(
            "Could not connect. The Wi-Fi password may be wrong."
        )

    raise NetworkConnectionError(f"Could not connect to Wi-Fi: {error_output}")
