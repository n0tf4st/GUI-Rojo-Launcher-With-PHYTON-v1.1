# File: gui/parts/tabs/server_log.py
# Function: Tab Server Log with search and export

import tkinter as tk
from ..theme import Theme
from ..search import create as create_search, create_export_buttons, highlight_text
from ..export import copy_to_clipboard, export_to_file, get_log_text


def create(parent):
    """Create log area with search and export. Return container."""
    container = tk.Frame(parent, bg=Theme.BG_SECONDARY)

    # Search bar
    def on_search(text):
        if log:
            highlight_text(log, text)

    search = create_search(container, on_search)

    # Export buttons
    def on_copy():
        text = get_log_text(log)
        if text:
            copy_to_clipboard(parent.winfo_toplevel(), text)

    def on_export():
        text = get_log_text(log)
        if text:
            export_to_file(parent.winfo_toplevel(), text, "server_log")

    create_export_buttons(search["export_frame"], on_copy, on_export)

    # Log area
    log = tk.Text(
        container, font=("Cascadia Code", 9), fg=Theme.TEXT,
        bg=Theme.BG_SECONDARY, insertbackground=Theme.TEXT,
        relief="flat", wrap="word", state="disabled", bd=0,
        padx=10, pady=6, selectbackground=Theme.BG_HOVER,
    )
    log.pack(fill="both", expand=True)

    for tag, color in [
        ("info", Theme.INFO), ("success", Theme.SUCCESS),
        ("error", Theme.ERROR), ("warn", Theme.WARNING),
        ("default", Theme.TEXT),
    ]:
        log.tag_configure(tag, foreground=color)

    container.log_widget = log
    return container


def log_msg(widget, text, tag="default"):
    """Add message to log."""
    widget.configure(state="normal")
    widget.insert("end", text + "\n", tag)
    widget.see("end")
    widget.configure(state="disabled")


def clear(widget):
    """Clear log."""
    widget.configure(state="normal")
    widget.delete("1.0", "end")
    widget.configure(state="disabled")
