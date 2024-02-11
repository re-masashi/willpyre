from typing import Any, Tuple, Union
from urllib import parse
import email
import json
from .schema import error_schema, validate_json, ErrorResponse, schema_to_json


class TypedMultiMap(dict):
    def __init__(self, mapping: Union[Any, None] = None):
        if isinstance(mapping, TypedMultiMap):
            dict.__init__(self, ((k, l[:]) for k, l in mapping.lists()))  # type: ignore
        elif isinstance(mapping, dict):
            temp = dict()
            for key, value in mapping.items():
                if isinstance(value, (tuple, list)):
                    if len(value) == 0:
                        continue
                    value = list(value)
                else:
                    value = [value]
                temp[key] = value
            dict.__init__(self, temp)
        else:
            temp = {}
            for key, value in mapping or ():
                temp.setdefault(key, []).append(value)
            dict.__init__(self, temp)

    def __iter__(self):
        return dict.__iter__(self)

    def __getitem__(self, key):
        """
        Returns only the first item and None, if key does not exist.
        """

        if key in self:
            lst = dict.__getitem__(self, key)
            if len(lst) > 0:
                return lst[0]
            else:
                return lst
        return None

    def __setitem__(self, key, value):
        """
        Used for assigning the value to an index.
        .. code-block :: python

            a = TypedMultiMap()
            a["key"] = "value"

        """
        dict.__setitem__(self, key, [value])

    def add(self, key, value):
        """
        Inserts a key for the value given.
        """
        dict.setdefault(self, key, []).append(value)  # type: ignore

    def to_dict(self, flat=True):
        """
        Return the contents as regular dict.

        Args:
            Flat: If set to ``True``, only first item is present. Else, a list is present.\
            Defaults to ``False``
        """

        if flat:
            return dict(self.items())
        return dict(self.lists())  # type: ignore

    def get_all(self, key, type_: Any = None):
        """
        Fetches the list of all the items present.
        """
        try:
            rv = dict.__getitem__(self, key)
        except KeyError:
            return []
        if type is None:
            return list(rv)
        result = []
        for item in rv:
            try:
                result.append(type_(item))
            except ValueError:
                pass
        return result

    def get(self, key, default=None, type_=None):
        if key in self:
            lst = dict.__getitem__(self, key)
            if len(lst) > 0:
                rv = lst[0]
            else:
                rv = lst
            if type_ is not None:
                try:
                    rv = type_(rv)
                except ValueError:
                    return rv
            return rv
        return default

    def items(self, multi=False):
        """
        Args:
            multi: When set to ``True``, you get a list. Else, a value.
        """
        for key, values in dict.items(self):
            if multi:
                for value in values:
                    yield key, value
            else:
                yield key, values[0]


def parse_multipart(
    content_type: str, data: bytes, decode: bool = False
) -> Tuple[TypedMultiMap, TypedMultiMap]:  # pragma: no cover
    post_data = f"""Content-Type: {content_type}

        {data.decode()}"""
    msg = email.message_from_string(post_data)
    files = TypedMultiMap({})
    body = TypedMultiMap({})
    if msg.is_multipart():
        for part in msg.get_payload():
            name = part.get_param("name", header="content-disposition")
            filename = part.get_param("filename", header="content-disposition")
            payload = part.get_payload(decode=True)
            if filename is not None:
                files[name] = FileObject(
                    {"name": name, "content": payload.decode(), "filename": filename}
                )
            else:
                body[name] = payload
    return body, files


class Response:
    """


    This class contains the Response data to be sent,
    in a manageable format.
    The `response` argument of the functions defined,
    objects of this class.


    The response object does not require external parameters,
    but has some attributes which can be set:
    Args:
      headers(dict[str,str]):\
      It is the HTTP headers set as a dict. Only [content-type] =  text/html is set by default.
      cookies(dict[str,maglev.Structure.Cookie])
      body(str)
      status(int)

    """

    def __init__(
        self,
        status=200,
        content_type="text/html",
        body="",
        headers=TypedMultiMap({}),
        cookies=dict(),
    ):
        self.headers = headers
        self.cookies = cookies
        self.content_type = content_type
        self.headers["content-type"] = self.content_type
        self.body = body
        self.status = status
        self.get_body = lambda : self.body


class Request:
    """


    This class contains the information requested by the user.
    The functions called by ``maglev.Router.handle`` take this as the first argument.

    Args:
      headers(list[list[bytes,bytes]]): Array of headers passed by the server, and converts them to a dict.
      method(str): It is the HTTP request method.
      path(str):  It is the HTTP request path.
      query(dict[str,list[str]]): It is obtained from the server as a string and is then parsed into the dictionary with `urllib.parse.parse_qs`


    """

    def __init__(
        self,
        method: str,
        path: str,
        raw_body: bytes,
        raw_query: bytes,
        headers,
        *args,
    ):
        """

        Args:
          self: The class ``maglev.structure.Request``
          method(str): The HTTP method used by the client.
          path(str): The path requested by the client.
          headers(list): The HTTP headers obtained from the ASGI scope, of send.
          query(str): The ``GET`` query string, obtained from ASGI scope of send.
          body(str): The HTTP request body.

        """
        self.params, self.cookies = {}, {}

        self.headers = TypedMultiMap({})
        self.method = method
        self.path = path
        self.raw_query = raw_query
        self.raw_body = raw_body
        self.query = TypedMultiMap(parse.parse_qs(raw_query.decode()))
        for header_pair in headers:
            self.headers[header_pair[0].decode()] = header_pair[1].decode()

        # print("head", self.headers)
        content_type = self.headers.get("content-type", default="")
        self.content_type: str = content_type

        if content_type.startswith("multipart/form-data"):
            self.body, self.files = parse_multipart(content_type, self.raw_body)
            # print(self.files)
        elif content_type.startswith("application/json"):
            self.body = TypedMultiMap(json.loads(self.raw_body.decode()))
            self.files = TypedMultiMap({})
        else:
            self.body = TypedMultiMap(parse.parse_qs(raw_body.decode()))
            self.files = TypedMultiMap({})

        if "cookie" in self.headers.keys():
            [
                self.cookies.update({_.split("=")[0]: _.split("=")[1]})
                for _ in self.headers["cookie"].split(";")  # type: ignore
            ]


class Response404(Response):
    def __init__(self):
        super().__init__()
        self.headers["content-type"] = "text/html"
        self.body =   "Not found"
        self.status = 404


class Response405(Response):
    def __init__(self):
        super().__init__()
        self.headers["content-type"] = "text/html"
        self.body =   "Method not allowed"
        self.status = 405


class Response500(Response):
    def __init__(self):
        super().__init__()
        self.headers["content-type"] = "text/html"
        self.body =   "Internal Server Error"
        self.status = 500


class Response404JSON(Response):
    def __init__(self):
        super().__init__()
        self.headers["content-type"] = "text/json"
        self.body =   str(
            schema_to_json(error_schema("Not found", 404)),
        )
        self.status = 404


class Response405JSON(Response):
    def __init__(self):
        super().__init__()
        self.headers["content-type"] = "text/json"
        self.body =   str(
            schema_to_json(error_schema("Method is invalid", 405)),
        )
        self.status = 405


class Response500JSON(Response):
    def __init__(self):
        super().__init__()
        self.headers["content-type"] = "text/json"
        self.body =   str(schema_to_json(error_schema("Internal server error", 500)))
        self.status = 500


class Response422JSON(Response):
    def __init__(self):
        super().__init__()
        self.headers["content-type"] = "text/json"
        self.body =   str(schema_to_json(error_schema("Validation error", 422)))
        self.status = 422


class Redirect(Response):
    """
    Sends a redirect response to the user.
    Args:
    - location(str): Path to send the user after redirect.
    - status(int): The HTTP status during redirect. Defaults to 303.
    (More about redirects)[https://developer.mozilla.org/en-US/docs/Web/HTTP/Redirections]
    """

    def __init__(self, location: str, status: int = 303):
        super().__init__()
        self.body =   "Redirecting to " + location
        self.status = (
            status  # https://developer.mozilla.org/en-US/docs/Web/HTTP/Redirections
        )
        self.headers["location"] = location


class Cookie:
    """
    This class is used to send cookies to the user.

    Args:
        value(str): Cookie value
        max_age(int): Max age of the cookie (default = 0)
        same_site(str): Same-site attribute value (default = "Lax")
        secure(bool):Secure attribute of the cookie. (default=True)
        http_only(bool): If True, cookie cannot be accesed from JavaScript. (default = True)


    It is not a callable class.

    .. note ::
        Try to keep the http_only to True as it prevents XSS attacks.
        Attackers cannot steal cookies from users through Cross-Site scripting if it is set.
        However, it requires an HTTPS connection, so you can disable it during development.

    """

    __slots__ = ("value", "max_age", "cookie_str", "same_site", "secure", "http_only")

    def __init__(
        self,
        value: str,
        max_age: int = 0,
        same_site: str = "Lax",
        secure: bool = True,
        http_only: bool = True,
    ):
        """

        Args:
            value(str): The value of cookie.
            max_age(int): The max_age of the cookie. Defaults to zero.
            same_site(str): The value of the same_site attribute. Defaults to Lax. Find more about same_site in https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite
            secure(bool): Is the cookie a secure cookie or not. Defaults to True
            http_only(bool): States if the cookie is HttpOnly cookie.

        """
        self.value = value.encode()
        self.max_age = str(max_age).encode()
        self.same_site = same_site.encode()
        self.secure = secure
        self.http_only = http_only
        self.cookie_str = (
            self.value
            + b"; Max-Age="
            + self.max_age
            + b"; SameSite="
            + same_site.encode()
        )
        if secure is True:
            self.cookie_str += b"; Secure"
        if http_only is True:
            self.cookie_str += b"; HttpOnly"


class FileObject:
    __slots__ = ("content", "name", "filename")

    def __init__(self, args):
        self.content = args["content"]
        self.name = args["name"]
        self.filename = args["filename"]
        del args


class HTTPException(Exception, Response):
    def __init__(
        self, status: int = 404, body: str = "Not found", content_type="text/html"
    ):
        # Do not use super() here. Makes a mess of multiple inheritances.
        Response.__init__(self)
        self.status = 404
        self.content_type = content_type
        self.body =   body


class JSONResponse(Response):
    def __init__(
        self,
        data={},
        status=200,
        content_type="application/json",
        headers=TypedMultiMap({}),
        cookies=dict(),
    ):
        super().__init__(
            headers=headers, cookies=cookies, content_type=content_type, status=status
        )
        self.body =   json.dumps(data)


class TextResponse(Response):
    def __init__(
        self,
        data="",
        status=200,
        content_type="text/plain",
        headers=TypedMultiMap({}),
        cookies=dict(),
    ):
        super().__init__(
            headers=headers, 
            cookies=cookies, 
            content_type=content_type, 
            status=status,
        )
        self.body =   data


class HTMLResponse(Response):
    def __init__(
        self,
        data="",
        status=200,
        content_type="text/html",
        headers=TypedMultiMap({}),
        cookies=dict(),
    ):
        super().__init__(
            headers=headers, 
            cookies=cookies, 
            content_type=content_type, 
            status=status,
        )
        self.body =   data
