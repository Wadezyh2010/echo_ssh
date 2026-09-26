"""
echo_ssh - Mirror / Sources Switcher
Provides pre-defined mirror sources per distro with ping latency tests
and one-click auto-switching (comment out official, append mirror).
"""

import threading
import time

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget,
    QListWidgetItem, QMessageBox, QProgressBar, QFrame
)

from i18n import tr
from system_info import SystemInfo


# ---------- Mirror definitions ----------
# Each mirror entry: (name_zh, name_en, base_url, apt_section_or_dir, test_cmd_hint)
# apt_section_or_dir = the mirror root path.
MIRRORS_APT = [
    ("阿里云", "Aliyun", "https://mirrors.aliyun.com/ubuntu", None),
    ("清华大学", "TUNA", "https://mirrors.tuna.tsinghua.edu.cn/ubuntu", None),
    ("中科大", "USTC", "https://mirrors.ustc.edu.cn/ubuntu", None),
    ("华为云", "Huawei", "https://repo.huaweicloud.com/ubuntu", None),
    ("腾讯云", "Tencent", "https://mirrors.tencent.com/ubuntu", None),
    ("网易", "163", "https://mirrors.163.com/ubuntu", None),
    ("Arch 官方", "Official Archive", "http://archive.ubuntu.com/ubuntu", None),
    ("CDN 官方", "CDN Archive", "http://cdn.archive.ubuntu.com/ubuntu", None),
]

MIRRORS_DEBIAN = [
    ("阿里云", "Aliyun", "https://mirrors.aliyun.com/debian", None),
    ("清华大学", "TUNA", "https://mirrors.tuna.tsinghua.edu.cn/debian", None),
    ("中科大", "USTC", "https://mirrors.ustc.edu.cn/debian", None),
    ("网易", "163", "https://mirrors.163.com/debian", None),
    ("Debian 官方", "Debian Official", "http://deb.debian.org/debian", None),
    ("Debian 安全", "Security", "http://security.debian.org/debian-security", None),
]

MIRRORS_CENTOS = [
    ("阿里云", "Aliyun", "https://mirrors.aliyun.com/centos", None),
    ("清华大学", "TUNA", "https://mirrors.tuna.tsinghua.edu.cn/centos-vault", None),
    ("华为云", "Huawei", "https://repo.huaweicloud.com/centos", None),
    ("腾讯云", "Tencent", "https://mirrors.tencent.com/centos", None),
]

MIRRORS_FEDORA = [
    ("阿里云", "Aliyun", "https://mirrors.aliyun.com/fedora", None),
    ("清华大学", "TUNA", "https://mirrors.tuna.tsinghua.edu.cn/fedora", None),
    ("华为云", "Huawei", "https://repo.huaweicloud.com/fedora", None),
    ("Fedora 官方", "Fedora Official", "https://download.fedoraproject.org/pub/fedora/linux", None),
]

MIRRORS_ARCH = [
    ("阿里云", "Aliyun", "https://mirrors.aliyun.com/archlinux/", None),
    ("清华大学", "TUNA", "https://mirrors.tuna.tsinghua.edu.cn/archlinux/$repo/os/$arch", None),
    ("中科大", "USTC", "https://mirrors.ustc.edu.cn/archlinux/$repo/os/$arch", None),
    ("华为云", "Huawei", "https://repo.huaweicloud.com/archlinux/$repo/os/$arch", None),
    ("Arch 官方", "Arch Official", "https://dlcdn.archlinux.org/", None),
]

MIRRORS_ALPINE = [
    ("阿里云", "Aliyun", "https://mirrors.aliyun.com/alpine", None),
    ("清华大学", "TUNA", "https://mirrors.tuna.tsinghua.edu.cn/alpine", None),
    ("Alpine 官方", "Alpine Official", "https://dl-cdn.alpinelinux.org/alpine", None),
]

MIRRORS_OPENSUSE = [
    ("阿里云", "Aliyun", "https://mirrors.aliyun.com/opensuse", None),
    ("清华大学", "TUNA", "https://mirrors.tuna.tsinghua.edu.cn/opensuse", None),
    ("openSUSE 官方", "openSUSE Official", "https://download.opensuse.org", None),
]


def get_mirrors(info: SystemInfo):
    if not info or not info.detected:
        return []
    d = info.distro.lower()
    if d == "ubuntu" or d == "pop" or d == "elementary":
        return MIRRORS_APT
    if d == "debian" or d == "kali" or d == "raspbian" or d == "deepin":
        return MIRRORS_DEBIAN
    if d in ("centos", "rhel", "redhat", "amzn") or info.package_manager == "yum":
        return MIRRORS_CENTOS
    if d in ("fedora", "rocky", "almalinux") or info.package_manager == "dnf":
        return MIRRORS_FEDORA
    if d in ("arch", "manjaro", "endeavouros") or info.package_manager == "pacman":
        return MIRRORS_ARCH
    if d == "alpine":
        return MIRRORS_ALPINE
    if d.startswith("opensuse") or d == "suse" or info.package_manager == "zypper":
        return MIRRORS_OPENSUSE
    return []


# ---------- Ping worker ----------
class PingWorker(QThread):
    progress = pyqtSignal(int, int)      # index, total
    result = pyqtSignal(int, float)      # index, latency_ms (-1 = fail)
    finished = pyqtSignal()

    def __init__(self, session, mirrors, parent=None):
        super().__init__(parent)
        self.session = session
        self.mirrors = mirrors
        self._stop = False

    def run(self):
        # Extract hostnames from URLs
        total = len(self.mirrors)
        for i, (zh, en, url, _) in enumerate(self.mirrors):
            if self._stop:
                break
            host = self._host_of(url)
            start = time.time()
            lat = -1.0
            if host:
                # ping 1 packet, max 2s, suppress output
                cmd = f"ping -c 1 -W 2000 {host} >/dev/null 2>&1 && echo OK || echo FAIL"
                out = self.session.exec_command(cmd).strip()
                if out.endswith("OK"):
                    lat = (time.time() - start) * 1000.0  # ms approx
                    lat = round(lat, 1)
            self.progress.emit(i + 1, total)
            self.result.emit(i, lat)
        self.finished.emit()

    def _host_of(self, url: str) -> str:
        try:
            # https://mirrors.tuna.tsinghua.edu.cn/ubuntu -> mirrors.tuna.tsinghua.edu.cn
            from urllib.parse import urlparse
            return urlparse(url).hostname or ""
        except Exception:
            return ""

    def stop(self):
        self._stop = True


# ---------- Dialog ----------
class MirrorDialog(QDialog):
    """Modal dialog for mirror selection with live ping latency."""

    switch_requested = pyqtSignal(str)  # emits shell command to run

    def __init__(self, session, info: SystemInfo, parent=None):
        super().__init__(parent)
        self.session = session
        self.info = info
        self.mirrors = get_mirrors(info)
        self._latencies = {}
        self._worker = None

        self.setWindowTitle(tr("mirror_title"))
        self.resize(560, 440)
        self.setStyleSheet(
            "QDialog { background-color: #1e1e2e; color: #cdd6f4; }"
            "QLabel { color: #cdd6f4; }"
            "QPushButton { background-color: #45475a; color: #cdd6f4; border: none;"
            " border-radius: 6px; padding: 8px 16px; font-weight: 500; }"
            "QPushButton:hover { background-color: #585b70; }"
            "QPushButton:disabled { background-color: #313244; color: #6c7086; }"
            "QPushButton#SwitchBtn { background-color: #89b4fa; color: #1e1e2e; font-weight: 700; }"
            "QPushButton#SwitchBtn:hover { background-color: #b4befe; }"
            "QListWidget { background-color: #181825; border: 1px solid #313244;"
            " border-radius: 8px; color: #cdd6f4; padding: 4px; }"
            "QListWidget::item { padding: 8px; border-radius: 4px; }"
            "QListWidget::item:selected { background-color: #313244; color: #89b4fa; }"
            "QListWidget::item:hover { background-color: #313244; }"
            "QProgressBar { background-color: #313244; border: none; border-radius: 4px; height: 8px; text-align: center; }"
            "QProgressBar::chunk { background-color: #89b4fa; border-radius: 4px; }"
        )

        self._build_ui()
        self._start_pings()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header
        tip = QLabel(tr("mirror_tip"))
        tip.setStyleSheet("color: #a6adc8; font-size: 12px;")
        tip.setWordWrap(True)
        layout.addWidget(tip)

        # System target
        target = QLabel(f"🎯  {self.info.distro_name} ({self.info.package_manager})")
        target.setStyleSheet("color: #a6e3a1; font-weight: 600;")
        layout.addWidget(target)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat(tr("mirror_ping_progress"))
        layout.addWidget(self.progress)

        # Mirror list
        self.list_widget = QListWidget()
        self._populate_list(self.mirrors, {})
        layout.addWidget(self.list_widget, 1)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.ping_btn = QPushButton(tr("mirror_reping"))
        self.ping_btn.clicked.connect(self._start_pings)
        btn_row.addWidget(self.ping_btn)

        self.switch_btn = QPushButton(tr("mirror_switch"))
        self.switch_btn.setObjectName("SwitchBtn")
        self.switch_btn.clicked.connect(self._do_switch)
        btn_row.addWidget(self.switch_btn)
        layout.addLayout(btn_row)

    def _populate_list(self, mirrors, latencies):
        self.list_widget.clear()
        items = []
        for i, (zh, en, url, _) in enumerate(mirrors):
            lat = latencies.get(i, -1.0)
            if lat < 0:
                lat_str = tr("mirror_no_ping")
                color = "#6c7086"
            else:
                lat_str = f"{lat:.1f} ms"
                if lat < 100:
                    color = "#a6e3a1"
                elif lat < 300:
                    color = "#f9e2af"
                else:
                    color = "#f38ba8"
            text = f"{zh} ({en})    ·    {lat_str}    ·    {url}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            item.setForeground(QColor(color))
            items.append(item)

        # Sort by latency ascending
        def key(it):
            idx = it.data(Qt.ItemDataRole.UserRole)
            lat = latencies.get(idx, 99999.0)
            return (lat, idx)
        items.sort(key=key)
        for it in items:
            self.list_widget.addItem(it)

    def _start_pings(self):
        self._latencies = {}
        self.progress.setValue(0)
        self.ping_btn.setEnabled(False)
        self.switch_btn.setEnabled(False)
        self._populate_list(self.mirrors, {})
        self.list_widget.clearSelection()
        if not self.mirrors:
            self.ping_btn.setEnabled(True)
            self.switch_btn.setEnabled(True)
            return
        self._worker = PingWorker(self.session, self.mirrors, self)
        self._worker.progress.connect(self._on_ping_progress)
        self._worker.result.connect(self._on_ping_result)
        self._worker.finished.connect(self._on_ping_done)
        self._worker.start()

    def _on_ping_progress(self, current, total):
        pct = int(100 * current / max(total, 1))
        self.progress.setValue(pct)

    def _on_ping_result(self, index, latency_ms):
        self._latencies[index] = latency_ms
        self._populate_list(self.mirrors, self._latencies)

    def _on_ping_done(self):
        self.ping_btn.setEnabled(True)
        self.switch_btn.setEnabled(True)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)  # auto-select lowest latency

    def _do_switch(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, tr("mirror_title"), tr("mirror_select_one"))
            return
        idx = self.list_widget.item(row).data(Qt.ItemDataRole.UserRole)
        mirror = self.mirrors[idx]
        cmd = build_switch_command(self.info, mirror)
        if not cmd:
            QMessageBox.warning(self, tr("mirror_title"), tr("mirror_not_supported"))
            return
        # Ask for confirmation
        ret = QMessageBox.question(
            self, tr("mirror_title"),
            tr("mirror_confirm").format(mirror=mirror[0]),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret != QMessageBox.StandardButton.Yes:
            return
        self.switch_requested.emit(cmd)
        self.accept()


# ---------- Command builder ----------
def build_switch_command(info: SystemInfo, mirror) -> str:
    """Build a single shell command that replaces the source list with the given mirror.
    Logic: backup → comment all existing lines → append mirror lines → apt-get update
    If vim is not installed, install it first."""
    zh, en, url, _ = mirror
    s = info.sudo if info else ""
    d = info.distro

    install_vim = (
        f"if ! command -v vim >/dev/null 2>&1; then "
        f"{_install_vim_cmd(info)}; fi; "
    )

    if d in ("ubuntu", "pop", "elementary", "debian", "kali", "raspbian", "deepin"):
        return install_vim + _switch_apt(info, url, zh, en)
    if d == "alpine":
        return install_vim + _switch_alpine(info, url, zh, en)
    if info.package_manager == "pacman":
        return install_vim + _switch_arch(info, url, zh, en)
    QMessageBox
    return ""


def _install_vim_cmd(info: SystemInfo) -> str:
    s = info.sudo if info else ""
    pm = info.package_manager
    if pm == "apt":
        return f"{s}apt-get update -y && {s}apt-get install -y vim"
    if pm == "dnf":
        return f"{s}dnf install -y vim"
    if pm == "yum":
        return f"{s}yum install -y vim"
    if pm == "pacman":
        return f"{s}pacman -Sy --noconfirm vim"
    if pm == "zypper":
        return f"{s}zypper --non-interactive install vim"
    if pm == "apk":
        return f"{s}apk add vim"
    return "echo 'please install vim manually'"


def _switch_apt(info: SystemInfo, url, zh, en) -> str:
    """Ubuntu/Debian apt sources.list replacement."""
    s = info.sudo
    ver = info.version or ""
    # Compute codename from os-release fallback (or ask via shell)
    backup = (
        f"{s}cp -f /etc/apt/sources.list /etc/apt/sources.list.bak.$(date +%Y%m%d%H%M%S); "
        f"{s}sed -i 's|^\\([^#]\\)|# \\1|g' /etc/apt/sources.list; "
    )
    mirror_block = f"""
# === echo_ssh mirror: {zh} ({en}) ===
deb {url} $(lsb_release -cs) main restricted universe multiverse
deb {url} $(lsb_release -cs)-updates main restricted universe multiverse
deb {url} $(lsb_release -cs)-security main restricted universe multiverse
# ====================================
""".strip()
    append = f"{s}bash -c \"cat >> /etc/apt/sources.list <<'EOF'\n{mirror_block}\nEOF\"\n"
    update = f"{s}apt-get update -y"
    return backup + append + update


def _switch_alpine(info: SystemInfo, url, zh, en) -> str:
    s = info.sudo
    backup = f"{s}cp -f /etc/apk/repositories /etc/apk/repositories.bak.$(date +%Y%m%d%H%M%S); "
    mirror_block = f"# === echo_ssh mirror: {zh} ({en}) ===\n{url}/$(cat /etc/alpine-release | cut -d. -f1-2)/main\n{url}/$(cat /etc/alpine-release | cut -d. -f1-2)/community\n# ===================================="
    append = f"{s}bash -c \"cat >> /etc/apk/repositories <<'EOF'\n{mirror_block}\nEOF\"\n"
    update = f"{s}apk update"
    return backup + append + update


def _switch_arch(info: SystemInfo, url, zh, en) -> str:
    s = info.sudo
    backup = f"{s}cp -f /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.bak.$(date +%Y%m%d%H%M%S); "
    append = (
        f"echo '# === echo_ssh mirror: {zh} ({en}) ===' | {s}tee -a /etc/pacman.d/mirrorlist; "
        f"echo 'Server = {url}' | {s}tee -a /etc/pacman.d/mirrorlist; "
        f"{s}pacman -Sy --noconfirm"
    )
    return backup + append
