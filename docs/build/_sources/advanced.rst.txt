Advanced
========

This sheet contains **slightly advanced** concepts, (comparative to the others given in the tutorial).

Extending the Router
--------------------

The classes on which the framework is based are highly customisable.
You can customise them to meet your specific needs.

The Router class actually has a lot.
To extend it, you can customise as per your need. For instance, consider that you need a vary fast url-router(C-implementation or Cythonised one) due to some reason.

Then, remember that it must your Router must have a  ``handle`` method, that accepts a ``request`` parameter, and must return an instance of ``structure.Response``. 
For more info, see :class:willpyre.Router.

Custom error responses
----------------------

If your application is a JSON based API, 
then you might not want to have errors in the format of test/html.
Or, if you are creating a web app, then you might not want to have a plain, default response.
Willpyre gives you that liberty. You have to change the config of :class:App.

.. code-block :: python

	from willpyre import Router, App, structure, json
	router = Router()
	# Do your stuff.

	class My404Response(structure.Response404):
		def __init__(self):
		self.status = 404
		self.content_type = "application/json"
		self.body = json.dumps({"error": 404})

	app = App(router)
	app.config["router_config"]["404Response"] = My404Response()

Startup and Shutdown tasks
--------------------------

You can schedule tasks to be performed on startup and shutdown.
Eg:

.. code-block :: python

	from willpyre import Router, App
	router = Router()
	# Some routing..

	def startup_task():
		print("Started")
	def shutdown_task():
		print("Shutting down.....")
	app = App(router)
	app.config["startup"] = startup_task
	app.config["shutdown"] = shutdown_task

These will be performed when your app starts and when gracefully shuts down.
If the process recieves a termination signal(Ctrl +C),
then your server, (Hypercorn, Uvicorn or Daphne) will send a shutdown event message
which will trigger the shutdown task.