import sys
from urllib.parse import urljoin

import aiohttp
import bson
from rich import print as pretty_print


class Client:
    def __init__(self, base_uri, token):
        self.base_uri = base_uri
        self.token = token

    async def process(self, message, websocket):
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.request(
                    method=message['method'],
                    url=urljoin(self.base_uri, message['url']),
                    headers=message['header'],
                    data=message['body'],
                )
            except:
                pretty_print(
                    f"[bold red]FAIL: [white]Error Processing Request At: {message['url']}", file=sys.stderr)
                return {
                    'request_id': message['id'],
                    'token': self.token,
                    'status': 500,
                    'header': {},
                    'body': b'Error Performing Request',
                }

            pretty_print(
                f'[bold green]{"INFO:":<10} [white] {self.base_uri} - "[bold bright_red]{message["method"]} [white]{message["url"]}"[bold cyan] {response.status}')

            body = await response.read()
            response_message = {
                'request_id': message['id'],
                'token': self.token,
                'status': response.status,
                'header': dict(response.headers),
                'body': body,
            }

            await websocket.send(bson.dumps(response_message))
