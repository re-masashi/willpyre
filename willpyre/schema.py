import collections
from typing import Union


class Constr:
    """
    used as `constr(10, 20)` to limit the length of a string between 10 and 20.
    """

    def __init__(self, min_: int, max_: int):
        self.min = min_
        self.max = max_

    def __repr__(self):
        return "string"


class Conint:
    """
    used as `constr(100, 1000)` to limit the value of an int between 100 and 1000.
    """

    def __init__(self, min_: int, max_: int):
        self.min = min_
        self.max = max_

    def __repr__(self):
        return "integer"


class Confloat:
    """
    used as `constr(0.1, 0.4)` to limit the value of an float between 0.1 and 0.4.
    """

    def __init__(self, min_: Union[int, float], max_: Union[int, float]):
        self.min = min_
        self.max = max_

    def __repr__(self):
        return "float"


class ValidationError(Exception):
    """Raised by validator.load when the input data is invalid."""

    def __init__(self, reasons) -> None:
        self.reasons = []


class MissingVal:
    """
    Opaque type of missing values of attributes in a schema.
    """

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover
        return "Missing value"


Missing = MissingVal()


Field = collections.namedtuple("Field", ["name", "annotation", "default"])


def schema(cls):
    """Construct a schema from a class.
    Schemas are plain Python classes that may be
    used to validate requests and serialize responses.
    Examples:
      >>> @schema
      ... class Account:
      ...   username: str
      ...   password: str
      ...   is_admin: bool
    Raises:
      RuntimeError: When the attributes are invalid.
    Args:
        cls(object): the schema class with fields
    """
    fields = {}

    annotations = cls.__annotations__
    for name, annotation in annotations.items():
        value = getattr(cls, name, Missing)

        fields[name] = Field(name=name, annotation=annotation, default=value)

        # Remove the attribute from the class definition.
        try:
            if value is not Missing:
                delattr(cls, name)
        except AttributeError:
            pass

    if not fields:
        raise RuntimeError(f"schema {cls.__name__} doesn't have any fields")

    setattr(cls, "__slots__", list(fields) + ["__FIELDS__"])
    setattr(cls, "__FIELDS__", fields)
    return cls


def _match_type(annotation, value):
    if annotation is str:
        if type(value) is str:
            return value
        else:
            raise ValidationError(
                f"Wrong type. Got {type(value)} instead of {annotation}."
            )
    if annotation is int:
        if type(value) is int:
            return value
        else:
            raise ValidationError(
                f"Wrong type. Got {type(value)} instead of {annotation}."
            )
    if annotation is float:
        if type(value) is float:
            return value
        else:
            raise ValidationError(
                f"Wrong type. Got {type(value)} instead of {annotation}."
            )

    if isinstance(annotation, Constr):
        if (
            type(value) is str
            and len(value) >= annotation.min
            and len(value) <= annotation.max
        ):
            return value
        else:
            raise ValidationError("Wrong type.")

    if isinstance(annotation, Conint):
        if type(value) is int and value >= annotation.min and value <= annotation.max:
            return value
        else:
            raise ValidationError("Wrong type.")

    if isinstance(annotation, Confloat):
        if type(value) is float and value >= annotation.min and value <= annotation.max:
            return value
        else:
            raise ValidationError("Wrong type.")

    raise NotImplementedError(f"Annotation {annotation} not implemented")


def _validate(field, value):
    if value is Missing:
        if field.default is not Missing:
            return field.default
        raise ValidationError(f"{field.name} field is required")

    return _match_type(field.annotation, value)


def validate_json(schema, data: dict):
    """
    Validate the given data dict object against a schema and
    instantiate the schema.
    Will not raise any error if there are extra fields in the dict. IT will remove them in the return value.
    Raises:
      ValidationError: When the input data is not valid.
    Parameters:
      schema: The schema class to validate the data against.
      data: Data to validate against and populate the schema with.
    """
    if not (isinstance(schema, type) and hasattr(schema, "__FIELDS__")):
        raise TypeError(f"{schema} is not a valid schema")

    errors, params = {}, {}
    for field in schema.__FIELDS__.values():  # type: ignore
        try:
            value = data.get(field.name, Missing)
            params[field.name] = _validate(field, value)
        except ValidationError as e:
            errors[field.name] = str(e)

    if errors != {}:
        raise ValidationError(errors)

    return params


def schema_repr(schema):
    """ """
    if not (isinstance(schema, type) and hasattr(schema, "__FIELDS__")):
        raise TypeError(f"{schema} is not a valid schema")

    params = {}
    for field in schema.__FIELDS__.values():  # type: ignore
        if field.annotation is int:
            annotation = "integer"
        elif field.annotation is float:
            annotation = "float"
        elif field.annotation is str:
            annotation = "string"
        elif field.annotation is dict:
            annotation = "object"
        elif isinstance(field.annotation, type) and hasattr(
            field.annotation, "__FIELDS__"
        ):
            annotation = schema_repr(schema)
        else:
            annotation = field.annotation.__repr__()

        params[field.name] = {"type": annotation}

    return params


def schema_to_json(schema):
    if not (isinstance(schema, type) and hasattr(schema, "__FIELDS__")):
        raise TypeError(f"{schema} is not a valid schema")

    errors, params = {}, {}
    for field in schema.__FIELDS__.values():  # type: ignore
        try:
            value = field.default
            if value is Missing:
                raise ValueError("Value cannot be unpopulated.")
            params[field.name] = _validate(field, value)
        except ValidationError as e:
            errors[field.name] = "error"

    if errors != {}:
        raise ValidationError(errors)
    return params


@schema
class ErrorResponse:
    message: str
    status: int


def populate_schema(schema, **kwargs):
    _copy = type(schema.__name__, (), {})
    setattr(_copy, "__FIELDS__", schema.__FIELDS__)
    setattr(_copy, "__slots__", schema.__slots__)
    for arg, val in kwargs.items():
        if schema.__FIELDS__.get(arg, None) is not None:
            _copy.__FIELDS__[arg] = Field(arg, _copy.__FIELDS__[arg].annotation, val)
    return _copy


def error_schema(message: str, status: int):
    return populate_schema(ErrorResponse, message=message, status=status)
