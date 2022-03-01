import socket
import threading
from rich import print as pretty_print


def pump_read_to_write(read_conn, write_conn):
    size = 1024 * 256
    buffer = read_conn.recv(size)

    while buffer:
        try:
            write_conn.send(buffer)
            buffer = read_conn.recv(size)
        except (ConnectionResetError, BrokenPipeError):
            break

    read_conn.close()
    pretty_print("[bold red]Connection Closed!")


class Client:
    def __init__(self, remote_server_host, remote_server_port, local_server_host, local_server_port):
        self.remote_server_host = remote_server_host
        self.remote_server_port = remote_server_port
        self.local_server_host = local_server_host
        self.local_server_port = local_server_port

    def process(self, message, websocket):
        remote_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_client.connect(
            (self.remote_server_host, self.remote_server_port))

        local_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_client.connect((self.local_server_host, self.local_server_port))

        port = message["public_client_port"]
        remote_client.send(
            bytearray([port >> 8 & 0xFF, port & 0xFF]))  # 16 bits

        threading.Thread(target=pump_read_to_write, args=(
            remote_client, local_client)).start()
        threading.Thread(target=pump_read_to_write, args=(
            local_client, remote_client)).start()
