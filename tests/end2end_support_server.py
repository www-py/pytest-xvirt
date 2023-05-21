import socket
from pathlib import Path
import tempfile
from distutils.dir_util import copy_tree
from threading import Thread

import pytest

from xvirt.events import Evt, EvtCollectionFinish

tcp_port = 1234567890


# this file is run in inception-level-1; it is executed inside pytester

def pytest_xvirt_collect_file(file_path, path, parent, xvirt_package):
    remote_root = tempfile.mkdtemp('remote_root')
    copy_tree(xvirt_package, remote_root)
    (Path(remote_root) / 'conftest.py').write_text(_end2end_support_client)
    ss = SocketServer()

    def client_pytest():
        pytest.run(f'{remote_root}/')
        pass

    Thread(target=client_pytest, daemon=True).start()

    evt = ss.read_event()
    assert isinstance(evt, EvtCollectionFinish)
    from xvirt.collectors import VirtCollector
    result = VirtCollector.from_parent(parent, name=file_path.name)
    result.nodeid_array = evt.node_ids
    return result


class SocketServer:

    def __init__(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', tcp_port))
        s.listen(0)
        self.socket = s
        self.client = None

    def read_event(self) -> Evt:

        if self.client is None:
            client, _ = self.socket.accept()
            self.client = client

        # todo handle both mtu/chunking & carriage return as message delimiter
        data = self.client.recv(1024 * 16)
        json_str = data.decode()
        return Evt.from_json(json_str)


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 4569))
    server_socket.listen(2)

    while True:
        input('press enter to socket.accept9)')
        client_socket, addr = server_socket.accept()
        print("Got a connection from %s" % str(addr))
        data = client_socket.recv(1024)
        print("Received: %s" % data.decode('utf-8'))

        client_socket.close()


# language=python
_end2end_support_client = """
##end2end_support_client_marker##
"""
