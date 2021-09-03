Tutorial
===========

If you have used ExpressJS, you will find the API to be similar.
The functions that handle the actions on a page, are called handlers. The handlers must have ``request`` and ``response`` parameters. 

For example:

.. code-block :: python

	from willpyre import App,Router
	router = Router()
	@router.get('/')
	async def index(request,response):
		response.body = "Hello, Willpyre"
		return response

	app = App(router,__name__)

The ``app`` is an ASGI callable. You can use it with any ASGI server.

For example if you use it with Uvicorn..,

.. code-block :: console

	$ uvicorn <file>:app

Please substitute the ``<file>`` with the name of your file. For instance, if you call your file ``example.py``, and you type this code. Then you must use ``example:app``.

Now, if Uvicorn returns a response like this...

.. code-block :: text

	INFO:     Waiting for application startup.
	INFO:     Application startup complete.
	INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)


Then the aplication is runnning and you have setup everything fine..

Now if you go to localhost:8000/, 
you will find the text **Hello, Willpyre** to be present there.

The ``@router.get()`` decorator required one path, to be specified. Here, it was passed as ``@router.get('/')``. Hence, only requests to '/' using HTTP ``GET`` method will be replied to. Others will lead to a 404 response.

-----------
URL Routing
-----------

Willpyre allows you to define static routes and dynamic using the ``Router`` class.

This can be imported from the ``willpyre`` module.
In the first example, the app will send a response only to requests to '/' or  http://localhost:8000**/**
This is because, nothing else was specified for other paths.

The router specifies only one method to be specified on one path.
If you want to specify more paths, you can use the function ``router.get('/anotherpath',index)`` then the function ``index``, that you defined in the example, will handle GET requests on ``/anotherpath`` as well. If you want POST requests to be handled.
Then use ``router.post`` instead of ``router.get``.

Thus, the above example would become..

.. code-block :: python

	from willpyre import App,Router
	router = Router()
	@router.get('/')
	async def index(request,response):
		response.body = "Hello, Willpyre"
		return response

	router.get('/anotherpath',index)
	app = App(router,__name__)

After running this with Uvicorn, you will see that if you go to http://localhost:8000/anotherpath/ The response will be the same as in http://localhost:8000

Variables in URL path
---------------------
If you want some variables in the path, then you can specify them like this.

.. code-block :: python

	@router.get('/:var')


Adding ``:`` before a variable allows it to match any value put. 
This can be accessed using the ``request.params`` in the function argument. 

Eg:

.. code-block :: python

	@router.get('/api/:var')
	async def api(request,response):
		response.body = "You requested the variable " + request.params.get('var')
		return response

Run this with Uvicorn and then, go to http://localhost:8000/api/hello

You will see that, you will find the text "**You requested the variable hello**".  

``request.params`` is a dictionary object. And as you specified the variable name as ``:var`` you can access its value ``var`` as a key in the ``request.params`` dictionary.

Request object
==============

The ``request`` object is useful for getting info about the incoming request. Such as cookies, headers, query, request body, etc. Most of these are in the form of a dictionary.

``request.query``
-----------------
If a client sends a request to ``/hello?name=Sasuke``
You can access it via ``request.query.get("name")``, and you will get the value ``Sasuke``.

.. note ::
	As the data is in dictionary format, please use query.get(value) instead of query[value].
	If the value is missing, and you use the quesry[value] notation, you will raise a KeyError. For other dictionary objects as well, try to use the .get() function, a fallback value with the .get() is even better. 

``request.body``
----------------
If a client sends a POST request to ``/login``. With a form that is something like this,

..code-block ::html

	<form action="/login" method="POST">
	<input type="text" name="id">
	<input type="submit">
	</form>

Then, you can access the ``id`` of the user(see the form) with the help of 
``request.body.get('id')``.
If he fills in his ID to be, "user", you will get "user" in "``request.body.get('id')``"

The same goes for multipart file uploads.


``request.cookies``
-------------------
These contain the cookies of the client that have been sent, i.e, request cookies. You can access the cookies via ``request.cookies.get(cookienamehere)``.

``request.headers``
-------------------
The HTTP headers sent by the client. All are in lower-case as per ASGI specification.
Eg: ``request.headers["content-type"]``

Response object
===============
This object contains data to be sent to the client.
Such as content-type, cookies, status, and the response body.



``response.headers``
--------------------
The headers to sent to the client.
Eg: 
..code-block ::python

	response.headers["x-powered-by"] = "willpyre"


The content-type of the response can be set with ``response.headers["content-type"]``




``response.cookies``
--------------------
These are the cookies sent to the client. Must be of type ``structure.Cookie``



``response.status``
-------------------
The status code of the response. Must be an int.
