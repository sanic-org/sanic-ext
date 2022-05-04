from __future__ import annotations

from inspect import isawaitable
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from sanic import Sanic
from sanic.compat import Header
from sanic.exceptions import SanicException
from sanic.response import HTTPResponse

if TYPE_CHECKING:
    from jinja2 import Environment


class LazyResponse(HTTPResponse):
    __slots__ = (
        "body",
        "status",
        "content_type",
        "headers",
        "_cookies",
        "context",
    )

    def __init__(
        self,
        context: Dict[str, Any],
        status: int = 0,
        headers: Optional[Union[Header, Dict[str, str]]] = None,
        content_type: Optional[str] = None,
    ):
        super().__init__(
            content_type=content_type, status=status, headers=headers
        )
        self.context = context


async def render(
    template_name: str = "",
    status: int = 200,
    headers: Optional[Dict[str, str]] = None,
    content_type: str = "text/html; charset=utf-8",
    app: Optional[Sanic] = None,
    environment: Optional[Environment] = None,
    context: Optional[Dict[str, Any]] = None,
    *,
    template_source: str = "",
) -> HTTPResponse:
    if app is None:
        try:
            app = Sanic.get_app()
        except SanicException as e:
            raise SanicException(
                "Cannot render template beause locating the Sanic application "
                "was ambiguous. Please return  render(..., app=some_app)."
            ) from e

    if template_name and template_source:
        raise SanicException(
            "You must provide template_name OR template_source, not both."
        )

    if environment is None:
        environment = app.ext.environment

    kwargs = context if context else {}
    if template_name or template_source:
        template = (
            environment.get_template(template_name)
            if template_name
            else environment.from_string(template_source)
        )

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
    else:
        return LazyResponse(
            kwargs, status=status, headers=headers, content_type=content_type
        )
