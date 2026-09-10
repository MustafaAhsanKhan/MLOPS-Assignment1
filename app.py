import math
from pathlib import Path

from flask import Flask, jsonify, request

APP_NAME = "student-ml-api"
# The VERSION file is the single source of truth for the application version
APP_VERSION = (Path(__file__).parent / "VERSION").read_text().strip()

app = Flask(__name__)
app.json.sort_keys = False  # keep response fields in the documented order


def predict_value(value):
    # Placeholder model: this project is about the delivery workflow, not model quality
    return value * 2


@app.get("/health")
def health():
    return jsonify(status="healthy", application=APP_NAME, version=APP_VERSION)


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or "value" not in payload:
        return jsonify(error="Request body must be JSON with a 'value' field"), 400

    value = payload["value"]
    # bool is a subclass of int in Python, so it has to be rejected explicitly
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return jsonify(error="'value' must be a finite number"), 400

    return jsonify(input=value, prediction=predict_value(value))


if __name__ == "__main__":
    # Local development only; the container runs gunicorn
    app.run(host="0.0.0.0", port=5000)
