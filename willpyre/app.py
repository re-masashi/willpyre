from . import router, structure
import logging
import asyncio


class App:
    '''
    The App class is used as the app.

    It which will be used for all activities.
    This requires a `Router` to be attached for serving responses accordingly.
    To instantiate a `name` value is also needed.
    The __call__ function has the ASGI app.
    '''

    def __init__(
        self,
        router: router.Router,
        response: structure.Response = structure.Response()
    ):
        def startup():
            pass

        def shutdown():
            pass

        self.config = {
            "startup": startup,
            "shutdown": shutdown,
            "logger": logging.debug,
            "router_config": {
                "logger_exception": logging.error,
                "logger_info": logging.info,
                "404Response": structure.Response404(),
                "405Response": structure.Response405(),
                "500Response": structure.Response500()
            },
        }
        self.router = router
        router.config = self.config["router_config"]
        self.response = response

    async def __call__(self, scope, receive, send):
        '''This will be serving as the ASGI app.
        The information about request will ge gained from the `scope` argument and response will be sent by `send`

        Args:
          self: The App class
          scope: The `scope` to communicate as per ASGI specification.
          recieve: ASGI recieve function
          send: ASGI send function
        '''
# HTTP
        if scope["type"] == "http":
            body = await self._recieve(receive, scope["method"], b'')

            response_ = await self.router.handle(
                structure.Request(
                    method=scope["method"],
                    path=scope["path"],
                    headers=scope["headers"],
                    raw_query=scope["query_string"],
                    raw_body=body
                ),
                self.response
            )

            if response_.cookies is not dict():
                response_cookies = [
                    [
                        b'Set-Cookie',
                        cookie_.encode() + b'=' +
                        response_.cookies[cookie_].cookie_str
                    ]
                    for cookie_ in response_.cookies.keys()]
            else:
                response_cookies = []

            resp_task = asyncio.ensure_future(
                self._send(send, response_, response_cookies))
            done, pending = await asyncio.wait(
                [resp_task], return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()

            await asyncio.gather(*pending, return_exceptions=True)

            for task in pending:
                if not task.cancelled() and task.exception() is not None:
                    raise task.exception()

            for task in done:
                if not task.cancelled() and task.exception() is not None:
                    raise task.exception()

# End HTTP
# lifespan
        elif scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message['type'] == 'lifespan.startup':
                    self.config["startup"]()
                    await send({'type': 'lifespan.startup.complete'})
                elif message['type'] == 'lifespan.shutdown':
                    self.config["shutdown"]()
                    await send({'type': 'lifespan.shutdown.complete'})
                    return
# End lifespan
# WebSocket
# Not implemented yet.
# End WebSocket

    async def _recieve(self, receive, method: str, body: bytes) -> None:
        '''
        Get the data in HTTP body as in POST and other bodied methods.
        '''
        if method not in self.router.bodied_methods:
            return b''
        more_body = True
        while more_body:
            message = await receive()
            if message["type"] == "http.disconnect":
                break
            if message["type"] == "http.request":
                body += message.get("body", b'')
                more_body = message.get("more_body", False)
            else:
                raise RuntimeError(
                    f"Unhandled message type: {message['type']}")
        return body

    async def _send(self, send, response: structure.Response, cookies: list) -> None:
        '''
        Send HTTP body.
        '''
        await send({
            'type': 'http.response.start',
            'status': response.status,
            'headers': [
                [value.encode() for value in header_pair] for header_pair in list(response.headers.items())
            ] + cookies
        })

        await send({
            'type': 'http.response.body',
            'body': response.body.encode(),
            'more_body': False
        })
