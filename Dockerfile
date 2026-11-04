FROM python:3.11-slim AS builder
WORKDIR /build
COPY pyproject.toml .
RUN pip install --no-cache-dir pip setuptools wheel &&     pip wheel --no-cache-dir --wheel-dir=/build/wheels pytest

FROM python:3.11-slim AS runner
RUN groupadd -g 10001 appgroup && useradd -u 10001 -g appgroup -m -s /bin/bash appuser
WORKDIR /app
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY pyproject.toml .
COPY src/ ./src
COPY tests/ ./tests
RUN pip install --no-cache-dir --no-deps -e .
RUN chown -R appuser:appgroup /app
USER appuser
CMD ["pytest", "-v", "tests/"]
