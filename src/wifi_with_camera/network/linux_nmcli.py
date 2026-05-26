"""
Linux NetworkManager CLI (nmcli) connector for WiFi connections.

Responsibilities:
  - Implement WiFi connection using nmcli command-line tool
  - Handle Linux-specific connection logic
  - Execute shell commands to manage WiFi networks

Class:
  LinuxNMCliConnector(Connector)
      Implements connect() using subprocess to call nmcli commands.
      Typical flow:
        1. nmcli dev wifi connect <SSID> password <PASSWORD>
        2. Handle errors (already connected, invalid password, etc.)
        3. Return success/failure status

Example:
    connector = LinuxNMCliConnector()
    credentials = {"ssid": "HomeWifi", "password": "secret123", "security": "WPA"}
    if connector.connect(credentials):
        print("Connected!")
    else:
        print("Failed to connect")

Note:
  Requires nmcli to be installed on the system.
  May require sudo for some operations.
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
            success=True, message=f"Successfully connectied to {credentials.ssid}"
        )

    error_output = result.stderr.strip() or result.stdout.strip()

    if "No network with SSID" in error_output:
        raise NetworkConnectionError(f"Wifi network not found: {credentials.ssid}")

    if "Secrets were required" in error_output or "password" in error_output.lower():
        raise NetworkConnectionError(
            "Could not connect. The WiFi password may be wrong."
        )

    raise NetworkConnectionError(f"Could not connect to Wifi: {error_output}")
