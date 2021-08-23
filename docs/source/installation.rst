Installation
==============

The installation process is simple, just install `Git`_. Then follow along. 

.. _Git: https://git-scm.com/downloads

Maglev Installation
-------------------
.. code-block :: console

	$ git clone https://github.com/Nafi-Amaan-Hossain/maglev
	$ cd maglev
	$ pip install .


A PyPi install is currently not present, (for version ``0.0.1``)

ASGI server installation
-------------------------
Maglev is based on the `ASGI specification`_ and can be used with any ASGI server.

.. _ASGI specification: https://asgi.readthedocs.com

.. note :: 
	Maglev, does not prefer any specific ASGI server. It gives you the choice.
	You can use any ASGI server like Uvicorn, Hypercorn, Daphne.

Testing framework installation
------------------------------

Testing applications can be done with the ASGI-testing module.
The Maglev module does not provide any testing module currently.



