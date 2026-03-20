# File: gui/parts/widgets.py
# Function: Custom widgets (HoverButton, StatusDot) for GUI
# How it works: HoverButton = canvas button with rounded corner & hover effect,
# StatusDot = animated dot for server status indicator.

import tkinter as tk
from .theme import Theme


class HoverButton(tk.Canvas):
    """Button custom dengan hover effect dan rounded corner."""
    def __init__(self, parent, text, bg, fg, hover_bg, command=None, width=120, height=34, **kwargs):
        super().__init__(parent, width=width, height=height, bg=Theme.BG, highlightthickness=0, **kwargs)
        self._bg = bg
        self._fg = fg
        self._hover_bg = hover_bg
        self._command = command
        self._text = text
        self._enabled = True
        self._width = width
        self._height = height
        self._radius = 6

        self._draw(bg)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _draw(self, bg):
        self.delete("all")
        if not self._enabled:
            bg = Theme.BG_TERTIARY
        self._round_rect(2, 2, self._width-2, self._height-2, self._radius, fill=bg, outline="")
        color = self._fg if self._enabled else Theme.TEXT_DIM
        self.create_text(self._width//2, self._height//2, text=self._text, fill=color,
                        font=("Segoe UI", 10, "bold"))

    def _on_enter(self, e):
        if self._enabled:
            self._draw(self._hover_bg)

    def _on_leave(self, e):
        self._draw(self._bg)

    def _on_click(self, e):
        if self._enabled and self._command:
            self._command()

    def set_enabled(self, enabled):
        self._enabled = enabled
        self._draw(self._bg)


class StatusDot(tk.Canvas):
    """Animated status indicator dot."""
    def __init__(self, parent, size=12, **kwargs):
        super().__init__(parent, width=size+4, height=size+4, bg=Theme.BG, highlightthickness=0, **kwargs)
        self._size = size
        self._running = False
        self._pulse_id = None
        self._alpha = 1.0
        self._direction = -1
        self._draw(Theme.ERROR)

    def _draw(self, color):
        self.delete("all")
        s = self._size
        pad = 2
        self.create_oval(pad, pad, pad+s, pad+s, fill=color, outline="")

    def set_status(self, running):
        self._running = running
        if running:
            self._draw(Theme.SUCCESS)
            self._start_pulse()
        else:
            self._stop_pulse()
            self._draw(Theme.ERROR)

    def _start_pulse(self):
        self._pulse_id = self.after(800, self._pulse)

    def _stop_pulse(self):
        if self._pulse_id:
            self.after_cancel(self._pulse_id)
            self._pulse_id = None

    def _pulse(self):
        if not self._running:
            return
        self._alpha += self._direction * 0.15
        if self._alpha <= 0.3:
            self._direction = 1
        elif self._alpha >= 1.0:
            self._direction = -1

        r = int(63 * self._alpha)
        g = int(185 * self._alpha)
        b = int(80 * self._alpha)
        color = f"#{r:02x}{g:02x}{b:02x}"
        self._draw(color)
        self._pulse_id = self.after(80, self._pulse)
