from . import structure


class ASGI:
    """
    Internal representation of an ASGI app.
    This is present inside the :class:willpyre.App.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # HTTP
        if scope["type"] == "http":
            body = await self._recieve(receive, scope["method"], b"")

            response_ = await self.app.router.handle(
                self.app.request_class(
                    method=scope["method"],
                    path=scope["path"],
                    headers=scope["headers"],
                    raw_query=scope["query_string"],
                    raw_body=body,
                ),
            )

            if response_.cookies is not dict():
                response_cookies = [
                    [
                        b"Set-Cookie",
                        cookie_.encode() + b"=" + response_.cookies[cookie_].cookie_str,
                    ]
                    for cookie_ in response_.cookies.keys()
                ]
            else:
                response_cookies = []

            await self._send(send, response_, response_cookies)

        # End HTTP
        # lifespan
        elif scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    self.app.config["startup"]()
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    self.app.config["shutdown"]()
                    await send({"type": "lifespan.shutdown.complete"})
                    return
        # End lifespan
        # WebSocket
        # Not implemented yet.
        # End WebSocket

    async def _recieve(self, receive, method: str, body: bytes) -> bytes:
        """
        Get the data in HTTP body as in POST and other bodied methods.
        """
        if method not in self.app.router.bodied_methods:
            return b""
        more_body = True
        while more_body:
            message = await receive()
            if message["type"] == "http.disconnect":
                break
            if message["type"] == "http.request":
                body += message.get("body", b"")
                more_body = message.get("more_body", False)
            else:
                raise RuntimeError(f"Unhandled message type: {message['type']}")
        return body

    async def _send(self, send, response: structure.Response, cookies: list) -> None:
        """
        Send HTTP body.
        """
        await send(
            {
                "type": "http.response.start",
                "status": response.status,
                "headers": [
                    [value.encode() for value in header_pair]
                    for header_pair in list(response.headers.items())
                ]
                + cookies,
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": response.get_body().encode(),
                "more_body": False,
            }
        )
