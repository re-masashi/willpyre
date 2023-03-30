from . import structure, asgi
from .router import Router, OpenAPIRouter
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
        self,
        router: Router,
        request_class: structure.Request = structure.Request,
        response: structure.Response = structure.Response(),
        config=None,
    ):
        def startup():
            pass

        def shutdown():
            pass

        if not config:
            self.config = {
                "startup": startup,
                "shutdown": shutdown,
                "logger": logging.debug,
            }
        self.request_class = request_class
        self.router = router
        self.response = response
        self._app = asgi.ASGI(self)

    async def __call__(self, scope, receive, send):
        await self._app(scope, receive, send)

    def add_middleware(self, middleware, **options) -> None:
        self._app = middleware(self._app, **options)
