# Willpyre

--------------------------
<p align="center">
	<img src="https://raw.githubusercontent.com/re-masashi/willpyre/main/docs/assets/logo_big.png">
</p>

--------------------------

[![Documentation Status](https://readthedocs.org/projects/willpyre/badge/?version=latest)](https://willpyre.readthedocs.io/en/latest/?badge=latest)
[![Test and PEP8](https://github.com/Nafi-Amaan-Hossain/willpyre/actions/workflows/actions.yml/badge.svg)](https://github.com/Nafi-Amaan-Hossain/willpyre/actions/workflows/actions.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/re-masashi/willpyre)


Willpyre is a micro ASGI framework. 
Willpyre gives flexibility and control, but abstracts ASGI to some extent and adds reusability to your code.
-------------------------

## [Quickstart](#Quickstart)

It is quite simple to use Willpyre.

```py
from willpyre import App, Router


router = Router()

@router.get('/')
async def index(req,res):
	res.body = "<h1>Please fasten your seatbelts!!</h1>"
	return res


app = App(router)
```

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
Tested on version 3.6 and above.

---------------------------------
## [Features](#Features)

* Predefined response objects for fast development.
* Optional base response object passed to handlers.
* Async.
* Light and tiny.
* And lots more..

--------------
## Contributions

It is open to contributors willing to commit.
Please open issues if you find something wierd.
Fork this if you want to propose changes.

------------