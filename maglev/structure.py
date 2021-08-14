import typing


class Response:
  headers = dict()
  cookies = dict()
  headers['content-type'] = 'text/html'
  body = ''
  status = 200
  def append(self,message):
    self.body += message


class Request:
  headers = dict()
  cookies = dict()
  def __init__(self,method:str,path:str,headers,*args):
    for header_pair in headers:
      self.headers[header_pair[0]]=header_pair[1]
    self.method = method
    self.path = path 
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
