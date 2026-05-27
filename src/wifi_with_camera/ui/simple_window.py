"""Simple PySide window for scanning and connecting to Wi-Fi QR codes."""

from typing import cast

import cv2
from PySide6 import QtCore, QtGui, QtWidgets

from wifi_with_camera.network.base import NetworkConnectionError
from wifi_with_camera.network.linux_nmcli import connect_to_wifi
from wifi_with_camera.parser.wifi_qr_parser import WifiCredentials, parse
from wifi_with_camera.scanner.opencv_scanner import (
    Frame,
    OpenCVScanner,
    QRDetection,
    draw_qr_overlay,
    mirror_qr_points,
)


class MyWidget(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.credentials: WifiCredentials | None = None
        self.scanner: OpenCVScanner | None = None
        self.last_qr_text: str | None = None

        self.setWindowTitle("Wi-Fi QR Scanner")

        self.camera_label = QtWidgets.QLabel("Starting camera...")
        self.camera_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        self.scan_button = QtWidgets.QPushButton("Restart camera")
        self.scan_button.clicked.connect(self.restart_camera)

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
        main_layout.addWidget(self.camera_label)
        main_layout.addWidget(self.scan_button)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.status_label)

        self.camera_timer = QtCore.QTimer(self)
        self.camera_timer.timeout.connect(self.update_camera_frame)

        self.update_credentials(None)
        self.start_camera()

    def start_camera(self) -> None:
        self.scanner = OpenCVScanner()
        if not self.scanner.is_opened():
            self.scanner.release()
            self.scanner = None
            self.camera_label.setText("Camera unavailable")
            self.status_label.setText("Could not open webcam")
            return

        self.camera_timer.start(30)
        self.status_label.setText("Waiting for Wi-Fi QR code")

    def restart_camera(self) -> None:
        self.stop_camera()
        self.last_qr_text = None
        self.camera_label.setText("Starting camera...")
        self.status_label.setText("Restarting camera...")
        self.start_camera()

    def stop_camera(self) -> None:
        self.camera_timer.stop()
        if self.scanner is not None:
            self.scanner.release()
            self.scanner = None

    def update_camera_frame(self) -> None:
        if self.scanner is None:
            return

        frame = self.scanner.read_frame()
        if frame is None:
            self.status_label.setText("Could not read frame from webcam")
            self.stop_camera()
            return

        detection = self.scanner.detect_qr_code(frame)
        self.show_camera_frame(frame, detection)

        if detection is not None:
            self.handle_qr_text(detection.text)

    def show_camera_frame(
        self,
        frame: Frame,
        detection: QRDetection | None,
    ) -> None:
        display_frame = cast(Frame, cv2.flip(frame, 1))

        if detection is not None:
            mirrored_points = mirror_qr_points(
                detection.points,
                frame_width=frame.shape[1],
            )
            draw_qr_overlay(display_frame, mirrored_points)

        rgb_frame = cast(Frame, cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB))
        height = rgb_frame.shape[0]
        width = rgb_frame.shape[1]
        bytes_per_line = rgb_frame.strides[0]

        image = QtGui.QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QtGui.QImage.Format.Format_RGB888,
        ).copy()
        pixmap = QtGui.QPixmap.fromImage(image)
        scaled_pixmap = pixmap.scaled(
            self.camera_label.size(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        self.camera_label.setPixmap(scaled_pixmap)

    def handle_qr_text(self, qr_text: str) -> None:
        if qr_text == self.last_qr_text:
            return

        self.last_qr_text = qr_text

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
            self.status_label.setText("Show a Wi-Fi QR code first")
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

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.stop_camera()
        super().closeEvent(event)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    widget = MyWidget()

    widget.show()

    sys.exit(app.exec())
