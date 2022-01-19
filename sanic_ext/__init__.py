from importlib.metadata import version

from sanic_ext.bootstrap import Extend
from sanic_ext.config import Config
from sanic_ext.extensions.http.cors import cors
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extras.serializer.decorator import serializer
from sanic_ext.extras.validation.decorator import validate

__version__ = version("sanic-ext")

__all__ = [
    "Config",
    "Extend",
    "cors",
    "openapi",
    "serializer",
    "validate",
]
