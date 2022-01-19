from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Union


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
class ModelListStr:
    foo: List[str]


@dataclass
class ModelListModel:
    foo: List[ModelStr]


@dataclass
class ModelOptionalList:
    foo: Optional[List[str]]


@dataclass
class ModelListUnion:
    foo: List[Union[int, float]]


@dataclass
class ModelOptionalListUnion:
    foo: Optional[List[Union[int, float]]]


@dataclass
class ModelModel:
    foo: ModelStr


@dataclass
class ModelOptionalModel:
    foo: Optional[ModelStr]


@dataclass
class ModelDictStr:
    foo: Dict[str, str]


@dataclass
class ModelDictModel:
    foo: Dict[str, ModelStr]


@dataclass
class ModelOptionalDict:
    foo: Optional[Dict[str, str]]


@dataclass
class ModelDictUnion:
    foo: Dict[str, Union[int, float]]


@dataclass
class ModelOptionalDictUnion:
    foo: Optional[Dict[str, Union[int, float]]]


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
    foo: List[str] = field(default_factory=list)
