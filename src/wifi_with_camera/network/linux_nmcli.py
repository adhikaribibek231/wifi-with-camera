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
