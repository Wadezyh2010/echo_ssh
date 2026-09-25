"""
echo_ssh - Main Window
A modern SSH client with terminal emulation and real-time performance
monitoring. Built with PyQt6, paramiko, pyte, and pyqtgraph.
"""

import sys
import os

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QSpinBox,
    QPushButton, QLabel, QTabWidget, QSplitter, QStatusBar, QMenu, QFileDialog,
    QMessageBox, QApplication, QToolBar, QSizePolicy
)
from PyQt6.QtCore import QSettings

from styles import apply_theme
from terminal_widget import TerminalWidget
from ssh_session import SSHSession
from performance_monitor import PerformanceMonitor
from i18n import tr, set_language, get_language, LANGUAGES, APP_NAME


class SessionTab(QWidget):
    """A single session tab containing terminal + performance monitor."""

    def __init__(self, host, port, username, password=None, key_path=None, passphrase=None, parent=None):
        super().__init__(parent)
        self.host = host
        self.username = username
        self.session = SSHSession()
        self.terminal = TerminalWidget()
        self.perf_monitor = PerformanceMonitor(self.session)
        self.perf_monitor.setMaximumWidth(420)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.terminal)
        splitter.addWidget(self.perf_monitor)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

        # Wire up signals
        self.terminal.data_sent.connect(self.session.send)
        self.session.data_received.connect(self.terminal.feed)
        self.session.connected.connect(self._on_connected)
        self.session.disconnected.connect(self._on_disconnected)
        self.session.connection_failed.connect(self._on_failed)
        self.session.status_changed.connect(self._on_status)

        # Resize PTY when terminal resizes
        self.terminal.installEventFilter(self)
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._apply_pty_resize)

        # Start connection
        self.session.connect(host, port, username, password, key_path, passphrase)

    def eventFilter(self, obj, event):
        if obj is self.terminal and event.type() == event.Type.Resize:
            self._resize_timer.start(200)
        return super().eventFilter(obj, event)

    def _apply_pty_resize(self):
        self.session.resize_pty(self.terminal.cols, self.terminal.rows)

    def _on_connected(self):
        self._apply_pty_resize()
        self.perf_monitor.start()

    def _on_disconnected(self):
        self.perf_monitor.stop()
        self.terminal.feed(f"\r\n\r\n{tr('msg_disconnected')}\r\n".encode())

    def _on_failed(self, msg):
        self.perf_monitor.stop()
        self.terminal.feed(f"\r\n\r\n[{msg}]\r\n".encode())

    def _on_status(self, msg):
        if hasattr(self, "_status_cb"):
            self._status_cb(msg)

    def set_status_callback(self, cb):
        self._status_cb = cb

    def retranslate_ui(self):
        self.perf_monitor.retranslate_ui()

    def close(self):
        self.perf_monitor.stop()
        self.session.disconnect()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("window_title"))
        self.resize(1280, 800)
        self.setMinimumSize(960, 600)

        self._build_ui()
        self._build_menu()
        self.retranslate_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Connection bar
        conn_bar = QWidget()
        conn_bar.setObjectName("ConnectionBar")
        conn_bar.setFixedHeight(60)
        bar_layout = QHBoxLayout(conn_bar)
        bar_layout.setContentsMargins(12, 10, 12, 10)
        bar_layout.setSpacing(8)

        self.title_label = QLabel()
        self.title_label.setObjectName("TitleLabel")
        bar_layout.addWidget(self.title_label)

        self.host_input = QLineEdit()
        self.host_input.setMinimumWidth(220)
        bar_layout.addWidget(self.host_input)

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(22)
        self.port_input.setFixedWidth(70)
        self.port_label = QLabel()
        bar_layout.addWidget(self.port_label)
        bar_layout.addWidget(self.port_input)

        self.user_input = QLineEdit()
        self.user_input.setFixedWidth(120)
        bar_layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setFixedWidth(120)
        bar_layout.addWidget(self.pass_input)

        self.key_btn = QPushButton()
        self.key_btn.setFixedWidth(60)
        self.key_btn.clicked.connect(self._pick_key)
        bar_layout.addWidget(self.key_btn)

        self.key_path = None
        self.key_label = QLabel("")
        self.key_label.setStyleSheet("color: #6c7086; font-size: 11px;")
        self.key_label.setFixedWidth(140)
        bar_layout.addWidget(self.key_label)

        self.connect_btn = QPushButton()
        self.connect_btn.setObjectName("ConnectBtn")
        self.connect_btn.setFixedWidth(90)
        self.connect_btn.clicked.connect(self._connect)
        bar_layout.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton()
        self.disconnect_btn.setObjectName("DisconnectBtn")
        self.disconnect_btn.setFixedWidth(100)
        self.disconnect_btn.clicked.connect(self._disconnect_current)
        self.disconnect_btn.setEnabled(False)
        bar_layout.addWidget(self.disconnect_btn)

        bar_layout.addStretch(1)

        main_layout.addWidget(conn_bar)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._tab_changed)
        main_layout.addWidget(self.tabs, 1)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status_label = QLabel()
        self.status.addWidget(self.status_label)

        # Welcome tab
        self._show_welcome()

    def _build_menu(self):
        menubar = self.menuBar()

        self.file_menu = menubar.addMenu("")
        self.new_tab_act = QAction("", self)
        self.new_tab_act.setShortcut("Ctrl+N")
        self.new_tab_act.triggered.connect(self._connect)
        self.file_menu.addAction(self.new_tab_act)
        self.file_menu.addSeparator()
        self.exit_act = QAction("", self)
        self.exit_act.setShortcut("Ctrl+Q")
        self.exit_act.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_act)

        self.edit_menu = menubar.addMenu("")
        self.copy_act = QAction("", self)
        self.copy_act.setShortcut("Ctrl+Shift+C")
        self.copy_act.triggered.connect(self._copy_current)
        self.edit_menu.addAction(self.copy_act)
        self.paste_act = QAction("", self)
        self.paste_act.setShortcut("Ctrl+Shift+V")
        self.paste_act.triggered.connect(self._paste_current)
        self.edit_menu.addAction(self.paste_act)

        # Language menu
        self.lang_menu = menubar.addMenu("")
        self.lang_actions = {}
        for code, name in LANGUAGES.items():
            act = QAction(name, self)
            act.setCheckable(True)
            act.triggered.connect(lambda checked, c=code: self._switch_language(c))
            self.lang_menu.addAction(act)
            self.lang_actions[code] = act
        self._sync_lang_checks()

        self.help_menu = menubar.addMenu("")
        self.about_act = QAction("", self)
        self.about_act.triggered.connect(self._about)
        self.help_menu.addAction(self.about_act)

    def _sync_lang_checks(self):
        current = get_language()
        for code, act in self.lang_actions.items():
            act.setChecked(code == current)

    def _switch_language(self, code):
        if code == get_language():
            return
        set_language(code)
        self._sync_lang_checks()
        # Persist choice
        try:
            settings = QSettings(APP_NAME, "echo_ssh")
            settings.setValue("language", code)
        except Exception:
            pass
        self.retranslate_ui()
        # Notify the user
        self.status_label.setText(tr("lang_changed"))

    def _show_welcome(self):
        welcome = QWidget()
        layout = QVBoxLayout(welcome)
        layout.setContentsMargins(40, 40, 40, 40)

        self.welcome_title = QLabel()
        self.welcome_title.setStyleSheet("font-size: 28px; font-weight: 700; color: #89b4fa;")
        layout.addWidget(self.welcome_title)

        self.welcome_subtitle = QLabel()
        self.welcome_subtitle.setStyleSheet("font-size: 15px; color: #a6adc8; line-height: 1.6;")
        layout.addWidget(self.welcome_subtitle)

        layout.addSpacing(20)

        self.welcome_features = QLabel()
        self.welcome_features.setStyleSheet("font-size: 13px; color: #cdd6f4; line-height: 1.8;")
        layout.addWidget(self.welcome_features)

        layout.addSpacing(20)
        self.welcome_hint = QLabel()
        self.welcome_hint.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(self.welcome_hint)

        layout.addStretch(1)
        self._welcome_index = self.tabs.addTab(welcome, tr("welcome_tab"))

    def retranslate_ui(self):
        """Update all visible strings for the current language."""
        self.setWindowTitle(tr("window_title"))

        # Connection bar
        self.title_label.setText(tr("title_label"))
        self.host_input.setPlaceholderText(tr("host_placeholder"))
        self.port_label.setText(tr("port_label"))
        self.user_input.setPlaceholderText(tr("user_placeholder"))
        self.pass_input.setPlaceholderText(tr("pass_placeholder"))
        self.key_btn.setText(tr("key_btn"))
        self.connect_btn.setText(tr("connect_btn"))
        self.disconnect_btn.setText(tr("disconnect_btn"))

        # Menus
        self.file_menu.setTitle(tr("menu_file"))
        self.new_tab_act.setText(tr("menu_new_session"))
        self.exit_act.setText(tr("menu_exit"))
        self.edit_menu.setTitle(tr("menu_edit"))
        self.copy_act.setText(tr("menu_copy"))
        self.paste_act.setText(tr("menu_paste"))
        self.lang_menu.setTitle(tr("menu_language"))
        self.help_menu.setTitle(tr("menu_help"))
        self.about_act.setText(tr("menu_about"))

        # Status bar default
        self.status_label.setText(tr("status_ready"))

        # Welcome tab
        self.welcome_title.setText(tr("welcome_title"))
        self.welcome_subtitle.setText(tr("welcome_subtitle"))
        self.welcome_features.setText(tr("welcome_features"))
        self.welcome_hint.setText(tr("welcome_hint"))
        if hasattr(self, "_welcome_index"):
            self.tabs.setTabText(self._welcome_index, tr("welcome_tab"))

        # Retranslate all open session tabs
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, SessionTab):
                w.retranslate_ui()

    def _pick_key(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("msg_select_key"), os.path.expanduser("~/.ssh"),
            tr("msg_key_filter")
        )
        if path:
            self.key_path = path
            self.key_label.setText(os.path.basename(path))

    def _connect(self):
        host = self.host_input.text().strip()
        port = self.port_input.value()
        username = self.user_input.text().strip()
        password = self.pass_input.text()

        if not host:
            QMessageBox.warning(self, tr("msg_missing_host_title"), tr("msg_missing_host"))
            return
        if not username:
            QMessageBox.warning(self, tr("msg_missing_user_title"), tr("msg_missing_user"))
            return
        if not password and not self.key_path:
            QMessageBox.warning(self, tr("msg_missing_cred_title"), tr("msg_missing_cred"))
            return

        # Remove welcome tab if present
        if hasattr(self, "_welcome_index") and self.tabs.widget(self._welcome_index) is not None:
            welcome_widget = self.tabs.widget(self._welcome_index)
            if welcome_widget is not None and not isinstance(welcome_widget, SessionTab):
                self.tabs.removeTab(self._welcome_index)
                self._welcome_index = None

        tab = SessionTab(host, port, username, password, self.key_path)
        tab.set_status_callback(self.status_label.setText)
        idx = self.tabs.addTab(tab, f"{username}@{host}")
        self.tabs.setCurrentIndex(idx)
        self.disconnect_btn.setEnabled(True)

    def _disconnect_current(self):
        idx = self.tabs.currentIndex()
        if idx < 0:
            return
        widget = self.tabs.widget(idx)
        if isinstance(widget, SessionTab):
            widget.close()
            self.tabs.removeTab(idx)
        if self.tabs.count() == 0:
            self._show_welcome()
            self.disconnect_btn.setEnabled(False)

    def _close_tab(self, idx):
        widget = self.tabs.widget(idx)
        if isinstance(widget, SessionTab):
            widget.close()
        self.tabs.removeTab(idx)
        if self.tabs.count() == 0:
            self._show_welcome()
            self.disconnect_btn.setEnabled(False)

    def _tab_changed(self, idx):
        widget = self.tabs.currentWidget()
        self.disconnect_btn.setEnabled(isinstance(widget, SessionTab))

    def _copy_current(self):
        widget = self.tabs.currentWidget()
        if isinstance(widget, SessionTab):
            widget.terminal.copy_selection()

    def _paste_current(self):
        widget = self.tabs.currentWidget()
        if isinstance(widget, SessionTab):
            widget.terminal.paste()

    def _about(self):
        QMessageBox.about(
            self, tr("about_title"), tr("about_text")
        )

    def closeEvent(self, event):
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, SessionTab):
                w.close()
        event.accept()


def main():
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    apply_theme(app)

    # Restore saved language
    try:
        settings = QSettings(APP_NAME, "echo_ssh")
        saved_lang = settings.value("language", "zh")
        if saved_lang in LANGUAGES:
            set_language(saved_lang)
    except Exception:
        pass

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
