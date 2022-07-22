AuthModelInvalid = Exception(
    "The auth model you passed to the app config"
    "should be a subclass of djask.auth.abstract.AbstractUser."
)
ModelTypeError = TypeError(
    "The arg passed to register_model() must be a subclass of"
    "Model instead of PureModel or something else."
)


class AppDirectoryNotFoundError(FileNotFoundError):
    def __init__(self, directory: str) -> None:
        super().__init__(
            "wsgi.py detected in current directory, "
            f"but {directory}/ does not exist."
            "(where the app is supposed to be)"
        )
