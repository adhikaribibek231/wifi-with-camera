from wifi_with_camera.network.linux_nmcli import build_nmcli_connect_command
from wifi_with_camera.parser.wifi_qr_parser import WifiCredentials


def test_build_nmcli_command_for_secured_wifi() -> None:
    credentials = WifiCredentials(
        ssid="HomeWifi",
        password="secret123",
        security="WPA",
    )

    result = build_nmcli_connect_command(credentials)

    assert result == [
        "nmcli",
        "device",
        "wifi",
        "connect",
        "HomeWifi",
        "password",
        "secret123",
    ]


def test_build_nmcli_command_for_open_wifi() -> None:
    credentials = WifiCredentials(
        ssid="OpenCafe",
        password=None,
        security="nopass",
    )

    result = build_nmcli_connect_command(credentials)

    assert result == [
        "nmcli",
        "device",
        "wifi",
        "connect",
        "OpenCafe",
    ]
