import sys
import ssl
import json
import certifi
import threading

import websockets
from rich import print as pretty_print

from .tcp import Client

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


async def open_tcp_tunnel(ws_uri, remote_server_host, local_server_port):
    async with websockets.connect(ws_uri, ssl=ssl_context) as websocket:
        message = json.loads(await websocket.recv())

        if message.get("warning"):
            pretty_print(
                f"[bold yellow]WARNING: {message['warning']}", file=sys.stderr)

        if message.get("error"):
            pretty_print(
                f"[bold yellow]ERROR: {message['error']}", file=sys.stderr)
            return

        local_server_host = '127.0.0.1'
        public_server_port = message["public_server_port"]
        private_server_port = message["private_server_port"]

        pretty_print(f"{'Tunnel Status:':<25}[bold green]Online")
        pretty_print(
            f"{'Forwarded:':<25}{f'[bold cyan]{remote_server_host}:{public_server_port} → 127.0.0.1:{local_server_port}'}")

        client = Client(
            remote_server_host=remote_server_host,
            remote_server_port=private_server_port,
            local_server_host=local_server_host,
            local_server_port=local_server_port,
        )

        while True:
            message = json.loads(await websocket.recv())
            pretty_print("[bold green]INFO: [bold white] New Connection +1")

            threading.Thread(
                target=client.process,
                args=(message, websocket)
            ).start()
