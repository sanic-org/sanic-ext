from sanic import Request
from sanic.exceptions import SanicException


def extract_request(*args) -> Request:
    request: Request
    if args and isinstance(args[0], Request):
        request = args[0]
    elif len(args) > 1:
        request = args[1]
    else:
        raise SanicException("Request could not be found")
    return request
