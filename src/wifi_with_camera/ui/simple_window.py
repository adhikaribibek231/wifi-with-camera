"""Simple PySide window for scanning and connecting to Wi-Fi QR codes."""

from PySide6 import QtCore, QtWidgets

from wifi_with_camera.network.base import NetworkConnectionError
from wifi_with_camera.network.linux_nmcli import connect_to_wifi
from wifi_with_camera.parser.wifi_qr_parser import WifiCredentials, parse
from wifi_with_camera.scanner.opencv_scanner import scan


class MyWidget(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.credentials: WifiCredentials | None = None

        self.setWindowTitle("Wi-Fi QR Scanner")

        self.scan_button = QtWidgets.QPushButton("Scan")
        self.scan_button.clicked.connect(self.scan_qr)

        self.ssid_label = QtWidgets.QLabel("-")
        self.security_label = QtWidgets.QLabel("-")
        self.password_label = QtWidgets.QLabel("-")
        self.password_label.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.copy_password_button = QtWidgets.QPushButton("Copy password")
        self.copy_password_button.clicked.connect(self.copy_password)

        self.connect_button = QtWidgets.QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_network)

        self.status_label = QtWidgets.QLabel("Ready")

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("SSID:", self.ssid_label)
        form_layout.addRow("Security:", self.security_label)
        form_layout.addRow("Password:", self.password_label)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.copy_password_button)
        button_layout.addWidget(self.connect_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.scan_button)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.status_label)

        self.update_credentials(None)

    def scan_qr(self) -> None:
        self.status_label.setText("Scanning...")
        QtWidgets.QApplication.processEvents()

        qr_text = scan()
        if qr_text is None:
            self.update_credentials(None)
            self.status_label.setText("No QR code detected")
            return

        try:
            credentials = parse(qr_text)
        except ValueError as error:
            self.update_credentials(None)
            self.status_label.setText(str(error))
            return

        self.update_credentials(credentials)
        self.status_label.setText("QR code parsed")

    def copy_password(self) -> None:
        if self.credentials is None or self.credentials.password is None:
            self.status_label.setText("No password to copy")
            return

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.credentials.password)
        self.status_label.setText("Password copied")

    def connect_to_network(self) -> None:
        if self.credentials is None:
            self.status_label.setText("Scan a Wi-Fi QR code first")
            return

        self.status_label.setText("Connecting...")
        QtWidgets.QApplication.processEvents()

        try:
            result = connect_to_wifi(self.credentials)
        except NetworkConnectionError as error:
            self.status_label.setText(str(error))
            return

        self.status_label.setText(result.message)

    def update_credentials(self, credentials: WifiCredentials | None) -> None:
        self.credentials = credentials

        if credentials is None:
            self.ssid_label.setText("-")
            self.security_label.setText("-")
            self.password_label.setText("-")
            self.copy_password_button.setEnabled(False)
            self.connect_button.setEnabled(False)
            return

        self.ssid_label.setText(credentials.ssid)
        self.security_label.setText(credentials.security)
        self.password_label.setText(credentials.password or "(none)")
        self.copy_password_button.setEnabled(credentials.password is not None)
        self.connect_button.setEnabled(True)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    widget = MyWidget()

    widget.show()

    sys.exit(app.exec())
