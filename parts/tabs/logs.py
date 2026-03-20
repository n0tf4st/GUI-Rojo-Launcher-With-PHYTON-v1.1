# File: gui/parts/tabs/logs.py
# Function: Tab Logs to display log file list and delete

import tkinter as tk
import os
from ..theme import Theme


def create(parent):
    """Create log file list with delete button. Return (listbox, delete_btn)."""
    top_bar = tk.Frame(parent, bg=Theme.BG_SECONDARY, height=32)
    top_bar.pack(fill="x", padx=8, pady=(6, 0))
    top_bar.pack_propagate(False)

    tk.Label(top_bar, text="gui/logs/", font=("Consolas", 9),
            fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY).pack(side="left", pady=4)

    list_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
    list_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))

    logs_list = tk.Listbox(
        list_frame, font=("Consolas", 9), fg=Theme.TEXT,
        bg=Theme.BG_SECONDARY, selectbackground=Theme.BG_HOVER,
        selectforeground=Theme.TEXT, relief="flat", bd=0,
        highlightthickness=0, activestyle="none",
    )
    logs_list.pack(side="left", fill="both", expand=True)

    delete_btn = tk.Label(
        top_bar, text=" 🗑 Delete All", font=("Segoe UI", 9),
        fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY, cursor="hand2",
    )
    delete_btn.pack(side="right", pady=4)

    delete_btn.bind("<Enter>", lambda e: delete_btn.configure(fg=Theme.ERROR))
    delete_btn.bind("<Leave>", lambda e: delete_btn.configure(fg=Theme.TEXT_DIM))

    refresh(logs_list)
    logs_list.bind("<Delete>", lambda e: delete_selected(logs_list))

    return logs_list, delete_btn


def _get_logs_dir():
    """Return path to logs folder."""
    parts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gui_dir = os.path.dirname(parts_dir)
    return os.path.join(gui_dir, "logs")


def refresh(logs_list):
    """Refresh log file list."""
    logs_list.delete(0, tk.END)
    logs_dir = _get_logs_dir()

    try:
        files = sorted(os.listdir(logs_dir), reverse=True)
    except OSError:
        return

    for f in files:
        if f.endswith(".log"):
            full_path = os.path.join(logs_dir, f)
            try:
                size = os.path.getsize(full_path)
                size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
            except OSError:
                size_str = "? B"
            logs_list.insert(tk.END, f"  {f}  ({size_str})")


def delete_selected(logs_list):
    """Delete selected log file."""
    sel = logs_list.curselection()
    if not sel:
        return

    idx = sel[0]
    text = logs_list.get(idx)
    filename = text.strip().split("  (")[0].strip()

    full_path = os.path.join(_get_logs_dir(), filename)
    try:
        os.remove(full_path)
        logs_list.delete(idx)
    except OSError as e:
        print(f"Failed to delete {filename}: {e}")


def delete_all(logs_list):
    """Delete all log files."""
    logs_dir = _get_logs_dir()
    try:
        files = os.listdir(logs_dir)
    except OSError:
        return

    for f in files:
        if f.endswith(".log"):
            try:
                os.remove(os.path.join(logs_dir, f))
            except OSError:
                pass
    logs_list.delete(0, tk.END)
