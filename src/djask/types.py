import typing as t

from .db.models import Model

Config = t.Union[t.Dict[str, t.Any], t.Any]
ErrorResponse = t.Union[t.Tuple[str, int], t.Tuple[str, int, t.Mapping[str, str]]]
ModelType = t.Type[Model]
ModelList = t.List[ModelType]
