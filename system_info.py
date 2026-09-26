"""
echo_ssh - System Information Detector
Auto-detects the remote operating system, distribution, and package manager
over SSH. Used to provide context-aware quick commands and app market.
"""

import re


class SystemInfo:
    """Holds detected information about the remote system."""

    def __init__(self):
        self.os_type = "linux"          # linux / bsd / unknown
        self.distro = "unknown"         # ubuntu / debian / centos / rhel / fedora / arch / alpine / opensuse / ...
        self.distro_name = "Unknown"    # Human-readable name
        self.version = ""
        self.package_manager = "unknown"  # apt / yum / dnf / pacman / zypper / apk / unknown
        self.sudo = ""                  # "sudo " if sudo available else ""
        self.detected = False

    def is_linux(self):
        return self.os_type == "linux"

    def is_debian_based(self):
        return self.package_manager == "apt"

    def is_rhel_based(self):
        return self.package_manager in ("yum", "dnf")

    def is_arch_based(self):
        return self.package_manager == "pacman"

    def is_suse_based(self):
        return self.package_manager == "zypper"

    def is_alpine(self):
        return self.package_manager == "apk"

    def summary(self):
        parts = [self.distro_name]
        if self.version:
            parts.append(self.version)
        if self.package_manager != "unknown":
            parts.append(f"({self.package_manager})")
        return " ".join(parts)


def detect_system(session) -> SystemInfo:
    """
    Detect the remote system by running commands over SSH.
    `session` must be a connected SSHSession with exec_command().
    """
    info = SystemInfo()
    if not session.is_connected():
        return info

    # Detect OS type via uname
    uname = session.exec_command("uname -s").strip().lower()
    if uname.startswith("linux"):
        info.os_type = "linux"
    elif "bsd" in uname:
        info.os_type = "bsd"
    elif uname.startswith("darwin"):
        info.os_type = "macos"
    else:
        info.os_type = "unknown"

    # Try /etc/os-release for distro info
    os_release = session.exec_command("cat /etc/os-release 2>/dev/null")
    distro_id = ""
    distro_version = ""
    distro_pretty = ""
    if os_release:
        for line in os_release.splitlines():
            line = line.strip()
            if line.startswith("ID="):
                distro_id = line[3:].strip().strip('"').lower()
            elif line.startswith("VERSION_ID="):
                distro_version = line[11:].strip().strip('"')
            elif line.startswith("PRETTY_NAME="):
                distro_pretty = line[12:].strip().strip('"')

    # Fallback: /etc/issue
    if not distro_id:
        issue = session.exec_command("cat /etc/issue 2>/dev/null").strip().lower()
        if "ubuntu" in issue:
            distro_id = "ubuntu"
        elif "debian" in issue:
            distro_id = "debian"
        elif "centos" in issue:
            distro_id = "centos"
        elif "red hat" in issue:
            distro_id = "rhel"
        elif "fedora" in issue:
            distro_id = "fedora"
        elif "arch" in issue:
            distro_id = "arch"
        elif "alpine" in issue:
            distro_id = "alpine"
        elif "suse" in issue or "opensuse" in issue:
            distro_id = "opensuse"

    info.distro = distro_id if distro_id else "unknown"
    info.version = distro_version
    info.distro_name = distro_pretty if distro_pretty else (distro_id.capitalize() if distro_id else "Unknown")

    # Determine package manager
    info.package_manager = _detect_package_manager(session, distro_id)

    # Check sudo availability
    sudo_check = session.exec_command("command -v sudo 2>/dev/null && echo yes || echo no").strip()
    info.sudo = "sudo " if sudo_check.endswith("yes") else ""

    info.detected = True
    return info


def _detect_package_manager(session, distro_id: str) -> str:
    """Detect the package manager, first by distro, then by command availability."""
    # Map distro to default package manager
    distro_pm = {
        "ubuntu": "apt", "debian": "apt", "linuxmint": "apt", "pop": "apt",
        "elementary": "apt", "kali": "apt", "raspbian": "apt", "deepin": "apt",
        "centos": "yum", "rhel": "yum", "redhat": "yum", "rocky": "dnf",
        "almalinux": "dnf", "fedora": "dnf", "amzn": "yum",
        "arch": "pacman", "manjaro": "pacman", "endeavouros": "pacman",
        "alpine": "apk",
        "opensuse": "zypper", "suse": "zypper", "opensuse-leap": "zypper",
        "opensuse-tumbleweed": "zypper",
        "gentoo": "emerge", "freebsd": "pkg",
    }
    if distro_id in distro_pm:
        return distro_pm[distro_id]

    # Fallback: check which package manager commands exist
    checks = [
        ("apt", "apt-get"),
        ("dnf", "dnf"),
        ("yum", "yum"),
        ("pacman", "pacman"),
        ("zypper", "zypper"),
        ("apk", "apk"),
    ]
    for pm_name, cmd in checks:
        result = session.exec_command(f"command -v {cmd} 2>/dev/null").strip()
        if result:
            return pm_name
    return "unknown"


# ---------- Package install commands per package manager ----------
def install_command(info: SystemInfo, packages: str) -> str:
    """Return the install command for the given packages based on detected PM."""
    s = info.sudo
    pm = info.package_manager
    if pm == "apt":
        return f"{s}apt-get update && {s}apt-get install -y {packages}"
    if pm == "dnf":
        return f"{s}dnf install -y {packages}"
    if pm == "yum":
        return f"{s}yum install -y {packages}"
    if pm == "pacman":
        return f"{s}pacman -Sy --noconfirm {packages}"
    if pm == "zypper":
        return f"{s}zypper --non-interactive install {packages}"
    if pm == "apk":
        return f"{s}apk add {packages}"
    return f"echo 'Package manager {pm} not supported; please install {packages} manually'"


def update_command(info: SystemInfo) -> str:
    """Return the system update command."""
    s = info.sudo
    pm = info.package_manager
    if pm == "apt":
        return f"{s}apt-get update && {s}apt-get upgrade -y"
    if pm == "dnf":
        return f"{s}dnf upgrade -y"
    if pm == "yum":
        return f"{s}yum update -y"
    if pm == "pacman":
        return f"{s}pacman -Syu --noconfirm"
    if pm == "zypper":
        return f"{s}zypper --non-interactive update"
    if pm == "apk":
        return f"{s}apk update && {s}apk upgrade"
    return "echo 'Package manager not supported'"


def reboot_command(info: SystemInfo) -> str:
    s = info.sudo
    return f"{s}reboot"


def shutdown_command(info: SystemInfo) -> str:
    s = info.sudo
    return f"{s}shutdown -h now"
