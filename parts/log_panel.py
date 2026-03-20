# File: gui/parts/log_panel.py
# Function: Main panel with 4 tabs (Server Log, File Changes, Folder Projek, Logs)
# How it works: Import tab modules from tabs folder, assemble into one panel with tab system.

import tkinter as tk
from .theme import Theme
from .tabs import server_log, file_changes, folder_projek, logs


def create_log_panel(parent):
    """Buat panel log dengan tabs. Return dict refs."""
    refs = {}

    # === Tab Bar ===
    tab_bar = tk.Frame(parent, bg=Theme.BG)
    tab_bar.pack(fill="x")

    active_tab = tk.StringVar(value="server")
    refs["active_tab"] = active_tab

    tab_defs = [
        ("server", "Server Log"),
        ("changes", "File Changes"),
        ("project", "Folder Projek"),
        ("logs", "Logs"),
    ]
    tab_widgets = {}

    for key, label in tab_defs:
        is_active = key == "server"
        w = tk.Label(tab_bar, text=label, font=("Segoe UI", 9),
                     fg=Theme.TEXT if is_active else Theme.TEXT_DIM,
                     bg=Theme.BG, cursor="hand2", padx=10, pady=4)
        w.pack(side="left")
        tab_widgets[key] = w

    tab_indicator = tk.Frame(tab_bar, bg=Theme.ACCENT_BLUE, height=2)
    refs["tab_indicator"] = tab_indicator

    # Separator
    tk.Frame(parent, bg=Theme.BORDER, height=1).pack(fill="x")

    # === Content Container ===
    container = tk.Frame(parent, bg=Theme.BG_SECONDARY)
    container.pack(fill="both", expand=True)

    # === Create Tab Panels ===
    # Server Log
    server_container = server_log.create(container)
    server_container.pack(fill="both", expand=True)
    refs["server_log"] = server_container.log_widget

    # File Changes
    changes_container = file_changes.create(container)
    changes_container.pack_forget()
    refs["changes_log"] = changes_container.log_widget

    # Folder Projek
    project_frame = tk.Frame(container, bg=Theme.BG_SECONDARY)
    project_tree, _ = folder_projek.create(project_frame)
    project_frame.pack_forget()
    refs["project_frame"] = project_frame
    refs["project_tree"] = project_tree

    # Logs
    logs_frame = tk.Frame(container, bg=Theme.BG_SECONDARY)
    logs_list, delete_btn = logs.create(logs_frame)
    logs_frame.pack_forget()
    refs["logs_frame"] = logs_frame
    refs["logs_list"] = logs_list
    refs["delete_btn"] = delete_btn

    # === Tab Switch Logic ===
    panels = {
        "server": server_container,
        "changes": changes_container,
        "project": project_frame,
        "logs": logs_frame,
    }

    def position_indicator():
        tab = tab_widgets.get(active_tab.get(), tab_widgets["server"])
        x = tab.winfo_x()
        w = tab.winfo_width()
        y = tab.winfo_y() + tab.winfo_height()
        tab_indicator.place(x=x, y=y, width=w)

    def switch_tab(name):
        active_tab.set(name)
        for key, lbl in tab_widgets.items():
            lbl.configure(fg=Theme.TEXT if key == name else Theme.TEXT_DIM)
        for key, panel in panels.items():
            panel.pack_forget() if key != name else panel.pack(fill="both", expand=True)
        if name == "logs":
            logs.refresh(logs_list)
        position_indicator()

    for key in tab_widgets:
        tab_widgets[key].bind("<Button-1>", lambda e, k=key: switch_tab(k))

    refs["switch_tab"] = switch_tab
    refs["position_indicator"] = position_indicator

    return refs


# === Forward functions for convenience ===
def log_msg(widget, text, tag="default"):
    server_log.log_msg(widget, text, tag)


def clear_log(widget):
    server_log.clear(widget)


def log_change(widget, timestamp, action, rel_path):
    file_changes.log_change(widget, timestamp, action, rel_path)


def delete_all_logs(logs_list):
    logs.delete_all(logs_list)
