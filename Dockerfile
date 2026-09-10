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

USER appuser

EXPOSE 5000

# Bind to 0.0.0.0 so the published port is reachable from outside the container
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app:app"]
