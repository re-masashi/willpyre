"""Willpyre. Fasten your seatbelts!"""


from . import router, app, structure
import json


__version__ = "0.0.4"

__all__ = ['JSONResponse', 'TextResponse', 'Router', 'App', 'Redirect']

Router, App, Cookie, Redirect = router.Router, app.App, structure.Cookie, structure.Redirect


class JSONResponse(structure.Response):
    def __init__(
            self,
            data,
            status=200,
            content_type="application/json",
            headers=structure.TypedMultiMap({}),
            cookies=dict()):
        super().__init__(headers=headers, cookies=cookies,
                         content_type=content_type, status=status)
        self.body = json.dumps(data)


class TextResponse(structure.Response):
    def __init__(
            self,
            data,
            status=200,
            content_type="text/plain",
            headers=structure.TypedMultiMap({}),
            cookies=dict()):
        super().__init__(headers=headers, cookies=cookies,
                         content_type=content_type, status=status)
        self.body = data
