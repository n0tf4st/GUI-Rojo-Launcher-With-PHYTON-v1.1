# Rojo GUI Launcher

> **v1.1** | A GUI launcher for [Rojo](https://github.com/rojo-rbx/rojo) server with file watcher and monitoring features.

## Features

### Core
- **Start/Stop Server** - Run and stop `rojo serve` with one click
- **File Watcher** - Detect file changes in `src/` in real-time
- **Log to File** - Save all logs to `gui/logs/` folder (ANSI codes stripped)
- **4 Tab Panels:**
  - Server Log - Rojo server output
  - File Changes - List of changed files with filter
  - Folder Projek - Tree view of `src/` structure with file info & preview
  - Logs - Manage log files (delete)

### New in v1.1
- **Search/Filter** - Search bar with filter buttons in logs
- **Double-click to Open** - Open files in default editor
- **File Preview** - Preview file content in Folder Projek tab
- **Toast Notification** - Popup when files change
- **Auto-restart** - Auto restart server on crash (max 3 retries)
- **Settings Panel** - Configure project path, editor, auto-restart, etc.
- **Log Rotation** - Auto delete old logs (max 50 files)
- **Export Log** - Copy to clipboard or save to file
- **Keyboard Shortcuts** - Ctrl+1/2/3/4, Ctrl+S/Q/L, F5
- **System Tray** - Minimize to tray with restore/quit menu
- **Multi-project** - Switch between projects with dropdown

### UI
- **Custom UI** - Dark theme, borderless, resizable, draggable
- **Taskbar Entry** - Appears in Windows taskbar
- **Close Confirmation** - Popup when closing while server is running
- **Error Handling** - Better handling of edge cases

## Requirements

- Python 3.8+ (with tkinter, included by default)
- [Rojo](https://github.com/rojo-rbx/rojo) installed and in PATH

> **Tip:** If you installed Python in a custom location, make sure "Add Python to PATH" was checked during install, or use the `py` command.

## Installation

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO/gui

# 2. Make sure Rojo is installed
rojo --version
```

## Usage

### GUI (Recommended)
```bash
# Choose one
py rojo_gui.py                    # Python Launcher
python rojo_gui.py                # From PATH
run.bat                           # Double-click (console auto-close)
```

### Command Line (Alternative)
```bash
# PowerShell
.\serve.ps1

# Or directly
rojo serve
```

> **Tip:** `run.bat` and `serve.ps1` automatically detect the project name from the current folder.

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| Ctrl+1 | Switch to Server Log |
| Ctrl+2 | Switch to File Changes |
| Ctrl+3 | Switch to Folder Projek |
| Ctrl+4 | Switch to Logs |
| Ctrl+L | Clear active log |
| Ctrl+S | Start server |
| Ctrl+Q | Stop server |
| Ctrl+, | Open settings |
| F5 | Refresh |

### Features Guide
1. **Search/Filter** - Use search bar to find logs, filter by type
2. **Double-click** - Click file in tree or changes list to open in editor
3. **Preview** - Click file to see preview in right panel
4. **Toast** - Notifications appear when files change
5. **Settings** - Click ⚙️ to configure project, editor, etc.
6. **Export** - Click 📋 to copy, 💾 to save log to file
7. **Multi-project** - Click project name to switch projects

## Project Structure
```
gui/
├── parts/
│   ├── __init__.py
│   ├── config.py           # Auto-detect project path, recent projects
│   ├── theme.py            # Color theme (GitHub Dark)
│   ├── widgets.py          # HoverButton, StatusDot
│   ├── title_bar.py        # Title bar, drag, resize
│   ├── log_panel.py        # Main panel (4 tabs)
│   ├── server.py           # Server controller with auto-restart
│   ├── file_watcher.py     # Monitor file changes
│   ├── search.py           # Search/filter bar
│   ├── file_opener.py      # Open file in editor
│   ├── preview.py          # File preview
│   ├── toast.py            # Toast notification
│   ├── settings.py         # Settings dialog
│   ├── log_rotation.py     # Auto-delete old logs
│   ├── export.py           # Copy/export log
│   ├── shortcuts.py        # Keyboard shortcuts
│   ├── tray.py             # System tray manager
│   └── tabs/
│       ├── __init__.py
│       ├── server_log.py   # Server Log tab
│       ├── file_changes.py # File Changes tab
│       ├── folder_projek.py# Folder Projek tab
│       └── logs.py         # Logs tab
├── config.json             # Project settings (auto-generated)
├── logs/                   # Log auto-generated
├── rojo_gui.py             # GUI entry point
├── run.bat                 # Launcher (console auto-close)
├── serve.ps1               # Command line launcher
├── README.md               # Documentation (English)
└── README_ID.md            # Documentation (Indonesian)
```

## Technical

| Component | Technology |
|-----------|------------|
| GUI | tkinter |
| Server | subprocess |
| Threading | threading |
| File Watch | os.stat (1 second interval) |
| Taskbar | ctypes (Windows API) |
| Config | JSON |

## Changelog

### v1.1
- Added search/filter in logs
- Added double-click to open files
- Added file preview
- Added toast notifications
- Added auto-restart on crash
- Added settings panel
- Added log rotation
- Added export log (copy/save)
- Added keyboard shortcuts
- Added system tray support
- Added multi-project support
- Fixed ANSI codes in log files
- Fixed thread safety issues
- Fixed hardcoded project name

### v1.0
- Initial release
- Basic Rojo server launcher
- File watcher
- 4 tab panels
- Dark theme UI

## License

MIT
