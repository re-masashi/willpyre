# -*- coding: utf-8 -*-

import re
import urllib.parse
import collections
from functools import lru_cache
from typing import Any, Tuple, List, Sequence, Dict, Union, Callable, Iterator
from .structure import HTTPException
from .schema import ValidationError

__all__ = ["Routes", "RouteResolved"]

# This is a nested structure similar to a linked-list
WrappedVariablePartsType = Tuple[tuple, Tuple[str, str]]
VariablePartsType = Tuple[Union[str, Tuple[str]]]
VariablePartsIterType = Iterator[Union[str, Tuple[str]]]
ValidateType = Dict[str, Callable[[str], bool]]

RouteResolved = collections.namedtuple("RouteResolved", ["params"])
RouteResolved.__doc__ = """
    Resolved route

    :param dict params: Pattern variables\
    to URL parts
    :param object anything: Literally anything.\
    This is attached to the URL pattern when\
    registering it
    """


def depth_of(parts: Sequence[str]) -> int:
    """
    Calculate the depth of URL parts

    :param parts: A list of URL parts
    :return: Depth of the list

    :private:
    """
    return len(parts) - 1


def normalize_url(url: str) -> str:
    """
    Remove leading and trailing slashes from a URL

    :param url: URL
    :return: URL with no leading and trailing slashes

    :private:
    """
    if url.startswith("/"):
        url = url[1:]

    if url.endswith("/"):
        url = url[:-1]

    return url


def decode_parts(parts):
    try:
        return tuple(
            urllib.parse.unquote(part, encoding="utf-8", errors="strict")
            for part in parts
        )
    except UnicodeDecodeError:
        raise HTTPException(400, "Bad Request")


def _unwrap(variable_parts: WrappedVariablePartsType) -> VariablePartsIterType:
    """
    Yield URL parts. The given parts are usually in reverse order.
    """
    curr_parts = variable_parts
    var_any = []

    while curr_parts:
        curr_parts, (var_type, part) = curr_parts

        if var_type == Routes._VAR_ANY_NODE:
            var_any.append(part)
            continue

        if var_type == Routes._VAR_ANY_BREAK:
            if var_any:
                yield tuple(reversed(var_any))
                var_any.clear()

            var_any.append(part)
            continue

        if var_any:
            yield tuple(reversed(var_any))
            var_any.clear()
            yield part
            continue

        yield part

    if var_any:
        yield tuple(reversed(var_any))


def unwrap(variable_parts: WrappedVariablePartsType) -> VariablePartsType:
    return tuple(reversed(tuple(_unwrap(variable_parts))))


def make_params(
    key_parts: Sequence[str], variable_parts: VariablePartsIterType
) -> Dict:
    """
    Map keys to variables. This map\
    URL-pattern variables to\
    a URL related parts

    :param key_parts: A list of URL parts
    :param variable_parts: A list of URL parts
    :return: The param dict with the values\
    assigned to the keys

    :private:
    """
    return dict(zip(key_parts, variable_parts))


def validate(
    key_parts: Sequence[str],
    variable_parts,
    params_validate: dict,
    validation_dict: dict,
) -> bool:
    for var in variable_parts:
        if isinstance(var, tuple):
            return True

    return all(
        validation_dict[params_validate[param]](value)
        for param, value in zip(key_parts, variable_parts)
    )


_Route = collections.namedtuple("_Route", ["key_parts", "validate"])
_Route.__doc__ = """
    Route pattern state. Every pattern has one of this.

    :param tuple key_parts: Pattern variable names
    :param object anything: Literally anything. For retrieving later
    :param dict validate: A map of ``{var: validator}``

    :private:
    """


def _route(key_parts: Sequence, validate: ValidateType) -> _Route:
    key_parts = tuple(key_parts)
    validate = validate or {}

    if not set(validate.keys()).issubset(set(key_parts)):
        raise RuntimeError(
            "{missing_vars} not found within the pattern".format(
                missing_vars=set(validate.keys()).difference(set(key_parts))
            )
        )

    return _Route(key_parts=key_parts, validate=validate)


def _resolve(variable_parts, routes: Sequence[_Route], validation_dict: dict) -> Any:
    for route in routes:
        if validate(route.key_parts, variable_parts, route.validate, validation_dict):
            return make_params(key_parts=route.key_parts, variable_parts=variable_parts)

        raise ValidationError("Invalid param type.")
    return None


class Routes:
    """
    Route URLs to registered URL patterns.

    Thread safety: every method has a doc note about this

    URL matcher supports ``:var`` for matching dynamic\
    path parts and ``:*var`` for matching multiple parts.

    Path parts have precedence: ``static > var > *var``.

    Usage::

        routes = willpyre.kua.Routes()
        routes.add('api/:foo')
        route = routes.match('api/hello-world')
        route.params
        # {'foo': 'hello-world'}

        # Matching any path
        routes.add('assets/:*foo')
        route = routes.match('assets/user/profile/avatar.jpg')
        route.params
        # {'foo': ('user', 'profile', 'avatar.jpg')}

        # Typed vars
        is_num = lambda part: part.isdigit()
        routes.add('api/user/:id')
        route = routes.match('api/user/123')
        route.params
        # {'id': '123'}

    :ivar max_depth: The maximum URL depth\
    (number of parts) willing to match. This only\
    takes effect when one or more URLs matcher\
    make use of any-var (i.e: ``:*var``), otherwise the\
    depth of the deepest URL is taken.
    """

    _VAR_NODE = ":var"
    _VAR_ANY_NODE = ":*var"
    _ROUTE_NODE = ":route"
    _VAR_ANY_BREAK = ":*var:break"

    def __init__(self, validation_dict: dict, max_depth: int = 10) -> None:
        """
        :ivar _routes: \
        Contain a graph with the parts of\
        each URL pattern. This is referred as\
        "partial route" later in the docs.
        :vartype _routes: dict
        :ivar _max_depth: Depth of the deepest\
        registered pattern
        :vartype _max_depth: int

        :private-vars:
        """
        self._max_depth_custom = max_depth
        self.validation_dict = validation_dict
        # Routes graph format for 'foo/:foobar/bar':
        # {
        #   'foo': {
        #       ':var': {
        #           'bar': {
        #               ':route': [_Route(), ...],
        #               ...
        #           },
        #           ...
        #        }
        #        ...
        #   },
        #   ...
        # }
        self._routes = {}
        self._max_depth = 0

    def _deconstruct_url(self, url: str) -> List[str]:
        """
        Split a regular URL into parts

        :param url: A normalized URL
        :return: Parts of the URL
        :raises kua.routes.RouteError: \
        If the depth of the URL exceeds\
        the max depth of the deepest\
        registered pattern

        :private:
        """
        parts = url.split("/", self._max_depth + 1)

        if depth_of(parts) > self._max_depth:
            raise HTTPException

        return parts

    def _match(self, parts: Sequence[str]) -> RouteResolved:
        """
        Match URL parts to a registered pattern.

        This function is basically where all\
        the CPU-heavy work is done.

        :param parts: URL parts
        :return: Matched route
        :raises kua.routes.RouteError: If there is no match

        :private:
        """
        # (route_partial, variable_parts, depth)
        # type: List[Tuple[dict, tuple, int]]
        to_visit = [(self._routes, tuple(), 0)]

        # Walk through the graph,
        # keep track of all possible
        # matching branches and do
        # backtracking if needed
        while to_visit:
            curr, curr_variable_parts, depth = to_visit.pop()

            try:
                part = parts[depth]
            except IndexError:
                if self._ROUTE_NODE not in curr:
                    continue
                route_resolved = _resolve(
                    variable_parts=unwrap(curr_variable_parts),
                    routes=curr[self._ROUTE_NODE],
                    validation_dict=self.validation_dict,
                )

                if route_resolved is None:
                    continue

                return route_resolved

            if self._VAR_ANY_NODE in curr:
                to_visit.append(
                    (
                        {self._VAR_ANY_NODE: curr[self._VAR_ANY_NODE]},
                        (curr_variable_parts, (self._VAR_ANY_NODE, part)),
                        depth + 1,  # type: ignore
                    )
                )
                to_visit.append(
                    (
                        curr[self._VAR_ANY_NODE],
                        (curr_variable_parts, (self._VAR_ANY_BREAK, part)),
                        depth + 1,  # type: ignore
                    )
                )

            if self._VAR_NODE in curr:
                to_visit.append(
                    (
                        curr[self._VAR_NODE],
                        (curr_variable_parts, (self._VAR_NODE, part)),
                        depth + 1,  # type: ignore
                    )
                )

            if part in curr:
                to_visit.append((curr[part], curr_variable_parts, depth + 1))  # type: ignore

        raise HTTPException()

    @lru_cache(maxsize=512)
    def match(self, url: str) -> Any:
        """
        Match a URL to a registered pattern.

        This method is thread-safe.

        :param url: URL
        :return: Matched route
        :raises kua.RouteError: If there is no match
        """
        original_url = url
        url = normalize_url(url)
        parts = self._deconstruct_url(url)

        if "%" in url:
            parts = decode_parts(parts)

        route_match = self._match(parts)

        for param in list(route_match.keys()):
            route_param: Union[Tuple, str] = route_match[param]  # type: ignore
            if isinstance(route_param, str):
                original_url = original_url.replace(route_param, param, 1)
            else:  # param is a list
                original_url = original_url.split(route_param[0])[0] + param

        if original_url[-1] != "/":
            original_url += "/"
        if original_url[0] != "/":
            original_url = "/" + original_url

        return route_match, original_url

    def add(self, url: str) -> Any:
        """
        Register a URL pattern into\
        the routes for later matching.

        Registration order does not matter.\
        Adding a URL first or last makes no difference.

        :param url: URL to be added.
        """
        url = normalize_url(url)
        parts = url.split("/")
        curr_partial_routes = self._routes
        curr_key_parts = []
        variablized_url = "/"
        validation = "str"
        validate = {}
        for part in parts:
            if part.startswith(":*"):
                curr_key_parts.append(part[2:])
                variablized_url += part[2:] + "/"
                part = self._VAR_ANY_NODE
                self._max_depth = self._max_depth_custom

            elif part.startswith(":"):
                _part = part[1:]
                if "|" not in _part:
                    _part += "|str"

                _part, validation = _part.split("|")
                validate[_part] = validation
                curr_key_parts.append(_part)
                variablized_url += _part + "/"
                part = self._VAR_NODE
            # This case happens while adding '/'
            elif part == "":
                variablized_url += part
            # Regular plain routes, i.e, not vars.
            else:
                variablized_url += part + "/"

            curr_partial_routes = curr_partial_routes.setdefault(part, {})

        (
            curr_partial_routes.setdefault(self._ROUTE_NODE, []).append(
                _route(key_parts=curr_key_parts, validate=validate)
            )
        )

        self._max_depth = max(self._max_depth, depth_of(parts))
        return variablized_url
