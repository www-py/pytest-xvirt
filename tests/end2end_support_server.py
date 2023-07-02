import socket
import tempfile
from distutils.dir_util import copy_tree
from pathlib import Path
from threading import Thread

import pytest

from xvirt.events import Evt

tcp_port = 1234567890


# this file is run in inception-level-1; it is executed inside pytester

def pytest_xvirt_collect_file(file_path, path, parent, events_handler):
    remote_root = tempfile.mkdtemp('remote_root')
    copy_tree(file_path.parent, remote_root)
    (Path(remote_root) / 'conftest.py').write_text(_end2end_support_client)

    def run_pytest():
        pytest.main([str(remote_root)])

    Thread(target=run_pytest, daemon=True).start()
    return events_handler(ss.read_event)


class SocketServer:
    timeout = 1.0

    def __init__(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', tcp_port))
        s.listen(0)
        s.settimeout(self.timeout)
        self.socket = s

    def read_event(self) -> str:
        client, _ = self.socket.accept()
        client.settimeout(self.timeout)

        data = client.recv(1024 * 16)
        json_str = data.decode('utf-8')
        return json_str


ss = SocketServer()

# language=python
_end2end_support_client = """
##end2end_support_client_marker##
"""
