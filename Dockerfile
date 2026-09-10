# Exact Python release pinned for reproducible builds (never python:latest)
FROM python:3.13.15-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Unprivileged runtime user; rarely changes, so it sits in an early cached layer
RUN useradd --no-create-home --uid 10001 appuser

# Dependencies before source code: this layer is reused until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code changes most often, so it is copied last
COPY VERSION app.py ./

# OCI metadata so every image can be traced back to its source commit.
# Declared after the pip layer: per-build values such as BUILD_DATE would
# otherwise invalidate the dependency cache on every release.
ARG APP_VERSION=dev
ARG GIT_COMMIT=unknown
ARG BUILD_DATE=unknown
ARG REPOSITORY_URL=unknown
LABEL org.opencontainers.image.title="student-ml-api" \
      org.opencontainers.image.description="Prediction API for the MLOps CI/CD exercise" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${GIT_COMMIT}" \
      org.opencontainers.image.source="${REPOSITORY_URL}" \
      org.opencontainers.image.created="${BUILD_DATE}"

USER appuser

EXPOSE 5000

# Bind to 0.0.0.0 so the published port is reachable from outside the container.
# Control socket disabled: Docker manages the process lifecycle and appuser has no home directory.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "--no-control-socket", "app:app"]
