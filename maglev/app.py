import typing
from . import router,structure

class App:

  def __init__(
    self,
    router:router.Router,
    name:str,
    response:structure.Response=structure.Response
    ):
    
    self.router = router
    self.name = name
    self.response = response

  async def __call__(self,scope,recieve,send):
    #Websocket implementation yet to do.

    if scope["type"] == "http":
      response_ = await self.router.handle(
          structure.Request(scope["method"],scope["path"],scope["headers"]),
          self.response)
      if response_.cookies != {}:
        response_cookies = [[b'Set-Cookie',cookie_.encode() + response_.cookies[cookie_].cookie_str]for cookie_ in response_.cookies.keys()]
      else:
        response_cookies = []
      await send({#letting the router object handle all the requests
        'type': 'http.response.start',
        'status': response_.status,
        'headers': [
        [value.encode() for value in header_pair] for header_pair in list(response_.headers.items())
        ] + response_cookies
        })
      
      await send({
        'type':'http.response.body',
        'body': response_.body.encode()
          })
        

    


