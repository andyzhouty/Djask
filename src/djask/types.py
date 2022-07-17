from __future__ import annotations

from typing import Any
from typing import Literal
from typing import Mapping
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import Union

from .db.models import Model

Config = Any
ErrorResponse = Union[Tuple[str, int], Tuple[str, int, Mapping[str, str]]]
ModelType = Type[Model]
ModelList = list[ModelType]
ModeLiteral = Literal["api", "ui"]
ModeArg = Tuple[ModeLiteral | Sequence[ModeLiteral]]
