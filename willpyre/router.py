from typing import Any, Callable, Dict, List
from copy import deepcopy
import traceback
import re
from .kua import Routes
from .structure import (
    HTTPException,
    Request,
    Response,
    Response405,
    Response405JSON,
    Response500,
    Response404,
    Response422JSON,
    Response404JSON,
    Response500JSON,
    Response404JSON,
    JSONResponse,
    HTMLResponse,
)
from .schema import schema_repr
from .openapi import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
    gen_openapi_schema,
)


class StaticRouter:
    """
    StaticRouter class has the HTTP methods, paths, and handlers.
    Not meant for usage. Acts as a base class.
    """

    def __init__(self, endpoint_prefix=""):
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
        self.config = dict()
        self.endpoints = dict()
        self.endpoint_prefix = endpoint_prefix

    def add_route(
        self, path: str, method: str, handler: Callable, endpoint_name: str = ""
    ) -> None:
        if path[-1] != "/":
            path += "/"
        self.add_endpoint(path, endpoint_name)
        self.routes[method][path] = handler

    def add_method(self, method: str):  # pragma: no cover
        """
        This should be used to adding custom HTTP methods to the routing dictionary

        Args:
          self: The :class:`Router`
          method(str): The method to add for the router to handle.

        Raises:
          NotImplementedError

        """

        # self.routes[method] = {}
        raise NotImplementedError

    def add_endpoint(self, route: str, name: str = ""):
        if not name:
            return
        if name in self.endpoints:
            raise RuntimeError(
                f"Name exists with value {name}:{self.endpoints[name]} you cannot override !!!"
            )
        self.endpoints[self.endpoint_prefix + name] = route

    def endpoint_for(self, name: str) -> str:
        return self.endpoints[name]

    def get(self, path: str, name: str = "", **opts) -> Callable:
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
          name(str): Endpoint name, default is none.

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(path=path, method="GET", handler=handler, endpoint_name=name)
            return handler

        return decorator

    def post(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a post request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="POST", handler=handler, endpoint_name=name
            )
            return handler

        return decorator

    def put(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a put request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(path=path, method="PUT", handler=handler, endpoint_name=name)
            return handler

        return decorator

    def fetch(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a fetch request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="FETCH", handler=handler, endpoint_name=name
            )
            return handler

        return decorator

    def patch(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a PATCH request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="PATCH", handler=handler, endpoint_name=name
            )
            return handler

        return decorator

    def connect(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a connect request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="CONNECT", handler=handler, endpoint_name=name
            )
            return handler

        return decorator

    def options(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on an options request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="OPTIONS", handler=handler, endpoint_name=name
            )
            return handler

        return decorator

    def trace(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a trace request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="TRACE", handler=handler, endpoint_name=name
            )
            return handler

        return decorator

    async def handle(self, request, response) -> Response:
        """
        The handle function wil handle the requests and send appropriate responses,
        based on the functions defined.

        Args:
          request: :class:`willpyre.structure.Request`
          response: :class:`willpyre.structure.Response`
        Returns:
          :class:`willpyre.structure.Response`

        """
        if request.path[-1] != "/":
            request.path += "/"
        try:
            if request.method == "HEAD":
                response_ = await self.routes["GET"][request.path](request, response)
            else:
                response_ = await self.routes[request.method][request.path](
                    request, response
                )
            return response_
        except KeyError:
            resp = Response404()
            return resp


class Router(StaticRouter):
    """The Router class handles routing of URLs.
    You need to give an endpoint prefix if you are embedding it."""

    def __init__(self, endpoint_prefix: str = ""):
        self.validation_dict = {
            "int": lambda var: var.isdigit(),
            "lcase": lambda var: var.islower(),
            "ucase": lambda var: var.isupper(),
            "alnum": lambda var: var.isalnum(),
            # Everything is a str
            "str": lambda var: True,
            "nomatch": lambda var: False,
        }
        self.KuaRoutes = Routes(self.validation_dict)
        self.WSKuaRoutes = Routes(self.validation_dict)
        super().__init__(endpoint_prefix)

    def add_route(
        self, path: str, method: str, handler: Callable, endpoint_name: str = ""
    ) -> None:
        if path[-1] != "/":
            path += "/"
        variablized_url = self.KuaRoutes.add(path)
        self.add_endpoint(path, endpoint_name)
        self.routes[method][variablized_url] = handler

    def add_ws_route(self, path: str, method: str, handler: Callable) -> None:
        raise NotImplementedError("You need to implement websockets.")

    def embed_router(self, mount_at: str, router) -> None:
        if mount_at[0] == "/":
            mount_at = mount_at[1:]
        if mount_at[-1] == "/":
            mount_at = mount_at[:-1]
        if (self.KuaRoutes._max_depth - router.KuaRoutes._max_depth) < 1:
            self.KuaRoutes._max_depth = router.KuaRoutes._max_depth + 1

        self.KuaRoutes._routes[mount_at] = deepcopy(router.KuaRoutes._routes)
        if router.KuaRoutes._routes.get("", "NOT_FOUND") != "NOT_FOUND":
            self.KuaRoutes._routes[mount_at][":route"] = router.KuaRoutes._routes[""][
                ":route"
            ]
            self.KuaRoutes._routes[mount_at].pop("")

        [
            self.routes[method].update(
                (f"/{mount_at}{route}", router.routes[method][route])
                for route in router.routes[method]
            )
            for method in router.routes
        ]
        for endpoint in router.endpoints:
            self.add_endpoint(router.endpoints[endpoint], endpoint)

    async def handle(self, request: Request, response: Response) -> Response:
        if request.path[-1] != "/":
            request.path += "/"
        try:
            if request.method == "HEAD":
                response_routes = self.routes["GET"]
            else:
                response_routes = self.routes[request.method]
        except KeyError:
            # pdb.set_trace()
            # Key errors occur on when no method is found on a route.
            response_ = self.config.get("405Response", Response405())
            return response_
        except Exception:
            # Catches other errors.
            self.config.get("logger_exception", print)(traceback.format_exc())
            response_ = self.config.get("500Response", Response500())  # noqa
            return response_
        try:
            request.params, variablized_url = self.KuaRoutes.match(request.path)
            response_ = await response_routes[variablized_url](request, response)
            return response_
        except KeyError:
            response_ = self.config.get("404Response", Response404())
            return response_
        except HTTPException:
            response_ = self.config.get("404Response", Response404())
            return response_
        except Exception:
            # Catches other errors.
            self.config.get("logger_exception", print)(traceback.format_exc())
            response_ = self.config.get("500Response", Response500())
            return response_

    async def handleWS(self, scope: dict, send, recieve) -> None:  # pragma: no cover
        # path = scope["path"]
        # if path[-1] != '/':
        #     path += '/'
        # try:
        #     params, variablized_url = self.KuaRoutes.match(
        #         scope["path"])
        #     await self.ws_routes[variablized_url](scope, send, recieve)
        # except (HTTPError, KeyError):
        #    await self.send({"type": "websocket.close", "code": 1006})
        raise NotImplementedError("You need to implement websockets, to use it.")


class OpenAPIRouter(Router):  # pragma: no cover
    def __init__(
        self,
        description: str = "",
        schemes: list = ["http", "https"],
        version: str = "0.0.1",
        endpoint_prefix: str = "",
        openapi_url: str = "/openapi.json",
        oauth_redirect_url: str = "/docs/openapi-rediect",
        tos_url: str = "/terms-of-service",
        openapi_version: str = "3.0.0",
        title: str = "",
        docs_url="/docs",
        tags=[],
        dependencies=None,
        swagger_params=None,
        swagger_favicon: str = "/favicon.ico",
        definitions: List[Any] = [],
        license=None,
        contact=None,
        host=None,
    ) -> None:
        self.openapi_url = openapi_url
        self.version = version
        self.oauth2_redirect_url = oauth_redirect_url
        self.tos_url = tos_url
        self.openapi_version = openapi_version
        self.title = title
        self.tags = tags
        self.dependencies = dependencies
        self.docs_url = docs_url
        self.swagger_params = swagger_params
        self.paths = {}
        self.definitions = definitions
        self.license = license
        self.schemes = schemes
        self.description = description
        self.contact = contact
        self.host = host

        self.openapi_schema = {}

        super().__init__(endpoint_prefix)
        definitions_dict = {}
        for model in definitions:
            defn: Dict[str, Any] = {"type": "object"}
            name = model.__name__
            defn["properties"] = schema_repr(model)
            definitions_dict[name] = defn
        self.definitions_dict = definitions_dict

        # Init done. Post-init stuff here

        if self.openapi_url:

            async def openapi(req: Request, res: Response) -> JSONResponse:
                return JSONResponse(self.openapi())

            self.add_route(self.openapi_url, "GET", openapi, no_docs=True)

        async def swagger_ui_html(req: Request, res: Response) -> HTMLResponse:
            self.openapi_url
            oauth2_redirect_url = self.oauth2_redirect_url
            if oauth2_redirect_url:
                oauth2_redirect_url = oauth_redirect_url
            return get_swagger_ui_html(
                openapi_url=openapi_url,
                title=self.title + " | Swagger UI",
                oauth2_redirect_url=oauth2_redirect_url,
                init_oauth=None,  # todo: Create some init option
                swagger_params=self.swagger_params,
            )

        self.add_route(self.docs_url, "GET", swagger_ui_html, no_docs=True)

        if self.oauth2_redirect_url:

            async def swagger_ui_redirect(req: Request) -> Response:
                return get_swagger_ui_oauth2_redirect_html()

            self.add_route(
                self.oauth2_redirect_url, "GET", swagger_ui_redirect, no_docs=True
            )
            self.add_route(
                self.oauth2_redirect_url, "POST", swagger_ui_redirect, no_docs=True
            )
            self.add_route(
                self.oauth2_redirect_url, "PUT", swagger_ui_redirect, no_docs=True
            )

    def add_route(
        self,
        path: str,
        method: str,
        handler: Callable,
        # OpenAPI stuff now
        endpoint_name: str = "",
        response_model=None,
        status: int = 200,
        deprecated: bool = False,
        operation_id=None,
        summary: str = "",
        openapi_extra=None,
        tags=[],
        consumes=["application/json"],
        produces=["application/json"],
        parameters=["parameters"],
        responses={"200": {"description": ""}},
        security=[],
        path_parameters=[],
        auto_path_parameters=True,
        no_docs: bool = False,
        **kwargs,
    ):
        Router.add_route(self, path, method, handler)

        if no_docs:
            return

        path_ = path

        match = re.search(r"/:[^/]+", path_)

        while match:  # match becomes None when there are no more occurences
            var = match.group()[2:]
            if "|" not in var:
                var += "|str"
            var, validation = var.split("|")
            path_ = path_[: match.span()[0]] + "/{" + var + "}/"

            params = [{"name": var, "reqired": True, "type": validation, "in": "path"}]
            match = re.search(r"/:[^/]+", path_)

            if auto_path_parameters:
                path_parameters += params

        description = handler.__doc__

        if response_model:
            responses["200"]["schema"] = {"$ref": "#/definitions/" + response_model}

        self.paths[path_] = {}
        self.paths[path_][method.lower()] = {
            "tags": tags,
            "summary": summary,
            "consumes": consumes,
            "produces": produces,
            "parameters": path_parameters,
            "responses": responses,
            "description": description,
            "security": security,
        }

    def add_api_route(
        self,
        path: str,
        handler: Callable,
        methods: list = ["GET", "POST"],
        # OpenAPI stuff now
        endpoint_name: str = "",
        response_model=None,
        status: int = 200,
        deprecated: bool = False,
        operation_id=None,
        summary: str = "",
        openapi_extra=None,
        tags=[],
        consumes=["application/json"],
        produces=["application/json"],
        parameters=["parameters"],
        responses={"200": {"description": ""}},
        security=[],
    ):
        for method in methods:
            self.add_route(
                path,
                method,
                handler,
                # OpenAPI stuff now
                endpoint_name,
                response_model=response_model,
                status=status,
                deprecated=deprecated,
                operation_id=operation_id,
                summary=summary,
                openapi_extra=openapi_extra,
                tags=tags,
                consumes=consumes,
                produces=produces,
                parameters=parameters,
                responses=responses,
                security=[],
            )

    def get(self, path: str, name: str = "", **opts) -> Callable:
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
          name(str): Endpoint name, default is none.

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="GET", handler=handler, endpoint_name=name, **opts
            )
            return handler

        return decorator

    def post(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a post request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="POST", handler=handler, endpoint_name=name, **opts
            )
            return handler

        return decorator

    def put(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a put request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="PUT", handler=handler, endpoint_name=name, **opts
            )
            return handler

        return decorator

    def fetch(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a fetch request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="FETCH", handler=handler, endpoint_name=name, **opts
            )
            return handler

        return decorator

    def patch(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a PATCH request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="PATCH", handler=handler, endpoint_name=name, **opts
            )
            return handler

        return decorator

    def connect(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a connect request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="CONNECT", handler=handler, endpoint_name=name, **opts
            )
            return handler

        return decorator

    def options(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on an options request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="OPTIONS", handler=handler, endpoint_name=name, **opts
            )
            return handler

        return decorator

    def trace(self, path: str, name: str = "", **opts) -> Callable:
        """
        This is meant to be used as a decorator on a function, that will be executed on a trace request to the path.

        Args:
          self: :class:`Router`
          path(str): The Request path

        """

        def decorator(handler: Callable) -> Callable:
            self.add_route(
                path=path, method="TRACE", handler=handler, endpoint_name=name, **opts
            )
            return handler

        return decorator

    def openapi(self):
        if not self.openapi_schema:
            self.openapi_schema = gen_openapi_schema(
                title=self.title,
                version=self.version,
                openapi_version=self.openapi_version,
                description=self.description,
                terms_of_service=self.tos_url,
                license=self.license,
                routes=self.routes,
                tags=self.tags,
                contact=self.contact,
                host=self.host,
                paths=self.paths,
                definitions=self.definitions_dict,
            )
        return self.openapi_schema

    async def handle(self, request: Request, response: Response) -> Response:
        if request.path[-1] != "/":
            request.path += "/"
        try:
            if request.method == "HEAD":
                response_routes = self.routes["GET"]
            else:
                response_routes = self.routes[request.method]
        except KeyError:
            # pdb.set_trace()
            # Key errors occur on when no method is found on a route.
            response_ = self.config.get("405Response", Response405JSON())
            return response_
        except Exception:
            # Catches other errors.
            self.config.get("logger_exception", print)(traceback.format_exc())
            response_ = self.config.get("500Response", Response500JSON())  # noqa
            return response_
        try:
            request.params, variablized_url = self.KuaRoutes.match(request.path)
            response_ = await response_routes[variablized_url](request, response)
            return response_
        except KeyError:
            response_ = self.config.get("404Response", Response404JSON())
            return response_
        except HTTPException:
            response_ = self.config.get("422Response", Response422JSON())
            return response_
        except Exception:
            # Catches other errors.
            self.config.get("logger_exception", print)(traceback.format_exc())
            response_ = self.config.get("500Response", Response500JSON())
            return response_
