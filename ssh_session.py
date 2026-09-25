"""
echo_ssh - SSH Session Manager
Handles SSH connections via paramiko: shell channel, data forwarding,
PTY resize, and connection state callbacks.
"""

import threading
import paramiko
from PyQt6.QtCore import QObject, pyqtSignal

from i18n import tr


class SSHSession(QObject):
    """Manages a single SSH connection and its interactive shell."""

    connected = pyqtSignal()
    disconnected = pyqtSignal()
    connection_failed = pyqtSignal(str)
    data_received = pyqtSignal(bytes)
    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.client = None
        self.channel = None
        self._recv_thread = None
        self._running = False
        self._host = ""
        self._port = 22

    def connect(self, host, port, username, password=None, key_path=None, passphrase=None):
        """Connect to an SSH server. Runs on a background thread."""
        self._host = host
        self._port = port
        self.status_changed.emit(tr("status_connecting", host=host, port=port))

        def _do_connect():
            try:
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                kwargs = dict(
                    hostname=host,
                    port=port,
                    username=username,
                    timeout=15,
                    allow_agent=False,
                    look_for_keys=False,
                )
                if key_path:
                    try:
                        pkey = paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
                    except Exception:
                        try:
                            pkey = paramiko.Ed25519Key.from_private_key_file(key_path, password=passphrase)
                        except Exception:
                            pkey = paramiko.ECDSAKey.from_private_key_file(key_path, password=passphrase)
                    kwargs["pkey"] = pkey
                else:
                    kwargs["password"] = password

                self.client.connect(**kwargs)
                self.status_changed.emit(tr("status_auth"))

                self.channel = self.client.invoke_shell(term="xterm-256color", width=80, height=24)
                self._running = True
                self.status_changed.emit(tr("status_connected", host=host, port=port))
                self.connected.emit()

                self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
                self._recv_thread.start()
            except paramiko.AuthenticationException:
                self.connection_failed.emit(tr("msg_auth_failed"))
            except paramiko.SSHException as e:
                self.connection_failed.emit(tr("msg_conn_failed", error=str(e)))
            except Exception as e:
                self.connection_failed.emit(tr("msg_conn_failed", error=str(e)))

        t = threading.Thread(target=_do_connect, daemon=True)
        t.start()

    def _recv_loop(self):
        while self._running and self.channel is not None:
            try:
                if self.channel.recv_ready():
                    data = self.channel.recv(65536)
                    if not data:
                        break
                    self.data_received.emit(data)
                else:
                    if self.channel.exit_status_ready():
                        break
                    import time
                    time.sleep(0.01)
            except Exception:
                break
        self._running = False
        self.disconnected.emit()

    def send(self, data: bytes):
        if self.channel and self._running:
            try:
                self.channel.send(data)
            except Exception:
                pass

    def resize_pty(self, cols, rows):
        if self.channel and self._running:
            try:
                self.channel.resize_pty(width=cols, height=rows)
            except Exception:
                pass

    def disconnect(self):
        self._running = False
        if self.channel:
            try:
                self.channel.close()
            except Exception:
                pass
            self.channel = None
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None
        self.disconnected.emit()

    def is_connected(self):
        return self._running and self.client is not None

    def exec_command(self, cmd: str) -> str:
        """Execute a command and return stdout. Used for performance monitoring."""
        if not self.client:
            return ""
        try:
            stdin, stdout, stderr = self.client.exec_command(cmd, timeout=10)
            return stdout.read().decode("utf-8", errors="replace")
        except Exception:
            return ""

    @property
    def host(self):
        return self._host
