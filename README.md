# Wi-Fi With Camera (WWC)

Connect to Wi-Fi networks by scanning Wi-Fi QR codes with your webcam.

WWC is a desktop utility that lets you scan a Wi-Fi QR code, read the Wi-Fi details, and connect from your computer. The goal is to bring the phone-like "scan and connect" Wi-Fi experience to desktop systems.

The project is currently Linux-first, with Windows support planned. The current
MVP scans a QR code, parses the Wi-Fi credentials, prints a copy-friendly result,
and can optionally try to connect on Linux through NetworkManager's `nmcli`.

> WWC is not currently designed as a PyPI package for end users.  
> The Python packaging setup exists mainly to keep the project clean, installable in development, and easy to run locally with `uv run wwc`.

---

## What It Does

WWC uses your webcam to scan a Wi-Fi QR code and extract:

- Wi-Fi name / SSID
- Security type
- Password

After scanning, WWC can:

- display the detected Wi-Fi details
- show the password locally on screen
- print copy-friendly `SSID`, `SECURITY`, and `PASSWORD` lines
- try to connect automatically on Linux when `nmcli` is available

This means the app is still useful even if automatic Wi-Fi connection fails.

For example, if automatic connection is not supported on the current system, WWC can still scan the QR code and show the password so the user does not need to type it from another device.

---

## Why This Exists

Phones can usually scan Wi-Fi QR codes and connect quickly. Desktop systems, especially many Linux desktops, often still require manually typing long or complex passwords.

WWC exists to make that process easier.

The main idea is simple:

```text
Open camera -> Scan Wi-Fi QR -> Read credentials -> Connect or show password
```

---

## Offline First

WWC is designed to work offline after installation.

It does not require:

- an account
- internet access
- a cloud service
- telemetry
- a backend server

The QR code is scanned locally using the webcam. Wi-Fi details are processed locally on the machine.

---

## Example Wi-Fi QR Format

A typical Wi-Fi QR code contains text like this:

```text
WIFI:T:WPA;S:MyNetwork;P:MyPassword;;
```

WWC parses this text into structured Wi-Fi information:

```text
SSID: MyNetwork
Security: WPA
Password: MyPassword
```

---

## Project Structure

The project uses a `src/` layout so the application code stays separate from tests, configuration, and repository files.

```text
wifi-with-camera/
├── README.md
├── pyproject.toml
├── uv.lock
├── .pre-commit-config.yaml
├── .python-version
├── .gitignore
│
├── src/
│   └── wifi_with_camera/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── scanner/
│       │   ├── __init__.py
│       │   └── opencv_scanner.py
│       │
│       ├── parser/
│       │   ├── __init__.py
│       │   └── wifi_qr_parser.py
│       │
│       ├── network/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── linux_nmcli.py
│       │
│       ├── display/
│       │   ├── __init__.py
│       │   └── result_display.py
│       │
│       └── ui/
│           ├── __init__.py
│           └── simple_window.py
│
└── tests/
    ├── test_wifi_qr_parser.py
    └── test_linux_nmcli.py
```

Some files are placeholders during early development.

---

## Module Overview

### `main.py`

Application entry point.

This file coordinates the main workflow:

```text
scanner -> parser -> result display -> optional Linux network connector
```

For local development, this file exposes a `main()` function so the app can be run using:

```bash
uv run wwc
```

---

### `scanner/opencv_scanner.py`

Handles webcam access and QR detection using OpenCV.

Responsibilities:

- open the webcam
- read video frames
- detect QR codes
- return the decoded QR text
- handle camera/window cleanup safely

This module should only care about scanning. It should not parse Wi-Fi credentials or connect to networks.

---

### `parser/wifi_qr_parser.py`

Parses raw Wi-Fi QR text into structured Wi-Fi credentials.

Example input:

```text
WIFI:T:WPA;S:MyNetwork;P:MyPassword;;
```

Example output:

```text
SSID: MyNetwork
Security: WPA
Password: MyPassword
```

This module should be highly testable because it does not need a camera or real Wi-Fi connection.

---

### `network/base.py`

Defines shared network result and error types:

- `ConnectionResult`
- `NetworkConnectionError`

The purpose of this file is to keep connection result handling consistent while
platform-specific code stays separated from the rest of the app.

---

### `network/linux_nmcli.py`

Linux-specific Wi-Fi connector using NetworkManager's `nmcli`.

Responsibilities:

- check whether `nmcli` is available
- build the `nmcli device wifi connect ...` command
- attempt Wi-Fi connection using SSID and password
- support open networks without a password argument
- return clear success messages
- raise clear connection errors

This is the first automatic connection backend in the project.

---

### `display/result_display.py`

Prints parsed Wi-Fi credentials and user-facing parse errors.

The current CLI output includes a readable result section and copy-friendly
environment-style lines:

```text
SSID=MyNetwork
SECURITY=WPA
PASSWORD=MyPassword
```

---

### `ui/simple_window.py`

Future desktop GUI.

The first version of the project uses a simple OpenCV camera window. Later, this
module can become the home of a real desktop interface.

Possible future GUI features:

- live camera preview
- scan status
- detected SSID display
- password visibility toggle
- copy password button
- connect button
- error messages
- platform support warnings

PyQt6 or PySide6 may be used for the future GUI.

---

## Development Setup

This project uses:

- `uv` for dependency management
- Hatchling so the project can be installed locally during development
- Ruff for linting and formatting
- Mypy for type checking
- Pytest for tests
- Pre-commit for automated checks before commits

The project is not currently published as a Python package. The packaging setup exists mainly so local commands like `uv run wwc` work cleanly.

---

## Install Dependencies

From the project root, run:

```bash
uv sync
```

This installs the runtime and development dependencies into the local virtual environment.

---

## Run the App

The project defines a local development command:

```toml
[project.scripts]
wwc = "wifi_with_camera.main:main"
```

This allows the app to be run with:

```bash
uv run wwc
```

This is preferred over writing a longer command every time.

If you activate the virtual environment manually, you can also run:

```bash
source .venv/bin/activate
wwc
```

---

## Run Checks

Run Ruff linting:

```bash
uv run ruff check .
```

Run Ruff formatting:

```bash
uv run ruff format .
```

Run Mypy:

```bash
uv run mypy
```

Run tests:

```bash
uv run pytest
```

Run all pre-commit checks manually:

```bash
uv run pre-commit run --all-files
```

---

## Pre-commit Setup

Install pre-commit hooks once per clone:

```bash
uv run pre-commit install
```

After this, checks will run automatically before commits.

The current pre-commit setup is intended to run:

- Ruff formatting
- Ruff linting
- Mypy type checking

---

## Planned Stack

Core application:

- Python
- OpenCV
- NetworkManager / `nmcli` on Linux
- `netsh wlan` on Windows

Future desktop UI:

- PyQt6 or PySide6

Development tooling:

- uv
- Hatchling
- Ruff
- Mypy
- Pytest
- pre-commit

Future distribution options:

- Linux AppImage
- Linux `.deb`
- Windows executable
- Windows installer

---

## Current Status

Early development.

The current Linux-first MVP flow is:

```text
Open webcam -> scan QR code -> parse Wi-Fi credentials -> display result -> optionally connect with nmcli
```

Implemented so far:

- webcam QR scanning with OpenCV
- Wi-Fi QR parsing into a `WifiCredentials` dataclass
- escaped semicolon and colon handling in SSIDs and passwords
- result display with copy-friendly output
- Linux `nmcli` command building and optional connection attempt
- parser and Linux command-builder tests

Windows support and a polished desktop GUI are planned later.

---

## Goals

WWC aims to be:

- lightweight
- offline-first
- privacy-friendly
- simple to use
- useful even without automatic connection
- Linux-first, with Windows support planned
- contributor-friendly
- understandable for learners and new contributors

---

## Non-Goals for Now

WWC is not trying to be:

- a cloud service
- a mobile app
- a web app
- a password manager
- a network monitoring tool
- a full Wi-Fi administration suite
- a PyPI-first Python library

The project should stay focused on one main job:

```text
Scan a Wi-Fi QR code and help the user connect from desktop.
```

---

## Roadmap

### Phase 1: Basic Scanner

- [x] Open webcam
- [x] Show camera preview
- [x] Detect QR code
- [x] Decode QR text
- [x] Handle closing the camera window safely

### Phase 2: Wi-Fi QR Parser

- [x] Parse standard Wi-Fi QR format
- [x] Extract SSID
- [x] Extract security type
- [x] Extract password
- [x] Handle open networks
- [x] Add parser tests

### Phase 3: Basic Result Display

- [x] Display SSID
- [x] Display security type
- [x] Display password
- [x] Add copy-friendly output
- [x] Add clear error messages for invalid QR codes

### Phase 4: Linux Auto-Connect

- [x] Detect whether `nmcli` is available
- [x] Connect using NetworkManager
- [x] Handle wrong password errors
- [x] Handle unavailable SSID errors
- [x] Show clear success/failure messages

### Phase 5: Desktop GUI

- [ ] Add proper desktop window
- [ ] Add scan button
- [ ] Add live preview
- [ ] Add password visibility toggle
- [ ] Add copy password button
- [ ] Add connect button
- [ ] Add status messages

### Phase 6: Windows Support

- [ ] Research `netsh wlan` workflow
- [ ] Create Windows connector
- [ ] Test Wi-Fi profile creation
- [ ] Test Windows connection flow
- [ ] Add Windows-specific error messages

### Phase 7: Installable Builds

- [ ] Create Linux executable
- [ ] Create AppImage or `.deb`
- [ ] Create Windows executable
- [ ] Create Windows installer
- [ ] Document installation steps

---

## Security and Privacy Notes

WWC reads Wi-Fi credentials from QR codes. These credentials may include plain-text Wi-Fi passwords.

For that reason:

- credentials should only be processed locally
- credentials should not be logged unnecessarily
- credentials should not be sent to any server
- password display should be intentional and visible to the user
- future GUI versions should include a password show/hide option

---

## License

No license file has been added yet.

---

## Author

Built as an independent open-source project by Bibek Adhikari.
