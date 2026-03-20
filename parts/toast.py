# File: gui/parts/toast.py
# Function: Toast notification popup
# How it works: Show small popup in bottom-right corner that auto-dismisses

import tkinter as tk
from .theme import Theme


class Toast:
    """Toast notification that appears and auto-dismisses."""

    def __init__(self, root):
        self.root = root
        self.popup = None
        self.dismiss_id = None

    def show(self, message, duration=3000, icon="ℹ️", on_click=None):
        """Show toast notification. duration in ms."""
        # Dismiss existing
        self.dismiss()

        # Create popup
        self.popup = tk.Toplevel(self.root)
        self.popup.overrideredirect(True)
        self.popup.attributes("-topmost", True)
        self.popup.configure(bg=Theme.BORDER)

        # Inner frame
        inner = tk.Frame(self.popup, bg=Theme.BG_SECONDARY)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        # Content
        content = tk.Frame(inner, bg=Theme.BG_SECONDARY)
        content.pack(fill="both", expand=True, padx=12, pady=8)

        # Icon + message
        tk.Label(content, text=f"{icon} ", font=("Segoe UI", 10),
                fg=Theme.TEXT, bg=Theme.BG_SECONDARY).pack(side="left")
        msg_label = tk.Label(content, text=message, font=("Segoe UI", 9),
                            fg=Theme.TEXT, bg=Theme.BG_SECONDARY, wraplength=250)
        msg_label.pack(side="left", padx=(0, 8))

        # Close button
        close_btn = tk.Label(content, text="✕", font=("Segoe UI", 9),
                            fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY, cursor="hand2")
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self.dismiss())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(fg=Theme.TEXT))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(fg=Theme.TEXT_DIM))

        # Click handler
        if on_click:
            inner.bind("<Button-1>", lambda e: (self.dismiss(), on_click()))
            msg_label.bind("<Button-1>", lambda e: (self.dismiss(), on_click()))
            content.bind("<Button-1>", lambda e: (self.dismiss(), on_click()))

        # Position bottom-right
        self.popup.update_idletasks()
        w = self.popup.winfo_width()
        h = self.popup.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = sw - w - 20
        y = sh - h - 60
        self.popup.geometry(f"+{x}+{y}")

        # Auto dismiss
        self.dismiss_id = self.popup.after(duration, self.dismiss)

    def dismiss(self):
        """Dismiss toast."""
        if self.dismiss_id:
            try:
                self.popup.after_cancel(self.dismiss_id)
            except:
                pass
            self.dismiss_id = None

        if self.popup:
            try:
                self.popup.destroy()
            except:
                pass
            self.popup = None
