from __future__ import annotations

from inspect import isawaitable
from typing import TYPE_CHECKING, Dict, Optional

from sanic import Sanic
from sanic.exceptions import SanicException
from sanic.response import HTTPResponse

if TYPE_CHECKING:
    from jinja2 import Environment


async def render(
    template_name: str,
    status: int = 200,
    headers: Optional[Dict[str, str]] = None,
    content_type: str = "text/html; charset=utf-8",
    app: Optional[Sanic] = None,
    environment: Optional[Environment] = None,
    **kwargs
) -> HTTPResponse:
    if app is None:
        try:
            app = Sanic.get_app()
        except SanicException as e:
            raise SanicException(
                "Cannot render template beause locating the Sanic application "
                "was ambiguous. Please return  render(..., app=some_app)."
            ) from e

    if environment is None:
        environment = app.ext.environment

    template = environment.get_template(template_name)
    render = (
        template.render_async
        if app.config.TEMPLATING_ENABLE_ASYNC
        else template.render
    )
    content = render(**kwargs)
    if isawaitable(content):
        content = await content  # type: ignore
    return HTTPResponse(  # type: ignore
        content, status=status, headers=headers, content_type=content_type
    )
