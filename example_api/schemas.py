from willpyre.schema import schema, Conint, Constr


@schema
class Ok:
    var: Conint(1, 2) = 21
    random: int = 1


@schema
class User:
    name: Constr(4, 250)
    usertag: Constr(4, 100)


@schema
class Event:
    title: str
    description: str
