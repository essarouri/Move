# 🐭 Move

**Move** is a lightweight Windows system tray utility that prevents your computer from sleeping using the native Windows API.

Unlike many alternatives, Move **does not move your mouse** or simulate keyboard input.

Instead, it uses `SetThreadExecutionState()`, the official Windows API for keeping the system awake.

## Features

* Prevents Windows from sleeping
* Prevents the display from turning off
* System tray application
* One-click enable/disable
* Timer modes (15 min – 8 hours)
* Unlimited mode
* Automatic activation on startup
* Tiny memory footprint
* No ads
* No telemetry
* No fake mouse movement

## Perfect For

* Remote Desktop
* Downloads
* Uploads
* Presentations
* Video rendering
* Development
* Automation
* Long-running scripts

## How It Works

Move periodically informs Windows that the system is still in use through the Windows `SetThreadExecutionState()` API.

Because it communicates directly with Windows, your cursor stays exactly where you left it.

## Requirements

* Windows 10
* Windows 11
* Python 3.10+ (or standalone executable)

## Technologies

* Python
* pystray
* Pillow
* ctypes

## License

Free to use.

## Author

Developed by Mohamed Essarouri.
