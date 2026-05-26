"""
Common network connection result types and errors.

Responsibilities:
  - Define the shared connection result object
  - Define the exception used for network connection failures
"""

from dataclasses import dataclass


@dataclass
class ConnectionResult:
    success: bool
    message: str


class NetworkConnectionError(RuntimeError):
    pass
