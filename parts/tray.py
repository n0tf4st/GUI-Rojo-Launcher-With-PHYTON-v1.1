# File: gui/parts/tray.py
# Function: Minimize to system tray (basic implementation)
# How it works: Hide window on minimize, show popup menu to restore/quit
# Note: Full system tray requires 'pystray' package. This is a basic fallback.

import tkinter as tk
from .theme import Theme


class TrayManager:
    """Basic minimize-to-tray manager."""

    def __init__(self, root, on_restore=None, on_quit=None):
        self.root = root
        self.on_restore = on_restore
        self.on_quit = on_quit
        self.is_minimized = False
        self.menu = None

    def minimize(self):
        """Hide window (minimize to tray)."""
        self.root.withdraw()
        self.is_minimized = True

    def restore(self):
        """Restore window from tray."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.is_minimized = False
        if self.on_restore:
            self.on_restore()

    def show_menu(self, x, y):
        """Show right-click menu at position."""
        if self.menu:
            self.menu.destroy()

        self.menu = tk.Menu(self.root, tearoff=0,
                           bg=Theme.BG_SECONDARY, fg=Theme.TEXT,
                           activebackground=Theme.BG_HOVER,
                           activeforeground=Theme.TEXT,
                           relief="flat", bd=1)

        self.menu.add_command(label="  Restore", command=self.restore)
        self.menu.add_separator()
        self.menu.add_command(label="  Quit", command=self._quit)

        try:
            self.menu.tk_popup(x, y)
        finally:
            self.menu.grab_release()

    def _quit(self):
        """Quit application."""
        if self.menu:
            self.menu.destroy()
        if self.on_quit:
            self.on_quit()

    def bind_minimize(self, button_widget):
        """Bind a button to minimize action."""
        button_widget.bind("<Button-1>", lambda e: self.minimize())
