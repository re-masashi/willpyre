import typing


class Response:
  headers = dict()
  headers['content-type'] = 'text/html'
  body = ''
  status = 200
  def append(self,message):
    self.body += message

class Request:
  headers = dict()
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