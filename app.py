from pathlib import Path

from flask import Flask, jsonify

APP_NAME = "student-ml-api"
# The VERSION file is the single source of truth for the application version
APP_VERSION = (Path(__file__).parent / "VERSION").read_text().strip()

app = Flask(__name__)
app.json.sort_keys = False  # keep response fields in the documented order


@app.get("/health")
def health():
    return jsonify(status="healthy", application=APP_NAME, version=APP_VERSION)


if __name__ == "__main__":
    # Local development only; the container runs gunicorn
    app.run(host="0.0.0.0", port=5000)
