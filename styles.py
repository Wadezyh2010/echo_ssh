"""
echo_ssh - Modern QSS stylesheet
A clean, modern dark theme with accent colors.
"""

DARK_THEME = """
* {
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 13px;
}

QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

/* Top connection bar */
#ConnectionBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
}

QLineEdit {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    color: #cdd6f4;
    selection-background-color: #585b70;
}

QLineEdit:focus {
    border: 1px solid #89b4fa;
}

QLineEdit:disabled {
    color: #6c7086;
    background-color: #282838;
}

QSpinBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 5px 8px;
    color: #cdd6f4;
}

QPushButton {
    background-color: #45475a;
    border: none;
    border-radius: 6px;
    padding: 7px 16px;
    color: #cdd6f4;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #585b70;
}

QPushButton:pressed {
    background-color: #313244;
}

QPushButton#ConnectBtn {
    background-color: #40a02b;
    color: #ffffff;
}

QPushButton#ConnectBtn:hover {
    background-color: #54a83f;
}

QPushButton#ConnectBtn:pressed {
    background-color: #36871f;
}

QPushButton#DisconnectBtn {
    background-color: #d20f39;
    color: #ffffff;
}

QPushButton#DisconnectBtn:hover {
    background-color: #e64553;
}

/* Tab widget */
QTabWidget::pane {
    border: 1px solid #313244;
    border-radius: 6px;
    background-color: #1e1e2e;
}

QTabBar::tab {
    background-color: #181825;
    color: #a6adc8;
    padding: 8px 18px;
    border: 1px solid #313244;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #1e1e2e;
    color: #89b4fa;
    border-bottom: 2px solid #89b4fa;
}

QTabBar::tab:hover:!selected {
    background-color: #313244;
}

QTabBar::close-button {
    image: none;
    subcontrol-position: right;
    padding: 2px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #181825;
    width: 10px;
    border: none;
}

QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #181825;
    height: 10px;
    border: none;
}

QScrollBar::handle:horizontal {
    background: #45475a;
    border-radius: 5px;
    min-width: 30px;
}

/* Menu */
QMenu {
    background-color: #1e1e2e;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #45475a;
    color: #ffffff;
}

/* Status bar */
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
}

/* Labels */
QLabel {
    color: #cdd6f4;
}

QLabel#TitleLabel {
    font-size: 16px;
    font-weight: 600;
    color: #89b4fa;
}

QLabel#StatusLabel {
    color: #a6adc8;
}

QLabel#MetricValue {
    font-size: 20px;
    font-weight: 700;
    color: #a6e3a1;
}

QLabel#MetricLabel {
    color: #6c7086;
    font-size: 11px;
}

/* Group box for performance panel */
QGroupBox {
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    color: #cdd6f4;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #89b4fa;
    font-weight: 600;
}

/* Splitter */
QSplitter::handle {
    background-color: #313244;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}
"""


def apply_theme(app):
    """Apply the dark modern theme to the application."""
    app.setStyleSheet(DARK_THEME)
