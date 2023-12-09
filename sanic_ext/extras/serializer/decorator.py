from functools import wraps
from inspect import isawaitable, signature
from typing import Callable, TypeVar

from sanic import response


T = TypeVar("T")


def serializer(func, *, status: int = 200) -> Callable[[T], T]:
    sig = signature(func)
    simple = len(sig.parameters) == 2 or (
        func
        in (
            response.HTTPResponse,
            response.file_stream,
            response.file,
            response.html,
            response.json,
            response.raw,
            response.redirect,
            response.text,
        )
    )

    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            retval = f(*args, **kwargs)
            if isawaitable(retval):
                retval = await retval

            if simple:
                return func(retval, status=status)
            else:
                kwargs["status"] = status
                return func(retval, *args, **kwargs)

        return decorated_function

    return decorator
