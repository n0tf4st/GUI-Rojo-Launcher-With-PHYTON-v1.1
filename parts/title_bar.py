# File: gui/parts/title_bar.py
# Function: Custom title bar with drag-to-move, minimize, close, and window resize
# How it works: Create title bar frame, bind mouse events for drag & resize,
# use Windows API to force taskbar entry.

import tkinter as tk
from .theme import Theme


def create_title_bar(root, on_minimize, on_close):
    """Buat custom title bar. Return frame title bar."""
    drag_data = {"x": 0, "y": 0}

    def on_drag_start(event):
        drag_data["x"] = event.x
        drag_data["y"] = event.y

    def on_drag_motion(event):
        x = root.winfo_x() + (event.x - drag_data["x"])
        y = root.winfo_y() + (event.y - drag_data["y"])
        root.geometry(f"+{x}+{y}")

    title_bar = tk.Frame(root, bg=Theme.BG_SECONDARY, height=36)
    title_bar.pack(fill="x")
    title_bar.pack_propagate(False)

    title_bar.bind("<Button-1>", on_drag_start)
    title_bar.bind("<B1-Motion>", on_drag_motion)

    # Left side: icon + title
    left = tk.Frame(title_bar, bg=Theme.BG_SECONDARY)
    left.pack(side="left", fill="y")
    left.bind("<Button-1>", on_drag_start)
    left.bind("<B1-Motion>", on_drag_motion)

    tk.Label(left, text=" ⬡", font=("Segoe UI", 11), fg=Theme.ACCENT_BLUE,
            bg=Theme.BG_SECONDARY).pack(side="left")
    tk.Label(left, text="Rojo Launcher", font=("Segoe UI", 10, "bold"), fg=Theme.TEXT,
            bg=Theme.BG_SECONDARY).pack(side="left", padx=(4, 0))

    # Right side: buttons
    right = tk.Frame(title_bar, bg=Theme.BG_SECONDARY)
    right.pack(side="right", fill="y")

    def make_btn(text, hover, cmd):
        btn = tk.Label(right, text=text, font=("Segoe UI", 11), fg=Theme.TEXT_DIM,
                      bg=Theme.BG_SECONDARY, width=3, cursor="hand2")
        btn.pack(side="left")
        btn.bind("<Enter>", lambda e: btn.configure(fg=Theme.TEXT, bg=hover))
        btn.bind("<Leave>", lambda e: btn.configure(fg=Theme.TEXT_DIM, bg=Theme.BG_SECONDARY))
        btn.bind("<Button-1>", lambda e: cmd())

    make_btn("─", Theme.BG_HOVER, on_minimize)
    make_btn("✕", Theme.ACCENT_RED, on_close)

    return title_bar


def setup_resize(root, margin=6):
    """Setup resize functionality untuk borderless window."""
    state = {"dir": None, "data": {}}

    def on_enter(event):
        m = margin
        w = root.winfo_width()
        h = root.winfo_height()
        x = event.x
        y = event.y

        left = x < m
        right = x > w - m
        top = y < m
        bottom = y > h - m

        if top and left:
            state["dir"] = "nw"
            root.config(cursor="size_nw_se")
        elif top and right:
            state["dir"] = "ne"
            root.config(cursor="size_ne_sw")
        elif bottom and left:
            state["dir"] = "sw"
            root.config(cursor="size_ne_sw")
        elif bottom and right:
            state["dir"] = "se"
            root.config(cursor="size_nw_se")
        elif top:
            state["dir"] = "n"
            root.config(cursor="sb_v_double_arrow")
        elif bottom:
            state["dir"] = "s"
            root.config(cursor="sb_v_double_arrow")
        elif left:
            state["dir"] = "w"
            root.config(cursor="sb_h_double_arrow")
        elif right:
            state["dir"] = "e"
            root.config(cursor="sb_h_double_arrow")
        else:
            state["dir"] = None
            root.config(cursor="")

    def on_start(event):
        if state["dir"]:
            state["data"] = {
                "x": event.x_root, "y": event.y_root,
                "w": root.winfo_width(), "h": root.winfo_height(),
                "wx": root.winfo_x(), "wy": root.winfo_y(),
            }

    def on_motion(event):
        if not state["dir"]:
            return
        dx = event.x_root - state["data"]["x"]
        dy = event.y_root - state["data"]["y"]
        min_w, min_h = 520, 360
        w, h = state["data"]["w"], state["data"]["h"]
        wx, wy = state["data"]["wx"], state["data"]["wy"]
        d = state["dir"]

        if "e" in d:
            w = max(min_w, w + dx)
        if "w" in d:
            new_w = max(min_w, w - dx)
            if new_w != w: wx += (w - new_w)
            w = new_w
        if "s" in d:
            h = max(min_h, h + dy)
        if "n" in d:
            new_h = max(min_h, h - dy)
            if new_h != h: wy += (h - new_h)
            h = new_h

        root.geometry(f"{w}x{h}+{wx}+{wy}")

    def on_end(event):
        state["dir"] = None
        root.config(cursor="")

    root.bind("<Motion>", on_enter)
    root.bind("<Button-1>", on_start)
    root.bind("<B1-Motion>", on_motion)
    root.bind("<ButtonRelease-1>", on_end)

    return on_end  # Return callback untuk reparent indicator


def force_taskbar_entry(root):
    """Paksa window muncul di taskbar menggunakan Windows API."""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        # Pastikan window visible dulu
        root.update_idletasks()
        root.update()

        # Coba dapatkan hwnd dengan berbagai cara
        hwnd = user32.GetParent(root.winfo_id())
        if not hwnd:
            hwnd = int(root.wm_frame(), 16) if hasattr(root, 'wm_frame') else 0
        if not hwnd:
            hwnd = kernel32.GetConsoleWindow()

        if not hwnd:
            return

        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080

        ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ex_style = (ex_style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)

        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOZORDER = 0x0004
        SWP_FRAMECHANGED = 0x0020
        user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                           SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)
    except Exception as e:
        print(f"Taskbar fix error: {e}")
