FROM python:3.12

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir uv

RUN uv sync

COPY . .

CMD ["uv", "run", "fastapi", "run"] 