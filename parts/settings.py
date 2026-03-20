# File: gui/parts/settings.py
# Function: Settings panel dialog
# How it works: Create popup dialog with settings for project path, editor, auto-restart, etc.

import tkinter as tk
from tkinter import filedialog
import os
from .theme import Theme
from .config import load_config, save_config, get_project_root, set_project_root


class SettingsPanel:
    """Settings dialog panel."""

    def __init__(self, root, on_save=None):
        self.root = root
        self.on_save = on_save
        self.popup = None
        self.vars = {}

    def show(self):
        """Show settings dialog."""
        if self.popup:
            self.popup.lift()
            return

        config = load_config()

        self.popup = tk.Toplevel(self.root)
        self.popup.title("Settings")
        self.popup.overrideredirect(True)
        self.popup.configure(bg=Theme.BORDER)
        self.popup.transient(self.root)
        self.popup.grab_set()

        # Size and position
        w, h = 400, 420
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
        self.popup.geometry(f"{w}x{h}+{x}+{y}")

        # Border
        border = tk.Frame(self.popup, bg=Theme.BORDER)
        border.pack(fill="both", expand=True, padx=1, pady=1)

        inner = tk.Frame(border, bg=Theme.BG_SECONDARY)
        inner.pack(fill="both", expand=True)

        # Title bar
        title_bar = tk.Frame(inner, bg=Theme.BG_TERTIARY, height=36)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        tk.Label(title_bar, text=" ⚙️ Settings", font=("Segoe UI", 11, "bold"),
                fg=Theme.TEXT, bg=Theme.BG_TERTIARY).pack(side="left", padx=12, pady=6)

        close_btn = tk.Label(title_bar, text="✕", font=("Segoe UI", 12),
                            fg=Theme.TEXT_DIM, bg=Theme.BG_TERTIARY, cursor="hand2", width=3)
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self.close())
        close_btn.bind("<Enter>", lambda e: close_btn.configure(fg=Theme.TEXT, bg=Theme.ACCENT_RED))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(fg=Theme.TEXT_DIM, bg=Theme.BG_TERTIARY))

        # Content
        content = tk.Frame(inner, bg=Theme.BG_SECONDARY)
        content.pack(fill="both", expand=True, padx=16, pady=12)

        # Project Path
        self._add_section(content, "Project", 0)
        self._add_path_field(content, "Project Path", "project_root",
                            config.get("project_root", ""), 1)

        # Editor
        self._add_section(content, "Editor", 3)
        self._add_path_field(content, "Default Editor", "editor",
                            config.get("editor", ""), 4)

        # Server
        self._add_section(content, "Server", 6)
        self._add_checkbox(content, "Auto-restart on crash", "auto_restart",
                          config.get("auto_restart", True), 7)
        self._add_spinbox(content, "Watcher interval (sec)", "watcher_interval",
                         config.get("watcher_interval", 1), 0.5, 10, 8)

        # Logs
        self._add_section(content, "Logs", 10)
        self._add_spinbox(content, "Max log files", "max_logs",
                         config.get("max_logs", 50), 10, 500, 11)

        # Buttons
        btn_frame = tk.Frame(inner, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))

        save_btn = tk.Label(btn_frame, text=" Save ", font=("Segoe UI", 10, "bold"),
                           fg=Theme.BG, bg=Theme.ACCENT_GREEN, cursor="hand2", padx=16, pady=4)
        save_btn.pack(side="right", padx=(8, 0))
        save_btn.bind("<Button-1>", lambda e: self._save())
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=Theme.ACCENT_GREEN_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=Theme.ACCENT_GREEN))

        cancel_btn = tk.Label(btn_frame, text=" Cancel ", font=("Segoe UI", 10),
                             fg=Theme.TEXT, bg=Theme.BG_TERTIARY, cursor="hand2", padx=12, pady=4)
        cancel_btn.pack(side="right")
        cancel_btn.bind("<Button-1>", lambda e: self.close())
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.configure(bg=Theme.BG_HOVER))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.configure(bg=Theme.BG_TERTIARY))

        # Focus
        self.popup.lift()
        self.popup.focus_force()

    def _add_section(self, parent, title, row):
        """Add section header."""
        frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(12, 2))
        tk.Label(frame, text=title, font=("Segoe UI", 9, "bold"),
                fg=Theme.ACCENT_BLUE, bg=Theme.BG_SECONDARY).pack(side="left")

    def _add_path_field(self, parent, label, key, default, row):
        """Add path field with browse button."""
        tk.Label(parent, text=label, font=("Segoe UI", 9),
                fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY, anchor="w").grid(
                    row=row, column=0, sticky="w", pady=(4, 0))

        frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
        frame.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(2, 0))

        var = tk.StringVar(value=default)
        self.vars[key] = var

        entry = tk.Entry(frame, textvariable=var, font=("Consolas", 8),
                        fg=Theme.TEXT, bg=Theme.BG_TERTIARY, insertbackground=Theme.TEXT,
                        relief="flat", bd=0)
        entry.pack(side="left", fill="x", expand=True, ipady=2)

        browse_btn = tk.Label(frame, text=" Browse ", font=("Segoe UI", 8),
                             fg=Theme.TEXT_DIM, bg=Theme.BG_TERTIARY, cursor="hand2")
        browse_btn.pack(side="right", padx=(4, 0))

        def do_browse():
            if key == "editor":
                path = filedialog.askopenfilename(title="Select Editor",
                    filetypes=[("Executables", "*.exe"), ("All files", "*.*")])
            else:
                path = filedialog.askdirectory(title="Select Project Folder")
            if path:
                var.set(path)

        browse_btn.bind("<Button-1>", lambda e: do_browse())

    def _add_checkbox(self, parent, label, key, default, row):
        """Add checkbox field."""
        var = tk.BooleanVar(value=default)
        self.vars[key] = var

        cb = tk.Checkbutton(parent, text=label, variable=var,
                           font=("Segoe UI", 9), fg=Theme.TEXT,
                           bg=Theme.BG_SECONDARY, selectcolor=Theme.BG_TERTIARY,
                           activebackground=Theme.BG_SECONDARY,
                           activeforeground=Theme.TEXT)
        cb.grid(row=row, column=0, columnspan=2, sticky="w", pady=(4, 0))

    def _add_spinbox(self, parent, label, key, default, min_val, max_val, row):
        """Add number field."""
        tk.Label(parent, text=label, font=("Segoe UI", 9),
                fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY, anchor="w").grid(
                    row=row, column=0, sticky="w", pady=(4, 0))

        var = tk.DoubleVar(value=default)
        self.vars[key] = var

        spin = tk.Spinbox(parent, from_=min_val, to=max_val, textvariable=var,
                         font=("Consolas", 9), width=10,
                         fg=Theme.TEXT, bg=Theme.BG_TERTIARY,
                         buttonbackground=Theme.BG_HOVER,
                         relief="flat", bd=0)
        spin.grid(row=row, column=1, sticky="e", pady=(4, 0))

    def _save(self):
        """Save settings."""
        config = load_config()

        for key, var in self.vars.items():
            if isinstance(var, tk.BooleanVar):
                config[key] = var.get()
            elif isinstance(var, tk.DoubleVar):
                config[key] = var.get()
            else:
                config[key] = var.get()

        save_config(config)

        # Update project root if changed
        new_root = config.get("project_root", "")
        if new_root and os.path.isdir(new_root):
            set_project_root(new_root)

        if self.on_save:
            self.on_save(config)

        self.close()

    def close(self):
        """Close settings dialog."""
        if self.popup:
            self.popup.grab_release()
            self.popup.destroy()
            self.popup = None
