import socket

from xvirt.events import Evt

tcp_port = 1234567890


# this file is run in inception-level-2; it is executed inside pytest that is executed inside a pytester

def pytest_xvirt_notify(event: Evt):
    evt_json = event.to_json()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', tcp_port))
    client_socket.sendall(evt_json.encode('utf-8'))
    client_socket.close()
