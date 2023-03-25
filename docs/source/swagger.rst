Using SwaggerUI (by OpenAPI)
============================

Willpyre has support for building APIs rapidly.


Step 0 (Define the Models):
---------------------------

Define the response schemas for various responses.

Check the  `models page <https://willpyre.readthedocs.io/en/latest/models.html>`_.

We will use the same models as the example there.



Step 1 (Import an APIRouter):
-----------------------------
APIRouter can be imported from willpyre.

.. code-block :: python

	from willpyre import APIRouter

.. note ::

	APIRouter is a shorter alias for OpenAPIRouter.



Step 2 (Initialise the Router):
-------------------------------

Initialise the router with the configuration you need.

.. code-block :: python

	apirouter = APIRouter(
		description="A basic API with willpyre",
		title="Basic API",
		definitions=[User, Event],
	)


Some possible arguments to APIRouter are:
	* **description** (str)- Description of the API.

	* **title** (str)- Title of the API.
	
	* **definitions** (list of schema objects)- Definitions of various models in your app.
	
	* **schemes** (list of URL schemes). Default = ['http','https'].
	
	* **version** (str). Default = "0.0.1"- Version of your API.
	
	* **openapi_version** (str). Default="3.0.0". Can either be '2.0' or '3.0.n'
	
	* **tos_url** (str). Default="/terms-of-service".
	
	* **docs_url** (str). Default="/docs".
	
	* **license**. Default=None.
	
	* **host**. Default=None.
	* **contact**. Default=None.




Step 3 (Register routes):
-------------------------

.. code-block :: python

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
    	body = validate_json(User,req.body)
    	if len(users) != 0:
        	return JSONResponse(schema_to_json(error_schema("User already exists", 404)))
    	usersdb.insert(body)
    	return JSONResponse(schema_to_json(populate_schema(User, **body)))

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


.. note ::

	SwaggerUI features are not thoroughly tested. 


