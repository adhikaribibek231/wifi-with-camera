"""
WiFi QR code parser module.

Responsibilities:
  - Parse raw QR text in WiFi standard format (WIFI:T:WPA;S:SSID;P:PASSWORD;;)
  - Extract WiFi credentials (SSID, password, security type)
  - Return structured data

WiFi QR Format:
  WIFI:T:<security>;S:<SSID>;P:<password>;;

  Examples:
    - WIFI:T:WPA;S:HomeWifi;P:secret123;;
    - WIFI:T:WEP;S:GuestNet;P:pass456;;
    - WIFI:T:nopass;S:PublicWifi;;

Functions:
  parse(qr_text: str) -> dict
      Extracts WiFi credentials from QR text.
      Returns dict with keys: ssid, password, security

Example:
    result = parse("WIFI:T:WPA;S:HomeWifi;P:secret123;;")
    # Returns: {"ssid": "HomeWifi", "password": "secret123", "security": "WPA"}
"""


# scuffed v0
# def parse(qr_text: str) -> dict[str, str]:
#     x = qr_text.split(";")
#     print("X:", x)
#     extract = x[1:3]
#     print("Extract:", extract)
#     result = dict(item.split(":") for item in extract)
#     sec = x[0].split(":")
#     return {
#         "ssid": result.get("S", ""),
#         "password": result.get("P", ""),
#         "security": sec[2],
#     }

from dataclasses import dataclass


@dataclass
class WifiCredentials:
    ssid: str
    password: str | None
    security: str


def split_unescaped_semicolons(text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    escaped = False

    for char in text:
        if escaped:
            current.append(char)
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        if char == ";":
            parts.append("".join(current))
            current = []
            continue

        current.append(char)

    if escaped:
        current.append("\\")

    parts.append("".join(current))

    return parts


def parse(qr_text: str) -> WifiCredentials:
    if not qr_text.startswith("WIFI:"):
        raise ValueError("Not a WiFi QR code")

    content = qr_text.removeprefix("WIFI:")
    parts = split_unescaped_semicolons(content)

    data: dict[str, str] = {}

    for part in parts:
        if part == "":
            continue

        if ":" not in part:
            continue

        key, value = part.split(":", 1)
        data[key] = value

    ssid = data.get("S")
    security = data.get("T", "nopass")
    password = data.get("P")

    if not ssid:
        raise ValueError("WiFi QR code does not contain an SSID")

    if security != "nopass" and not password:
        raise ValueError("Secured WiFi QR code does not contain a password")

    return WifiCredentials(
        ssid=ssid,
        password=password,
        security=security,
    )
