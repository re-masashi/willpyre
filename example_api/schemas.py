from willpyre.schema import schema, Conint

@schema
class Ok:
    var: Conint(1, 2) = 21
    random: int = 1

