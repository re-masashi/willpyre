# TODOS
-------
- Implement a better router. The router should support dynamic routing. Eg: 
```py
@router.get('/abc/{user:str}')
async def abc(req,res,path):
  a = path["user"]
  .....
```

- Write better docs.
- Write automatic testing scripts, so as to enable a CI service.
- Create beautiful sphinx theme.
-------

