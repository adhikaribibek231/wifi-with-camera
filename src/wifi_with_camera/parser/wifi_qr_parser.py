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
