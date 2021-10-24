from apiflask import APIFlask
from apiflask.exceptions import HTTPError
from apiflask.types import ErrorCallbackType


class Djask(APIFlask):

    # Rename the 'error_processor' method as 'api_error_processor'
    error_processor = property()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def api_error_processor(self, error: HTTPError) -> ErrorCallbackType:
        return super().error_processor(error)
