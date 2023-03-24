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
from willpyre.schema import schema_to_json, populate_schema, error_schema, validate_json
from .schemas import Ok, User, Event
from tinydb import TinyDB, Query

usersdb = TinyDB("example_api/users.json")
eventsdb = TinyDB("example_api/events.json")

apirouter = APIRouter(
    description="Simple API",
    title="Simple API",
    definitions=[Ok, User, Event],
)


@apirouter.get("/users/get/:usertag", tags=["user"], response_model=User)
async def getUser(req, res):
    """
    Gets the user from DB and returns it.
    """
    USER = Query()
    users = usersdb.search(USER.usertag == req.params["usertag"])
    if len(users) == 0:
        return JSONResponse(schema_to_json(error_schema("User doesn't exist", 200)))
    user = validate_json(User, users[0])
    return JSONResponse(schema_to_json(populate_schema(User, **user)))


@apirouter.post(
    "/users/create",
    tags=["user"],
    response_model=User,
    body_model=User,
)
async def createUser(req, res):
    """
    Creates a User and returns it.
    Will return a message if user exists.
    """
    USER = Query()
    users = usersdb.search(USER.usertag == req.body["usertag"])
    body = validate_json(User, req.body)
    if len(users) != 0:
        return JSONResponse(schema_to_json(error_schema("User already exists", 404)))
    usersdb.insert(body)
    return JSONResponse(schema_to_json(populate_schema(User, **body)))


@apirouter.post(
    "/events/create",
    tags=["event"],
    response_model=Event,
    body_model=Event,
)
async def createUser(req, res):
    """
    Creates an Event and returns it.
    Will return a message if it exists.
    """
    EVENT = Query()
    body = validate_json(Event, req.body)
    events = eventsdb.search(EVENT.title == req.body["title"])
    if len(events) != 0:
        return JSONResponse(schema_to_json(error_schema("Event already exists", 200)))
    eventsdb.insert(body)
    return JSONResponse(schema_to_json(populate_schema(Event, **body)))


@apirouter.get("/events/get/:title", tags=["event"], response_model=Event)
async def getEvent(req, res):
    """
    Gets the event from DB and returns it.
    """
    EVENT = Query()
    events = eventsdb.search(EVENT.title == req.params["title"])
    if len(events) == 0:
        return JSONResponse(schema_to_json(error_schema("Event doesn't exist", 404)))
    event = validate_json(Event, events[0])
    return JSONResponse(schema_to_json(populate_schema(Event, **event)))
