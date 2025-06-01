FROM python:alpine

WORKDIR /app

COPY uv.lock pyproject.toml ./

RUN pip install --no-cache-dir uv && \
    uv sync --no-cache && \
    rm -f uv.lock pyproject.toml

COPY src/ .

EXPOSE 7086

ENTRYPOINT ["uv", "run", "index.py"]
