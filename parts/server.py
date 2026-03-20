# File: gui/parts/server.py
# Function: Control Rojo server (start, stop, read output, auto-restart)
# How it works: Uses subprocess to run rojo serve,
# threading to read output without freezing GUI.

import subprocess
import threading
import os
import sys


class ServerController:
    """Control Rojo server process."""

    MAX_RETRIES = 3
    RESTART_DELAY = 2000  # ms

    def __init__(self):
        self.process = None
        self.is_running = False
        self._on_output = None
        self._on_end = None
        self._on_crash = None
        self._project_root = None
        self._auto_restart = False
        self._retry_count = 0
        self._stopped_manually = False

    def set_callbacks(self, on_output, on_end, on_crash=None):
        """Set callback for output, when process ends, and on crash."""
        self._on_output = on_output
        self._on_end = on_end
        self._on_crash = on_crash

    def set_auto_restart(self, enabled):
        """Enable/disable auto-restart on crash."""
        self._auto_restart = enabled
        if enabled:
            self._retry_count = 0

    def start(self, project_root):
        """Run rojo serve. Return (success, error_message)."""
        if self.is_running:
            return False, "Server already running"

        self._project_root = project_root
        self._stopped_manually = False

        return self._do_start()

    def _do_start(self):
        """Internal start method."""
        env = os.environ.copy()
        try:
            self.process = subprocess.Popen(
                ["rojo", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
                cwd=self._project_root,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            self.is_running = True
            threading.Thread(target=self._read_output, daemon=True).start()
            return True, None
        except FileNotFoundError:
            return False, "'rojo' not found. Install Rojo first."
        except Exception as e:
            return False, str(e)

    def stop(self):
        """Stop server manually (disables auto-restart)."""
        self._stopped_manually = True
        self._auto_restart = False
        if self.process and self.is_running:
            self.process.terminate()
            self.process = None
            self.is_running = False

    def _read_output(self):
        """Read server output in separate thread."""
        if not self.process or not self.process.stdout:
            self.is_running = False
            if self._on_end:
                self._on_end()
            return

        try:
            for line in self.process.stdout:
                if not line:  # Handle empty lines
                    continue
                text = line.rstrip()
                tag = "default"
                lower = text.lower()
                if "error" in lower or "failed" in lower:
                    tag = "error"
                elif "warn" in lower:
                    tag = "warn"
                elif "listening" in lower or "connected" in lower or "started" in lower:
                    tag = "success"
                if self._on_output:
                    self._on_output(text, tag)
        except (ValueError, OSError):
            # Handle case where stdout is closed or becomes invalid
            pass

        self.is_running = False

        # Check if crashed (not stopped manually)
        if not self._stopped_manually and self._auto_restart:
            if self._retry_count < self.MAX_RETRIES:
                self._retry_count += 1
                if self._on_crash:
                    self._on_crash(self._retry_count, self.MAX_RETRIES)
            else:
                if self._on_end:
                    self._on_end()
        else:
            self._retry_count = 0
            if self._on_end:
                self._on_end()

    def try_restart(self):
        """Try to restart server. Return (success, error_message)."""
        if not self._project_root:
            return False, "No project root set"

        if self.is_running:
            self.process.terminate()
            self.process = None
            self.is_running = False

        return self._do_start()
