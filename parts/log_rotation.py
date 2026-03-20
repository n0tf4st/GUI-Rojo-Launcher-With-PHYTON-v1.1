# File: gui/parts/log_rotation.py
# Function: Log rotation - delete old log files when max count exceeded
# How it works: Check log folder, delete oldest files if count > max

import os
import glob


def rotate_logs(logs_dir, max_files=50):
    """Delete old log files if count exceeds max_files. Return number deleted."""
    if not os.path.isdir(logs_dir):
        return 0

    # Get all log files sorted by modification time (oldest first)
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    if len(log_files) <= max_files:
        return 0

    # Sort by modification time
    log_files.sort(key=os.path.getmtime)

    # Delete oldest files
    to_delete = log_files[:len(log_files) - max_files]
    deleted = 0

    for f in to_delete:
        try:
            os.remove(f)
            deleted += 1
        except OSError:
            pass

    return deleted


def get_logs_dir():
    """Return path to logs folder."""
    gui_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(gui_dir, "logs")


def get_log_count():
    """Return number of log files."""
    logs_dir = get_logs_dir()
    if not os.path.isdir(logs_dir):
        return 0
    return len(glob.glob(os.path.join(logs_dir, "*.log")))


def cleanup_if_needed(max_files=50):
    """Auto cleanup if log count exceeds max."""
    logs_dir = get_logs_dir()
    deleted = rotate_logs(logs_dir, max_files)
    return deleted
