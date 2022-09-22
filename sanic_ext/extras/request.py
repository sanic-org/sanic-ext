from itertools import count

from sanic import Request, Sanic
from sanic.compat import Header
from sanic.models.protocol_types import TransportProtocol


class CountedRequest(Request):
    __slots__ = ()

    _counter = count()
    count = next(_counter)

    def __init__(
        self,
        url_bytes: bytes,
        headers: Header,
        version: str,
        method: str,
        transport: TransportProtocol,
        app: Sanic,
        head: bytes = b"",
        stream_id: int = 0,
    ):
        super().__init__(
            url_bytes,
            headers,
            version,
            method,
            transport,
            app,
            head,
            stream_id,
        )
        self.__class__._increment()
        if hasattr(self.app, "multiplexer"):
            self.app.multiplexer.state["request_count"] = self.__class__.count

    @classmethod
    def _increment(cls):
        cls.count = next(cls._counter)

    @classmethod
    def reset_count(cls):
        cls._counter = count()
        cls.count = next(cls._counter)
