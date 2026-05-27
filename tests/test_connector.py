from pytest import MonkeyPatch

import wifi_with_camera.network.connector as connector
from wifi_with_camera.network.base import ConnectionResult
from wifi_with_camera.parser.wifi_qr_parser import WifiCredentials


def test_connect_to_wifi_uses_windows_backend(monkeypatch: MonkeyPatch) -> None:
    credentials = WifiCredentials(
        ssid="HomeWifi",
        password="secret123",
        security="WPA",
    )
    called: dict[str, str] = {}

    def fake_connect_to_wifi(credentials: WifiCredentials) -> ConnectionResult:
        called["ssid"] = credentials.ssid
        return ConnectionResult(success=True, message="windows")

    monkeypatch.setattr(
        "wifi_with_camera.network.connector.platform.system", lambda: "Windows"
    )
    monkeypatch.setattr(
        "wifi_with_camera.network.windows_netsh.connect_to_wifi",
        fake_connect_to_wifi,
    )

    result = connector.connect_to_wifi(credentials)

    assert result.message == "windows"
    assert called == {"ssid": "HomeWifi"}


def test_connect_to_wifi_uses_linux_backend(monkeypatch: MonkeyPatch) -> None:
    credentials = WifiCredentials(
        ssid="HomeWifi",
        password="secret123",
        security="WPA",
    )
    called: dict[str, str] = {}

    def fake_connect_to_wifi(credentials: WifiCredentials) -> ConnectionResult:
        called["ssid"] = credentials.ssid
        return ConnectionResult(success=True, message="linux")

    monkeypatch.setattr(
        "wifi_with_camera.network.connector.platform.system", lambda: "Linux"
    )
    monkeypatch.setattr(
        "wifi_with_camera.network.linux_nmcli.connect_to_wifi",
        fake_connect_to_wifi,
    )

    result = connector.connect_to_wifi(credentials)

    assert result.message == "linux"
    assert called == {"ssid": "HomeWifi"}
