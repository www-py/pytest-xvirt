import os
import socket
import subprocess
from pathlib import Path
import tempfile
from distutils.dir_util import copy_tree
from threading import Thread
from time import sleep

import pytest

from xvirt.events import Evt, EvtCollectionFinish, EvtRuntestLogreport

tcp_port = 1234567890


# this file is run in inception-level-1; it is executed inside pytester

def pytest_xvirt_collect_file(file_path, path, parent):
    remote_root = tempfile.mkdtemp('remote_root')
    remote_root = '/home/simone/Documents/python/pytest-xvirt/fake_rem'
    copy_tree(file_path.parent, remote_root)
    (Path(remote_root) / 'conftest.py').write_text(_end2end_support_client)

    def run_pytest():
        pytest.main([str(remote_root)])

    Thread(target=run_pytest, daemon=True).start()
    sleep(0.2)  # todo fix timeout patch
    evt_cf = ss.read_event()
    assert isinstance(evt_cf, EvtCollectionFinish)
    from xvirt.collectors import VirtCollector
    result = VirtCollector.from_parent(parent, name=file_path.name)
    result.nodeid_array = evt_cf.node_ids

    # report phase
    config = parent.config
    recv_count = 0
    while recv_count < len(evt_cf.node_ids):
        evt_rep = ss.read_event()
        assert isinstance(evt_rep, EvtRuntestLogreport)
        rep = config.hook.pytest_report_from_serializable(config=config, data=evt_rep.data)
        config.hook.pytest_runtest_logreport(report=rep)
        recv_count += 1

    return result


class SocketServer:
    timeout = 20.0

    def __init__(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', tcp_port))
        s.listen(0)
        s.settimeout(self.timeout)
        self.socket = s

    def read_event(self) -> Evt:
        client, _ = self.socket.accept()
        client.settimeout(self.timeout)

        # todo handle both mtu/chunking & carriage return as message delimiter
        data = client.recv(1024 * 16)
        json_str = data.decode('utf-8')
        s = '-' * 20
        print('\n' + s + json_str + s + '\n')
        return Evt.from_json(json_str)


ss = SocketServer()

# language=python
_end2end_support_client = """
##end2end_support_client_marker##
"""
