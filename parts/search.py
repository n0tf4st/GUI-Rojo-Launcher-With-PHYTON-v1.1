# File: gui/parts/search.py
# Function: Search and filter bar for log panels
# How it works: Creates a search bar with filter buttons, filters log content in real-time

import tkinter as tk
from .theme import Theme


def create(parent, on_search=None):
    """Create search bar with filter buttons. Return dict of refs."""
    refs = {}

    bar = tk.Frame(parent, bg=Theme.BG_SECONDARY, height=32)
    bar.pack(fill="x")
    bar.pack_propagate(False)

    # Search icon
    tk.Label(bar, text=" 🔍", font=("Segoe UI", 9),
            fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY).pack(side="left", padx=(8, 0), pady=4)

    # Search entry
    search_var = tk.StringVar()
    entry = tk.Entry(bar, textvariable=search_var, font=("Cascadia Code", 9),
                    fg=Theme.TEXT, bg=Theme.BG_TERTIARY, insertbackground=Theme.TEXT,
                    relief="flat", bd=0, width=30)
    entry.pack(side="left", padx=4, pady=6, ipady=2)

    # Placeholder
    def on_focus_in(e):
        if entry.get() == "Search...":
            entry.delete(0, tk.END)
            entry.configure(fg=Theme.TEXT)

    def on_focus_out(e):
        if entry.get() == "":
            entry.insert(0, "Search...")
            entry.configure(fg=Theme.TEXT_DIM)

    entry.insert(0, "Search...")
    entry.configure(fg=Theme.TEXT_DIM)
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    # Clear button
    clear_btn = tk.Label(bar, text=" ✕", font=("Segoe UI", 9),
                        fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY, cursor="hand2")
    clear_btn.pack(side="left", pady=4)
    clear_btn.bind("<Enter>", lambda e: clear_btn.configure(fg=Theme.TEXT))
    clear_btn.bind("<Leave>", lambda e: clear_btn.configure(fg=Theme.TEXT_DIM))

    def do_clear():
        search_var.set("")
        entry.configure(fg=Theme.TEXT_DIM)
        entry.insert(0, "Search...")
        if on_search:
            on_search("")

    clear_btn.bind("<Button-1>", lambda e: do_clear())

    # Filter buttons (optional - shown if filters provided)
    filter_frame = tk.Frame(bar, bg=Theme.BG_SECONDARY)
    filter_frame.pack(side="right", padx=8, pady=4)

    # Export buttons
    export_frame = tk.Frame(bar, bg=Theme.BG_SECONDARY)
    export_frame.pack(side="right", padx=4, pady=4)

    refs["bar"] = bar
    refs["entry"] = entry
    refs["search_var"] = search_var
    refs["filter_frame"] = filter_frame
    refs["export_frame"] = export_frame
    refs["clear_btn"] = clear_btn

    # Bind search
    def on_key_release(e):
        text = search_var.get()
        if text == "Search...":
            text = ""
        if on_search:
            on_search(text)

    entry.bind("<KeyRelease>", on_key_release)

    return refs


def create_filters(parent, filters, on_filter):
    """Create filter buttons. filters = [(label, value), ...]"""
    btns = {}

    for label, value in filters:
        btn = tk.Label(parent, text=f" {label} ", font=("Segoe UI", 8),
                      fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY, cursor="hand2", padx=4)
        btn.pack(side="left", padx=1)

        def make_click(b, v):
            def click(e):
                # Reset all
                for b2 in btns.values():
                    b2.configure(fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY)
                # Highlight selected
                b.configure(fg=Theme.TEXT, bg=Theme.BG_HOVER)
                on_filter(v)
            return click

        btn.bind("<Button-1>", make_click(btn, value))
        btn.bind("<Enter>", lambda e, b=btn: b.configure(fg=Theme.TEXT) if b.cget("bg") != Theme.BG_HOVER else None)
        btn.bind("<Leave>", lambda e, b=btn: b.configure(fg=Theme.TEXT_DIM) if b.cget("bg") != Theme.BG_HOVER else None)
        btns[value] = btn

    # Set first as active
    if btns:
        first = list(btns.values())[0]
        first.configure(fg=Theme.TEXT, bg=Theme.BG_HOVER)

    return btns


def highlight_text(widget, search_text, tag="highlight"):
    """Highlight all occurrences of search_text in widget."""
    # Remove old highlights
    widget.tag_remove(tag, "1.0", "end")

    if not search_text or search_text == "Search...":
        return

    # Configure highlight tag
    widget.tag_configure(tag, background=Theme.ACCENT_YELLOW, foreground=Theme.BG)

    # Find and highlight
    start = "1.0"
    count = 0
    while True:
        pos = widget.search(search_text, start, tk.END, nocase=True)
        if not pos:
            break
        end = f"{pos}+{len(search_text)}c"
        widget.tag_add(tag, pos, end)
        start = end
        count += 1

    return count


def create_export_buttons(parent, on_copy, on_export):
    """Create copy and export buttons. on_copy and on_export are callbacks."""
    # Copy button
    copy_btn = tk.Label(parent, text=" 📋", font=("Segoe UI", 9),
                       fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY, cursor="hand2")
    copy_btn.pack(side="left", padx=1)
    copy_btn.bind("<Button-1>", lambda e: on_copy())
    copy_btn.bind("<Enter>", lambda e: copy_btn.configure(fg=Theme.TEXT))
    copy_btn.bind("<Leave>", lambda e: copy_btn.configure(fg=Theme.TEXT_DIM))

    # Export button
    export_btn = tk.Label(parent, text=" 💾", font=("Segoe UI", 9),
                         fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY, cursor="hand2")
    export_btn.pack(side="left", padx=1)
    export_btn.bind("<Button-1>", lambda e: on_export())
    export_btn.bind("<Enter>", lambda e: export_btn.configure(fg=Theme.TEXT))
    export_btn.bind("<Leave>", lambda e: export_btn.configure(fg=Theme.TEXT_DIM))

    return copy_btn, export_btn
