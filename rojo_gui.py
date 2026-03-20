# File: gui/rojo_gui.py
# Function: Main entry point for Rojo Launcher GUI
# How it works: Import separate modules (theme, widgets, title_bar, log_panel, server)
# then assemble into one application.

import tkinter as tk
import os
import sys
import re
import ctypes
import logging
from datetime import datetime

# Sembunyikan console & set app name di taskbar
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("RojoLauncher")
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)
except Exception:
    pass

# Import modul lokal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parts.theme import Theme
from parts.widgets import StatusDot, HoverButton
from parts.title_bar import create_title_bar, setup_resize
from parts.log_panel import create_log_panel, log_msg, clear_log, log_change, delete_all_logs
from parts.server import ServerController
from parts.file_watcher import FileWatcher
from parts.config import get_project_root, get_src_folder, load_config
from parts.toast import Toast
from parts.settings import SettingsPanel
from parts.log_rotation import cleanup_if_needed
from parts.shortcuts import bind_shortcuts
from parts.tray import TrayManager


def strip_ansi(text):
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


class RojoLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Rojo Launcher")
        self.root.minsize(520, 360)
        self.root.configure(bg=Theme.BG)
        # Jangan pakai overrideredirect - bikin taskbar hilang

        # Center window
        w, h = 640, 460
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        self.change_count = 0
        self.file_watcher = None
        self.server = ServerController()
        self.toast = Toast(root)
        self.tray = TrayManager(root, on_restore=self._on_tray_restore, on_quit=self._on_tray_quit)

        self._setup_logger()
        self._build_ui()

        # Setelah window muncul, sembunyikan title bar Windows
        self.root.after(100, self._hide_titlebar)

        # Right-click on window to show tray menu (when minimized)
        self.root.bind("<Button-3>", lambda e: self.tray.show_menu(e.x_root, e.y_root))

    def _setup_logger(self):
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)

        # Auto cleanup old logs (max 50)
        config = load_config()
        max_logs = int(config.get("max_logs", 50))
        cleanup_if_needed(max_logs)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(log_dir, f"rojo_{ts}.log")
        self.file_logger = logging.getLogger("RojoGUI")
        self.file_logger.setLevel(logging.DEBUG)
        h = logging.FileHandler(self.log_file_path, encoding="utf-8")
        h.setFormatter(logging.Formatter("%(asctime)s | %(message)s", datefmt="%H:%M:%S"))
        self.file_logger.addHandler(h)

    def _hide_titlebar(self):
        """Sembunyikan title bar Windows tapi tetap pertahankan taskbar entry."""
        try:
            import ctypes
            user32 = ctypes.windll.user32

            self.root.update()
            self.root.update_idletasks()

            # Dapatkan window handle
            hwnd = user32.GetParent(self.root.winfo_id())

            # Constants
            GWL_STYLE = -16
            WS_CAPTION = 0x00C00000
            WS_THICKFRAME = 0x00040000
            WS_MINIMIZEBOX = 0x00020000
            WS_MAXIMIZEBOX = 0x00010000

            # Hapus caption (title bar) tapi pertahankan window
            style = user32.GetWindowLongW(hwnd, GWL_STYLE)
            style = style & ~WS_CAPTION & ~WS_THICKFRAME & ~WS_MINIMIZEBOX & ~WS_MAXIMIZEBOX
            user32.SetWindowLongW(hwnd, GWL_STYLE, style)

            # Update window
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOZORDER = 0x0004
            SWP_FRAMECHANGED = 0x0020
            user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                               SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)

            # Pastikan muncul di taskbar
            self.root.lift()
            self.root.focus_force()
        except Exception as e:
            print(f"Hide titlebar error: {e}")

    def _build_ui(self):
        # Title bar
        def on_minimize():
            self.tray.minimize()

        def on_close():
            if self.server.is_running:
                self._show_confirm_close()
            else:
                self.root.destroy()

        create_title_bar(self.root, on_minimize, on_close)
        setup_resize(self.root)

        # Separator
        tk.Frame(self.root, bg=Theme.BORDER, height=1).pack(fill="x")

        # Content
        content = tk.Frame(self.root, bg=Theme.BG)
        content.pack(fill="both", expand=True)

        # Header
        header = tk.Frame(content, bg=Theme.BG, height=46)
        header.pack(fill="x", padx=16, pady=(10, 0))
        header.pack_propagate(False)

        left_h = tk.Frame(header, bg=Theme.BG)
        left_h.pack(side="left", fill="y")

        self.status_dot = StatusDot(left_h)
        self.status_dot.pack(side="left", pady=6)

        sf = tk.Frame(left_h, bg=Theme.BG)
        sf.pack(side="left", padx=(8, 0))

        # Project name (clickable for dropdown)
        project_root = get_project_root()
        project_name = os.path.basename(project_root) if project_root else "No Project"

        self.project_label = tk.Label(sf, text=f"{project_name} ▾", font=("Segoe UI", 13, "bold"),
                fg=Theme.TEXT, bg=Theme.BG, cursor="hand2")
        self.project_label.pack(anchor="w")
        self.project_label.bind("<Button-1>", lambda e: self._show_project_menu(e.x_root, e.y_root))
        self.project_label.bind("<Enter>", lambda e: self.project_label.configure(fg=Theme.ACCENT_BLUE))
        self.project_label.bind("<Leave>", lambda e: self.project_label.configure(fg=Theme.TEXT))
        self.status_var = tk.StringVar(value="Server Stopped")
        self.status_label = tk.Label(sf, textvariable=self.status_var,
                                     font=("Segoe UI", 9), fg=Theme.TEXT_DIM, bg=Theme.BG)
        self.status_label.pack(anchor="w")

        self.counter_var = tk.StringVar(value="0 changes · 0 files")
        tk.Label(header, textvariable=self.counter_var, font=("Segoe UI", 9),
                fg=Theme.TEXT_DIM, bg=Theme.BG).pack(side="right", anchor="e", pady=10)

        # Settings button
        self.settings_panel = SettingsPanel(self.root, self._on_settings_save)
        settings_btn = tk.Label(header, text=" ⚙️", font=("Segoe UI", 11),
                               fg=Theme.TEXT_DIM, bg=Theme.BG, cursor="hand2")
        settings_btn.pack(side="right", padx=(0, 8), pady=10)
        settings_btn.bind("<Button-1>", lambda e: self.settings_panel.show())
        settings_btn.bind("<Enter>", lambda e: settings_btn.configure(fg=Theme.TEXT))
        settings_btn.bind("<Leave>", lambda e: settings_btn.configure(fg=Theme.TEXT_DIM))

        # Buttons
        btn_bar = tk.Frame(content, bg=Theme.BG)
        btn_bar.pack(fill="x", padx=16, pady=10)

        self.start_btn = HoverButton(btn_bar, "▶  Start", Theme.ACCENT_GREEN,
                                     Theme.BG, Theme.ACCENT_GREEN_HOVER,
                                     command=self._start_server, width=90, height=30)
        self.start_btn.pack(side="left", padx=(0, 4))

        self.stop_btn = HoverButton(btn_bar, "■  Stop", Theme.ACCENT_RED,
                                    Theme.BG, Theme.ACCENT_RED_HOVER,
                                    command=self._stop_server, width=90, height=30)
        self.stop_btn.pack(side="left", padx=(0, 4))
        self.stop_btn.set_enabled(False)

        HoverButton(btn_bar, "Clear", Theme.BG_TERTIARY,
                    Theme.TEXT_DIM, Theme.BG_HOVER,
                    command=self._clear_active_log, width=60, height=30).pack(side="right")

        # Log panel
        self.log_refs = create_log_panel(content)

        # Bind delete all logs button
        self.log_refs["delete_btn"].bind("<Button-1>",
            lambda e: delete_all_logs(self.log_refs["logs_list"]))

        # Callbacks
        self.server.set_callbacks(self._on_output, self._on_server_end, self._on_server_crash)

        # Enable auto-restart by default
        self.server.set_auto_restart(True)

        # Keyboard shortcuts
        actions = {
            "tab_server": lambda: self.log_refs["switch_tab"]("server"),
            "tab_changes": lambda: self.log_refs["switch_tab"]("changes"),
            "tab_project": lambda: self.log_refs["switch_tab"]("project"),
            "tab_logs": lambda: self.log_refs["switch_tab"]("logs"),
            "clear_log": self._clear_active_log,
            "start_server": self._start_server,
            "stop_server": self._stop_server,
            "settings": lambda: self.settings_panel.show(),
        }
        bind_shortcuts(self.root, actions)

        # Footer
        footer = tk.Frame(content, bg=Theme.BG, height=18)
        footer.pack(fill="x", padx=16, pady=(0, 6))
        footer.pack_propagate(False)
        tk.Label(footer, text=f"Log → {os.path.basename(self.log_file_path)}",
                font=("Consolas", 7), fg=Theme.TEXT_DIM, bg=Theme.BG).pack(side="left", pady=1)

        self.root.after(1, self.log_refs["position_indicator"])

    # ---- Server handlers ----
    def _set_status(self, running):
        self.status_dot.set_status(running)
        self.start_btn.set_enabled(not running)
        self.stop_btn.set_enabled(running)
        if running:
            self.status_var.set("Server Running")
            self.status_label.configure(fg=Theme.SUCCESS)
        else:
            self.status_var.set("Server Stopped")
            self.status_label.configure(fg=Theme.TEXT_DIM)

    def _start_server(self):
        if self.server.is_running:
            return

        clear_log(self.log_refs["server_log"])
        log_msg(self.log_refs["server_log"], "Starting server...", "info")
        self._set_status(True)

        project_root = get_project_root()
        if not project_root:
            log_msg(self.log_refs["server_log"], "ERROR: Project root not found!", "error")
            log_msg(self.log_refs["server_log"], "Click ⚙️ in Folder Projek tab to set path.", "warn")
            self._set_status(False)
            return

        log_msg(self.log_refs["server_log"], f"Project: {os.path.basename(project_root)}", "info")
        log_msg(self.log_refs["server_log"], "Open Roblox Studio → Plugin Rojo → Connect", "warn")
        log_msg(self.log_refs["server_log"], "", "default")

        # File watcher
        src_folder = get_src_folder()
        if src_folder:
            self.file_watcher = FileWatcher(src_folder, self._on_file_change)
            self.file_watcher.start()
            fc = self.file_watcher.get_file_count()
            log_msg(self.log_refs["server_log"], f"Watching {fc} files in src/", "info")
            log_msg(self.log_refs["server_log"], "", "default")

        ok, err = self.server.start(project_root)
        if not ok:
            log_msg(self.log_refs["server_log"], f"ERROR: {err}", "error")
            self._set_status(False)
            if self.file_watcher:
                self.file_watcher.stop()

    def _stop_server(self):
        if self.server.is_running:
            log_msg(self.log_refs["server_log"], "Stopping server...", "error")
            self.server.stop()

    def _on_output(self, text, tag):
        self.root.after(0, lambda: log_msg(self.log_refs["server_log"], text, tag))
        # Strip ANSI codes before saving to log file
        clean_text = strip_ansi(text)
        self.file_logger.info(clean_text)

    def _on_server_end(self):
        self.root.after(0, self._set_status, False)
        if self.file_watcher:
            self.file_watcher.stop()
            self.file_watcher = None
        self.root.after(0, lambda: log_msg(self.log_refs["server_log"], "", "default"))
        self.root.after(0, lambda: log_msg(self.log_refs["server_log"], "Server stopped.", "warn"))

    def _on_server_crash(self, retry_count, max_retries):
        """Handle server crash - auto-restart."""
        def do_restart():
            log_msg(self.log_refs["server_log"], "", "default")
            log_msg(self.log_refs["server_log"],
                   f"Server crashed! Restarting ({retry_count}/{max_retries})...", "error")

            self.toast.show(
                f"Server crashed! Restarting ({retry_count}/{max_retries})...",
                duration=3000,
                icon="🔄",
            )

            ok, err = self.server.try_restart()
            if ok:
                log_msg(self.log_refs["server_log"], "Server restarted.", "success")
                self._set_status(True)
            else:
                log_msg(self.log_refs["server_log"], f"Restart failed: {err}", "error")
                self._set_status(False)

        self.root.after(2000, do_restart)  # Wait 2 seconds before restart

    def _on_file_change(self, timestamp, action, rel_path):
        """Handle file change - called from file_watcher thread."""
        icon_map = {"ADDED": "+", "MODIFIED": "~", "DELETED": "-"}
        toast_icon = {"ADDED": "📄+", "MODIFIED": "📝", "DELETED": "🗑️"}
        icon = icon_map.get(action, "?")

        # All Tkinter operations must be in main thread
        def update_ui():
            log_change(self.log_refs["changes_log"], timestamp, action, rel_path)

            self.change_count += 1
            fc = self.file_watcher.get_file_count() if self.file_watcher else 0
            self.counter_var.set(f"{self.change_count} changes · {fc} files")

            # Show toast notification
            action_text = action.lower()
            toast_ic = toast_icon.get(action, "📄")
            self.toast.show(
                f"{rel_path} {action_text}",
                duration=3000,
                icon=toast_ic,
                on_click=lambda: self.log_refs["switch_tab"]("changes"),
            )

        self.root.after(0, update_ui)
        self.file_logger.info(f"{icon} [{action}] {rel_path}")

    def _clear_active_log(self):
        tab = self.log_refs["active_tab"].get()
        if tab == "server":
            clear_log(self.log_refs["server_log"])
        elif tab == "changes":
            clear_log(self.log_refs["changes_log"])

    def _on_settings_save(self, config):
        """Handle settings save."""
        # Update auto-restart
        auto_restart = config.get("auto_restart", True)
        self.server.set_auto_restart(auto_restart)

        # Show toast
        self.toast.show("Settings saved!", duration=2000, icon="✅")

    def _on_tray_restore(self):
        """Handle restore from tray."""
        self.toast.show("Window restored", duration=1500, icon="✅")

    def _on_tray_quit(self):
        """Handle quit from tray."""
        if self.server.is_running:
            self.server.stop()
        self.root.destroy()

    def _show_project_menu(self, x, y):
        """Show project selection dropdown menu."""
        from parts.config import get_recent_projects, set_project_root

        menu = tk.Menu(self.root, tearoff=0,
                      bg=Theme.BG_SECONDARY, fg=Theme.TEXT,
                      activebackground=Theme.BG_HOVER,
                      activeforeground=Theme.TEXT,
                      relief="flat", bd=1)

        recent = get_recent_projects()

        if recent:
            for path in recent:
                name = os.path.basename(path)
                menu.add_command(
                    label=f"  {name}",
                    command=lambda p=path: self._switch_project(p)
                )
            menu.add_separator()

        menu.add_command(label="  Browse...", command=self._browse_project)

        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _switch_project(self, path):
        """Switch to a different project."""
        from parts.config import set_project_root, get_src_folder

        if self.server.is_running:
            self.toast.show("Stop server first!", duration=2000, icon="⚠️")
            return

        set_project_root(path)
        name = os.path.basename(path)
        self.project_label.configure(text=f"{name} ▾")
        self.toast.show(f"Switched to {name}", duration=2000, icon="📁")

    def _browse_project(self):
        """Browse for project folder."""
        from tkinter import filedialog
        from parts.config import set_project_root

        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self._switch_project(folder)

    def _show_confirm_close(self):
        """Popup konfirmasi saat close saat server running."""
        popup = tk.Toplevel(self.root)
        popup.title("")
        popup.overrideredirect(True)
        popup.configure(bg=Theme.BG_SECONDARY)
        popup.transient(self.root)
        popup.grab_set()

        # Center popup relative to main window
        pw, ph = 280, 130
        mx = self.root.winfo_x() + (self.root.winfo_width() - pw) // 2
        my = self.root.winfo_y() + (self.root.winfo_height() - ph) // 2
        popup.geometry(f"{pw}x{ph}+{mx}+{my}")

        # Border
        border = tk.Frame(popup, bg=Theme.BORDER)
        border.pack(fill="both", expand=True, padx=1, pady=1)

        inner = tk.Frame(border, bg=Theme.BG_SECONDARY)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        # Message
        tk.Label(inner, text="Are you sure?", font=("Segoe UI", 13, "bold"),
                fg=Theme.TEXT, bg=Theme.BG_SECONDARY).pack(pady=(20, 16))

        # Buttons
        btn_frame = tk.Frame(inner, bg=Theme.BG_SECONDARY)
        btn_frame.pack(pady=(0, 16))

        def on_yes():
            popup.destroy()
            self.server.stop()
            self.root.destroy()

        def on_no():
            popup.destroy()

        # Escape key to close
        popup.bind("<Escape>", lambda e: on_no())

        # Yes button
        yes_btn = tk.Label(btn_frame, text=" Yes, Sure ", font=("Segoe UI", 10, "bold"),
                          fg=Theme.BG, bg=Theme.ACCENT_GREEN, cursor="hand2", padx=14, pady=4)
        yes_btn.pack(side="left", padx=(0, 8))
        yes_btn.bind("<Button-1>", lambda e: on_yes())
        yes_btn.bind("<Enter>", lambda e: yes_btn.configure(bg=Theme.ACCENT_GREEN_HOVER))
        yes_btn.bind("<Leave>", lambda e: yes_btn.configure(bg=Theme.ACCENT_GREEN))

        # No button
        no_btn = tk.Label(btn_frame, text=" No ", font=("Segoe UI", 10, "bold"),
                         fg=Theme.BG, bg=Theme.ACCENT_RED, cursor="hand2", padx=18, pady=4)
        no_btn.pack(side="left")
        no_btn.bind("<Button-1>", lambda e: on_no())
        no_btn.bind("<Enter>", lambda e: no_btn.configure(bg=Theme.ACCENT_RED_HOVER))
        no_btn.bind("<Leave>", lambda e: no_btn.configure(bg=Theme.ACCENT_RED))

        # Focus popup
        popup.lift()
        popup.focus_force()


if __name__ == "__main__":
    root = tk.Tk()
    app = RojoLauncher(root)
    root.mainloop()
