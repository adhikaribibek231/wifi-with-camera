import sys
from pathlib import Path

from PySide6 import QtGui, QtWidgets

from wifi_with_camera.ui.simple_window import MyWidget

ICON_PATH = Path(__file__).parent / "assets" / "icons" / "wwc.png"


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)

    icon = QtGui.QIcon(str(ICON_PATH))
    app.setWindowIcon(icon)

    widget = MyWidget()
    widget.setWindowTitle("WWC — WiFi With Camera")
    widget.setWindowIcon(icon)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
