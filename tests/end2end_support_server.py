import socket
import tempfile
from queue import Queue
from distutils.dir_util import copy_tree
from pathlib import Path
from threading import Thread

import pytest

from xvirt import XVirt


# this file is run in inception-level-1; it is executed inside pytester

def pytest_xvirt_setup(config):
    return XvirtTest1()


class XvirtTest1(XVirt):

    def __init__(self) -> None:
        self.ss = SocketServer(1234567890)  # this a placeholder marker

    def virtual_path(self) -> str:
        return '##xvirt_package_marker##'

    def run(self):
        remote_root = tempfile.mkdtemp('remote_root')
        copy_tree(self.virtual_path(), remote_root)
        (Path(remote_root) / 'conftest.py').write_text(_end2end_support_client)

        def run_pytest():
            pytest.main([str(remote_root)])

        Thread(target=run_pytest, daemon=True).start()

    def recv_event(self) -> str:
        return self.ss.recv_event()

    def finalize(self):
        (Path(__file__).parent / '##finalize_marker##').touch()


class SocketServer:
    timeout = 1.0

    def __init__(self, tcp_port) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', tcp_port))
        s.listen(0)
        s.settimeout(self.timeout)
        self.socket = s
        self.events = Queue()
        Thread(target=self._pipe_events, daemon=True).start()

    def _pipe_events(self):
        while True:
            client, _ = self.socket.accept()
            client.settimeout(self.timeout)

            data = client.recv(1024 * 16)
            json_str = data.decode('utf-8')
            self.events.put(json_str)

    def recv_event(self) -> str:
        return self.events.get(timeout=30)


# language=python
_end2end_support_client = """
##end2end_support_client_marker##
"""
