from willpyre import (
    App,
    APIRouter,
    JSONResponse,
    Cookie,
    TextResponse,
    Redirect,
    Router,
    HTMLResponse,
)
from .schemas import Ok

apirouter = APIRouter(
    description="Simple API",
    title="Simple API",
    definitions=[Ok],
)


@apirouter.get("/:var|int", tags=["easy"], response_model="Ok")
async def var(req, res):
    """
    Return ok. JSON.
    """
    return JSONResponse(
        {
            "response": "OK",
            "var": req.params.get("var"),
        }
    )
