Installation
==============

The installation process is simple, just install `Git`_. Then follow along. 

.. _Git: https://git-scm.com/downloads

Willpyre Installation
-------------------
.. code-block :: console

	$ git clone https://github.com/re-masashi/willpyre
	$ cd willpyre
	$ pip install .


A PyPi install is currently not present, (for version ``0.0.1``)

ASGI server installation
-------------------------
Willpyre is based on the `ASGI specification`_ and can be used with any ASGI server.

.. _ASGI specification: https://asgi.readthedocs.com

.. note :: 
	Willpyre, does not prefer any specific ASGI server. It gives you the choice.
	You can use any ASGI server like `Uvicorn <https://github.com/encode/uvicorn>`_, `Hypercorn <https://github.com/pgjones/hypercorn>`_, `Daphne <https://github.com/django/daphne>`_ or `Granian <https://github.com/emmett-framework/granian>`_.

Testing framework installation
------------------------------

Testing applications can be done with the ASGI-testing module.
The Willpyre module does not provide any testing module currently.



