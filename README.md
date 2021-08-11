# Maglev

-------------------------
Maglev is a micro ASGI framework. 
Maglev gives flexibility and control, but removes the low level complexities of ASGI.
-------------------------

## [Quickstart](#Quickstart)

It is quite simple to use Maglev.

```py
from maglev import app,router


r = router.Router()

@r.get('/')
async def index(req,res):
	res.body = "<h1>Please fasten your seatbelts!!</h1>"
	return res


app = app.App(r,__name__)
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

