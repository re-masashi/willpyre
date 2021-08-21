import typing
import inspect
from . import structure
from . import kua

class StaticRouter:
  '''StaticRouter class has the HTTP methods, paths, and handlers.'''
  def __init__(self):
    self.routes = dict()
    self.routes["GET"] = {}
    self.routes["POST"] = {}
    self.routes["PUT"] = {}
    self.routes["FETCH"] = {}
    self.routes["HEAD"] = {}
    self.routes["PATCH"] = {}
    self.routes["CONNECT"] = {}
    self.routes["OPTIONS"] = {}
    self.routes["TRACE"] = {}

    self.bodied_methods = ("POST","PUT","PATCH")
  
  def add_route(self,path:str,method:str,handler:typing.Callable) -> None:
    if path[-1] != '/':
      path += '/' 
    self.routes[method][path] = handler
  
  def add_method(self,method:str):
    '''
    This should be used to adding HTTP methods to the routing dictionary 

    Args:
      self: The :class:`Router`
      method(str): The method to add for the router to handle.
    Raises:
      NotImplementedError
    '''
    
    #self.routes[method] = {}
    raise NotImplementedError

  def get(self,path:str,**opts) -> typing.Callable:
    """
    This is meant to be used as a decorator on a function, that will be executed on a get query to the path.
    Eg: 
    
    @router.get('/'):
    def landing():
        return "Index page"

    Args:
      self: :class:`Router`
      path(str): The Request path
    """
    def decorator(handler: typing.Callable) -> typing.Callable:
      self.add_route(path=path,method="GET",handler=handler)
      return handler
    return decorator
  
  def post(self,path:str,**opts)-> typing.Callable:
    """
    This is meant to be used as a decorator on a function, that will be executed on a post query to the path.
    Eg: 
    
    @router.post('/form'):
    def landing(req,res):
        form = req.body
        ...
        res.send("OK! Form submitted") 
    
    Args:
      self: :class:`Router`
      path(str): The Request path
    """
    def decorator(handler: typing.Callable) -> typing.Callable:
      self.add_route(path=path,method="POST",handler=handler)
      return handler
    return decorator

  async def handle(self,request,response):
    '''
    The handle function wil handle the requests and send appropriate responses,
    based on the functions defined.

    Args:
      request: :class:`maglev.structure.Request`
      response: :class:`maglev.structure.Response`
    Returns:
      :class:`maglev.structure.Response`
    '''
    if request.path[-1] != '/':
      request.path += '/' 
    try:
      if request.method == "HEAD":
        response_ = await self.routes["GET"][request.path](request,response)
      else:
        response_ = await self.routes[request.method][request.path](request,response)
      return response_
    except KeyError:
      resp = structure.Response404()
      return resp
    #Value: Response object(9/8/21).


class Router(StaticRouter):
    
  def __init__(self):
    self.KuaRoutes = kua.Routes()
    super().__init__()

  def add_route(self,path:str,method:str,handler:typing.Callable) -> None:
    if path[-1] != '/':
      path += '/' 
    variablized_url = self.KuaRoutes.add(path)
    self.routes[method][variablized_url] = handler

  async def handle(self,request,response):
    if request.path[-1] != '/':
      request.path += '/'
    try:
      request.params, variablized_url = self.KuaRoutes.match(request.path)
      if variablized_url not in self.routes[request.method]:
        print(f'{request.path} is not registered urls')
      if request.method == "HEAD": 
        response_ = await self.routes["GET"][variablized_url](request,response)
      else:
        response_ = await self.routes[request.method][variablized_url](request,response)
      return response_
    except (kua.RouteError,KeyError):
      response_ = structure.Response404()
      return response_
