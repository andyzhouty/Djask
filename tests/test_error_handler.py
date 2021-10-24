from flask import abort
from apiflask import HTTPError


def test_default_error_processor(app, client):
    @app.get("/404")
    def handle_404():
        abort(404)

    rv = client.get("/404")
    assert rv.status_code == 404
    assert "Not Found" in rv.get_data(as_text=True)


def test_custom_error_processor(app, client):
    @app.error_processor
    def handler(error: HTTPError):
        return (
            {"error_message": error.message, **error.extra_data},
            error.status_code,
            error.headers,
        )

    @app.get("/404")
    def handle_custom_404():
        abort(404)

    rv = client.get("/404")
    assert rv.status_code == 404
    assert rv.get_json()["error_message"] == "Not Found"
