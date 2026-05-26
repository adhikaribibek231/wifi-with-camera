"""
Base connector interface for WiFi network connections.

Responsibilities:
  - Define common interface all connectors must implement
  - Abstract away OS-specific connection logic

All platform-specific connectors (Linux, Windows, macOS) should inherit from Connector
and implement the connect() method.

Abstract Base Class:
  Connector
      Abstract method: connect(credentials: dict) -> bool
          Takes WiFi credentials dict with keys: ssid, password, security
          Returns True if connection successful, False otherwise

Example:
    connector = LinuxNMCliConnector()
    credentials = {"ssid": "HomeWifi", "password": "secret123", "security": "WPA"}
    success = connector.connect(credentials)
"""

from dataclasses import dataclass


@dataclass
class ConnectionResult:
    success: bool
    message: str


class NetworkConnectionError(RuntimeError):
    pass
