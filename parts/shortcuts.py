# File: gui/parts/shortcuts.py
# Function: Keyboard shortcuts for GUI
# How it works: Bind keyboard shortcuts to actions

SHORTCUTS = {
    "Ctrl+1": "Switch to Server Log",
    "Ctrl+2": "Switch to File Changes",
    "Ctrl+3": "Switch to Folder Projek",
    "Ctrl+4": "Switch to Logs",
    "Ctrl+L": "Clear active log",
    "Ctrl+S": "Start server",
    "Ctrl+Q": "Stop server",
    "Ctrl+,": "Open settings",
    "Escape": "Close popup / confirm",
    "F5": "Refresh",
}


def bind_shortcuts(root, actions):
    """Bind keyboard shortcuts. actions = dict of action_name -> callback."""
    # Tab switching
    root.bind_all("<Control-Key-1>", lambda e: actions.get("tab_server", lambda: None)())
    root.bind_all("<Control-Key-2>", lambda e: actions.get("tab_changes", lambda: None)())
    root.bind_all("<Control-Key-3>", lambda e: actions.get("tab_project", lambda: None)())
    root.bind_all("<Control-Key-4>", lambda e: actions.get("tab_logs", lambda: None)())

    # Clear log
    root.bind_all("<Control-l>", lambda e: actions.get("clear_log", lambda: None)())

    # Server control
    root.bind_all("<Control-s>", lambda e: actions.get("start_server", lambda: None)())
    root.bind_all("<Control-q>", lambda e: actions.get("stop_server", lambda: None)())

    # Settings
    root.bind_all("<Control-comma>", lambda e: actions.get("settings", lambda: None)())

    # Refresh
    root.bind_all("<F5>", lambda e: actions.get("refresh", lambda: None)())


def get_shortcuts_text():
    """Return formatted text of all shortcuts."""
    lines = []
    for key, desc in SHORTCUTS.items():
        lines.append(f"  {key:12} {desc}")
    return "\n".join(lines)
