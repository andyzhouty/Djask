from apiflask import abort
from apiflask import HTTPError


def test_api_error_processor(app, client):
    assert not hasattr(app, "error_processor")

    @app.api_error_processor
    def handler(error: HTTPError):
        return (
            {"error_message": error.message, **error.extra_data},
            error.status_code,
            error.headers,
        )

    @app.get("/404")
    def handle_api_404():
        abort(404)

    rv = client.get("/404")
    assert rv.status_code == 404
    assert rv.get_json()["error_message"] == "Not Found"
