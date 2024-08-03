Middlewares
===========

Global Middlewares
------------------

Global middlewares are a special type of 'mini app'.
It can be embedded in the app to perform some special modifications on every request.

A global middleware in Willpyre is fully ASGI compilant, i.e., other frameworks can use Willpyre's middlewares and vice versa.

A global middleware must be an `ASGI callable <https://asgi.readthedocs.org>`_.

It is better to create the middleware as a class.
If it is a class, it must have an:
``async def  __call__`(self, scope, recieve, send)``

Other methods such as ``__init__``, etc. can be set if you want to define them.

.. code-block :: python

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

The middleware shown above will edit the response at '/middleware', i.e., no matter what the response is in that path, the middleware will return "OK" with a status of 200.

.. note ::
	You should reconsider if you **really** need a global middleware before using one.
	Maybe you can work without one.

Path Specific Middlewares
-------------------------

In most cases, you will not need the middleware to do it's job on every request. 
Let's say you have a middleware ``is_logged_in``, it might not be needed on every request and it will become messy to manage that with a global middleware.

Per request middlewares can either be specified to run before the handler function or after the handler function.

Pre-Handler Middlewares
-----------------------

These middlewares are run before your handler is executed.

Thus, we filter out requests before they are handled. This is very useful while defining paths requiring authentication.

For example:

.. code-block :: python

	# other code
	async def is_logged_in(request, response):
	    if request.query.get("user", "") != '':
	        return (request, response)
	    else:
	        response.body = "Login needed"
	        return (request, HijackedMiddlewareResponse(response))
	
	@router.get("/secret-path", middlewares=[is_logged_in])
	async def fumo(req, res):
	    return TextResponse("Welcome Fumo!")

The ``HijackedMiddlewareResponse`` class tells Willpyre to not execute the handler and directly send the response returned from the middleware to the user.

Sometimes, you might want the middleware to make changes and then return the request and response to the handler.

.. code-block :: python

	# other code
	async def turn_to_lowercase(request, response):
	    request.query['username'] = request.query.get('username', '').lower()
	    request.query['email'] = request.query.get('email', '').lower()
	    request.query['city'] = request.query.get('city', '').lower()
	    request.query['language'] = request.query.get('language', '').lower()
	    return (request, response)
	

'Pass Through' Middlewares
--------------------------

Pass through middlewares are run after your handler is executed.

.. code-block :: python

	# other code
	async def turn_to_pizza(request, response):
		response.body = " ".join(["🍕" for x in response.body.split()])
	    return (request, response)

Let's say your handler returns the response "Hello world". It will turn to " 🍕  🍕 "