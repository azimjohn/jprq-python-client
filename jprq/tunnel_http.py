import sys
import ssl
import bson
import certifi
import asyncio
import websockets
from rich import print as pretty_print

from .http import Client

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())


async def open_http_tunnel(ws_uri: str, http_uri):
    async with websockets.connect(ws_uri, ssl=ssl_context) as websocket:
        message = bson.loads(await websocket.recv())

        if message.get("warning"):
            pretty_print(
                f"[bold yellow]WARNING: {message['warning']}", file=sys.stderr)

        if message.get("error"):
            pretty_print(
                f"[bold yellow]ERROR: {message['error']}", file=sys.stderr)
            return

        host, token = message["host"], message["token"]

        pretty_print(f"{'Tunnel Status:':<25}[bold green]Online")
        pretty_print(
            f"{'Forwarded:':<25}{f'[bold cyan]{host} → {http_uri}'}")
        pretty_print(f"\n[bold bright_magenta]:tada: Visit: https://{host}\n")

        client = Client(http_uri, token)
        while True:
            message = bson.loads(await websocket.recv())
            asyncio.ensure_future(client.process(message, websocket))
