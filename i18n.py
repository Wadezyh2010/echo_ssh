"""
echo_ssh - Internationalization (i18n) module
Provides bilingual (中文 / English) translation support.
"""

APP_NAME = "echo_ssh"

# Supported languages
LANGUAGES = {
    "zh": "简体中文",
    "en": "English",
}

# Translation dictionaries. Keys are shared across languages.
TRANSLATIONS = {
    "zh": {
        # App identity
        "app_name": "echo_ssh",
        "window_title": "echo_ssh - 现代 SSH 客户端",
        "about_title": "关于 echo_ssh",
        "about_text": (
            "echo_ssh v1.1\n\n"
            "一款现代 SSH 客户端，集成终端仿真、\n"
            "实时性能监控、快捷命令与应用市场。\n\n"
            "基于 PyQt6、paramiko、pyte、pyqtgraph 构建。"
        ),

        # Connection bar
        "title_label": "echo_ssh",
        "host_placeholder": "主机（如 192.168.1.1 或 example.com）",
        "port_label": "端口:",
        "user_placeholder": "用户名",
        "pass_placeholder": "密码",
        "key_btn": "密钥...",
        "connect_btn": "连接",
        "disconnect_btn": "断开",

        # Menu
        "menu_file": "文件(&F)",
        "menu_new_session": "新建会话(&S)",
        "menu_exit": "退出(&X)",
        "menu_edit": "编辑(&E)",
        "menu_copy": "复制",
        "menu_paste": "粘贴",
        "menu_language": "语言",
        "menu_help": "帮助(&H)",
        "menu_about": "关于 echo_ssh",

        # Welcome tab
        "welcome_title": "欢迎使用 echo_ssh",
        "welcome_subtitle": (
            "一款现代 SSH 客户端，拥有简洁的终端界面和\n"
            "实时图形化性能监控。"
        ),
        "welcome_features": (
            "功能特性：\n"
            "  •  完整的终端仿真，支持 256 色\n"
            "  •  实时 CPU、内存、网络与磁盘性能图表\n"
            "  •  自动识别远程系统，提供快捷命令（更新/重启等）\n"
            "  •  应用市场：一键安装常用软件，新手友好\n"
            "  •  复制 / 粘贴（Ctrl+Shift+C / Ctrl+Shift+V 或右键菜单）\n"
            "  •  密码与 SSH 密钥认证\n"
            "  •  多会话标签页 · 中/英双语"
        ),
        "welcome_hint": "请在上方填写连接信息，然后点击「连接」开始使用。",
        "welcome_tab": "欢迎",

        # Status
        "status_ready": "就绪。请填写连接信息并点击「连接」。",
        "status_connecting": "正在连接 {host}:{port} ...",
        "status_auth": "认证成功，正在打开 Shell ...",
        "status_connected": "已连接到 {host}:{port}",

        # Messages
        "msg_missing_host_title": "缺少主机地址",
        "msg_missing_host": "请输入主机地址。",
        "msg_missing_user_title": "缺少用户名",
        "msg_missing_user": "请输入用户名。",
        "msg_missing_cred_title": "缺少认证信息",
        "msg_missing_cred": "请提供密码或 SSH 密钥。",
        "msg_auth_failed": "认证失败，请检查用户名/密码或密钥。",
        "msg_conn_failed": "连接失败：{error}",
        "msg_disconnected": "已断开连接",
        "msg_select_key": "选择 SSH 私钥文件",
        "msg_key_filter": "所有文件 (*);;PEM 文件 (*.pem)",

        # Terminal context menu
        "ctx_copy": "复制  (Ctrl+Shift+C)",
        "ctx_paste": "粘贴  (Ctrl+Shift+V)",
        "ctx_clear": "清空回滚缓冲",

        # Performance panel
        "perf_cpu": "CPU 使用率 (%)",
        "perf_mem": "内存使用率 (%)",
        "perf_net": "网络 I/O (KB/s)",
        "perf_disk": "磁盘 I/O (KB/s)",
        "metric_cpu": "CPU",
        "metric_mem": "内存",
        "metric_net_in": "网络 入",
        "metric_net_out": "网络 出",

        # Language switch notification
        "lang_changed": "语言已切换，新会话与欢迎页将使用新语言。",

        # Quick commands
        "qc_detecting": "识别系统中...",
        "qc_sysinfo": "系统信息",
        "qc_update": "更新软件包",
        "qc_disk": "磁盘使用",
        "qc_mem": "内存信息",
        "qc_top": "进程排行",
        "qc_reboot": "重启",
        "qc_shutdown": "关机",
        "qc_mirror": "换源",

        # Mirror switcher
        "mirror_title": "镜像源切换",
        "mirror_tip": "自动 ping 测试各镜像源延迟（越低越好）。点击后将自动注释官方源并写入所选镜像源。",
        "mirror_ping_progress": "正在测试 ping 延迟... %p%",
        "mirror_no_ping": "— (未连通)",
        "mirror_reping": "重新 ping",
        "mirror_switch": "切换到此源",
        "mirror_select_one": "请先选择一个镜像源",
        "mirror_not_supported": "该发行版暂不支持自动换源，请手动操作。",
        "mirror_not_connected": "请先连接远程主机再切换镜像源。",
        "mirror_confirm": "确认切换到「{mirror}」？\n\n将执行以下操作：\n  1. 备份当前 sources.list\n  2. 注释掉所有官方源\n  3. 写入所选镜像源地址\n  4. 运行 apt-get update\n\n继续？",

        # App market
        "market_detecting": "正在识别远程系统...",
        "market_install": "一键安装",
        "market_no_packages": "当前分类暂无适配此系统的软件包",
        "cat_all": "全部分类",
        "cat_dev": "开发工具",
        "cat_web": "网页服务",
        "cat_database": "数据库",
        "cat_system": "系统工具",
        "cat_network": "网络工具",
        "cat_security": "安全防护",
        "cat_media": "多媒体",
        "tab_performance": "性能监控",
        "tab_appmarket": "应用市场",
    },

    "en": {
        "app_name": "echo_ssh",
        "window_title": "echo_ssh - Modern SSH Client",
        "about_title": "About echo_ssh",
        "about_text": (
            "echo_ssh v1.1\n\n"
            "A modern SSH client with terminal emulation,\n"
            "real-time performance monitoring, quick commands\n"
            "and an app market.\n\n"
            "Built with PyQt6, paramiko, pyte, pyqtgraph."
        ),

        "title_label": "echo_ssh",
        "host_placeholder": "Host (e.g. 192.168.1.1 or example.com)",
        "port_label": "Port:",
        "user_placeholder": "Username",
        "pass_placeholder": "Password",
        "key_btn": "Key...",
        "connect_btn": "Connect",
        "disconnect_btn": "Disconnect",

        "menu_file": "&File",
        "menu_new_session": "New &Session",
        "menu_exit": "E&xit",
        "menu_edit": "&Edit",
        "menu_copy": "Copy",
        "menu_paste": "Paste",
        "menu_language": "Language",
        "menu_help": "&Help",
        "menu_about": "About echo_ssh",

        "welcome_title": "Welcome to echo_ssh",
        "welcome_subtitle": (
            "A modern SSH client with a clean terminal interface and\n"
            "real-time graphical performance monitoring."
        ),
        "welcome_features": (
            "Features:\n"
            "  •  Full terminal emulation with 256-color support\n"
            "  •  Real-time CPU, Memory, Network & Disk performance charts\n"
            "  •  Auto-detect remote OS with context-aware quick commands\n"
            "  •  App Market: one-click install of popular software\n"
            "  •  Copy / Paste (Ctrl+Shift+C / Ctrl+Shift+V or right-click)\n"
            "  •  Password & SSH key authentication\n"
            "  •  Multiple session tabs · 中文/English bilingual"
        ),
        "welcome_hint": "Fill in the connection details above and click Connect to begin.",
        "welcome_tab": "Welcome",

        "status_ready": "Ready. Enter connection details and click Connect.",
        "status_connecting": "Connecting to {host}:{port} ...",
        "status_auth": "Authenticated. Opening shell ...",
        "status_connected": "Connected to {host}:{port}",

        "msg_missing_host_title": "Missing host",
        "msg_missing_host": "Please enter a host address.",
        "msg_missing_user_title": "Missing username",
        "msg_missing_user": "Please enter a username.",
        "msg_missing_cred_title": "Missing credentials",
        "msg_missing_cred": "Please provide a password or SSH key.",
        "msg_auth_failed": "Authentication failed. Check username/password or key.",
        "msg_conn_failed": "Connection failed: {error}",
        "msg_disconnected": "[Disconnected]",
        "msg_select_key": "Select SSH private key",
        "msg_key_filter": "All files (*);;PEM files (*.pem)",

        "ctx_copy": "Copy  (Ctrl+Shift+C)",
        "ctx_paste": "Paste  (Ctrl+Shift+V)",
        "ctx_clear": "Clear scrollback",

        "perf_cpu": "CPU Usage (%)",
        "perf_mem": "Memory Usage (%)",
        "perf_net": "Network I/O (KB/s)",
        "perf_disk": "Disk I/O (KB/s)",
        "metric_cpu": "CPU",
        "metric_mem": "Memory",
        "metric_net_in": "Net In",
        "metric_net_out": "Net Out",

        "lang_changed": "Language switched. New sessions and the welcome page will use the new language.",

        # Quick commands
        "qc_detecting": "Detecting system...",
        "qc_sysinfo": "System Info",
        "qc_update": "Update Packages",
        "qc_disk": "Disk Usage",
        "qc_mem": "Memory Info",
        "qc_top": "Top Processes",
        "qc_reboot": "Reboot",
        "qc_shutdown": "Shutdown",
        "qc_mirror": "Switch Mirror",

        # Mirror switcher
        "mirror_title": "Mirror Source Switcher",
        "mirror_tip": "Automatically pings each mirror to test latency (lower is better). Clicking Switch will comment out the official sources and append the selected mirror.",
        "mirror_ping_progress": "Pinging mirrors... %p%",
        "mirror_no_ping": "— (unreachable)",
        "mirror_reping": "Re-ping",
        "mirror_switch": "Switch to this",
        "mirror_select_one": "Please select a mirror first.",
        "mirror_not_supported": "Automatic source switching is not supported for this distro yet.",
        "mirror_not_connected": "Please connect to a remote host before switching mirrors.",
        "mirror_confirm": "Switch to '{mirror}'?\n\nThis will:\n  1. Back up your current sources.list\n  2. Comment out all existing entries\n  3. Append the selected mirror\n  4. Run apt-get update\n\nContinue?",

        # App market
        "market_detecting": "Detecting remote system...",
        "market_install": "Install",
        "market_no_packages": "No packages for this system in the selected category",
        "cat_all": "All",
        "cat_dev": "Development",
        "cat_web": "Web Servers",
        "cat_database": "Databases",
        "cat_system": "System Tools",
        "cat_network": "Network",
        "cat_security": "Security",
        "cat_media": "Media",
        "tab_performance": "Performance",
        "tab_appmarket": "App Market",
    },
}

_current_lang = "zh"


def set_language(lang):
    """Set the current language. Falls back to zh if unknown."""
    global _current_lang
    if lang in TRANSLATIONS:
        _current_lang = lang


def get_language():
    return _current_lang


def tr(key, **kwargs):
    """Translate a key. Supports str.format-style keyword arguments."""
    text = TRANSLATIONS.get(_current_lang, TRANSLATIONS["zh"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text
