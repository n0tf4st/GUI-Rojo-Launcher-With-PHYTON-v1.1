# File: gui/parts/tabs/file_changes.py
# Function: Tab File Changes with search, filter, double-click, and export

import tkinter as tk
import os
from ..theme import Theme
from ..search import create as create_search, create_filters, create_export_buttons, highlight_text
from ..file_opener import open_file
from ..config import get_src_folder
from ..export import copy_to_clipboard, export_to_file, get_log_text


def create(parent):
    """Create log area with search and filter. Return container."""
    container = tk.Frame(parent, bg=Theme.BG_SECONDARY)

    # Current filter
    current_filter = {"value": "all"}

    # Search bar
    def on_search(text):
        if log:
            highlight_text(log, text)

    search = create_search(container, on_search)

    # Filter buttons
    filters = [("All", "all"), ("+ Added", "added"), ("~ Modified", "modified"),
               ("- Deleted", "deleted"), ("Error", "error")]

    def on_filter(value):
        current_filter["value"] = value
        _apply_filter(log, value)

    create_filters(search["filter_frame"], filters, on_filter)

    # Export buttons
    def on_copy():
        text = get_log_text(log)
        if text:
            copy_to_clipboard(parent.winfo_toplevel(), text)

    def on_export():
        text = get_log_text(log)
        if text:
            export_to_file(parent.winfo_toplevel(), text, "file_changes")

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
        ("added", Theme.SUCCESS), ("modified", Theme.INFO),
        ("deleted", Theme.ERROR), ("timestamp", Theme.TEXT_DIM),
        ("error", Theme.ERROR), ("hidden", Theme.BG_SECONDARY),
    ]:
        log.tag_configure(tag, foreground=color)

    # Double-click to open file
    def on_double_click(event):
        # Get line at click position
        index = log.index(f"@{event.x},{event.y}")
        line = log.get(f"{index} linestart", f"{index} lineend")
        # Extract file path from line (after icon)
        parts = line.split("  ")
        if len(parts) >= 3:
            rel_path = parts[2].strip()
            src = get_src_folder()
            if src:
                full_path = os.path.join(src, rel_path)
                if os.path.exists(full_path):
                    open_file(full_path)

    log.bind("<Double-1>", on_double_click)

    container.log_widget = log
    container.current_filter = current_filter
    return container


def _apply_filter(log_widget, filter_value):
    """Show/hide lines based on filter."""
    log_widget.configure(state="normal")

    # First show all
    for tag in ["added", "modified", "deleted", "timestamp"]:
        log_widget.tag_configure(tag, foreground=_get_color(tag))

    if filter_value == "all":
        log_widget.configure(state="disabled")
        return

    # Get all lines and their tags
    content = log_widget.get("1.0", "end-1c")
    lines = content.split("\n")

    for i, line in enumerate(lines):
        line_start = f"{i+1}.0"
        line_end = f"{i+1}.end"

        # Check if line matches filter
        match = False
        if filter_value == "added" and "+" in line:
            match = True
        elif filter_value == "modified" and "~" in line:
            match = True
        elif filter_value == "deleted" and "-" in line:
            match = True
        elif filter_value == "error" and ("error" in line.lower() or "fail" in line.lower()):
            match = True

        if not match and line.strip():
            # Dim non-matching lines
            log_widget.tag_add("hidden", line_start, line_end)

    log_widget.configure(state="disabled")


def _get_color(tag):
    """Get color for tag."""
    colors = {
        "added": Theme.SUCCESS,
        "modified": Theme.INFO,
        "deleted": Theme.ERROR,
        "timestamp": Theme.TEXT_DIM,
    }
    return colors.get(tag, Theme.TEXT)


def log_change(widget, timestamp, action, rel_path):
    """Add file change to log."""
    tag_map = {"ADDED": "added", "MODIFIED": "modified", "DELETED": "deleted"}
    icon_map = {"ADDED": "+", "MODIFIED": "~", "DELETED": "-"}
    tag = tag_map.get(action, "added")
    icon = icon_map.get(action, "?")

    widget.configure(state="normal")
    widget.insert("end", f"{timestamp}  ", "timestamp")
    widget.insert("end", f"{icon} ", tag)
    widget.insert("end", f"{rel_path}\n", tag)
    widget.see("end")
    widget.configure(state="disabled")


def clear(widget):
    """Clear log."""
    widget.configure(state="normal")
    widget.delete("1.0", "end")
    widget.configure(state="disabled")
