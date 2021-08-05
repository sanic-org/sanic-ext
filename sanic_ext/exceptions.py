from sanic.exceptions import SanicException


class ValidationError(SanicException):
    status_code = 400
