import typing
from . import router,structure
from urllib import parse

class App:
  '''
  The App class is used as the app which will be used for all activities.
  This requires a `Router` to be attached for serving responses accordingly.
  To instantiate a `name` value is also needed. 
  The __call__ function has the ASGI app.
  '''
   
  def __init__(
    self,
    router:router.Router,
    name:str,
    response:structure.Response=structure.Response
    ):
    
    self.router = router
    self.name = name
    self.response = response

#Websocket implementation yet to do.
  async def __call__(self,scope,recieve,send):
    '''This will be serving as the ASGI app.
    The information about request will ge gained from the `scope` argument and response will be sent by `send`
    '''

    if scope["type"] == "http":
      response_ = await self.router.handle(
          structure.Request(
            scope["method"],
            scope["path"],
            scope["headers"],
            parse.parse_qs(scope["query_string"].decode()),
            ),
          self.response)

      if response_.cookies != dict():
        response_cookies = [[b'Set-Cookie',cookie_.encode() + b'='+ response_.cookies[cookie_].cookie_str]for cookie_ in response_.cookies.keys()]
      else:
        response_cookies = []
      await send({
        #letting the router object handle all the requests
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
        

    


