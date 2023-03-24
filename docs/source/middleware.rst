Middlewares
===========

Middlewares are a special type of 'mini app'.
It can be embedded in the app to perform some special modifications on every request.

A middleware in Willpyre is fully ASGI compilant, i.e., other frameworks can use Willpyre's middlewares and vice versa.

A middleware must be an `ASGI callable <https://asgi.readthedocs.org>`_.

It is better to create a middleware as a class.
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
	You should reconsider if you **really** need a middleware before using one.
	Maybe you can work without one.
