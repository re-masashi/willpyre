import typing
from . import structure
from . import kua


class StaticRouter:
    '''
    StaticRouter class has the HTTP methods, paths, and handlers.
    '''

    def __init__(self):
        self.routes = dict()
        self.routes["GET"] = {}
        self.routes["POST"] = {}
        self.routes["PUT"] = {}
        self.routes["FETCH"] = {}
        self.routes["HEAD"] = {}
        self.routes["PATCH"] = {}
        self.routes["CONNECT"] = {}
        self.routes["OPTIONS"] = {}
        self.routes["TRACE"] = {}

        self.bodied_methods = ("POST", "PUT", "PATCH")

        self.ws_routes = dict()

    def add_route(self, path: str, method: str, handler: typing.Callable) -> None:
        if path[-1] != '/':
            path += '/'
        self.routes[method][path] = handler

    def add_method(self, method: str):
        '''
        This should be used to adding HTTP methods to the routing dictionary 

        Args:
          self: The :class:`Router`
          method(str): The method to add for the router to handle.

        Raises:
          NotImplementedError

        '''

        #self.routes[method] = {}
        raise NotImplementedError

    def get(self, path: str, **opts) -> typing.Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a get query to the path.

        Usage::

            @router.get('/'):
            def landing(request,response):
              #Some application logic 
              return response



        Args:
          self: :class:`Router`
          path(str): The Request path


        """
        def decorator(handler: typing.Callable) -> typing.Callable:
            self.add_route(path=path, method="GET", handler=handler)
            return handler
        return decorator

    def post(self, path: str, **opts) -> typing.Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a post request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """
        def decorator(handler: typing.Callable) -> typing.Callable:
            self.add_route(path=path, method="POST", handler=handler)
            return handler
        return decorator

    def put(self, path: str, **opts) -> typing.Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a put request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """
        def decorator(handler: typing.Callable) -> typing.Callable:
            self.add_route(path=path, method="PUT", handler=handler)
            return handler
        return decorator

    def fetch(self, path: str, **opts) -> typing.Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a fetch request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """
        def decorator(handler: typing.Callable) -> typing.Callable:
            self.add_route(path=path, method="FETCH", handler=handler)
            return handler
        return decorator

    def patch(self, path: str, **opts) -> typing.Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a PATCH request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """
        def decorator(handler: typing.Callable) -> typing.Callable:
            self.add_route(path=path, method="PATCH", handler=handler)
            return handler
        return decorator

    def connect(self, path: str, **opts) -> typing.Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a connect request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """
        def decorator(handler: typing.Callable) -> typing.Callable:
            self.add_route(path=path, method="CONNECT", handler=handler)
            return handler
        return decorator

    def options(self, path: str, **opts) -> typing.Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on an options request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """
        def decorator(handler: typing.Callable) -> typing.Callable:
            self.add_route(path=path, method="OPTIONS", handler=handler)
            return handler
        return decorator

    def trace(self, path: str, **opts) -> typing.Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a trace request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """
        def decorator(handler: typing.Callable) -> typing.Callable:
            self.add_route(path=path, method="TRACE", handler=handler)
            return handler
        return decorator

    async def handle(self, request, response):
        '''
        The handle function wil handle the requests and send appropriate responses,
        based on the functions defined.

        Args:
          request: :class:`willpyre.structure.Request`
          response: :class:`willpyre.structure.Response`
        Returns:
          :class:`willpyre.structure.Response`

        '''
        if request.path[-1] != '/':
            request.path += '/'
        try:
            if request.method == "HEAD":
                response_ = await self.routes["GET"][request.path](request, response)
            else:
                response_ = await self.routes[request.method][request.path](request, response)
            return response_
        except KeyError:
            resp = structure.Response404()
            return resp
        # Value: Response object(9/8/21).


class Router(StaticRouter):

    def __init__(self, config: dict = {}):
        self.KuaRoutes = kua.Routes()
        self.WSKuaRoutes = kua.Routes()
        self.config = config
        super().__init__()

    def add_route(self, path: str, method: str, handler: typing.Callable) -> None:
        if path[-1] != '/':
            path += '/'
        variablized_url = self.KuaRoutes.add(path)
        self.routes[method][variablized_url] = handler

    def add_ws_route(self, path: str, method: str, handler: typing.Callable) -> None:
        if path[-1] != '/':
            path += '/'
        variablized_url = self.WSKuaRoutes.add(path)
        self.ws_routes[variablized_url] = handler

    def embed_router(self, endpoint: str, router) -> None:
        if endpoint[0] == '/':
            endpoint = endpoint[1:]
        if endpoint[-1] == '/':
            endpoint = endpoint[:-1]
        if (self.KuaRoutes._max_depth - router.KuaRoutes._max_depth) < 1:
            self.KuaRoutes._max_depth = router.KuaRoutes._max_depth + 1

        self.KuaRoutes._routes[endpoint] = router.KuaRoutes._routes
        if router.KuaRoutes._routes.get('', "NOT_FOUND") != "NOT_FOUND":
            self.KuaRoutes._routes[endpoint][":route"] = router.KuaRoutes._routes[''][':route']
            self.KuaRoutes._routes[endpoint].pop('')

        for method in router.routes.keys():
            for route in router.routes[method].keys():
                self.routes[method]['/' + endpoint + route] = router.routes[method][route]

        
    async def handle(self, request, response):
        if request.path[-1] != '/':
            request.path += '/'
        try:
            request.params, variablized_url = self.KuaRoutes.match(
                request.path)
            if request.method == "HEAD":
                response_ = await self.routes["GET"][variablized_url](request, response)
            else:
                response_ = await self.routes[request.method][variablized_url](request, response)
            return response_
        except (kua.RouteError, KeyError):
            response_ = self.config.get("404Response", structure.Response404())
            return response_

    async def handleWS(self, scope, send, recieve) -> None:
        path = scope["path"]
        if path[-1] != '/':
            path += '/'
        try:
            params, variablized_url = self.KuaRoutes.match(
                scope["path"])
            await self.ws_routes[variablized_url](scope, send, recieve)
        except (kua.RouteError, KeyError):
            await self.send({"type": "websocket.close", "code": 1006})
