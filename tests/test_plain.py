from async_asgi_testclient import TestClient
from myapp import main
import pytest


@pytest.mark.asyncio
async def test_willpyre_app():
    async with TestClient(main) as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        assert resp.text == "index page"


@pytest.mark.asyncio
async def test_willpyre_post():
    async with TestClient(main) as client:
        resp = await client.post("/login/", data="a=anything")
        assert resp.status_code == 200
        assert resp.text == "anything"


@pytest.mark.asyncio
async def test_willpyre_get():
    async with TestClient(main) as client:
        resp = await client.get("/login/?user=admin")
        assert resp.status_code == 200
        assert resp.text == "Welcome admin"


@pytest.mark.asyncio
async def test_trailing_slash():
    async with TestClient(main) as client:
        resp = await client.get("/login")
        assert resp.status_code == 200
        assert resp.text == "Welcome ordinary user"


@pytest.mark.asyncio
async def test_url_vars():
    async with TestClient(main) as client:
        resp = await client.get("/api/123")
        assert resp.status_code == 200
        assert resp.text == "You requested the variable 123"
        resp = await client.get("/api/hello")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_url_many():
    async with TestClient(main) as client:
        resp = await client.get("/static/foo/bar/baz")
        assert resp.status_code == 200
        assert resp.text == "foobarbaz"


@pytest.mark.asyncio
async def test_utils():
    async with TestClient(main) as client:
        resp = await client.get("/json")
        assert resp.json() == {"a": "b"}
        assert resp.headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_response404():
    async with TestClient(main) as client:
        resp = await client.get("/non-existent")
        assert resp.text == "Not found"
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_response405():
    async with TestClient(main) as client:
        resp = await client.open("/login", method="NO_SUCH_METHOD")
        assert resp.text == "Method not allowed"
        assert resp.status_code == 405


@pytest.mark.asyncio
async def test_put():
    async with TestClient(main) as client:
        resp = await client.put("/others")
        assert resp.text == "others"


@pytest.mark.asyncio
async def test_patch():
    async with TestClient(main) as client:
        resp = await client.patch("/others")
        assert resp.text == "others"
