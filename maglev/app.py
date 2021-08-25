import typing
from . import router,structure
from urllib import parse

class App:
  '''
  The App class is used as the app.

  It which will be used for all activities.
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
    def startup():
      pass

    def shutdown():
      pass

    self.config = {"startup":startup,"shutdown":shutdown}
    self.router = router
    self.name = name
    self.response = response

#Websocket implementation yet to do.
  async def __call__(self,scope,receive,send):
    '''This will be serving as the ASGI app.
    The information about request will ge gained from the `scope` argument and response will be sent by `send`
    
    Args:
      self: The App class
      scope: The `scope` to communicate as per ASGI specification.
      recieve: ASGI recieve function
      send: ASGI send function
    '''
####HTTP
    if scope["type"] == "http":
      body = b''
      if scope["method"] in self.router.bodied_methods:
        more_body = True
        while more_body:
          message = await receive()
          body += message.get("body", b"")
          more_body = message.get("more_body", False)

      response_ = await self.router.handle(
          structure.Request(
            method = scope["method"],
            path = scope["path"],
            headers = scope["headers"],
            query = parse.parse_qs(scope["query_string"].decode()),
            body = parse.parse_qs(body.decode())
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
####End HTTP
####lifespan
    elif scope["type"] == "lifespan":
      while True:
        message = await receive()
        if message['type'] == 'lifespan.startup':
          self.config["startup"]()
          await send({'type': 'lifespan.startup.complete'})
        elif message['type'] == 'lifespan.shutdown':
          self.config["shutdown"]()
          await send({'type': 'lifespan.shutdown.complete'})
          return
#####End lifespan
#####Websocket
#####End web socket

