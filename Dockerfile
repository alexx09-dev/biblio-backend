# Dockerfile
# Define cómo construir la imagen Docker de la API

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Puerto actualizado a 2603
EXPOSE 2603

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "2603"]