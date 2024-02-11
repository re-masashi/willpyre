"""Willpyre. Fasten your seatbelts!"""


from . import router, app, structure


__version__ = "0.0.12"

__all__ = [
    "JSONResponse",
    "TextResponse",
    "HTMLResponse",
    "Router",
    "OpenAPIRouter",
    "APIRouter",  # just a shorter alias
    "App",
    "Redirect",
]

Router = router.Router
App = app.App
Cookie = structure.Cookie
Redirect = structure.Redirect
OpenAPIRouter = router.OpenAPIRouter
APIRouter = OpenAPIRouter

JSONResponse = structure.JSONResponse
HTMLResponse = structure.HTMLResponse
TextResponse = structure.TextResponse
