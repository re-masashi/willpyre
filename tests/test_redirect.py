from async_asgi_testclient import TestClient
from myapp import main
import pytest


@pytest.mark.asyncio
async def test_willpyre_redirect():
    async with TestClient(main) as client:
        resp = await client.get("/returntohome")
        assert resp.status_code == 200
        assert resp.text == "index page"
