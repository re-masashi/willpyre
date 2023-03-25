from .schema import schema, Conint, Constr, Confloat
import logging
from . import structure

router_config = {
    "logger_exception": logging.error,
    "logger_info": logging.info,
    "404Response": structure.Response404(),
    "405Response": structure.Response405(),
    "500Response": structure.Response500(),
    "response": structure.Response(),
}

apirouter_config = {
    "logger_exception": logging.error,
    "logger_info": logging.info,
    "404Response": structure.Response404JSON(),
    "405Response": structure.Response405JSON(),
    "500Response": structure.Response500JSON(),
    "422Response": structure.Response422JSON(),
    "response": structure.JSONResponse(),
}
