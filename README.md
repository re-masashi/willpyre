# Willpyre

-------------------------

[![Documentation Status](https://readthedocs.org/projects/willpyre/badge/?version=latest)](https://willpyre.readthedocs.io/en/latest/?badge=latest)
[![Test and PEP8](https://github.com/Nafi-Amaan-Hossain/willpyre/actions/workflows/actions.yml/badge.svg)](https://github.com/Nafi-Amaan-Hossain/willpyre/actions/workflows/actions.yml)

Willpyre is a micro ASGI framework. 
Willpyre gives flexibility and control, but abstracts ASGI to some extent and adds reusability to your code.
-------------------------

## [Quickstart](#Quickstart)



It is quite simple to use Willpyre.

```py
from willpyre import App,Router


router = Router()

@router.get('/')
async def index(req,res):
	res.body = "<h1>Please fasten your seatbelts!!</h1>"
	return res


app = App(router)
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

### Why Willpyre?

Willpyre wants to be precise in action that can be performed on a URL, allowing only one method while registering a URL.
However, it won't enforce it. You can create your own Router by etending the Router class and implementing other approaches.
Willpyre's API wants to keep the entire context in `request` and `response`.

------
