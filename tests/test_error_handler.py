from apiflask import HTTPError
from flask import abort


def test_default_error_processor(app, client):
    @app.get("/404")
    def handle_404():
        abort(404)

    resp = client.get("/404")
    assert resp.status_code == 404
    assert "Not Found" in resp.get_data(as_text=True)


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

    resp = client.get("/404")
    assert resp.status_code == 404
    assert resp.json["error_message"] == "Not Found"
