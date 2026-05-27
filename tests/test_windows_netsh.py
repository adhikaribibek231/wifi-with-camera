import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from wifi_with_camera.network.base import NetworkConnectionError
from wifi_with_camera.network.windows_netsh import (
    WLAN_PROFILE_NAMESPACE,
    build_netsh_add_profile_command,
    build_netsh_connect_command,
    build_windows_wifi_profile_xml,
    connect_to_wifi,
    translate_netsh_error,
)
from wifi_with_camera.parser.wifi_qr_parser import WifiCredentials


def test_build_netsh_add_profile_command() -> None:
    result = build_netsh_add_profile_command(r"C:\Temp\wifi-profile.xml")

    assert result == [
        "netsh",
        "wlan",
        "add",
        "profile",
        r"filename=C:\Temp\wifi-profile.xml",
        "user=current",
    ]


def test_build_netsh_connect_command() -> None:
    credentials = WifiCredentials(
        ssid="HomeWifi",
        password="secret123",
        security="WPA",
    )

    result = build_netsh_connect_command(credentials)

    assert result == [
        "netsh",
        "wlan",
        "connect",
        "name=HomeWifi",
        "ssid=HomeWifi",
    ]


def test_build_windows_profile_xml_for_wpa_wifi() -> None:
    credentials = WifiCredentials(
        ssid="HomeWifi",
        password="secret123",
        security="WPA",
    )

    result = build_windows_wifi_profile_xml(credentials)
    root = ET.fromstring(result)

    assert find_text(root, "name") == "HomeWifi"
    assert find_text(root, "authentication") == "WPA2PSK"
    assert find_text(root, "encryption") == "AES"
    assert find_text(root, "keyType") == "passPhrase"
    assert find_text(root, "protected") == "false"
    assert find_text(root, "keyMaterial") == "secret123"


def test_build_windows_profile_xml_for_open_wifi() -> None:
    credentials = WifiCredentials(
        ssid="OpenCafe",
        password=None,
        security="nopass",
    )

    result = build_windows_wifi_profile_xml(credentials)
    root = ET.fromstring(result)

    assert find_text(root, "name") == "OpenCafe"
    assert find_text(root, "authentication") == "open"
    assert find_text(root, "encryption") == "none"
    assert root.find(f".//{{{WLAN_PROFILE_NAMESPACE}}}sharedKey") is None


def test_build_windows_profile_xml_escapes_xml_text() -> None:
    credentials = WifiCredentials(
        ssid="Cafe & Work",
        password="pass<word>&123",
        security="WPA",
    )

    result = build_windows_wifi_profile_xml(credentials)

    assert "Cafe &amp; Work" in result
    assert "pass&lt;word&gt;&amp;123" in result


def test_build_windows_profile_xml_rejects_unsupported_security() -> None:
    credentials = WifiCredentials(
        ssid="OldWifi",
        password="abc12345",
        security="WEP",
    )

    with pytest.raises(NetworkConnectionError, match="does not support WEP"):
        build_windows_wifi_profile_xml(credentials)


def test_connect_to_wifi_deletes_temp_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    credentials = WifiCredentials(
        ssid="HomeWifi",
        password="secret123",
        security="WPA",
    )
    commands: list[list[str]] = []
    profile_paths: list[Path] = []

    def fake_is_netsh_available() -> bool:
        return True

    def fake_write_temp_profile(credentials: WifiCredentials) -> Path:
        path = Path("/tmp/windows-netsh-test-profile.xml")
        path.write_text(credentials.ssid, encoding="utf-8")
        profile_paths.append(path)
        return path

    def fake_run_netsh(command: list[str]) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "wifi_with_camera.network.windows_netsh.is_netsh_available",
        fake_is_netsh_available,
    )
    monkeypatch.setattr(
        "wifi_with_camera.network.windows_netsh.write_temp_profile",
        fake_write_temp_profile,
    )
    monkeypatch.setattr(
        "wifi_with_camera.network.windows_netsh.run_netsh",
        fake_run_netsh,
    )

    result = connect_to_wifi(credentials)

    assert result.success is True
    assert result.message == "Connection requested for HomeWifi"
    assert commands == [
        [
            "netsh",
            "wlan",
            "add",
            "profile",
            "filename=/tmp/windows-netsh-test-profile.xml",
            "user=current",
        ],
        [
            "netsh",
            "wlan",
            "connect",
            "name=HomeWifi",
            "ssid=HomeWifi",
        ],
    ]
    assert profile_paths[0].exists() is False


def test_translate_netsh_network_not_found_error() -> None:
    result = subprocess.CompletedProcess(
        ["netsh"],
        returncode=1,
        stdout="The network specified by profile is not available to connect.",
        stderr="",
    )

    error = translate_netsh_error(result, "Could not connect to Wi-Fi")

    assert str(error) == "Wi-Fi network not found."


def test_translate_netsh_password_error() -> None:
    result = subprocess.CompletedProcess(
        ["netsh"],
        returncode=1,
        stdout="The network security key is not correct.",
        stderr="",
    )

    error = translate_netsh_error(result, "Could not connect to Wi-Fi")

    assert str(error) == "Could not connect. The Wi-Fi password may be wrong."


def find_text(root: ET.Element, name: str) -> str | None:
    element = root.find(f".//{{{WLAN_PROFILE_NAMESPACE}}}{name}")
    if element is None:
        return None

    return element.text
