# File: gui/parts/config.py
# Function: Handle project path configuration (auto-detect, config file, fallback)
# How it works:
# 1. Search for default.project.json / rokit.toml in parent folders (auto-detect)
# 2. If not found, check config.json
# 3. If still not found, return None (user needs to select manually)

import os
import json


CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
ROJO_MARKERS = ["default.project.json", "rokit.toml"]


def detect_project_root():
    """Auto-detect project root by searching for Rojo marker files."""
    # Start from gui folder, go up until marker is found
    current = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    max_levels = 10  # Limit how far up to search

    for _ in range(max_levels):
        for marker in ROJO_MARKERS:
            if os.path.exists(os.path.join(current, marker)):
                return current
        parent = os.path.dirname(current)
        if parent == current:  # Already at drive root
            break
        current = parent

    return None


def load_config():
    """Load config from config.json. Return dict or {}."""
    if not os.path.exists(CONFIG_FILE):
        return {}

    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(config):
    """Save config to config.json."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except IOError:
        return False


def get_project_root():
    """Return project root path. Priority: auto-detect > config > None."""
    # 1. Auto-detect
    detected = detect_project_root()
    if detected:
        return detected

    # 2. Config file
    config = load_config()
    saved_path = config.get("project_root")
    if saved_path and os.path.isdir(saved_path):
        return saved_path

    # 3. Not found
    return None


def set_project_root(path):
    """Save project root to config.json."""
    config = load_config()
    config["project_root"] = path

    # Add to recent projects
    recent = config.get("recent_projects", [])
    if path in recent:
        recent.remove(path)
    recent.insert(0, path)
    config["recent_projects"] = recent[:10]  # Keep max 10

    return save_config(config)


def get_recent_projects():
    """Return list of recent project paths."""
    config = load_config()
    recent = config.get("recent_projects", [])
    # Filter out non-existent paths
    return [p for p in recent if os.path.isdir(p)]


def remove_recent_project(path):
    """Remove a project from recent list."""
    config = load_config()
    recent = config.get("recent_projects", [])
    if path in recent:
        recent.remove(path)
        config["recent_projects"] = recent
        save_config(config)


def get_src_folder():
    """Return path ke folder src/ dari project root."""
    root = get_project_root()
    if root:
        src = os.path.join(root, "src")
        if os.path.isdir(src):
            return src
    return None
