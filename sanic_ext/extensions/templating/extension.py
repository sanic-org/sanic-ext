from __future__ import annotations

import os

from collections import abc
from pathlib import Path
from typing import TYPE_CHECKING, Sequence, Union

from jinja2 import (
    Environment,
    FileSystemLoader,
    __version__,
    select_autoescape,
)

from sanic_ext.extensions.templating.engine import Templating

from ..base import Extension


if TYPE_CHECKING:
    from sanic_ext import Extend


class TemplatingExtension(Extension):
    name = "templating"

    def startup(self, bootstrap: Extend) -> None:
        self._add_template_paths_to_reloader(
            self.config.TEMPLATING_PATH_TO_TEMPLATES
        )
        loader = FileSystemLoader(self.config.TEMPLATING_PATH_TO_TEMPLATES)

        if not hasattr(bootstrap, "environment"):
            bootstrap.environment = Environment(
                loader=loader,
                autoescape=select_autoescape(),
                enable_async=self.config.TEMPLATING_ENABLE_ASYNC,
            )
        if not hasattr(bootstrap, "templating"):
            bootstrap.templating = Templating(
                environment=bootstrap.environment, config=self.config
            )
        bootstrap.templating.environment.globals["url_for"] = self.app.url_for

    def label(self):
        return f"jinja2=={__version__}"

    def _add_template_paths_to_reloader(
        self, path: Union[str, os.PathLike, Sequence[Union[str, os.PathLike]]]
    ) -> None:
        if not isinstance(path, abc.Iterable) or isinstance(path, str):
            path = [path]

        for item in path:
            self.app.state.reload_dirs.add(Path(item))
