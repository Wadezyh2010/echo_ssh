"""
echo_ssh - Terminal Widget
A modern terminal emulator widget built on pyte + PyQt6.
Supports ANSI colors, scrollback, selection, copy/paste.
"""

import pyte
from PyQt6.QtCore import Qt, QTimer, QRect, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QFontMetrics, QKeyEvent, QTextCursor,
    QGuiApplication, QClipboard
)
from PyQt6.QtWidgets import QWidget, QMenu

from i18n import tr


# xterm 256-color palette (subset used by pyte)
def _build_palette():
    palette = {}
    # 16 standard colors
    std = [
        "#000000", "#cc0000", "#4e9a06", "#c4a000",
        "#3465a4", "#75507b", "#06989a", "#d3d7cf",
        "#555753", "#ef2929", "#8ae234", "#fce94f",
        "#729fcf", "#ad7fa8", "#34e2e2", "#eeeeec",
    ]
    for i, c in enumerate(std):
        palette[i] = c
    # 216 color cube
    ramps = [0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff]
    idx = 16
    for r in range(6):
        for g in range(6):
            for b in range(6):
                palette[idx] = "#{:02x}{:02x}{:02x}".format(
                    ramps[r], ramps[g], ramps[b]
                )
                idx += 1
    # 24 grayscale
    for i in range(24):
        v = 8 + i * 10
        palette[idx] = "#{:02x}{:02x}{:02x}".format(v, v, v)
        idx += 1
    return palette


PALETTE = _build_palette()
DEFAULT_FG = "#cdd6f4"
DEFAULT_BG = "#1e1e2e"


class TerminalWidget(QWidget):
    """A terminal emulator widget."""

    data_sent = pyqtSignal(bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cols = 80
        self.rows = 24
        self.font = QFont("Consolas", 11)
        self.font.setStyleHint(QFont.StyleHint.Monospace)
        self.fm = QFontMetrics(self.font)
        self.char_w = self.fm.horizontalAdvance("M")
        self.char_h = self.fm.height()

        self.screen = pyte.Screen(self.cols, self.rows)
        self.stream = pyte.Stream(self.screen)

        self._scrollback_lines = []  # list of (row_index, line) for scrollback
        self._max_scrollback = 5000
        self._scroll_offset = 0

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

        # Selection
        self._selecting = False
        self._sel_start = None  # (row, col)
        self._sel_end = None    # (row, col)

        # Cursor blink
        self._cursor_visible = True
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._toggle_cursor)
        self._blink_timer.start(500)

        # Render timer (throttle repaints)
        self._dirty = False
        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.timeout.connect(self.update)
        self._render_timer.setInterval(16)

        self.setMinimumSize(self.cols * self.char_w, self.rows * self.char_h)
        self.update_geometry()

    # ----- Geometry / sizing -----
    def update_geometry(self):
        w = self.width()
        h = self.height()
        new_cols = max(1, w // self.char_w)
        new_rows = max(1, h // self.char_h)
        if new_cols != self.cols or new_rows != self.rows:
            self.cols = new_cols
            self.rows = new_rows
            self._resize_screen()

    def _resize_screen(self):
        new_screen = pyte.Screen(self.cols, self.rows)
        # Copy visible content
        old = self.screen
        for r in range(min(old.lines, self.rows)):
            for c in range(min(old.columns, self.cols)):
                ch = old.buffer.get(r, {}).get(c)
                if ch:
                    new_screen.buffer[r][c] = ch
        new_screen.cursor.y = min(old.cursor.y, self.rows - 1)
        new_screen.cursor.x = min(old.cursor.x, self.cols - 1)
        self.screen = new_screen
        self.stream.attach(self.screen)

    def resizeEvent(self, event):
        self.update_geometry()
        super().resizeEvent(event)

    # ----- Data input (from SSH) -----
    def feed(self, data: bytes):
        """Feed raw bytes from the SSH channel into the terminal."""
        try:
            text = data.decode("utf-8", errors="replace")
        except Exception:
            text = data.decode("latin-1", errors="replace")
        self.stream.feed(text)
        self._schedule_render()

    def _schedule_render(self):
        if not self._render_timer.isActive():
            self._render_timer.start()

    # ----- Cursor blink -----
    def _toggle_cursor(self):
        self._cursor_visible = not self._cursor_visible
        self.update()

    # ----- Painting -----
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font)
        painter.fillRect(self.rect(), QColor(DEFAULT_BG))

        # Determine which rows to render based on scroll offset
        total_rows = self.rows
        start_row = -self._scroll_offset
        end_row = self.rows - self._scroll_offset

        # Render scrollback history if scrolled up
        if self._scroll_offset > 0:
            history = self._scrollback_lines
            visible_hist = history[-self._scroll_offset:] if len(history) >= self._scroll_offset else history
            # Draw history lines at top
            for i, line_data in enumerate(visible_hist):
                if i >= self.rows:
                    break
                self._draw_line(painter, i, line_data, is_history=True)

        # Draw current screen
        screen_start = max(0, self._scroll_offset)
        for r in range(self.rows):
            hist_count = min(self._scroll_offset, len(self._scrollback_lines))
            if r < hist_count:
                continue
            screen_row = r - hist_count
            if 0 <= screen_row < self.rows:
                line = self.screen.buffer.get(screen_row, {})
                self._draw_line(painter, r, line, is_history=False)

        # Cursor
        if self._scroll_offset == 0 and self._cursor_visible:
            cx = self.screen.cursor.x
            cy = self.screen.cursor.y
            if 0 <= cy < self.rows and 0 <= cx < self.cols:
                painter.fillRect(
                    cx * self.char_w, cy * self.char_h,
                    self.char_w, self.char_h,
                    QColor("#f5e0dc")
                )

        painter.end()

    def _draw_line(self, painter, row, line, is_history=False):
        y = row * self.char_h
        baseline = y + self.fm.ascent()
        for col in range(self.cols):
            cell = line.get(col) if hasattr(line, "get") else None
            char = " "
            fg = DEFAULT_FG
            bg = DEFAULT_BG
            bold = False
            if cell and cell.data != "":
                char = cell.data
                fg = self._resolve_color(cell.fg, DEFAULT_FG)
                bg = self._resolve_color(cell.bg, DEFAULT_BG)
                bold = cell.bold
            x = col * self.char_w
            if bg != DEFAULT_BG:
                painter.fillRect(x, y, self.char_w, self.char_h, QColor(bg))
            painter.setPen(QColor(fg))
            f = QFont(self.font)
            if bold:
                f.setBold(True)
                painter.setFont(f)
            painter.drawText(x, baseline, char)
            painter.setFont(self.font)

    def _resolve_color(self, color, default):
        if color is None or color == "default":
            return default
        if isinstance(color, str) and color.startswith("#"):
            return color
        if isinstance(color, int):
            return PALETTE.get(color, default)
        if hasattr(color, "red"):
            return "#{:02x}{:02x}{:02x}".format(color.red, color.green, color.blue)
        return default

    # ----- Keyboard input -----
    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        # Ctrl+Shift+C = copy, Ctrl+Shift+V = paste
        if modifiers & Qt.KeyboardModifier.ControlModifier and modifiers & Qt.KeyboardModifier.ShiftModifier:
            if key == Qt.Key.Key_C:
                self.copy_selection()
                return
            if key == Qt.Key.Key_V:
                self.paste()
                return

        # Ctrl+C (interrupt)
        if modifiers & Qt.KeyboardModifier.ControlModifier and not (modifiers & Qt.KeyboardModifier.ShiftModifier):
            if key == Qt.Key.Key_C:
                self._send(b"\x03")
                return
            if key == Qt.Key.Key_L:
                self._send(b"\x0c")
                return
            if key == Qt.Key.Key_Z:
                self._send(b"\x1a")
                return
            if key == Qt.Key.Key_D:
                self._send(b"\x04")
                return
            if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
                self._send(bytes([key - Qt.Key.Key_A + 1]))
                return

        # Special keys
        mapping = {
            Qt.Key.Key_Return: b"\r",
            Qt.Key.Key_Enter: b"\r",
            Qt.Key.Key_Backspace: b"\x7f",
            Qt.Key.Key_Tab: b"\t",
            Qt.Key.Key_Escape: b"\x1b",
            Qt.Key.Key_Left: b"\x1b[D",
            Qt.Key.Key_Right: b"\x1b[C",
            Qt.Key.Key_Up: b"\x1b[A",
            Qt.Key.Key_Down: b"\x1b[B",
            Qt.Key.Key_Home: b"\x1b[H",
            Qt.Key.Key_End: b"\x1b[F",
            Qt.Key.Key_PageUp: b"\x1b[5~",
            Qt.Key.Key_PageDown: b"\x1b[6~",
            Qt.Key.Key_Insert: b"\x1b[2~",
            Qt.Key.Key_Delete: b"\x1b[3~",
        }
        if key in mapping:
            # PageUp/PageDown scroll when not used for input
            if key == Qt.Key.Key_PageUp:
                self._scroll_offset = min(self._scroll_offset + self.rows, len(self._scrollback_lines))
                self.update()
                return
            if key == Qt.Key.Key_PageDown:
                self._scroll_offset = max(0, self._scroll_offset - self.rows)
                self.update()
                return
            self._send(mapping[key])
            return

        # Function keys
        if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F12:
            n = key - Qt.Key.Key_F1 + 1
            if n <= 4:
                self._send("\x1bOP"[0:2] + chr(ord("P") + n - 1).encode())
            else:
                self._send("\x1b[{}~".format(n).encode())
            return

        # Regular text
        text = event.text()
        if text:
            self._send(text.encode("utf-8"))

    def _send(self, data: bytes):
        self._scroll_offset = 0  # reset scroll on input
        self.data_sent.emit(data)

    # ----- Mouse / selection -----
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._selecting = True
            pos = self._pos_to_cell(event.position())
            self._sel_start = pos
            self._sel_end = pos
            self.update()

    def mouseMoveEvent(self, event):
        if self._selecting:
            self._sel_end = self._pos_to_cell(event.position())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._selecting = False

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        copy_action = menu.addAction(tr("ctx_copy"))
        paste_action = menu.addAction(tr("ctx_paste"))
        menu.addSeparator()
        clear_action = menu.addAction(tr("ctx_clear"))
        action = menu.exec(event.globalPos())
        if action == copy_action:
            self.copy_selection()
        elif action == paste_action:
            self.paste()
        elif action == clear_action:
            self._scrollback_lines.clear()
            self._scroll_offset = 0
            self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self._scroll_offset = min(self._scroll_offset + 3, len(self._scrollback_lines))
        else:
            self._scroll_offset = max(0, self._scroll_offset - 3)
        self.update()

    def _pos_to_cell(self, pos):
        col = int(pos.x() // self.char_w)
        row = int(pos.y() // self.char_h)
        return (row, col)

    def get_selected_text(self) -> str:
        if not self._sel_start or not self._sel_end:
            return ""
        r1, c1 = self._sel_start
        r2, c2 = self._sel_end
        if r1 > r2 or (r1 == r2 and c1 > c2):
            r1, r2 = r2, r1
            c1, c2 = c2, c1
        lines = []
        for r in range(r1, r2 + 1):
            line = ""
            start_c = c1 if r == r1 else 0
            end_c = c2 if r == r2 else self.cols - 1
            for c in range(start_c, end_c + 1):
                cell = self.screen.buffer.get(r, {}).get(c)
                line += cell.data if (cell and cell.data) else " "
            lines.append(line.rstrip())
        return "\n".join(lines)

    def copy_selection(self):
        text = self.get_selected_text()
        if text:
            QGuiApplication.clipboard().setText(text)

    def paste(self):
        text = QGuiApplication.clipboard().text()
        if text:
            self._send(text.replace("\n", "\r").encode("utf-8"))

    def clear(self):
        self.screen.reset()
        self.update()

    # ----- Scrollback management -----
    def push_scrollback(self):
        """Push the current top line to scrollback when screen scrolls."""
        # pyte handles scrolling internally; we capture via screen events.
        pass
