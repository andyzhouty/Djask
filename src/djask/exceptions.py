class ModelNotFoundError(Exception):
    def __init__(self, model: str) -> None:
        super().__init__(
            f"The '{model}' is neither a table name nor a model class name"
            ", check if there is a typo."
        )


class InvalidAuthModelError(TypeError):
    def __init__(self) -> None:
        super().__init__(
            "The auth model you passed to the app config "
            "should be a subclass of djask.auth.abstract.AbstractUser."
        )


class ModelTypeError(TypeError):
    def __init__(self) -> None:
        super().__init__(
            "The arg passed to register_model() must be a subclass of "
            "Model instead of PureModel or something else."
        )


class AppDirectoryNotFoundError(FileNotFoundError):
    def __init__(self, directory: str) -> None:
        super().__init__(
            "wsgi.py detected in current directory, "
            f"but {directory}/ does not exist."
            "(where the app is supposed to be)"
        )
