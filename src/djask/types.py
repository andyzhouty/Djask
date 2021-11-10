import typing as t

from .extensions import db

Config = t.Union[t.Dict[str, t.Any], t.Any]
ErrorResponse = t.Union[t.Tuple[str, int], t.Tuple[str, int, t.Mapping[str, str]]]
ModelType = t.Type[db.Model]
ModelList = t.List[ModelType]
