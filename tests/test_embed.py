from willpyre import Router, TextResponse, App
from async_asgi_testclient import TestClient
import pytest


router = Router(endpoint_prefix="embed.")


@router.get("/", "home")
async def index(req, res):
    return TextResponse("INDEX")


@router.get("/foo", "foo")
async def foo(req, res):
    return TextResponse("FOO")


router2 = Router()
router2.embed_router("/embed", router)
app = App(router2)


def test_embed():
    assert router2.KuaRoutes._routes.get("embed", "FAILED") != "FAILED"
    assert router2.endpoint_for("embed.foo") == "/foo/"
    assert router2.KuaRoutes._routes["embed"].get(
        ":route", "FAILED") != "FAILED"
    assert router2.KuaRoutes._routes["embed"].get("foo", "FAILED") != "FAILED"


@pytest.mark.asyncio
async def test_embed_in_app():

    async with TestClient(app) as client:
        resp = await client.get("/embed/")
        assert resp.text == "INDEX"
