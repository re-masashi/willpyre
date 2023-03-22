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

from .crud import apirouter


router = Router()


@router.get("/")
async def index(req, res):
    return HTMLResponse(data="INDEX")


router.embed_router("/api", apirouter)

main = App(router)
