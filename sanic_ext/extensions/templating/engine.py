from __future__ import annotations

from functools import wraps
from inspect import isawaitable
from typing import TYPE_CHECKING

from jinja2 import Environment
from sanic.response import HTTPResponse

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
        content_type: str = "text/html; charset=utf-8",
        **kwargs
    ):
        template = self.environment.get_template(file_name)
        render = (
            template.render_async
            if self.config.TEMPLATING_ENABLE_ASYNC
            else template.render
        )

        def decorator(f):
            @wraps(f)
            async def decorated_function(request, *args, **kwargs):

                context = f(request, *args, **kwargs)
                if isawaitable(context):
                    context = await context

                content = render(**context)
                if isawaitable(content):
                    content = await content

                return HTTPResponse(
                    content,
                    content_type=content_type,
                    status=status,
                )

            return decorated_function

        return decorator
