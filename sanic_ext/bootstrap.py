from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Type, Union

from sanic import Sanic, __version__
from sanic.exceptions import SanicException
from sanic.log import logger

from sanic_ext.config import Config, add_fallback_config
from sanic_ext.extensions.base import Extension
from sanic_ext.extensions.http.extension import HTTPExtension
from sanic_ext.extensions.injection.extension import InjectionExtension
from sanic_ext.extensions.injection.registry import InjectionRegistry
from sanic_ext.extensions.openapi.extension import OpenAPIExtension

MIN_SUPPORT = (21, 3, 2)


class Extend:
    def __init__(
        self,
        app: Sanic,
        *,
        extensions: Optional[List[Type[Extension]]] = None,
        built_in_extensions: bool = True,
        config: Optional[Union[Config, Dict[str, Any]]] = None,
        **kwargs,
    ) -> None:
        """
        Ingress for instantiating sanic-ext

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

        self.app = app
        self._injection_registry: Optional[InjectionRegistry] = None
        app.ctx.ext = self

        if not isinstance(config, Config):
            config = Config.from_dict(config or {})
        self.config = add_fallback_config(app, config, **kwargs)

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
        init_logs = ["Sanic Extensions:"]
        for extclass in extensions[::-1]:
            extension = extclass(app, self.config)
            extension._startup(self)
            init_logs.append(f"  > {extension.name} {extension.label()}")

        list(map(logger.info, init_logs))

    def injection(
        self,
        type: Type,
        constructor: Optional[Callable[..., Any]] = None,
    ) -> None:
        if not self._injection_registry:
            raise SanicException("Injection extension not enabled")
        self._injection_registry.register(type, constructor)
