import typing as t

Config = t.Union[t.Dict[str, t.Any], t.Any]
ErrorResponse = t.Union[t.Tuple[str, int], t.Tuple[str, int, t.Mapping[str, str]]]
