FROM python:alpine AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1

WORKDIR /app

COPY uv.lock pyproject.toml ./

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN uv sync --frozen --no-dev


FROM python:alpine

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY src/ .

EXPOSE 7086

ENTRYPOINT ["python", "index.py"]