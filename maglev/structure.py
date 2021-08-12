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
    headers['content-type'] = 'text/html'
    body = 'Not found!!'
    status = 404

class Cookie:
  __slots__ = ('value','max_age','cookie_str')
  def __init__(self,value:str,max_age:int):
    self.value = value
    self.max_age = max_age
    self.cookie_str = value + ';Max-Age=' + str(max_age)
