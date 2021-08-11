from . import router,structure,app

r = router.Router()

@r.get('/')
async def index(req,res):
	res.body = "<h1>Please fasten your seatbelts!!</h1>"
	return res

@r.get('/hello')
async def hello(req,res):
	res.body = f'{req.path}, world!'
	return res

app = app.App(r,__name__)
