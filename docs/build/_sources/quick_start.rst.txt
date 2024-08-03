Quick Start
===========

The functions that handle the actions on a page, are called handlers. The handlers must have ``request`` and ``response`` parameters. 

For example:

.. code-block :: python

	from willpyre import App,Router
	router = Router()
	@router.get('/')
	async def index(request,response):
		response.body = "Hello, Willpyre"
		return response

	app = App(router)

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

The ``@router.get`` decorator required one path, to be specified. Here, it was passed as ``@router.get('/')``. Hence, only requests to '/' using HTTP ``GET`` method will be replied to. Others will lead to a 404 response.

-----------
URL Routing
-----------

Willpyre allows you to define static routes and dynamic using the ``Router`` class.

This can be imported from the ``willpyre`` module.
In the first example, the app will send a response only to requests to '/' or  http://localhost:8000/. If you try requesting other routes such as '/asd' or '/qwerty' or anything else, you will get a 'Not found' response.
This is because, nothing else was specified for other paths.

The router specifies only one method to be specified on one path.
If you specified some path with `.get` method, it wulll only respond to HTTP `GET` requests.
POST, PUT, FETCH, etc will result in a 'Not Found' response. 

.. code-block :: python

	@router.get('/')
	async def index_get(request, response):
		response.body = "Get"
		return response

The above code will only respond to GET requests.

If you want to specify more paths, you can use the function ``router.get('/anotherpath',index)`` then the function ``index``, that you defined in the example, will handle GET requests on ``/anotherpath`` as well. If you want POST requests to be handled. Then use ``router.post`` instead of ``router.get``.

Thus, the above example would become..

.. code-block :: python

	from willpyre import App,Router
	router = Router()
	@router.get('/')
	async def index(request, response):
		response.body = "Hello, Willpyre"
		return response

	router.get('/anotherpath',index)
	app = App(router)

After running this with Uvicorn, you will see that if you go to http://localhost:8000/anotherpath/ The response will be the same as in http://localhost:8000

Embed a router
--------------

Sometimes you have multiple paths with a common prefix. It can be messy too usethem separately and, also typo-prone. You can instead embed the logic of common prefixes inside of a main router. In the end, we will pass the main router to the App.

.. code-block :: python

	from willpyre import App, Router
	main_router = Router()
	@main_router.get('/')
	async def index(request, response):
		response.body = "Index"
		return response

	subrouter = Router()
	@subrouter.get('/')
	async def subindex(req, res):
		response.body = "Subrouter index"
		return response

	@subrouter.post('/hello')
	async def subfoo(req, res):
		response.body = "Foo"
		return response

	main_router.embed_router("/sub", sub_router)

	app = App(main_router)

Now, you can request to http://localhost:8000/sub/, and you will see the text 
``"Subrouter index"``. If you go to http://localhost:8000/sub/hello, you will see "Foo".
And the other links will work as it is.

.. note :: 

	Do not make changes to the router after embedding it. This will lead to unexpected and undesirable outcomes.

The router has an internal representation of routes.
This representation is embedded in the router which wraps another router.
You can check the [source code](https://github.com/re-masashi/willpyre/tree/main/willpyre/kua.py), to see how its implemented.


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

Now, say you want to have something like, ``https://example.com/api/:userid`` (where 
``userid`` is an integer), which returns user by id. How can you check if it is an integer? 
Doing that on every parameter seems ugly.

Here comes a solution:

Validation
----------
Wilpyre supports validation of request parameters.
A validator basically checks if the variable in URL is of a desired type, else it returns a 'Not Found'.
You can add the routes like:

.. code-block :: python

	@router.get("/api/:userid|int")
	# Do something
	@router.add("/api/:username|lcase")
	# Do something

Thus, if the user sends 

THe default validation is ``'str'`` which matches everything and 
is implicitly passed when nothing is specified.

The default validators are:

``int``, ``lcase``, ``ucase``, ``str``, ``alnum``, ``nomatch``

You can add custom validators as well. 
.. code-block :: python

	router.validation_dict["super"] = lambda var: var == 'super'

Now, if the parameter (something|super) is equal to 'super'.
You should make sure that your validator shall be either a function or a lambda that takes one argument and returns a dict.

Multiple Vars
-------------

You can also have varying number parameters in the url, just like the ``*args`` in functions.
However, type validation cannot be done here. It just matches everything.

Eg:

.. code-block :: python

	@router.get('/files/:*filepath')
	async def file_hosting(request, response):
		filepath = request.params.get('filepath')
		path = '/'
		for part in path:
			path.join(path+'/')
		response.body = f'You requested a file at {path}'
		return response

Add this in your routes, and run your file with uvicorn 
and if you head to http://localhost:8000/files/home/user/, 
you will see that the message will be "You requested a file at /home/user/". 
If you request http://localhost:8000/files/somepath/some/other/,
you will see that the message will be "You requested a path at /somepath/some/other"

.. see-also::
	Don't trust user input as filenames. See below.


Request object
==============

The ``request`` object is useful for getting info about the incoming request. Such as cookies, headers, query, request body, etc. Most of these are in the form of a dictionary.

``request.query``
-----------------
If a client sends a request to ``/hello?name=Sasuke``
You can access it via ``request.query.get("name")``, and you will get the value ``Sasuke``.

.. admonition:: A Good Practice
	:class: note

	As the ``query`` is a :class:`TypedMultiDict` object, use ``query.get(value, fallback)`` instead of ``query[value]``.
	If the value is missing, and you use the ``query[value]`` notation, you will get a ``KeyError``. For other dict-like objects as well, try to use the ``query.get(value, fallback)`` function, with a fallback value. 

``request.body``
----------------
If a client sends a POST request to ``/login``. With a form that is something like this,

.. code-block :: html

	<form action="/login" method="POST">
	<input type="text" name="id">
	<input type="submit">
	</form>

Then, you can access the ``id`` of the user(see the form) with the help of 
``request.body.get('id')``.
If he fills in his ID to be, "user", you will get "user" in "``request.body.get('id')``"

The same goes for multipart file uploads.

``request.files``
-----------------
This is a dict-like collection of the files uploaded. 
The files uploaded are present as :class:`FileObject`s. These :class:`FileObject`s have ``filename``,
``name`` and ``payload`` which store the filename, name of the POST parameter, (i.e.
the name in the HTML form.) and the content of the file.

.. admonition:: Do not trust uploaded file names
	:class: warning
	
	Attackers may post malicious filenames. Such as "../../../../etc/passwd", or "../../../../etc/shadows/" and can have control on the server file system. Hence, it is better to not trust user uploaded file names and always saniize the names.


.. admonition:: request.files or request.body?
	:class: info
	
	If your uploaded data has a filename attribute in the HTTP headers, it is in ``files`, else in ``body``.
	
``request.cookies``
-------------------
These contain the cookies of the client that have been sent, i.e, request cookies. You can access the cookies by ``request.cookies.get(cookienamehere)`` or, 
``request.cookies["cookienamehere"]``.

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

.. code-block :: python

	response.headers["x-powered-by"] = "willpyre"


The content-type of the response can be set with ``response.headers["content-type"]``


``response.cookies``
--------------------
These are the cookies sent to the client. Must be of type ``structure.Cookie``



``response.status``
-------------------
The status code of the response. Must be an int.


