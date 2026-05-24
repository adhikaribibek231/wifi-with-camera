
# WiFi With Camera (WWC)

Connect to WiFi networks by scanning WiFi QR codes with your webcam.

WWC is a free and open-source desktop utility that lets you scan a WiFi QR code, read the WiFi details, and connect from your computer. After installation, it should work without needing an internet connection.

## What It Does

WWC uses your webcam to scan a WiFi QR code and extract:

- WiFi name / SSID
- Security type
- Password

After scanning, WWC can:

- try to connect automatically
- show the password on screen
- let you manually copy/type the password if automatic connection fails

This makes the app useful even when automatic connection does not work.

## Project Structure

```
wifi-with-camera/
├── README.md
├── pyproject.toml
├── uv.lock
├── .pre-commit-config.yaml
├── .python-version
├── .gitignore
├── src/
│   └── wifi_with_camera/
│       ├── __init__.py
│       ├── main.py                 # App entry point, coordinates workflow
│       ├── scanner/
│       │   ├── __init__.py
│       │   └── opencv_scanner.py  # Camera + QR detection
│       ├── parser/
│       │   ├── __init__.py
│       │   └── wifi_qr_parser.py  # Parse QR text to WiFi credentials
│       ├── network/
│       │   ├── __init__.py
│       │   ├── base.py            # Abstract connector interface
│       │   └── linux_nmcli.py     # Linux-specific WiFi connector
│       └── ui/
│           ├── __init__.py
│           └── simple_window.py   # PyQt GUI (future)
└── tests/
    ├── test_wifi_qr_parser.py
    └── test_linux_nmcli.py
```

### Module Overview

- **main.py**: Orchestrates the workflow (scanner → parser → connector)
- **scanner/opencv_scanner.py**: Captures video frames and detects QR codes
- **parser/wifi_qr_parser.py**: Converts QR text (WIFI:T:WPA;S:SSID;P:PASSWORD;;) to structured data
- **network/base.py**: Defines the abstract `Connector` interface for WiFi connections
- **network/linux_nmcli.py**: Implements WiFi connection using `nmcli` on Linux
- **ui/simple_window.py**: PyQt GUI (not implemented yet)

## Development Setup

This project uses `uv` for dependency management and Hatchling for Python packaging.

Install the project and development tools:

```bash
uv sync
```

After syncing, the CLI entry point should be available:

```bash
uv run wwc
```

If you activate the virtual environment, you can also run:

```bash
source .venv/bin/activate
wwc
```

Install pre-commit hooks once per clone:

```bash
uv run pre-commit install
```

Run the checks manually:

```bash
uv run ruff check .
uv run ruff format .
uv run mypy
uv run pytest
uv run pre-commit run --all-files
```

The current pre-commit setup runs Ruff formatting/linting and mypy.

## Why This Exists

Phones can usually scan WiFi QR codes and connect quickly. Desktop systems, especially Linux desktops, often still require manually typing long passwords.

WWC brings that simple scan-and-connect experience to desktop.

## Offline First

WWC is designed to work offline after installation.

It does not require:

- an account
- internet access
- a cloud service
- telemetry
- a backend server

The QR code is scanned locally using the webcam.

## Example WiFi QR Format

```text
WIFI:T:WPA;S:MyNetwork;P:MyPassword;;
```

## Planned Stack

* Python
* OpenCV
* PyQt6 for the future desktop GUI
* NetworkManager (`nmcli`) on Linux
* `netsh wlan` on Windows
* uv, Hatchling, Ruff, Mypy, Pytest, and pre-commit for development

## Current Status

Early development / planning stage.

## Goals

The project aims to be:

* lightweight
* easy to install
* cross-platform
* privacy-friendly
* contributor-friendly
* useful for everyday users

## Roadmap

* [ ] Webcam scanning
* [ ] QR detection
* [ ] WiFi QR parser
* [ ] Display SSID, security type, and password
* [ ] Copy password button
* [ ] Linux WiFi connector
* [ ] Desktop GUI
* [ ] Windows support
* [ ] Installable builds

## License

MIT License (planned)

---

Built as an independent open-source project by Bibek Adhikari.
