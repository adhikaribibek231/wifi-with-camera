import pytest

from wifi_with_camera.parser.wifi_qr_parser import (
    WifiCredentials,
    parse,
    split_unescaped_semicolons,
)


def test_parse_secured_wifi_qr() -> None:
    result = parse("WIFI:T:WPA;S:HomeWifi;P:secret123;;")

    assert result == WifiCredentials(
        ssid="HomeWifi",
        password="secret123",
        security="WPA",
    )


def test_parse_open_wifi_qr() -> None:
    result = parse("WIFI:T:nopass;S:OpenCafe;;")

    assert result == WifiCredentials(
        ssid="OpenCafe",
        password=None,
        security="nopass",
    )


def test_parse_wifi_qr_with_semicolon_inside_ssid() -> None:
    result = parse(r"WIFI:T:WPA;S:home\;wifi;P:secret123;;")

    assert result == WifiCredentials(
        ssid="home;wifi",
        password="secret123",
        security="WPA",
    )


def test_parse_wifi_qr_with_semicolon_inside_password() -> None:
    result = parse(r"WIFI:T:WPA;S:HomeWifi;P:1234\;4324;;")

    assert result == WifiCredentials(
        ssid="HomeWifi",
        password="1234;4324",
        security="WPA",
    )


def test_parse_wifi_qr_with_colon_inside_ssid() -> None:
    result = parse(r"WIFI:T:WPA;S:home\:wifi;P:secret123;;")

    assert result == WifiCredentials(
        ssid=r"home:wifi",
        password="secret123",
        security="WPA",
    )


def test_parse_wifi_qr_with_colon_inside_password() -> None:
    result = parse(r"WIFI:T:WPA;S:HomeWifi;P:W\:1234;;")

    assert result == WifiCredentials(
        ssid="HomeWifi",
        password=r"W:1234",
        security="WPA",
    )


def test_parse_wifi_qr_with_semicolon_and_colon_inside_ssid_and_password() -> None:
    result = parse(r"WIFI:T:WPA;S:home\;wifi\:join;P:W\:1234\;4324;;")

    assert result == WifiCredentials(
        ssid=r"home;wifi:join",
        password=r"W:1234;4324",
        security="WPA",
    )


def test_missing_ssid_raises_error() -> None:
    with pytest.raises(ValueError):
        parse("WIFI:T:WPA;P:secret123;;")


def test_secured_wifi_without_password_raises_error() -> None:
    with pytest.raises(ValueError):
        parse("WIFI:T:WPA;S:HomeWifi;;")


def test_non_wifi_qr_raises_error() -> None:
    with pytest.raises(ValueError):
        parse("name:Bibek;age:25;role:developer;")


def test_split_unescaped_semicolons() -> None:
    result = split_unescaped_semicolons(r"T:WPA;S:home\;wifi;P:1234\;4324;;")

    assert result == [
        "T:WPA",
        "S:home;wifi",
        "P:1234;4324",
        "",
        "",
    ]
