import typing


class Response:
  '''
  This class contains the Response data to be sent in a manageable format.
  The response object does not take external parametrs, but has some attributes which can be set by accessing.
  The attributes are:
  `headers` of type dict, it has the HTTP headers to be sent back to the user.
  `cookies` of type dict, it has the cookies to send back to the user. The cookies to be sent must be of type `maglev.structure.Cookie`
  eg:
  ```py
  response.cookies["sessid"] = Cookie("no_login",20*60)
  ```
  ''' 
  headers = dict()
  cookies = dict()
  headers['content-type'] = 'text/html'
  body = ''
  status = 200
  def append(self,message):
    self.body += message


class Request:
  '''
  This class contains the information requested by the user.
  The functions called by `Router.handler` take this as the first argument.
  It takes:
  `headers` as an array of headers passed by the server, and converts them to a dict.
  `method` as a string which is passed by the server. It is the HTTP request method.
  `path` as a string which is passed by the server. It is the HTTP request path.
  `query` as a dict(string,array). It is obtained from the server as a string and is then parsed into the dictionary with `urllib.parse.parse_qs`

  '''

  headers = dict()
  cookies = dict()
  query = dict()
  def __init__(self, method:str, path:str, headers, query, *args):
    self.method = method
    self.path = path
    self.query = query
    self.query.update( (k,query[k][0]) for k in query )
    for header_pair in headers:
      self.headers[header_pair[0].decode()]=header_pair[1].decode()
    if 'cookie' in self.headers.keys():
      [self.cookies.update({_.split('=')[0]:_.split('=')[1]}) for _ in self.headers['cookie'].split(';')] 
    self.path_array = list(
      filter(
        lambda x: x!='',path.split('/')
        )
      )

class Response404:
    headers = dict()
    cookies = dict()
    headers['content-type'] = 'text/html'
    body = 'Not found!!'
    status = 404


class Cookie:
  '''
  This class is used to send cookies to the user.
  Eg:
  ```py
  @router.get('/')
  async def index(request,response):
    response.cookies["sessid"] = Cookie("no_login",20*60)
    ...
    return response
  ```
  This takes: 
  `value` as string,
  `max_age` as integer (default = 0),
  `same_site` as string (default = "Lax"),
  `secure` as boolean (default=True)
   Is not a callable class
   '''

  __slots__ = ('value','max_age','cookie_str','same_site','secure')

  def __init__(self, value:str, max_age:int=0, same_site:str="Lax", secure:bool=True):
    self.value = value.encode()
    self.max_age = str(max_age).encode()
    self.same_site = same_site.encode()
    self.secure = secure
    self.cookie_str = self.value + b';Max-Age=' + self.max_age + b';SameSite=' + same_site.encode()
    if secure == True:
      self.cookie_str += b';Secure'