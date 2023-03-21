from . import router, structure, asgi
import logging


class App:
    """
    The App class is used as the app.

    It which will be used for all activities.
    This requires a `Router` to be attached for serving responses accordingly.
    To instantiate a `name` value is also needed.
    The __call__ function has the ASGI app.
    """

    def __init__(
        self, router: router.Router, response: structure.Response = structure.Response()
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
                "500Response": structure.Response500(),
            },
        }
        self.router = router
        router.config = self.config["router_config"]
        self.response = response
        self._app = asgi.ASGI(self)

    async def __call__(self, scope, receive, send):
        await self._app(scope, receive, send)

    def add_middleware(self, middleware, **options) -> None:
        self._app = middleware(self._app, **options)
