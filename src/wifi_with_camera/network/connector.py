"""Choose the Wi-Fi connector for the current operating system."""

from collections.abc import Callable
import platform

from wifi_with_camera.network.base import ConnectionResult
from wifi_with_camera.parser.wifi_qr_parser import WifiCredentials

Connector = Callable[[WifiCredentials], ConnectionResult]


def get_connector() -> Connector:
    if platform.system() == "Windows":
        from wifi_with_camera.network.windows_netsh import connect_to_wifi

        return connect_to_wifi

    from wifi_with_camera.network.linux_nmcli import connect_to_wifi

    return connect_to_wifi


def connect_to_wifi(credentials: WifiCredentials) -> ConnectionResult:
    return get_connector()(credentials)
