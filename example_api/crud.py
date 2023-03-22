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
from willpyre.schema import schema_to_json, populate_schema, error_schema
from .schemas import Ok, User, Todo
from tinydb import TinyDB, Query

usersdb = TinyDB("example_api/users.json")

apirouter = APIRouter(
    description="Simple API",
    title="Simple API",
    definitions=[Ok, User, Todo],
)


@apirouter.get("/users/get/:usertag", tags=["user"], response_model=User)
async def getUser(req, res):
    """
    Gets the user from DB and returns it.
    """
    USER = Query()
    users = usersdb.search(USER.usertag == req.params["usertag"])
    if len(users) == 0:
        return JSONResponse(schema_to_json(error_schema("User exists", 200)))
    usertag = users[0]["usertag"]
    name = users[0]["name"]
    return JSONResponse(
        schema_to_json(populate_schema(User, usertag=usertag, name=name))
    )


@apirouter.post(
    "/users/create",
    tags=["user"],
    response_model=User,
    auto_path_parameters=False,
    body_model=User,
)
async def createUser(req, res):
    '''
    Creates a User and returns it. 
    Will return a message if user exists.
    '''
    USER = Query()
    users = usersdb.search(USER.usertag == req.body["usertag"])
    if len(users) != 0:
        return JSONResponse(schema_to_json(error_schema("User already exists", 404)))
    usertag = req.body["usertag"]
    name = req.body["name"]
    usersdb.insert({"name": name, "usertag": usertag})
    return JSONResponse(
        schema_to_json(populate_schema(User, usertag=usertag, name=name))
    )
