from willpyre import (
    App,
    APIRouter,
    JSONResponse,
    Cookie,
    TextResponse,
    Redirect
)


router = APIRouter(
    description="Simple API",
    title="Simple API"
)  # Use APIRouter maybe

async def var(req, res): 
    return JSONResponse({
        "response":"OK",
        "var": req.params.get('var')
    })

router.add_api_route('/api/:var',  var)



main = App(router)