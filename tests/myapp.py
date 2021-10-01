from willpyre import (
    App,
    Router,
    JSONResponse,
    Cookie,
    TextResponse)


router = Router()


@router.get('/')
async def index(request, response):
    response.body = "index page"
    return response


@router.get('/login/')
async def login(request, response):
    if request.query.get('user') == 'admin':
        response.body = "Welcome admin"
    else:
        response.body = "Welcome ordinary user"
    return response


@router.post('/login/')
async def post_login(request, response):
    response.body = request.body.get("a", "No_data")
    return response


@router.get('/api/:var')
async def api(request, response):
    response.body = "You requested the variable " + \
        request.params.get("var", "and you got it..")
    return response


@router.get('/cookie')
async def cookie(request, response):
    response.cookies["sessID"] = Cookie("Default", 60 * 60)
    response.body = "OK"
    return response


@router.get('/json')
async def json_(req, res):
    return JSONResponse({'a': 'b'})


async def other_methods(req, res):
    return TextResponse("others")


router.add_route('/others', "FETCH", other_methods)
router.add_route('/others', "TRACE", other_methods)
router.add_route('/others', "PATCH", other_methods)
router.add_route('/others', "PUT", other_methods)

main = App(router)
