# student-ml-api

A small prediction API used to practise a production-style MLOps workflow:
feature branches, pull requests, GitHub Actions CI, Docker and GHCR releases.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Service health and application version |
| POST | `/predict` | Returns a prediction for `{"value": <number>}` |

```bash
curl http://localhost:5000/health
# {"status":"healthy","application":"student-ml-api","version":"1.0.0"}

curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{"value": 10}'
# {"input":10,"prediction":20}
```

Missing or invalid input returns `400` with an `error` message.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
python app.py
```

## Docker

```bash
docker build -t student-ml-api:1.0.0 .
docker run -d --name student-ml-api -p 5000:5000 student-ml-api:1.0.0
```

Released images are published to `ghcr.io/mustafaahsankhan/student-ml-api`.

## Workflow

- Changes reach `main` only through a feature branch and a pull request.
- **CI** (`.github/workflows/ci.yml`) runs on every PR to `main`: unit tests, then a Docker build and a container smoke test. It never pushes an image.
- **Release** (`.github/workflows/release.yml`) runs when a `vX.Y.Z` tag is pushed: tests, build, tag the image as `X.Y.Z`, `latest` and the short commit SHA, then push to GHCR.
- The image version is derived from the Git tag and must match the `VERSION` file.

```bash
git checkout main && git pull
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```
