# Maglev

-------------------------

[![Documentation Status](https://readthedocs.org/projects/maglev/badge/?version=latest)](https://maglev.readthedocs.io/en/latest/?badge=latest)


Maglev is a micro ASGI framework. 
Maglev gives flexibility and control, but removes the low level complexities of ASGI.
-------------------------

## [Quickstart](#Quickstart)



It is quite simple to use Maglev.

```py
from maglev import App,Router


router = Router()

@router.get('/')
async def index(req,res):
	res.body = "<h1>Please fasten your seatbelts!!</h1>"
	return res


app = App(router,__name__)
```

Just that will do.

It should run with any ASGI server like ``Uvicorn``, ``Daphne``, ``Hypercorn``.

To run with Uvicorn, install Uvicorn using 
```bash
pip install uvicorn
```
and then
```bash
uvicorn <file>:app
```

The framework is written in pure-python and can run in PyPy or CPython.

----

### Why Maglev?

Maglev wants to be precise in action that can be performed on a URL, allowing only one method while registering a URL.
However, it won't enforce it. You can create your own Router by etending the Router class and implementing other approaches.
Maglev's API is heavily inspired by `ExpressJS` and wants to keep the entire context in `request` and `response`.

------
