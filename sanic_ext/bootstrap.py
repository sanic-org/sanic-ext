from __future__ import annotations

from typing import Any, Callable, List, Optional, Type

from sanic import Sanic, __version__
from sanic.exceptions import SanicException
from sanic.log import logger

from sanic_ext.config import add_fallback_config
from sanic_ext.extensions.base import Extension
from sanic_ext.extensions.http.extension import HTTPExtension
from sanic_ext.extensions.injection.extension import InjectionExtension
from sanic_ext.extensions.injection.registry import InjectionRegistry
from sanic_ext.extensions.openapi.extension import OpenAPIExtension

MIN_SUPPORT = (21, 3, 2)


class Apply:
    def __init__(
        self,
        app: Sanic,
        *,
        extensions: Optional[List[Type[Extension]]] = None,
        built_in_extensions: bool = True,
        all_http_methods: bool = True,
        auto_head: bool = True,
        auto_options: bool = True,
        auto_trace: bool = False,
        cors: bool = True,
        **kwargs,
    ) -> None:
        """
        Ingres for instantiating sanic-ext

        :param app: Sanic application
        :type app: Sanic
        """
        if not isinstance(app, Sanic):
            raise SanicException(
                f"Cannot apply SanicExt to {app.__class__.__name__}"
            )

        sanic_version = tuple(map(int, __version__.split(".")))

        if MIN_SUPPORT > sanic_version:
            min_version = ".".join(map(str, MIN_SUPPORT))
            raise SanicException(
                f"SanicExt only works with Sanic v{min_version} and above. "
                f"It looks like you are running {__version__}."
            )

        add_fallback_config(app)
        kwargs.update(
            {
                "all_http_methods": all_http_methods,
                "auto_head": auto_head,
                "auto_options": auto_options,
                "auto_trace": auto_trace,
                "cors": cors,
            }
        )

        if not extensions:
            extensions = []
        if built_in_extensions:
            extensions.extend(
                [
                    InjectionExtension,
                    OpenAPIExtension,
                    HTTPExtension,
                ]
            )
        logger.info("Sanic Extensions:")
        for extclass in extensions[::-1]:
            extension = extclass(app, kwargs)
            extension._startup(self)

            logger.info(f"  > {extension.name} {extension.label()}")

        self.app = app
        self._injection_registry: Optional[InjectionRegistry] = None
        app.ctx.ext = self

    def injection(
        self,
        type: Type,
        constructor: Optional[Callable[..., Any]] = None,
    ) -> None:
        if not self._injection_registry:
            raise SanicException("Injection extension not enabled")
        self._injection_registry.register(type, constructor)
