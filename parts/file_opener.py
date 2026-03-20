# File: gui/parts/file_opener.py
# Function: Open files in default editor
# How it works: Detect default editor from config, fallback to system default

import os
import subprocess
import sys
from .config import load_config


def open_file(file_path):
    """Open file in default editor."""
    if not os.path.exists(file_path):
        return False, "File not found"

    config = load_config()
    editor = config.get("editor", "")

    try:
        if editor and os.path.exists(editor):
            # Use configured editor
            subprocess.Popen([editor, file_path])
        else:
            # Use system default
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", file_path])
            else:
                subprocess.Popen(["xdg-open", file_path])
        return True, None
    except Exception as e:
        return False, str(e)


def open_folder(folder_path):
    """Open folder in file explorer."""
    if not os.path.exists(folder_path):
        return False, "Folder not found"

    try:
        if sys.platform == "win32":
            os.startfile(folder_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder_path])
        else:
            subprocess.Popen(["xdg-open", folder_path])
        return True, None
    except Exception as e:
        return False, str(e)
