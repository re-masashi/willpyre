from maglev import App,Router

router = Router()

@router.get('/')
async def index(request,response):
	response.body = "index page"
	return response

print(router.routes["GET"])

@router.get('/login/')
async def login(request,response):
	if request.query.get('user') == 'admin':
		response.body = "Welcome admin"
	else:
		response.body = "Welcome ordinary user"
	return response

@router.post('/login/')
async def post_login(request,response):
	response.body = request.body.get("a","No_data")
	return response

@router.get('/api/:var')
async def api(request,response):
	response.body = "You requested the variable " + request.params.get("var","and you got it..")
	return response

main = App(router,__name__)
