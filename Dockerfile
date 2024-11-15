FROM python:3.11-slim-buster as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml ./
RUN pip install --no-cache-dir build && \
    pip install --no cache-dir ".[dev, nlp, vector]"

FROM python:3.11-slim-buster

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgompl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser
USER appuser

WORKDIR /app

COPY --chown=appuser:appuser . .
