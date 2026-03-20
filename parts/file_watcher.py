# File: gui/parts/file_watcher.py
# Function: Monitor file changes in src/ folder in real-time
# How it works: Uses threading to check file modification time every 1 second,
# then reports changed files to the given callback.

import os
import time
import threading
from datetime import datetime


class FileWatcher:
    def __init__(self, watch_folder, callback):
        self.watch_folder = os.path.abspath(watch_folder)
        self.callback = callback
        self.is_running = False
        self.thread = None
        self.file_states = {}
        self.first_scan_done = False

    def _scan_files(self):
        """Scan all files in folder and subfolders."""
        current = {}

        # Check if watch folder still exists
        if not os.path.isdir(self.watch_folder):
            return current

        try:
            for root, dirs, files in os.walk(self.watch_folder):
                # Skip certain folders
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                for fname in files:
                    if fname.endswith(('.luau', '.lua', '.json', '.toml')):
                        full_path = os.path.join(root, fname)
                        try:
                            mtime = os.path.getmtime(full_path)
                            rel_path = os.path.relpath(full_path, self.watch_folder)
                            current[rel_path] = mtime
                        except OSError:
                            pass
        except OSError:
            # Folder was deleted or is inaccessible
            pass

        return current

    def _check_changes(self):
        """Compare current file state with previous."""
        current = self._scan_files()
        changes = []

        if not self.first_scan_done:
            self.first_scan_done = True
            self.file_states = current
            return changes

        # New or modified files
        for rel_path, mtime in current.items():
            if rel_path not in self.file_states:
                changes.append(('ADDED', rel_path))
            elif mtime != self.file_states[rel_path]:
                changes.append(('MODIFIED', rel_path))

        # Deleted files
        for rel_path in self.file_states:
            if rel_path not in current:
                changes.append(('DELETED', rel_path))

        self.file_states = current
        return changes

    def _watch_loop(self):
        """Main loop running in separate thread."""
        while self.is_running:
            changes = self._check_changes()
            if changes:
                timestamp = datetime.now().strftime("%H:%M:%S")
                for action, rel_path in changes:
                    self.callback(timestamp, action, rel_path)
            time.sleep(1)

    def start(self):
        """Mulai file watcher."""
        if self.is_running:
            return
        self.is_running = True
        self.file_states = self._scan_files()
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Hentikan file watcher."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None

    def get_file_count(self):
        """Return jumlah file yang di-monitor."""
        return len(self.file_states)
