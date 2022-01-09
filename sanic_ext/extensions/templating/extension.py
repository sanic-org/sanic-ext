from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sanic_ext.extensions.templating.engine import Templating

from ..base import Extension

if TYPE_CHECKING:
    from sanic_ext import Extend


class TemplatingExtension(Extension):
    name = "templating"

    def startup(self, bootstrap: Extend) -> None:
        loader = FileSystemLoader(self.config.TEMPLATING_PATH_TO_TEMPLATES)

        # TODO:
        # - API to customize environment, autoescape, etc
        bootstrap.environment = Environment(
            loader=loader,
            autoescape=select_autoescape(),
            enable_async=self.config.TEMPLATING_ENABLE_ASYNC,
        )
        bootstrap.templating = Templating(
            environment=bootstrap.environment, config=self.config
        )

        @self.app.after_server_start
        async def setup_request_context(app, _):
            app.ctx.__request__ = ContextVar("request")

        @self.app.on_request
        async def attach_request(request):
            request.app.ctx.__request__.set(request)
