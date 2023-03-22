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
from willpyre.schema import schema, Conint


@schema
class Ok:
    var: Conint(1, 2) = 21
    random: int = 1


apirouter = APIRouter(
    description="Simple API",
    title="Simple API",
    definitions=[Ok],
)


@apirouter.get("/:var|int", tags=["easy"], response_model=Ok)
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


router = Router()


@router.get("/")
async def index(req, res):
    return HTMLResponse(data="INDEX")


router.embed_router("/api", apirouter)

main = App(router)
