# 📚 Biblioteca Personal API

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=flat)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)

Backend REST profesional para gestionar un catálogo de libros personales.
Construido con FastAPI y MySQL, con soporte para búsqueda, filtrado por género
y actualización parcial de registros.

---

## 🧰 Tecnologías

| Tecnología | Versión | Rol |
|---|---|---|
| FastAPI | 0.115.0 | Framework web REST |
| Python | 3.12 | Lenguaje base |
| MySQL | 8.0 | Base de datos |
| SQLAlchemy | 2.0 | ORM |
| Alembic | 1.13.3 | Migraciones |
| Pydantic v2 | 2.x | Validación de datos |
| Pydantic Settings | 2.5.2 | Configuración tipada |
| Docker + Compose | latest | Portabilidad |

---

## 📋 Requisitos previos

- Python 3.12+
- MySQL 8.0 corriendo en localhost:3306
- pip actualizado
- (Opcional) Docker Desktop para ejecución con contenedores

---

## ⚙️ Instalación sin Docker

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/biblioteca_fastapi_v2.git
cd biblioteca_fastapi_v2
```

### 2. Crear y activar entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:
```ini
DB_USER=root
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=3306
DB_NAME=biblioteca_atlas
APP_NAME=Biblioteca Personal API
APP_VERSION=2.0.0
```

### 5. Crear la base de datos en MySQL
```sql
CREATE DATABASE IF NOT EXISTS biblioteca_atlas
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

### 6. Ejecutar migraciones
```bash
python migrate.py
```

### 7. Iniciar la API
```bash
uvicorn main:app --reload --port 2603
```

La API estará disponible en `http://localhost:2603`

---

## 🐳 Instalación con Docker

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/biblioteca_fastapi_v2.git
cd biblioteca_fastapi_v2
```

### 2. Levantar los servicios
```bash
docker-compose up --build
```

Docker levantará automáticamente:
- MySQL 8 en el puerto `3307`
- La API FastAPI en el puerto `2603`
- Las migraciones se ejecutan automáticamente al iniciar

### 3. Detener los servicios
```bash
docker-compose down
```

---

## 🌐 Endpoints

| Método | Endpoint | Descripción |
|---|---|---|
| GET | /api/libros | Listar todos los libros |
| GET | /api/libros?genero=Terror | Filtrar por género |
| GET | /api/libros?busqueda=garcia | Buscar por título o autor |
| GET | /api/libros?genero=Terror&busqueda=casa | Filtros combinados |
| GET | /api/libros/{id} | Obtener libro por ID |
| POST | /api/libros | Crear nuevo libro |
| PUT | /api/libros/{id} | Actualizar libro (parcial) |
| DELETE | /api/libros/{id} | Eliminar libro |

### Ejemplo de request — Crear libro
```json
POST /api/libros
{
    "titulo": "Dune",
    "autor": "Frank Herbert",
    "rating": 5,
    "isbn": "978-84-450-7315-5",
    "genero": "Ciencia Ficción",
    "anio": 1965
}
```

### Ejemplo de response — 201 Created
```json
{
    "id": 1,
    "titulo": "Dune",
    "autor": "Frank Herbert",
    "rating": 5,
    "isbn": "978-84-450-7315-5",
    "genero": "Ciencia Ficción",
    "anio": 1965
}
```

### Formato de errores

Todos los errores devuelven la misma estructura:
```json
{
    "status": 404,
    "mensaje": "Recurso no encontrado",
    "detalle": "No se encontró ningún libro con id=99"
}
```

---

## 📊 Estructura del proyecto
```
biblioteca_fastapi_v2/
├── main.py                 ← Punto de entrada, configuración FastAPI
├── config.py               ← Variables de entorno con Pydantic Settings
├── database.py             ← Motor SQLAlchemy y sesiones
├── schemas.py              ← Modelos Pydantic de entrada/salida
├── logger.py               ← Logging estructurado
├── migrate.py              ← Script de migraciones Alembic
├── requirements.txt        ← Dependencias del proyecto
├── Dockerfile              ← Imagen Docker de la API
├── docker-compose.yml      ← Orquestación API + MySQL
├── .env                    ← Variables de entorno (no subir a GitHub)
├── alembic.ini             ← Configuración Alembic
├── alembic/                ← Historial de migraciones
├── models/
│   └── libro.py            ← Modelo ORM tabla libros
├── services/
│   └── libro_service.py    ← Lógica de negocio y acceso a datos
├── api/
│   └── libros.py           ← Router y endpoints REST
└── exceptions/
    └── handlers.py         ← Manejadores globales de errores
```

---

## 📖 Documentación interactiva

Una vez iniciada la API, accede a la documentación automática:

| URL | Descripción |
|---|---|
| http://localhost:2603/docs | Swagger UI — probar endpoints |
| http://localhost:2603/redoc | ReDoc — documentación navegable |

---

## 📸 Screenshots

> *Próximamente — Swagger UI y ejemplos de requests en Postman*

---

## 🔮 Próximos pasos

- [ ] Frontend en React + Vite consumiendo esta API
- [ ] Autenticación con JWT
- [ ] Paginación en el listado de libros
- [ ] Portadas de libros via Open Library usando el ISBN
- [ ] Deployment en Railway o Render

---

## 👤 Autor

Desarrollado como proyecto de aprendizaje de FastAPI + MySQL.