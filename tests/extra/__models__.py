import sys

from dataclasses import dataclass, field
from typing import Literal, Optional, Union


@dataclass
class ModelStr:
    foo: str


@dataclass
class ModelInt:
    foo: int


@dataclass
class ModelFloat:
    foo: float


@dataclass
class ModelBool:
    foo: bool


@dataclass
class ModelOptionalStr:
    foo: Optional[str]


@dataclass
class ModelUnion:
    foo: Union[int, float]


@dataclass
class ModelUnionModels:
    foo: Union[ModelInt, ModelFloat]


@dataclass
class ModelUnionStrInt:
    foo: Union[str, int]


@dataclass
class ModelUnionIntStr:
    foo: Union[int, str]


@dataclass
class ModelOptionalUnionStrInt:
    foo: Optional[Union[str, int]]


@dataclass
class ModelOptionalUnionIntStr:
    foo: Optional[Union[int, str]]


@dataclass
class ModelListStr:
    foo: list[str]


@dataclass
class ModelListModel:
    foo: list[ModelStr]


@dataclass
class ModelOptionalList:
    foo: Optional[list[str]]


@dataclass
class ModelListUnion:
    foo: list[Union[int, float]]


@dataclass
class ModelOptionalListUnion:
    foo: Optional[list[Union[int, float]]]


@dataclass
class ModelModel:
    foo: ModelStr


@dataclass
class ModelOptionalModel:
    foo: Optional[ModelStr]


@dataclass
class ModelDictStr:
    foo: dict[str, str]


@dataclass
class ModelDictModel:
    foo: dict[str, ModelStr]


@dataclass
class ModelOptionalDict:
    foo: Optional[dict[str, str]]


@dataclass
class ModelDictUnion:
    foo: dict[str, Union[int, float]]


@dataclass
class ModelOptionalDictUnion:
    foo: Optional[dict[str, Union[int, float]]]


@dataclass
class ModelSingleLiteral:
    foo: Literal[True]


@dataclass
class ModelMultipleLiteral:
    foo: Literal[True, "y", "Y", 1]


@dataclass
class ModelOptionalSingleLiteral:
    foo: Optional[Literal[True]]


@dataclass
class ModelOptionalMultipleLiteral:
    foo: Optional[Literal[True, "y", "Y", 1]]


@dataclass
class ModelListStrWithDefaultFactory:
    foo: list[str] = field(default_factory=list)


if sys.version_info > (3, 10):

    @dataclass
    class ModelUnionTypeStrNone:
        foo: str | None

    @dataclass
    class ModelUnionTypeStrIntNone:
        foo: str | int | None

    @dataclass
    class ModelUnionTypeStrInt:
        foo: str | int
