"""
Windows netsh connector for Wi-Fi connections.

This backend supports WPA/WPA2 personal networks and open networks. Enterprise
Wi-Fi is intentionally out of scope for now.
"""

from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import cast
import xml.etree.ElementTree as ET

from wifi_with_camera.network.base import ConnectionResult, NetworkConnectionError
from wifi_with_camera.parser.wifi_qr_parser import WifiCredentials

WLAN_PROFILE_NAMESPACE = "http://www.microsoft.com/networking/WLAN/profile/v1"
ET.register_namespace("", WLAN_PROFILE_NAMESPACE)


def is_netsh_available() -> bool:
    return shutil.which("netsh") is not None


def build_netsh_add_profile_command(profile_path: str) -> list[str]:
    return [
        "netsh",
        "wlan",
        "add",
        "profile",
        f"filename={profile_path}",
        "user=current",
    ]


def build_netsh_connect_command(credentials: WifiCredentials) -> list[str]:
    return [
        "netsh",
        "wlan",
        "connect",
        f"name={credentials.ssid}",
        f"ssid={credentials.ssid}",
    ]


def build_windows_wifi_profile_xml(credentials: WifiCredentials) -> str:
    authentication, encryption = get_authentication_settings(credentials)

    root = profile_element("WLANProfile")
    ET.SubElement(root, profile_tag("name")).text = credentials.ssid

    ssid_config = ET.SubElement(root, profile_tag("SSIDConfig"))
    ssid = ET.SubElement(ssid_config, profile_tag("SSID"))
    ET.SubElement(ssid, profile_tag("name")).text = credentials.ssid

    ET.SubElement(root, profile_tag("connectionType")).text = "ESS"
    ET.SubElement(root, profile_tag("connectionMode")).text = "manual"

    msm = ET.SubElement(root, profile_tag("MSM"))
    security = ET.SubElement(msm, profile_tag("security"))
    auth_encryption = ET.SubElement(security, profile_tag("authEncryption"))
    ET.SubElement(auth_encryption, profile_tag("authentication")).text = authentication
    ET.SubElement(auth_encryption, profile_tag("encryption")).text = encryption
    ET.SubElement(auth_encryption, profile_tag("useOneX")).text = "false"

    if authentication != "open" and credentials.password is not None:
        shared_key = ET.SubElement(security, profile_tag("sharedKey"))
        ET.SubElement(shared_key, profile_tag("keyType")).text = "passPhrase"
        ET.SubElement(shared_key, profile_tag("protected")).text = "false"
        ET.SubElement(
            shared_key, profile_tag("keyMaterial")
        ).text = credentials.password

    xml_bytes = cast(bytes, ET.tostring(root, encoding="utf-8", xml_declaration=True))
    return xml_bytes.decode("utf-8")


def profile_element(name: str) -> ET.Element:
    return ET.Element(profile_tag(name))


def profile_tag(name: str) -> str:
    return f"{{{WLAN_PROFILE_NAMESPACE}}}{name}"


def get_authentication_settings(credentials: WifiCredentials) -> tuple[str, str]:
    security = credentials.security.upper()

    if security == "NOPASS" or credentials.password is None:
        return "open", "none"

    if security in {"WPA", "WPA2", "WPA2PSK"}:
        return "WPA2PSK", "AES"

    if security == "WPAPSK":
        return "WPAPSK", "TKIP"

    raise NetworkConnectionError(
        f"Windows netsh connector does not support {credentials.security} Wi-Fi"
    )


def connect_to_wifi(credentials: WifiCredentials) -> ConnectionResult:
    if not is_netsh_available():
        raise NetworkConnectionError("netsh is not installed or not available")

    profile_path = write_temp_profile(credentials)

    try:
        add_profile_result = run_netsh(
            build_netsh_add_profile_command(str(profile_path))
        )
        if add_profile_result.returncode != 0:
            raise translate_netsh_error(
                add_profile_result,
                default_message="Could not add Windows Wi-Fi profile",
            )

        connect_result = run_netsh(build_netsh_connect_command(credentials))
        if connect_result.returncode != 0:
            raise translate_netsh_error(
                connect_result,
                default_message="Could not connect to Wi-Fi",
            )
    finally:
        profile_path.unlink(missing_ok=True)

    return ConnectionResult(
        success=True,
        message=f"Connection requested for {credentials.ssid}",
    )


def write_temp_profile(credentials: WifiCredentials) -> Path:
    profile_xml = build_windows_wifi_profile_xml(credentials)

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        delete=False,
        suffix=".xml",
    ) as profile_file:
        profile_file.write(profile_xml)
        return Path(profile_file.name)


def run_netsh(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def translate_netsh_error(
    result: subprocess.CompletedProcess[str],
    default_message: str,
) -> NetworkConnectionError:
    output = (result.stderr.strip() or result.stdout.strip()).strip()
    output_lower = output.lower()

    if "no wireless interface" in output_lower:
        return NetworkConnectionError("No Windows Wi-Fi adapter was found.")

    if "profile" in output_lower and "not found" in output_lower:
        return NetworkConnectionError("Windows could not find the Wi-Fi profile.")

    if (
        "network specified by profile" in output_lower
        or "not available to connect" in output_lower
    ):
        return NetworkConnectionError("Wi-Fi network not found.")

    if "key" in output_lower or "password" in output_lower:
        return NetworkConnectionError(
            "Could not connect. The Wi-Fi password may be wrong."
        )

    if output:
        return NetworkConnectionError(f"{default_message}: {output}")

    return NetworkConnectionError(default_message)
