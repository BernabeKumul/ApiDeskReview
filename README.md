# FastAPI Backend Project

Un proyecto FastAPI con arquitectura limpia y escalable, preconfigurado para integración con MongoDB, Qdrant y OpenAI.

## 🚀 Características

- ⚡ **FastAPI** con Uvicorn para alto rendimiento
- 🐍 **Python 3.13+** Compatible
- 🏗️ **Arquitectura modular** y escalable
- 🔧 **Configuración basada en variables de entorno**
- 📊 **MongoDB** ready (Motor + PyMongo)
- 🔍 **Qdrant** vector database ready
- 🤖 **OpenAI** integration ready
- 📝 **Documentación automática** con Swagger/OpenAPI
- 🧪 **Testing** setup con pytest
- 🔒 **CORS** configurado
- ✅ **Compatibilidad verificada** con Python 3.13.5

## 📁 Estructura del Proyecto

```
BackEnd/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación principal FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Configuración y settings
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py         # Router principal v1
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── health.py  # Endpoints de salud y hello world
│   ├── models/                # Modelos de datos (futuro)
│   ├── schemas/               # Schemas Pydantic
│   │   ├── __init__.py
│   │   └── base.py
│   ├── services/              # Servicios de negocio
│   │   ├── __init__.py
│   │   ├── database.py        # MongoDB service (placeholder)
│   │   ├── vector_store.py    # Qdrant service (placeholder)
│   │   └── ai_service.py      # OpenAI service (placeholder)
│   └── utils/                 # Utilidades
│       ├── __init__.py
│       └── logger.py
├── requirements.txt
├── run.py                     # Script de ejecución
└── README.md
```

## 🛠️ Instalación y Configuración

### 0. Verificar compatibilidad con Python 3.13

```bash
# Verificar que tienes Python 3.13+
python --version

# Ejecutar verificación de compatibilidad
python check_compatibility.py
```

### 1. Crear entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en el directorio raíz con el siguiente contenido:

```env
# Application Configuration
APP_NAME=FastAPI Backend
APP_VERSION=1.0.0
DEBUG=True
HOST=127.0.0.1
PORT=8000

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=fastapi_db

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=documents

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
ALLOWED_METHODS=["GET", "POST", "PUT", "DELETE"]
ALLOWED_HEADERS=["*"]
```

## 🚀 Ejecutar la aplicación

### Opción 1: Usando el script run.py
```bash
python run.py
```

### Opción 2: Usando uvicorn directamente
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## 📚 Endpoints Disponibles

Una vez que la aplicación esté ejecutándose, puedes acceder a:

- **Hello World**: `http://127.0.0.1:8000/api/v1/`
- **Health Check**: `http://127.0.0.1:8000/api/v1/health`
- **App Info**: `http://127.0.0.1:8000/api/v1/info`
- **Root**: `http://127.0.0.1:8000/`
- **Documentación API**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Ejecutar tests con coverage
pytest --cov=app tests/
```

## 🔧 Desarrollo

### Agregar nuevos endpoints

1. Crea un nuevo archivo en `app/api/v1/endpoints/`
2. Define tus endpoints usando FastAPI
3. Incluye el router en `app/api/v1/api.py`

### Conectar servicios externos

Los servicios para MongoDB, Qdrant y OpenAI están preconfigurados como placeholders en:
- `app/services/database.py` - MongoDB
- `app/services/vector_store.py` - Qdrant
- `app/services/ai_service.py` - OpenAI

## 📦 Dependencias Principales

- **FastAPI**: Framework web moderno y rápido
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **Pydantic**: Validación de datos y configuración
- **PyMongo + Motor**: Drivers MongoDB síncronos y asíncronos
- **Qdrant-client**: Cliente para Qdrant vector database
- **OpenAI**: Cliente oficial de OpenAI
- **Python-dotenv**: Manejo de variables de entorno

## 🎯 Próximos Pasos

1. Implementar la lógica de conexión a MongoDB en `database.py`
2. Configurar Qdrant en `vector_store.py`
3. Implementar la integración con OpenAI en `ai_service.py`
4. Agregar autenticación y autorización
5. Implementar modelos de datos específicos
6. Agregar logging avanzado
7. Configurar testing completo

---

¡Tu proyecto FastAPI está listo para desarrollo! 🎉