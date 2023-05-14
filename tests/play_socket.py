import socket


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


if __name__ == "__main__":
    start_server()
