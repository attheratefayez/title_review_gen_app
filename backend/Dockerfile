FROM python:3.12-slim

WORKDIR /app

# install java 
RUN apt-get update && apt-get install --no-install-recommends \
    openjdk-25-jdk-headless \
    && rm -rf /var/log/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml .
# RUN pip install --no-cache-dir -r requirements.txt
RUN uv sync 

COPY . .

ENV JAVA_HOME=/app/app/llm_app/.java/jdk25
ENV PATH=$JAVA_HOME/bin:$PATH
EXPOSE 8000

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]
