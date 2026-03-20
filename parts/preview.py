# File: gui/parts/preview.py
# Function: Preview file content
# How it works: Read first N lines of a file and display in a text widget

import os


def read_preview(file_path, max_lines=20):
    """Read first N lines of a file. Return (lines_list, total_lines, error)."""
    if not os.path.exists(file_path):
        return [], 0, "File not found"

    if os.path.isdir(file_path):
        return [], 0, "Is a directory"

    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()
    previewable = (".luau", ".lua", ".json", ".txt", ".md", ".toml", ".py", ".js", ".ts",
                   ".html", ".css", ".xml", ".yaml", ".yml", ".ini", ".cfg", ".bat", ".ps1")

    if ext not in previewable:
        return [], 0, f"Cannot preview {ext} files"

    try:
        # Check file size (max 1MB for preview)
        size = os.path.getsize(file_path)
        if size > 1024 * 1024:
            return [], 0, "File too large (>1MB)"

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                lines.append(line.rstrip("\n"))

            # Count total lines
            f.seek(0)
            total = sum(1 for _ in f)

        return lines, total, None
    except Exception as e:
        return [], 0, str(e)
