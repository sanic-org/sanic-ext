from __future__ import annotations

from abc import ABCMeta
from dataclasses import dataclass, field
from enum import Enum, auto
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Type, TypedDict, Union

from sanic.helpers import Default, _default

from .base import BaseDecorator
from .registry import DefinitionRegistry

DEFAULT_META = {
    "duplicate": False,
    "merge": False,
}


class BaseEnum(str, Enum):
    def _generate_next_value_(name: str, *args) -> str:  # type: ignore
        return name.lower()

    def __str__(self):
        return self.name.lower()


class ParameterInChoice(BaseEnum):
    QUERY = auto()
    HEADER = auto()
    PATH = auto()
    COOKIE = auto()


class ParameterStyleChoice(BaseEnum):
    DEFAULT = auto()
    FORM = auto()
    SIMPLE = auto()
    MATRIX = auto()
    LABEL = auto()
    SPACE_DELIMITED = auto()
    PIPE_DELIMITED = auto()
    DEEP_OBJECT = auto()


class DefinitionType(ABCMeta):
    def __new__(cls, name, bases, attrs, **kwargs):
        meta = {**DEFAULT_META}
        if defined := attrs.pop("Meta", None):
            meta.update(
                {
                    k: v
                    for k, v in defined.__dict__.items()
                    if not k.startswith("_")
                }
            )
        attrs["meta"] = SimpleNamespace(**meta)
        gen_class = super().__new__(cls, name, bases, attrs, **kwargs)
        return gen_class


class Definition(BaseDecorator, metaclass=DefinitionType):
    def setup(self):
        key = f"{self.func.__module__}.{self.func.__qualname__}"
        DefinitionRegistry()[key] = self
        super().setup()


class Extendable:
    """
    This object is extendable according to Specification Extensions. For more
    information: https://swagger.io/specification/#specification-extensions

    As an example:

        @oas.foo(..., something_additional=1234)

    Will translate into the property:

        x-something-additional
    """

    extension: Dict[str, Any]

    def __new__(cls, *args, **kwargs):
        if args and args[0] is cls:
            args = args[1:]
        if not hasattr(cls, "_init"):
            cls._init = cls.__init__
            cls.__init__ = lambda *a, **k: None

        obj = object.__new__(cls)
        obj.extension = {
            key: kwargs.pop(key)
            for key in list(kwargs.keys())
            if key not in cls.__dataclass_fields__
        }
        cls._init(obj, *args, **kwargs)

        return obj


@dataclass
class Description:
    description: Optional[str] = None


@dataclass
class URL:
    url: str


@dataclass
class ExternalDocument(Description, URL, Extendable):
    """Some documentation about external documents"""


@dataclass
class Name:
    name: str


@dataclass
class Text:
    text: str


@dataclass
class Summary:
    summary: Optional[str] = None


@dataclass
class Required:
    required: bool = False


@dataclass
class Deprecated:
    deprecated: bool = False


@dataclass
class ParameterIn:
    _in: ParameterInChoice = ParameterInChoice.QUERY


@dataclass
class Schema:  # TODO: Schema https://swagger.io/specification/#schema-object
    model: Type[object]

    def __post_init__(self):
        if isinstance(self.model, Default):
            self.schema = str


@dataclass
class SchemaArg:
    schema: Optional[
        Union[Default, Schema, str, float, int, bool, Reference]
    ] = _default


@dataclass
class SimpleExample:
    example: Any = None


@dataclass
class Example(Description, Summary, Extendable):
    value: Any = None
    external_value: Union[Default, str] = _default

    def __post_init__(self):
        if not isinstance(self.external_value, Default) and self.value:
            raise ValueError


@dataclass
class Examples:
    examples: Dict[str, Union[Example, Reference]] = field(
        default_factory=list
    )


@dataclass
class Content:
    content: Optional[Union[Default, MediaType]] = _default


@dataclass
class Parameter(
    Examples,
    SimpleExample,
    Deprecated,
    Required,
    Description,
    Content,
    SchemaArg,
    ParameterIn,
    Name,
    Extendable,
):
    style: ParameterStyleChoice = ParameterStyleChoice.DEFAULT
    allow_empty_value: bool = False
    allow_reserved: bool = False
    explode: Union[Default, bool] = _default

    __ENUMS__ = (("_in", ParameterInChoice), ("style", ParameterStyleChoice))

    def __post_init__(self):
        for name, choices in self.__ENUMS__:
            value = getattr(self, name)
            if not isinstance(value, choices):
                setattr(self, name, choices(value))

        if self._in is ParameterInChoice.PATH:
            self.required = True

        if self.style is ParameterStyleChoice.DEFAULT:
            self.style = (
                ParameterStyleChoice.FORM
                if self._in
                in (ParameterInChoice.QUERY, ParameterInChoice.COOKIE)
                else ParameterStyleChoice.SIMPLE
            )

        if self.allow_empty_value and self._in is not ParameterInChoice.QUERY:
            raise ValueError

        if isinstance(self.explode, Default):
            self.explode = self.style is ParameterStyleChoice.FORM

        if self.example and self.examples:
            raise ValueError

        if isinstance(self.schema, Default) and isinstance(
            self.content, Default
        ):
            self.schema = str
            self.content = None
        elif isinstance(self.schema, Default) and not isinstance(
            self.content, Default
        ):
            self.schema = None
        elif not isinstance(self.schema, Default) and isinstance(
            self.content, Default
        ):
            self.content = None
        else:
            raise ValueError

        if self.schema and not isinstance(self.schema, Schema):
            self.schema = Schema(model=self.schema)


@dataclass
class Reference:
    ...


@dataclass
class MediaType:
    ...


@dataclass
class RequestBody(Required, Description, Content):
    def __post_init__(self):
        if isinstance(self.content, Default):
            raise ValueError


# !!!!!!! DICTS !!!!!!! #


class ParameterDict(TypedDict):
    name: str


# !!!!!!! DECORATORS !!!!!!! #


@dataclass
class tags(Definition):
    values: List[str]

    class Meta:
        merge = True

    def merge(self, target: tags) -> None:
        self.values.extend(target.values)


@dataclass
class tag(Text, BaseDecorator):
    def setup(self):
        tags([self.text])(self.func)


@dataclass
class summary(Text, Definition):
    ...


@dataclass
class description(Text, Definition):
    ...


@dataclass
class external_docs(Definition):
    documents: List[ExternalDocument]

    class Meta:
        merge = True

    def merge(self, target: external_docs) -> None:
        self.documents.extend(target.documents)


@dataclass
class external_doc(ExternalDocument, BaseDecorator):
    """something"""

    def setup(self):
        external_docs([self])(self.func)


document = external_doc


@dataclass
class operation_id(Text, Definition):
    ...


@dataclass
class parameters(Definition):  # TODO: Reference
    values: List[Union[Parameter, Reference, ParameterDict]]

    class Meta:
        merge = True

    def merge(self, target: parameters) -> None:
        self.values.extend(target.values)

    def __post_init__(self):
        self.values = [
            val if isinstance(val, Parameter) else Parameter(**val)
            for val in self.values
        ]


@dataclass
class parameter(Parameter, BaseDecorator):
    def setup(self):
        parameters([self])(self.func)


@dataclass
class request_body(RequestBody, Reference, Definition):  # TODO
    ...


body = request_body


@dataclass
class responses(Definition):  # TODO
    ...


@dataclass
class callbacks(Definition):  # TODO
    ...


@dataclass
class deprecated(Definition):  # TODO
    ...


@dataclass
class security(Definition):  # TODO
    ...


@dataclass
class servers(Definition):  # TODO
    ...


# "definitions",
# "body",
# "component",
# "definition",
# "deprecated",
# "description",
# "document",
# "exclude",
# "no_autodoc",
# "operation",
# "parameter",
# "response",
# "secured",
# "summary",
