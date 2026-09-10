from pathlib import Path

import pytest

from app import app

EXPECTED_VERSION = (Path(__file__).resolve().parent.parent / "VERSION").read_text().strip()


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "healthy",
        "application": "student-ml-api",
        "application_version": EXPECTED_VERSION,
        "model_version": "model-1",
    }


@pytest.mark.parametrize("value, expected", [(10, 20), (0, 0), (-3, -6), (2.5, 5.0)])
def test_predict_success(client, value, expected):
    response = client.post("/predict", json={"value": value})

    assert response.status_code == 200
    assert response.get_json() == {"input": value, "prediction": expected}


@pytest.mark.parametrize("payload", [{}, {"val": 10}, None])
def test_predict_missing_value(client, payload):
    response = client.post("/predict", json=payload)

    assert response.status_code == 400
    assert "value" in response.get_json()["error"]


@pytest.mark.parametrize("value", ["ten", None, True, [10], {"number": 10}, float("nan")])
def test_predict_invalid_value(client, value):
    response = client.post("/predict", json={"value": value})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_predict_rejects_non_json_body(client):
    response = client.post("/predict", data="value=10", content_type="text/plain")

    assert response.status_code == 400
