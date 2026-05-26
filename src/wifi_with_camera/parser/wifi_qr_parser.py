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


def parse(qr_text: str) -> dict[str, str]:
    x = qr_text.split(";")
    print("X:", x)
    extract = x[1:3]
    print("Extract:", extract)
    result = dict(item.split(":") for item in extract)
    sec = x[0].split(":")
    return {
        "ssid": result.get("S", ""),
        "password": result.get("P", ""),
        "security": sec[2],
    }
