#Maglev

-------------------------
Maglev is a micro ASGI framework. 
Maglev gives flexibility and control, but removes the low level complexities of ASGI.
-------------------------

##[Quickstart][#Quickstart]

It is quite simple to use Maglev.

```py
import app
from utils import router,app


r = router.Router()

@r.get('/')
async def index(req,res):
	res.body = "<h1>Please fasten your seatbelts!!</h1>"
	return res


app = app.App(r,__name__)
```

Just that will do.

It should run with any ASGI server like ``Uvicorn``, ``Daphne``, ``Hypercorn``.

To run with Uvicorn, 

```bash
$ uvicorn <file>:app
```

The framework is written in pure-python and can run in PyPy or CPython.

