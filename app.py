from itertools import count

from flask import Flask, abort, request, url_for
from werkzeug.exceptions import HTTPException

app = Flask(__name__)


@app.before_request
def require_json():
    """Run before matched item writes to check the request body."""
    if (
        request.endpoint in {"create_item", "replace_item"}
        and request.method in {"POST", "PUT"}
    ):
        if not request.is_json:
            abort(415, description="Use Content-Type: application/json.")
        if not isinstance(request.get_json(), dict):
            abort(400, description="The JSON body must be an object.")


@app.errorhandler(HTTPException)
def json_error(error):
    # Keep HTTP headers such as Allow on 405 responses.
    response = error.get_response()
    response.data = app.json.dumps({"error": error.description})
    response.content_type = "application/json"
    return response


# Demo storage: resets whenever the server restarts.
items = {1: {"id": 1, "name": "Apple"}}
item_ids = count(2)


def read_name():
    name = request.get_json().get("name")
    if not isinstance(name, str) or not name.strip():
        abort(400, description="name must be a non-empty string.")
    return name.strip()


@app.get("/items")
def list_items():
    return list(items.values())


@app.get("/items/<int:item_id>")
def get_item(item_id):
    if item_id not in items:
        abort(404, description="Item not found.")
    return items[item_id]


@app.post("/items")
def create_item():
    name = read_name()
    item_id = next(item_ids)
    items[item_id] = {"id": item_id, "name": name}
    return items[item_id], 201, {"Location": url_for("get_item", item_id=item_id)}


@app.put("/items/<int:item_id>")
def replace_item(item_id):
    get_item(item_id)
    items[item_id] = {"id": item_id, "name": read_name()}
    return items[item_id]


@app.delete("/items/<int:item_id>")
def delete_item(item_id):
    get_item(item_id)
    del items[item_id]
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
