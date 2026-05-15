FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV JAVA_HOME=/app/app/llm_app/.java/jdk25
ENV PATH=$JAVA_HOME/bin:$PATH
EXPOSE 8000

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]
