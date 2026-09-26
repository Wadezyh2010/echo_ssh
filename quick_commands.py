"""
echo_ssh - Quick Commands Toolbar
A row of one-click command buttons that adapt to the detected remote system.
Commands are sent to the interactive shell (shown in the terminal).
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QScrollArea, QFrame
)

from i18n import tr
from system_info import (
    SystemInfo, update_command, reboot_command, shutdown_command
)


class QuickCommands(QWidget):
    """A horizontal scrollable toolbar of quick command buttons."""

    command_requested = pyqtSignal(str)  # emits command to send to shell
    open_mirror_requested = pyqtSignal()  # request mirror dialog

    def __init__(self, system_info: SystemInfo, parent=None):
        super().__init__(parent)
        self.info = system_info
        self._buttons = []
        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(8, 6, 8, 6)
        outer.setSpacing(6)

        # System indicator label
        self.sys_label = QLabel()
        self.sys_label.setStyleSheet(
            "color: #89b4fa; font-weight: 600; font-size: 12px; padding: 0 8px;"
        )
        outer.addWidget(self.sys_label)

        # Scrollable button area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFixedHeight(40)

        inner = QWidget()
        self.btn_layout = QHBoxLayout(inner)
        self.btn_layout.setContentsMargins(0, 0, 0, 0)
        self.btn_layout.setSpacing(6)
        scroll.setWidget(inner)
        outer.addWidget(scroll, 1)

        self._update_sys_label()
        self._build_buttons()

    def _update_sys_label(self):
        if self.info and self.info.detected:
            self.sys_label.setText(f"🖥️ {self.info.distro_name} {self.info.version}")
        else:
            self.sys_label.setText(tr("qc_detecting"))

    def _build_buttons(self):
        # Clear existing buttons
        while self.btn_layout.count():
            item = self.btn_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._buttons = []

        cmds = self._get_commands()
        for icon, key, cmd in cmds:
            btn = QPushButton(f"{icon} {tr(key)}")
            btn.setStyleSheet(
                "QPushButton { background-color: #313244; color: #cdd6f4; border: none;"
                " border-radius: 6px; padding: 6px 12px; font-size: 12px; }"
                "QPushButton:hover { background-color: #45475a; }"
                "QPushButton:pressed { background-color: #585b70; }"
            )
            btn.clicked.connect(lambda checked, c=cmd: self.command_requested.emit(c + "\r"))
            self.btn_layout.addWidget(btn)
            self._buttons.append(btn)

        # Mirror switcher button (opens dialog, not a shell command)
        mirror_btn = QPushButton(f"🔁 {tr('qc_mirror')}")
        mirror_btn.setStyleSheet(
            "QPushButton { background-color: #f9e2af; color: #1e1e2e; border: none;"
            " border-radius: 6px; padding: 6px 12px; font-size: 12px; font-weight: 600; }"
            "QPushButton:hover { background-color: #fab387; }"
            "QPushButton:pressed { background-color: #f38ba8; }"
        )
        mirror_btn.clicked.connect(self.open_mirror_requested.emit)
        self.btn_layout.addWidget(mirror_btn)

        self.btn_layout.addStretch(1)

    def _get_commands(self):
        """Return list of (icon, i18n_key, command) based on detected system."""
        info = self.info

        cmds = [
            ("ℹ️", "qc_sysinfo", "uname -a"),
            ("📦", "qc_update", update_command(info) if info else "echo 'system not detected'"),
            ("🔥", "qc_top", "top -bn1 | head -20"),
            ("🔄", "qc_reboot", reboot_command(info) if info else "reboot"),
            ("⏻", "qc_shutdown", shutdown_command(info) if info else "shutdown -h now"),
        ]
        return cmds

    def set_system_info(self, info: SystemInfo):
        self.info = info
        self._update_sys_label()
        self._build_buttons()

    def retranslate_ui(self):
        self._build_buttons()
        self._update_sys_label()
