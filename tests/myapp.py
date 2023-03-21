from willpyre import App, Router, JSONResponse, Cookie, TextResponse, Redirect


router = Router()  # Use APIRouter maybe


@router.get("/")
async def index(request, response):
    response.body = "index page"
    return response


@router.get("/static/:*params")
async def statics(request, response):
    response.body = "".join(request.params["params"])
    return response


@router.get("/trybruda/")
async def trybr(request, response):
    response.body = """
    <form action="/trybruda" method="post" enctype="multipart/form-data">
      <p><input type="text" name="text" value="text default">
      <p><input type="file" name="file1">
      <p><input type="file" name="file2">
      <p><button type="submit">Submit</button>
    </form>
    """
    return response


@router.post("/trybruda/")
async def trybrg(request, response):
    response.body = request.files.get("file1", "No_data").content
    return response


@router.get("/login/")
async def login(request, response):
    if request.query.get("user") == "admin":
        response.body = "Welcome admin"
    else:
        response.body = "Welcome ordinary user"
    return response


@router.post("/login/")
async def post_login(request, response):
    response.body = request.body.get("a", "No_data")
    print(response.body)
    return response


@router.get("/api/:var|int")
async def api(request, response):
    print("firsr")
    response.body = "You requested the variable " + request.params.get(
        "var", "and you got it.."
    )
    return response


@router.get("/cookie")
async def cookie(request, response):
    response.cookies["sessID"] = Cookie("Default", 60 * 60)
    response.body = "OK"
    return response


@router.get("/returntohome")
async def red(request, response):
    return Redirect("/")


@router.get("/json")
async def json_(req, res):
    return JSONResponse({"a": "b"})


async def other_methods(req, res):
    return TextResponse("others")


@router.put("/multipart")
async def multi(req, res):
    print(req.files)
    print("content type", req.content_type)
    return TextResponse(req.files.get("foo", "").content)


router.add_route("/others", "FETCH", other_methods)
router.add_route("/others", "TRACE", other_methods)
router.add_route("/others", "PATCH", other_methods)
router.add_route("/others", "PUT", other_methods)


class Middleware:
    def __init__(self, app, **options):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        if scope["path"] == "/middleware":
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"text/html")],
                }
            )

            await send(
                {"type": "http.response.body", "body": b"OK", "more_body": False}
            )
        else:
            await self.app(scope, receive, send)


main = App(router)
main.add_middleware(Middleware)
