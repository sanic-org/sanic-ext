from __future__ import annotations

from typing import TYPE_CHECKING

from sanic_ext.extensions.openapi.builders import SpecificationBuilder

from ..base import Extension
from .blueprint import blueprint_factory

if TYPE_CHECKING:
    from sanic_ext import Extend


class OpenAPIExtension(Extension):
    name = "openapi"

    def startup(self, bootstrap: Extend) -> None:
        if self.app.config.OAS:
            self.bp = blueprint_factory(self.app.config)
            self.app.blueprint(self.bp)
            bootstrap._openapi = SpecificationBuilder()

    def label(self):
        if self.app.config.OAS:
            return self._make_url()

        return ""

    def _make_url(self):
        name = f"{self.bp.name}.index"
        _server = (
            None
            if "SERVER_NAME" in self.app.config
            else self.app.serve_location
        ) or None
        _external = bool(_server) or "SERVER_NAME" in self.app.config
        return (
            f"[{self.app.url_for(name, _external=_external, _server=_server)}]"
        )
