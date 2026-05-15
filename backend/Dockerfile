FROM python:3.14-slim

WORKDIR /app

# install java 
RUN apt-get update && apt-get install --no-install-recommends -y \
    openjdk-25-jdk-headless \
    && rm -rf /var/log/apt/lists/*

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml .
RUN uv pip install --system . -r pyproject.toml

COPY . .

EXPOSE 8000

CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]
