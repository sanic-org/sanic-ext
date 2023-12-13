from __future__ import annotations

from functools import wraps
from inspect import isawaitable
from typing import TYPE_CHECKING, Dict, Optional, Union

from jinja2 import Environment
from sanic.compat import Header
from sanic.request import Request
from sanic.response import HTTPResponse

from sanic_ext.extensions.templating.render import (
    LazyResponse,
    TemplateResponse,
)


if TYPE_CHECKING:
    from sanic_ext import Config


class Templating:
    def __init__(self, environment: Environment, config: Config) -> None:
        self.environment = environment
        self.config = config

    def template(
        self,
        file_name: str,
        status: int = 200,
        headers: Optional[Union[Header, Dict[str, str]]] = None,
        content_type: str = "text/html; charset=utf-8",
        **kwargs,
    ):
        template = self.environment.get_template(file_name)
        render = (
            template.render_async
            if self.config.TEMPLATING_ENABLE_ASYNC
            else template.render
        )

        def decorator(f):
            @wraps(f)
            async def decorated_function(*args, **kwargs):
                context = f(*args, **kwargs)
                if isawaitable(context):
                    context = await context
                if isinstance(context, HTTPResponse) and not isinstance(
                    context, TemplateResponse
                ):
                    return context

                # TODO
                # - Allow each of these to be a callable that is executed here
                params = {
                    "status": status,
                    "content_type": content_type,
                    "headers": headers,
                }

                if isinstance(context, LazyResponse):
                    for attr in ("status", "headers", "content_type"):
                        value = getattr(context, attr, None)
                        if value:
                            params[attr] = value
                    context = context.context

                context["request"] = Request.get_current()

                content = render(**context)
                if isawaitable(content):
                    content = await content

                return HTTPResponse(content, **params)

            return decorated_function

        return decorator
