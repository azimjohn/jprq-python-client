import sys
import click
import asyncio
from getpass import getuser

from rich import print as pretty_print

from .tunnel_http import open_http_tunnel
from .tunnel_tcp import open_tcp_tunnel
from . import __version__


@click.group()
def main():
    pass


banner = f"""[bold cyan]
  (_)_ __  _ __ __ _ 
  | | '_ \| '__/ _` |
  | | |_) | | | (_| |
 _/ | .__/|_|  \__, |
|__/|_|           |_|
{f'v{__version__}':>14}

[bold yellow]Press Ctrl+C to quit.
"""


@main.command()
@click.argument('port')
@click.option('-s', '--subdomain', default='')
@click.option('--host', default='open.jprq.io')
def http(**kwargs):
    host, port = kwargs['host'], kwargs['port']
    username = kwargs['subdomain'] or getuser()

    pretty_print(banner)
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(
            open_http_tunnel(
                ws_uri=f'wss://{host}/_ws/?username={username}&port={port}&version={__version__}',
                http_uri=f'http://127.0.0.1:{port}',
            )
        )
    except KeyboardInterrupt:
        pretty_print(f"[bold red]\njprq tunnel closed!")
        sys.exit(1)


@main.command()
@click.argument('port', type=click.INT)
@click.option('--host', default='tcp.jprq.io')
def tcp(**kwargs):
    host, port = kwargs['host'], kwargs['port']

    pretty_print(banner)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            open_tcp_tunnel(
                remote_server_host=host,
                ws_uri=f'wss://{host}/_ws/',
                local_server_port=port
            )
        )
    except KeyboardInterrupt:
        pretty_print(f"[bold red]\njprq tunnel closed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
