# File: gui/parts/tabs/folder_projek.py
# Function: Tab Folder Projek to display src/ structure with file info

import tkinter as tk
from tkinter import ttk, filedialog
import os
import time
from datetime import datetime
from ..theme import Theme
from ..config import get_src_folder, set_project_root, get_project_root
from ..file_opener import open_file, open_folder
from ..preview import read_preview


def create(parent):
    """Buat split panel: tree di kiri, info file di kanan. Return (tree, frame)."""
    src_path = get_src_folder()

    # Top bar with refresh + settings button
    top_bar = tk.Frame(parent, bg=Theme.BG_SECONDARY, height=30)
    top_bar.pack(fill="x", side="top")
    top_bar.pack_propagate(False)

    path_label = tk.Label(top_bar, font=("Consolas", 9),
                          fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY)
    path_label.pack(side="left", padx=8, pady=4)

    # Settings button
    settings_btn = tk.Label(top_bar, text=" ⚙️", font=("Segoe UI", 9),
                            fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY, cursor="hand2")
    settings_btn.pack(side="right", padx=(0, 4), pady=4)
    settings_btn.bind("<Enter>", lambda e: settings_btn.configure(fg=Theme.TEXT))
    settings_btn.bind("<Leave>", lambda e: settings_btn.configure(fg=Theme.TEXT_DIM))

    # Refresh button
    refresh_btn = tk.Label(top_bar, text=" 🔄 Refresh", font=("Segoe UI", 9),
                           fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY, cursor="hand2")
    refresh_btn.pack(side="right", padx=4, pady=4)
    refresh_btn.bind("<Enter>", lambda e: refresh_btn.configure(fg=Theme.TEXT))
    refresh_btn.bind("<Leave>", lambda e: refresh_btn.configure(fg=Theme.TEXT_DIM))

    # Main split area
    split = tk.Frame(parent, bg=Theme.BG_SECONDARY)
    split.pack(fill="both", expand=True)

    # Left: Tree
    left = tk.Frame(split, bg=Theme.BG_SECONDARY)
    left.pack(side="left", fill="both", expand=True)

    # Right: File info
    right = tk.Frame(split, bg=Theme.BG_TERTIARY, width=220)
    right.pack(side="right", fill="y")
    right.pack_propagate(False)

    # Separator
    tk.Frame(split, bg=Theme.BORDER, width=1).pack(side="right", fill="y")

    tree = _make_tree(left)
    info_labels = _make_info_panel(right)

    # Update path label
    def update_path_label():
        src = get_src_folder()
        if src:
            path_label.configure(text=f" {os.path.basename(os.path.dirname(src))}/src/")
        else:
            path_label.configure(text=" ⚠️ Path not found")

    # Bind selection
    def on_select(event):
        sel = tree.selection()
        if not sel:
            return
        item = tree.item(sel[0])
        tags = item.get("tags", ())
        if tags and len(tags) > 1:
            _update_info(info_labels, tags[1], item["text"].strip())

    tree.bind("<<TreeviewSelect>>", on_select)

    # Double-click to open file/folder
    def on_double_click(event):
        sel = tree.selection()
        if not sel:
            return
        item = tree.item(sel[0])
        tags = item.get("tags", ())
        if tags and len(tags) > 1:
            path = tags[1]
            if os.path.isdir(path):
                open_folder(path)
            else:
                open_file(path)

    tree.bind("<Double-1>", on_double_click)

    # Refresh button
    def do_refresh():
        for item in tree.get_children():
            tree.delete(item)
        src = get_src_folder()
        if src:
            _populate(tree, "", src)
        update_path_label()

    refresh_btn.bind("<Button-1>", lambda e: do_refresh())

    # Settings button - browse folder
    def browse_folder(root_window=None):
        folder = filedialog.askdirectory(title="Pilih Folder Projek (yang ada src/)")
        if folder:
            # Cek apakah ada src/ di dalam
            src = os.path.join(folder, "src")
            if os.path.isdir(src):
                set_project_root(folder)
                do_refresh()
            else:
                # Coba cari src/ di subfolder
                for item in os.listdir(folder):
                    if item == "src" and os.path.isdir(os.path.join(folder, item)):
                        set_project_root(folder)
                        do_refresh()
                        return
                # No src/ found, but still save
                set_project_root(folder)
                do_refresh()

    settings_btn.bind("<Button-1>", lambda e: browse_folder(parent.winfo_toplevel()))

    # Initial load
    update_path_label()
    if src_path:
        _populate(tree, "", src_path)

    return tree, parent


def _make_tree(parent):
    """Buat treeview struktur folder."""
    tree = ttk.Treeview(parent, show="tree", selectmode="browse")

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview",
        background=Theme.BG_SECONDARY, foreground=Theme.TEXT,
        fieldbackground=Theme.BG_SECONDARY, borderwidth=0,
        font=("Cascadia Code", 9), rowheight=22)
    style.map("Treeview",
        background=[("selected", Theme.BG_HOVER)],
        foreground=[("selected", Theme.TEXT)])

    scrollbar = tk.Scrollbar(parent, orient="vertical", command=tree.yview,
                             bg=Theme.BG_SECONDARY, troughcolor=Theme.BG_SECONDARY,
                             activebackground=Theme.BG_HOVER, width=8)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack_forget()
    tree.pack(fill="both", expand=True)

    # Jangan populate di sini - di-handle oleh create()

    for tag, color in [("folder", Theme.FOLDER), ("file_luau", Theme.FILE_LUAU),
                        ("file_json", Theme.FILE_JSON), ("file_other", Theme.FILE_OTHER),
                        ("new_file", Theme.ACCENT_GREEN)]:
        tree.tag_configure(tag, foreground=color)

    return tree


def _populate(tree, parent, folder):
    """Rekursif isi treeview."""
    try:
        entries = sorted(os.listdir(folder))
    except OSError:
        return

    now = time.time()
    one_hour = 3600

    dirs = [e for e in entries if os.path.isdir(os.path.join(folder, e))]
    files = [e for e in entries if not os.path.isdir(os.path.join(folder, e))]

    for d in dirs:
        full_path = os.path.join(folder, d)
        node = tree.insert(parent, "end", text=f"  📁 {d}", open=False,
                          tags=("folder", full_path))
        _populate(tree, node, full_path)

    for f in files:
        full_path = os.path.join(folder, f)
        ext = os.path.splitext(f)[1].lower()

        try:
            is_new = (now - os.path.getctime(full_path)) < one_hour
        except OSError:
            is_new = False

        if is_new:
            icon, tag = "  ✨", "new_file"
        elif ext in (".luau", ".lua"):
            icon, tag = "  📄", "file_luau"
        elif ext == ".json":
            icon, tag = "  📋", "file_json"
        else:
            icon, tag = "  📄", "file_other"

        tree.insert(parent, "end", text=f"{icon} {f}", tags=(tag, full_path))


def _make_info_panel(parent):
    """Create file info panel with preview on the right."""
    # Header
    header = tk.Frame(parent, bg=Theme.BG_TERTIARY, height=30)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text=" File Info", font=("Segoe UI", 9, "bold"),
            fg=Theme.TEXT, bg=Theme.BG_TERTIARY).pack(side="left", padx=8, pady=6)

    # File info content
    content = tk.Frame(parent, bg=Theme.BG_TERTIARY)
    content.pack(fill="x", padx=10, pady=(4, 0))

    labels = {}

    def add_row(key, label_text, row):
        tk.Label(content, text=label_text, font=("Segoe UI", 8),
                fg=Theme.TEXT_DIM, bg=Theme.BG_TERTIARY, anchor="w").grid(
                    row=row, column=0, sticky="w", pady=(4, 0))
        val = tk.Label(content, text="-", font=("Cascadia Code", 8),
                      fg=Theme.TEXT, bg=Theme.BG_TERTIARY, anchor="w", wraplength=180)
        val.grid(row=row+1, column=0, sticky="w", pady=(0, 0))
        labels[key] = val

    add_row("name", "Name", 0)
    add_row("type", "Type", 2)
    add_row("size", "Size", 4)
    add_row("created", "Created", 6)
    add_row("modified", "Modified", 8)
    content.grid_columnconfigure(0, weight=1)

    # Separator
    tk.Frame(parent, bg=Theme.BORDER, height=1).pack(fill="x", padx=10, pady=6)

    # Preview header
    preview_header = tk.Frame(parent, bg=Theme.BG_TERTIARY, height=24)
    preview_header.pack(fill="x")
    preview_header.pack_propagate(False)
    tk.Label(preview_header, text=" Preview", font=("Segoe UI", 8, "bold"),
            fg=Theme.TEXT_DIM, bg=Theme.BG_TERTIARY).pack(side="left", padx=8, pady=2)

    # Preview content
    preview_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
    preview_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

    preview_text = tk.Text(
        preview_frame, font=("Cascadia Code", 7), fg=Theme.TEXT_DIM,
        bg=Theme.BG_SECONDARY, relief="flat", wrap="none", state="disabled",
        bd=0, padx=6, pady=4, height=8,
    )
    preview_text.pack(fill="both", expand=True)

    labels["_preview"] = preview_text

    return labels


def _format_time(timestamp):
    """Format timestamp ke readable string."""
    dt = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    diff = now - dt

    if diff.days == 0:
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60} min ago"
        else:
            return f"{diff.seconds // 3600}h ago"
    elif diff.days == 1:
        return f"Yesterday {dt.strftime('%H:%M')}"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    else:
        return dt.strftime("%Y-%m-%d %H:%M")


def _update_info(labels, full_path, filename):
    """Update panel info dengan data file."""
    if not os.path.exists(full_path):
        for k in labels: labels[k].configure(text="-")
        labels["name"].configure(text=filename)
        return

    labels["name"].configure(text=filename)

    if os.path.isdir(full_path):
        labels["type"].configure(text="Folder")
        try:
            labels["size"].configure(text=f"{len(os.listdir(full_path))} items")
        except OSError:
            labels["size"].configure(text="?")
    else:
        ext = os.path.splitext(filename)[1].lower()
        type_map = {".luau": "Luau Script", ".lua": "Lua Script", ".json": "JSON"}
        labels["type"].configure(text=type_map.get(ext, ext or "File"))
        size = os.path.getsize(full_path)
        if size < 1024:
            labels["size"].configure(text=f"{size} B")
        elif size < 1024 * 1024:
            labels["size"].configure(text=f"{size / 1024:.1f} KB")
        else:
            labels["size"].configure(text=f"{size / (1024*1024):.1f} MB")

    try:
        labels["created"].configure(text=_format_time(os.path.getctime(full_path)))
    except OSError:
        labels["created"].configure(text="-")

    try:
        labels["modified"].configure(text=_format_time(os.path.getmtime(full_path)))
    except OSError:
        labels["modified"].configure(text="-")

    # Update preview
    preview_widget = labels.get("_preview")
    if preview_widget:
        preview_widget.configure(state="normal")
        preview_widget.delete("1.0", "end")

        if not os.path.isdir(full_path):
            lines, total, error = read_preview(full_path)
            if error:
                preview_widget.insert("1.0", f"  {error}")
            elif lines:
                for line in lines:
                    preview_widget.insert("end", f"  {line}\n")
                if total > len(lines):
                    preview_widget.insert("end", f"\n  ... ({total - len(lines)} more lines)")
            else:
                preview_widget.insert("1.0", "  (empty file)")
        else:
            preview_widget.insert("1.0", "  (folder - no preview)")

        preview_widget.configure(state="disabled")
