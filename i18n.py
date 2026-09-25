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
            "echo_ssh v1.0\n\n"
            "一款现代 SSH 客户端，集成终端仿真与\n"
            "实时性能监控。\n\n"
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
            "  •  复制 / 粘贴（Ctrl+Shift+C / Ctrl+Shift+V 或右键菜单）\n"
            "  •  密码与 SSH 密钥认证\n"
            "  •  多会话标签页"
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
    },

    "en": {
        "app_name": "echo_ssh",
        "window_title": "echo_ssh - Modern SSH Client",
        "about_title": "About echo_ssh",
        "about_text": (
            "echo_ssh v1.0\n\n"
            "A modern SSH client with terminal emulation\n"
            "and real-time performance monitoring.\n\n"
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
            "  •  Copy / Paste (Ctrl+Shift+C / Ctrl+Shift+V or right-click)\n"
            "  •  Password & SSH key authentication\n"
            "  •  Multiple session tabs"
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
