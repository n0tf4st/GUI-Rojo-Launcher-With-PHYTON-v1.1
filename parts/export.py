# File: gui/parts/export.py
# Function: Export log to clipboard or file
# How it works: Copy log content to clipboard or save to file

import tkinter as tk
from tkinter import filedialog
import os
from datetime import datetime


def copy_to_clipboard(root, text):
    """Copy text to clipboard."""
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()


def export_to_file(root, text, default_name="log"):
    """Export text to file. Return True if saved."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = filedialog.asksaveasfilename(
        title="Export Log",
        defaultextension=".txt",
        initialfile=f"{default_name}_{ts}.txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    if filename:
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)
            return True
        except IOError:
            return False
    return False


def get_log_text(widget):
    """Get all text from a text widget."""
    return widget.get("1.0", "end-1c")
