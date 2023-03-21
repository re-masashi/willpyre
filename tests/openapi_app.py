from willpyre import (
    App,
    APIRouter,
    JSONResponse,
    Cookie,
    TextResponse,
    Redirect
)
from willpyre.schema import schema, Conint

@schema
class Ok:
    var: Conint(1,2) = 21
    random: int = 1


router = APIRouter(
    description="Simple API",
    title="Simple API",
    definitions=[Ok]
)

async def var(req, res):
    '''
    Return ok. JSON.
    '''
    return JSONResponse({
        "response":"OK",
        "var": req.params.get('var')
    })

router.add_api_route(
    '/api/:var',  
    var, 
    ["GET"], 
    tags=["easy"],
)

main = App(router)
