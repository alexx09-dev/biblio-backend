# Imagen base
FROM python:3.12-slim

# Variables de entorno (logs en tiempo real y sin .pyc)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Copiamos dependencias primero (mejora cache)
COPY requirements.txt .

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del proyecto
COPY . .

# Puerto que usa Render
EXPOSE 10000

# Comando de arranque (CORREGIDO)
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
