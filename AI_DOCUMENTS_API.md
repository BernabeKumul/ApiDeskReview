# API de Documentos de IA - Implementación MongoDB

## Resumen
Se ha implementado una solución completa para extraer y gestionar la colección `AIDocuments` de MongoDB, incluyendo:

1. **Clase genérica para MongoDB** - Reutilizable para cualquier colección
2. **Servicio específico** - Para operaciones con AIDocuments
3. **Endpoints completos** - API REST para todas las operaciones CRUD
4. **Filtros avanzados** - Búsqueda por FileName, DocumentId y contenido

## Estructura de la Colección AIDocuments

```json
{
  "_id": ObjectId("68388291247d5d496a81071a"),
  "DocumentId": 853346,
  "FileName": "DOC20250307135412.352.pdf",
  "DocumentType": "Document",
  "Content": "Next Crop: 29\nRoom: 308...",
  "TotalReading": 8,
  "CreatedAt": ISODate("2025-05-29T15:51:45.489Z"),
  "UpdatedAt": ISODate("2025-05-29T17:46:41.930Z"),
  "Inactive": false
}
```

## Configuración

### 1. Base de Datos
Actualizar la configuración en `app/core/config.py`:

```python
# MongoDB Configuration
mongodb_url: str = "mongodb://usuario:password@localhost:27017"  # Cambiar por credenciales reales
mongodb_database: str = "azzule_ai_db"
```

### 2. Variables de Entorno
Crear un archivo `.env` con:

```env
MONGODB_URL=mongodb://usuario:password@localhost:27017
MONGODB_DATABASE=azzule_ai_db
```

## Endpoints Disponibles

### 1. Buscar Documento por Filtros
```http
GET /api/v1/ai-documents/search?file_name=DOC20250307135412.352.pdf&document_id=853346
```

**Parámetros de consulta:**
- `file_name` (opcional): Nombre exacto del archivo
- `document_id` (opcional): ID del documento

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Documento encontrado exitosamente",
  "data": {
    "id": "68388291247d5d496a81071a",
    "document_id": 853346,
    "file_name": "DOC20250307135412.352.pdf",
    "document_type": "Document",
    "content": "Next Crop: 29...",
    "total_reading": 8,
    "created_at": "2025-05-29T15:51:45.489Z",
    "updated_at": "2025-05-29T17:46:41.930Z",
    "inactive": false
  }
}
```

### 2. Obtener Todos los Documentos
```http
GET /api/v1/ai-documents/?page=1&page_size=10&sort_by=CreatedAt&sort_order=desc
```

**Parámetros de consulta:**
- `document_id` (opcional): Filtrar por ID del documento
- `file_name` (opcional): Filtrar por nombre de archivo
- `document_type` (opcional): Filtrar por tipo de documento
- `inactive` (opcional): Filtrar por estado (true/false)
- `page` (opcional, default=1): Número de página
- `page_size` (opcional, default=10): Tamaño de página
- `sort_by` (opcional, default="CreatedAt"): Campo para ordenar
- `sort_order` (opcional, default="desc"): Orden (asc/desc)

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Se encontraron 5 documentos",
  "data": [...],
  "total_count": 25,
  "page": 1,
  "page_size": 10
}
```

### 3. Obtener Documento por ID de MongoDB
```http
GET /api/v1/ai-documents/{document_id}
```

### 4. Crear Nuevo Documento
```http
POST /api/v1/ai-documents/
Content-Type: application/json

{
  "document_id": 123456,
  "file_name": "nuevo_documento.pdf",
  "document_type": "Document",
  "content": "Contenido del documento...",
  "total_reading": 0,
  "inactive": false
}
```

### 5. Actualizar Documento
```http
PUT /api/v1/ai-documents/{document_id}
Content-Type: application/json

{
  "content": "Contenido actualizado...",
  "total_reading": 5
}
```

### 6. Eliminar Documento (Físico)
```http
DELETE /api/v1/ai-documents/{document_id}
```

### 7. Eliminación Lógica (Marcar como Inactivo)
```http
PATCH /api/v1/ai-documents/{document_id}/soft-delete
```

### 8. Buscar por Contenido
```http
GET /api/v1/ai-documents/search/content?search_term=Room&page=1&page_size=10
```

## Servicios Implementados

### 1. GenericMongoRepository
Clase genérica reutilizable para cualquier colección:

```python
from app.services.database import database_service

# Obtener repositorio para cualquier colección
repository = database_service.get_repository("mi_coleccion")

# Usar métodos genéricos
documents = await repository.find_many({"status": "active"})
document = await repository.find_one({"_id": ObjectId("...")})
```

### 2. AIDocumentService
Servicio específico para AIDocuments:

```python
from app.services.ai_document_service import ai_document_service

# Buscar por filtros específicos
document = await ai_document_service.get_document_by_filters(
    file_name="documento.pdf",
    document_id=123
)

# Obtener todos con filtros
documents = await ai_document_service.get_all_documents(
    filters=AIDocumentFilterModel(inactive=False),
    skip=0,
    limit=10
)
```

## Modelos de Datos

### AIDocumentModel
Modelo principal para documentos:
- Conversión automática entre MongoDB y Pydantic
- Manejo de ObjectId como string
- Aliases para campos de MongoDB

### AIDocumentFilterModel
Para filtros de búsqueda:
- Conversión automática a filtros de MongoDB
- Soporte para búsqueda parcial

### Esquemas de Respuesta
- `AIDocumentResponse`: Respuesta individual
- `AIDocumentListResponse`: Lista con paginación
- `AIDocumentCreateRequest`: Crear documento
- `AIDocumentUpdateRequest`: Actualizar documento

## Health Checks

### Verificar Estado General
```http
GET /api/v1/health
```

### Verificar Solo MongoDB
```http
GET /api/v1/health/mongodb
```

## Inicialización

El sistema se conecta automáticamente a MongoDB durante el startup:

```python
# En main.py
@app.on_event("startup")
async def startup_event():
    await database_service.connect()
    
@app.on_event("shutdown") 
async def shutdown_event():
    await database_service.disconnect()
```

## Logging

Todos los servicios incluyen logging detallado:
- Operaciones exitosas
- Errores con contexto
- Información de debug para desarrollo

## Ejemplos de Uso

### Buscar Documento Específico
```bash
curl -X GET "http://localhost:8000/api/v1/ai-documents/search?file_name=DOC20250307135412.352.pdf"
```

### Obtener Todos los Documentos Activos
```bash
curl -X GET "http://localhost:8000/api/v1/ai-documents/?inactive=false&page=1&page_size=20"
```

### Buscar en Contenido
```bash
curl -X GET "http://localhost:8000/api/v1/ai-documents/search/content?search_term=Room%20308"
```

## Notas Importantes

1. **Conexión MongoDB**: Actualizar credenciales reales en configuración
2. **Manejo de Errores**: Todos los endpoints incluyen manejo completo de errores
3. **Paginación**: Implementada en todos los endpoints de listado
4. **Validación**: Validación automática de datos con Pydantic
5. **Extensibilidad**: La clase genérica permite agregar nuevas colecciones fácilmente

## Próximos Pasos

1. Actualizar `mongodb_url` con credenciales reales
2. Configurar variables de entorno de producción
3. Probar conexión con MongoDB Compass
4. Implementar autenticación si es necesario
5. Agregar índices de base de datos para optimización