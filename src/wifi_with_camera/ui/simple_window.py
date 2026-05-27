"""Simple PySide window for scanning and connecting to Wi-Fi QR codes."""

import os
from typing import cast

os.environ.setdefault("OPENCV_LOG_LEVEL", "SILENT")

import cv2
from PySide6 import QtCore, QtGui, QtWidgets

from wifi_with_camera.network.base import NetworkConnectionError
from wifi_with_camera.network.connector import connect_to_wifi
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
        self.resize(860, 760)
        self.setMinimumSize(720, 640)

        self.title_label = QtWidgets.QLabel("Wi-Fi QR Scanner")
        self.title_label.setObjectName("titleLabel")

        self.camera_label = QtWidgets.QLabel("Starting camera...")
        self.camera_label.setObjectName("cameraPreview")
        self.camera_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setMinimumSize(640, 420)
        self.camera_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        self.scan_button = QtWidgets.QPushButton("Restart camera")
        self.scan_button.setProperty("variant", "secondary")
        self.scan_button.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.scan_button.clicked.connect(self.restart_camera)

        self.ssid_label = QtWidgets.QLabel("-")
        self.security_label = QtWidgets.QLabel("-")
        self.password_label = QtWidgets.QLabel("-")
        for label in (self.ssid_label, self.security_label, self.password_label):
            label.setProperty("role", "value")

        self.password_label.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.show_password_checkbox = QtWidgets.QCheckBox("Show password")
        self.show_password_checkbox.toggled.connect(self.refresh_password_label)

        self.copy_password_button = QtWidgets.QPushButton("Copy password")
        self.copy_password_button.setProperty("variant", "secondary")
        self.copy_password_button.clicked.connect(self.copy_password)

        self.connect_button = QtWidgets.QPushButton("Connect")
        self.connect_button.setProperty("variant", "primary")
        self.connect_button.clicked.connect(self.connect_to_network)

        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setObjectName("statusLabel")

        form_layout = QtWidgets.QFormLayout()
        form_layout.setContentsMargins(14, 14, 14, 14)
        form_layout.setHorizontalSpacing(16)
        form_layout.setVerticalSpacing(12)
        form_layout.addRow("SSID:", self.ssid_label)
        form_layout.addRow("Security:", self.security_label)
        form_layout.addRow("Password:", self.password_label)
        form_layout.addRow("", self.show_password_checkbox)

        credentials_box = QtWidgets.QGroupBox("Network details")
        credentials_box.setLayout(form_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        button_layout.addWidget(self.copy_password_button)
        button_layout.addWidget(self.connect_button)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(12)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.scan_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(14)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.camera_label)
        main_layout.addWidget(credentials_box)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.status_label)

        self.camera_timer = QtCore.QTimer(self)
        self.camera_timer.timeout.connect(self.update_camera_frame)

        self.apply_styles()
        self.update_credentials(None)
        self.start_camera()

    def apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background: #f5f7fa;
                color: #172033;
                font-size: 14px;
            }

            QLabel#titleLabel {
                color: #111827;
                font-size: 24px;
                font-weight: 700;
                padding-bottom: 2px;
            }

            QLabel#cameraPreview {
                background: #111827;
                border: 1px solid #273244;
                border-radius: 8px;
                color: #e5e7eb;
                font-size: 16px;
            }

            QGroupBox {
                background: #ffffff;
                border: 1px solid #d9e1ea;
                border-radius: 8px;
                font-weight: 700;
                margin-top: 12px;
                padding-top: 10px;
            }

            QGroupBox::title {
                color: #475569;
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }

            QLabel[role="value"] {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                color: #111827;
                font-family: monospace;
                padding: 7px 9px;
            }

            QCheckBox {
                spacing: 8px;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }

            QPushButton {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-weight: 700;
                min-height: 34px;
                padding: 0 16px;
            }

            QPushButton[variant="primary"] {
                background: #0f766e;
                border-color: #0f766e;
                color: #ffffff;
            }

            QPushButton[variant="primary"]:hover {
                background: #115e59;
                border-color: #115e59;
            }

            QPushButton[variant="secondary"] {
                background: #ffffff;
                color: #172033;
            }

            QPushButton[variant="secondary"]:hover {
                background: #eef2f7;
            }

            QPushButton:disabled {
                background: #e5e7eb;
                border-color: #d1d5db;
                color: #8a94a6;
            }

            QLabel#statusLabel {
                background: #ecfdf5;
                border: 1px solid #a7f3d0;
                border-radius: 6px;
                color: #065f46;
                padding: 9px 12px;
            }
            """
        )

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
            self.show_password_checkbox.setChecked(False)
            self.show_password_checkbox.setEnabled(False)
            self.copy_password_button.setEnabled(False)
            self.connect_button.setEnabled(False)
            return

        self.ssid_label.setText(credentials.ssid)
        self.security_label.setText(credentials.security)
        self.show_password_checkbox.setChecked(False)
        self.show_password_checkbox.setEnabled(credentials.password is not None)
        self.refresh_password_label()
        self.copy_password_button.setEnabled(credentials.password is not None)
        self.connect_button.setEnabled(True)

    def refresh_password_label(self, _checked: bool | None = None) -> None:
        if self.credentials is None:
            self.password_label.setText("-")
            return

        password = self.credentials.password
        if password is None:
            self.password_label.setText("(none)")
            return

        if self.show_password_checkbox.isChecked():
            self.password_label.setText(password)
            return

        self.password_label.setText("*" * len(password))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.stop_camera()
        super().closeEvent(event)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    widget = MyWidget()

    widget.show()

    sys.exit(app.exec())
