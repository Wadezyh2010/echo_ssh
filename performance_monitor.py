"""
echo_ssh - Performance Monitor
Polls remote server metrics over SSH and renders real-time charts
using pyqtgraph. Shows CPU, memory, network I/O, and disk usage.
"""

import re
import time
from collections import deque

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QGridLayout
)
import pyqtgraph as pg

from i18n import tr


class PerformanceMonitor(QWidget):
    """Real-time performance panel for the connected remote host."""

    def __init__(self, ssh_session, parent=None):
        super().__init__(parent)
        self.session = ssh_session
        self._running = False

        # History buffers (last N samples)
        self._max_points = 60
        self._cpu_history = deque(maxlen=self._max_points)
        self._mem_history = deque(maxlen=self._max_points)
        self._net_in_history = deque(maxlen=self._max_points)
        self._net_out_history = deque(maxlen=self._max_points)
        self._disk_read_history = deque(maxlen=self._max_points)
        self._disk_write_history = deque(maxlen=self._max_points)

        # Previous samples for rate calculation
        self._prev_net = None
        self._prev_disk = None
        self._prev_cpu = None
        self._prev_time = None

        self._init_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._sample)
        self._timer.setInterval(2000)  # 2s sampling

    def _init_ui(self):
        pg.setConfigOptions(antialias=True, background="#1e1e2e", foreground="#cdd6f4")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Metric value cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(8)

        self.cpu_value, self.cpu_lbl = self._make_metric_card(cards_layout, tr("metric_cpu"), 0, 0)
        self.mem_value, self.mem_lbl = self._make_metric_card(cards_layout, tr("metric_mem"), 0, 1)
        self.net_in_value, self.net_in_lbl = self._make_metric_card(cards_layout, tr("metric_net_in"), 1, 0)
        self.net_out_value, self.net_out_lbl = self._make_metric_card(cards_layout, tr("metric_net_out"), 1, 1)

        layout.addLayout(cards_layout)

        # CPU chart
        self.cpu_group = QGroupBox(tr("perf_cpu"))
        cpu_layout = QVBoxLayout(self.cpu_group)
        self.cpu_plot = self._make_plot("#a6e3a1")
        self.cpu_curve = self.cpu_plot.plot(pen=pg.mkPen("#a6e3a1", width=2), fillLevel=0, brush=pg.mkBrush(40, 163, 80, 60))
        cpu_layout.addWidget(self.cpu_plot)
        layout.addWidget(self.cpu_group)

        # Memory chart
        self.mem_group = QGroupBox(tr("perf_mem"))
        mem_layout = QVBoxLayout(self.mem_group)
        self.mem_plot = self._make_plot("#89b4fa")
        self.mem_curve = self.mem_plot.plot(pen=pg.mkPen("#89b4fa", width=2), fillLevel=0, brush=pg.mkBrush(137, 180, 250, 60))
        mem_layout.addWidget(self.mem_plot)
        layout.addWidget(self.mem_group)

        # Network chart
        self.net_group = QGroupBox(tr("perf_net"))
        net_layout = QVBoxLayout(self.net_group)
        self.net_plot = self._make_plot("#f9e2af")
        self.net_in_curve = self.net_plot.plot(pen=pg.mkPen("#a6e3a1", width=2), name="In")
        self.net_out_curve = self.net_plot.plot(pen=pg.mkPen("#f38ba8", width=2), name="Out")
        net_layout.addWidget(self.net_plot)
        layout.addWidget(self.net_group)

        # Disk chart
        self.disk_group = QGroupBox(tr("perf_disk"))
        disk_layout = QVBoxLayout(self.disk_group)
        self.disk_plot = self._make_plot("#cba6f7")
        self.disk_read_curve = self.disk_plot.plot(pen=pg.mkPen("#89dceb", width=2), name="Read")
        self.disk_write_curve = self.disk_plot.plot(pen=pg.mkPen("#fab387", width=2), name="Write")
        disk_layout.addWidget(self.disk_plot)
        layout.addWidget(self.disk_group)

        layout.addStretch(1)

    def _make_metric_card(self, grid, title, row, col):
        card = QWidget()
        card.setStyleSheet(
            "QWidget { background-color: #181825; border: 1px solid #313244; "
            "border-radius: 8px; }"
        )
        v = QVBoxLayout(card)
        v.setContentsMargins(10, 8, 10, 8)
        lbl = QLabel(title)
        lbl.setStyleSheet("color: #6c7086; font-size: 11px; border: none;")
        val = QLabel("--")
        val.setStyleSheet("color: #a6e3a1; font-size: 20px; font-weight: 700; border: none;")
        v.addWidget(lbl)
        v.addWidget(val)
        grid.addWidget(card, row, col)
        return val, lbl

    def retranslate_ui(self):
        """Update all visible strings after a language change."""
        self.cpu_lbl.setText(tr("metric_cpu"))
        self.mem_lbl.setText(tr("metric_mem"))
        self.net_in_lbl.setText(tr("metric_net_in"))
        self.net_out_lbl.setText(tr("metric_net_out"))
        self.cpu_group.setTitle(tr("perf_cpu"))
        self.mem_group.setTitle(tr("perf_mem"))
        self.net_group.setTitle(tr("perf_net"))
        self.disk_group.setTitle(tr("perf_disk"))

    def _make_plot(self, color):
        plot = pg.PlotWidget()
        plot.setBackground("#181825")
        plot.showGrid(x=True, y=True, alpha=0.15)
        plot.setMenuEnabled(False)
        plot.setMouseEnabled(x=False, y=False)
        plot.hideButtons()
        plot.setYRange(0, 100, padding=0)
        plot.setXRange(0, self._max_points, padding=0)
        plot.getAxis("left").setPen(pg.mkPen("#45475a"))
        plot.getAxis("bottom").setPen(pg.mkPen("#45475a"))
        plot.getAxis("left").setTextPen("#a6adc8")
        plot.getAxis("bottom").setTextPen("#a6adc8")
        return plot

    def start(self):
        self._running = True
        self._timer.start()

    def stop(self):
        self._running = False
        self._timer.stop()

    def _sample(self):
        if not self._running or not self.session.is_connected():
            return

        now = time.time()
        dt = 1.0
        if self._prev_time is not None:
            dt = max(0.5, now - self._prev_time)
        self._prev_time = now

        # Sample all metrics in one command batch to reduce SSH overhead
        cmd = (
            "cat /proc/stat | head -1; "
            "free -b | awk '/Mem:/{print $2,$3}'; "
            "cat /proc/net/dev; "
            "cat /proc/diskstats"
        )
        out = self.session.exec_command(cmd)
        if not out:
            return

        lines = out.split("\n")
        try:
            cpu_line = lines[0].strip()
            self._update_cpu(cpu_line)
        except Exception:
            pass

        try:
            mem_line = lines[1].strip()
            self._update_mem(mem_line)
        except Exception:
            pass

        # Network
        self._update_net(lines[2:], dt)

        # Disk
        self._update_disk(lines, dt)

        self._update_curves()

    def _update_cpu(self, line):
        # cpu  user nice system idle iowait irq softirq ...
        parts = line.split()
        if len(parts) < 5:
            return
        vals = [int(x) for x in parts[1:]]
        idle = vals[3] if len(vals) > 3 else 0
        total = sum(vals)
        if self._prev_cpu is not None:
            prev_total, prev_idle = self._prev_cpu
            d_total = total - prev_total
            d_idle = idle - prev_idle
            if d_total > 0:
                usage = 100.0 * (1.0 - d_idle / d_total)
                usage = max(0.0, min(100.0, usage))
                self._cpu_history.append(usage)
                self.cpu_value.setText(f"{usage:.1f}%")
        self._prev_cpu = (total, idle)

    def _update_mem(self, line):
        parts = line.split()
        if len(parts) < 2:
            return
        try:
            total = int(parts[0])
            used = int(parts[1])
            if total > 0:
                pct = 100.0 * used / total
                self._mem_history.append(pct)
                self.mem_value.setText(f"{pct:.1f}%")
        except Exception:
            pass

    def _update_net(self, lines, dt):
        # Parse /proc/net/dev
        rx_total = 0
        tx_total = 0
        for line in lines:
            line = line.strip()
            if ":" not in line:
                continue
            iface_part, stats = line.split(":", 1)
            iface = iface_part.strip()
            if iface in ("lo",):
                continue
            stats = stats.split()
            if len(stats) < 16:
                continue
            try:
                rx_bytes = int(stats[0])
                tx_bytes = int(stats[8])
                rx_total += rx_bytes
                tx_total += tx_bytes
            except Exception:
                continue

        if self._prev_net is not None:
            prev_rx, prev_tx = self._prev_net
            d_rx = max(0, rx_total - prev_rx)
            d_tx = max(0, tx_total - prev_tx)
            rx_kbps = (d_rx / 1024.0) / dt
            tx_kbps = (d_tx / 1024.0) / dt
            self._net_in_history.append(rx_kbps)
            self._net_out_history.append(tx_kbps)
            self.net_in_value.setText(f"{rx_kbps:.1f} KB/s")
            self.net_out_value.setText(f"{tx_kbps:.1f} KB/s")
        self._prev_net = (rx_total, tx_total)

    def _update_disk(self, lines, dt):
        # Find diskstats section (after /proc/net/dev lines)
        read_total = 0
        write_total = 0
        disk_start = None
        for i, line in enumerate(lines):
            if line.startswith("  ram") or line.startswith("  loop") or line.startswith("   ") is False:
                pass
        # Simpler: scan lines that look like diskstats (many numeric fields)
        for line in lines:
            parts = line.split()
            if len(parts) >= 14:
                # diskstats: major minor name reads_merged ...
                try:
                    # field 3 = sectors read (512-byte sectors), field 7 = sectors written
                    sectors_read = int(parts[5])
                    sectors_written = int(parts[9])
                    # Skip loop/ram devices by name check
                    name = parts[2]
                    if name.startswith(("loop", "ram", "sr")):
                        continue
                    read_total += sectors_read * 512
                    write_total += sectors_written * 512
                except Exception:
                    continue

        if self._prev_disk is not None:
            prev_read, prev_write = self._prev_disk
            d_read = max(0, read_total - prev_read)
            d_write = max(0, write_total - prev_write)
            read_kbps = (d_read / 1024.0) / dt
            write_kbps = (d_write / 1024.0) / dt
            self._disk_read_history.append(read_kbps)
            self._disk_write_history.append(write_kbps)
        self._prev_disk = (read_total, write_total)

    def _update_curves(self):
        x = list(range(len(self._cpu_history)))
        if self._cpu_history:
            self.cpu_curve.setData(x, list(self._cpu_history))
        if self._mem_history:
            self.mem_curve.setData(x, list(self._mem_history))
        if self._net_in_history:
            nx = list(range(len(self._net_in_history)))
            self.net_in_curve.setData(nx, list(self._net_in_history))
            self.net_out_curve.setData(nx, list(self._net_out_history))
            self.net_plot.setYRange(0, max(1, max(self._net_in_history + self._net_out_history) * 1.1))
        if self._disk_read_history:
            dx = list(range(len(self._disk_read_history)))
            self.disk_read_curve.setData(dx, list(self._disk_read_history))
            self.disk_write_curve.setData(dx, list(self._disk_write_history))
            self.disk_plot.setYRange(0, max(1, max(self._disk_read_history + self._disk_write_history) * 1.1))
