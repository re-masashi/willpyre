from . import router, structure, asgi
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
        self._app = asgi.ASGI(self)

    async def __call__(self, scope, receive, send):
        await self._app(scope, receive, send)

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

    def add_middleware(self, middleware, **options)->None:
        self._app = middleware(self._app, **options)
