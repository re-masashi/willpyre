from async_asgi_testclient import TestClient
from myapp import main
import pytest


@pytest.mark.asyncio
async def test_willpyre_middleware():
    async with TestClient(main) as client:
        resp = await client.get("/middleware")
        assert resp.status_code == 200
        assert resp.text == "OK"
