import typing as t

from .db.models import Model

Config = t.Any
ErrorResponse = t.Union[t.Tuple[str, int], t.Tuple[str, int, t.Mapping[str, str]]]
ModelType = t.Type[Model]
ModelList = t.List[ModelType]
ModeLiteral = t.Literal["api", "ui"]
ModeArg = t.Tuple[t.Union[ModeLiteral, t.Sequence[ModeLiteral]]]
