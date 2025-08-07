# Implementación BAAI/bge-m3

Esta implementación proporciona una nueva funcionalidad de embeddings y búsqueda vectorial usando el modelo **BAAI/bge-m3**, con las siguientes características:

## 🚀 Características Principales

### 1. **Búsqueda Híbrida Inteligente**
- **Primero por ID**: Busca en documentos específicos por sus IDs
- **Luego por texto**: Complementa con búsqueda por similitud de texto
- **Sin duplicados**: Evita resultados duplicados automáticamente
- **Ordenamiento por relevancia**: Resultados ordenados por score de similitud

### 2. **Procesamiento desde JSON**
- Lee documentos directamente desde `JSON/AzzuleAI.AIDocuments.json`
- **Evita duplicados**: Verifica si el documento ya existe antes de procesarlo
- **Procesamiento eficiente**: Chunks optimizados para embeddings
- **Metadatos completos**: Preserva toda la información del documento

### 3. **Modelo BAAI/bge-m3**
- **1024 dimensiones**: Embeddings de alta calidad
- **Mejor rendimiento**: Superior a modelos anteriores
- **Colección separada**: `AIDocumentsTestBAAI` para evitar conflictos

## 📁 Archivos Creados

### Servicios
- `app/services/baai_embedding_service.py` - Servicio de embeddings BAAI
- `app/services/baai_vector_store.py` - Servicio de vector store BAAI
- `app/services/baai_document_processor.py` - Procesador de documentos BAAI

### Esquemas
- `app/schemas/baai_search.py` - Esquemas de respuesta para BAAI

### Endpoints
- `app/api/v1/endpoints/baai_search.py` - Endpoints de búsqueda BAAI

### Pruebas
- `test_baai_integration.py` - Script de prueba completo

## 🔧 Configuración

### Configuración en `app/core/config.py`
```python
qdrant_BAAI_collection_name: str = "AIDocumentsTestBAAI"  # Colección para BAAI embeddings
```

### Dependencias
El modelo BAAI/bge-m3 se descarga automáticamente la primera vez que se usa.

## 📡 Endpoints Disponibles

### 1. **Búsqueda Híbrida**
```http
POST /baai-search/search
```
**Body:**
```json
{
  "query_text": "steamout resteam",
  "document_ids": [853346, 853347],
  "limit": 10,
  "score_threshold": 0.7
}
```

### 2. **Búsqueda por Similitud**
```http
GET /baai-search/search/similar?query_text=steamout&limit=10&score_threshold=0.7
```

### 3. **Búsqueda por IDs Específicos**
```http
GET /baai-search/search/by-ids?document_ids=853346,853347&query_text=steamout&limit=10
```

### 4. **Procesar Documentos**
```http
POST /baai-search/process
```
**Body:**
```json
{
  "process_all": true,
  "limit": 100
}
```
o
```json
{
  "document_ids": [853346, 853347, 853348]
}
```

### 5. **Estadísticas de la Colección**
```http
GET /baai-search/stats
```

### 6. **Obtener Chunks de un Documento**
```http
GET /baai-search/document/{document_id}/chunks
```

## 🧪 Pruebas

### Ejecutar Pruebas de Integración
```bash
python test_baai_integration.py
```

### Ejecutar Pruebas de Endpoints (con servidor corriendo)
```bash
# Descomentar la línea en test_baai_integration.py
python test_baai_integration.py
```

## 🔍 Ejemplos de Uso

### 1. Procesar Documentos desde JSON
```python
from app.services.baai_document_processor import baai_document_processor

# Procesar todos los documentos
result = await baai_document_processor.process_all_documents(limit=100)

# Procesar documentos específicos
result = await baai_document_processor.process_documents_by_ids([853346, 853347])
```

### 2. Búsqueda Híbrida
```python
from app.services.baai_vector_store import baai_vector_store_service

# Conectar al servicio
await baai_vector_store_service.connect()

# Búsqueda híbrida
results = await baai_vector_store_service.hybrid_search(
    document_ids=[853346, 853347],
    query_text="steamout resteam",
    limit=10,
    score_threshold=0.7
)

# Desconectar
await baai_vector_store_service.disconnect()
```

### 3. Búsqueda por Similitud
```python
results = await baai_vector_store_service.search_similar(
    query_text="steamout resteam",
    limit=10,
    score_threshold=0.7
)
```

## 📊 Estructura de Respuesta

### Respuesta de Búsqueda
```json
{
  "success": true,
  "message": "Búsqueda completada exitosamente. 5 resultados encontrados.",
  "results": [
    {
      "score": 0.85,
      "document_id": 853346,
      "file_name": "DOC20250307135412.352.pdf",
      "document_type": "Document",
      "content": "Steamout Resteam Pre & Post Spawn...",
      "chunk_index": 0,
      "total_chunks": 3,
      "created_at": "2025-05-29T15:51:45.489Z",
      "total_reading": 8
    }
  ],
  "total_results": 5,
  "search_type": "hybrid_with_ids"
}
```

### Respuesta de Procesamiento
```json
{
  "success": true,
  "message": "Procesamiento completado: 50 procesados, 10 saltados, 0 errores",
  "processed": 50,
  "skipped": 10,
  "errors": 0,
  "total_documents": 60,
  "collection_stats": {
    "collection_name": "AIDocumentsTestBAAI",
    "vector_size": 1024,
    "points_count": 150,
    "segments_count": 1,
    "status": "green"
  }
}
```

## 🔄 Diferencias con la Implementación Anterior

| Característica | Implementación Anterior | BAAI/bge-m3 |
|----------------|------------------------|--------------|
| **Modelo** | all-MiniLM-L6-v2 (384d) | BAAI/bge-m3 (1024d) |
| **Colección** | AIDocumentsTest | AIDocumentsTestBAAI |
| **Búsqueda** | Solo por similitud | Híbrida (ID + texto) |
| **Duplicados** | Posibles | Evitados automáticamente |
| **Fuente de datos** | MongoDB | JSON directo |
| **Procesamiento** | Manual | Automático desde JSON |

## 🚀 Ventajas de la Nueva Implementación

1. **Mejor Calidad**: Modelo BAAI/bge-m3 de 1024 dimensiones
2. **Búsqueda Inteligente**: Híbrida con prioridad por IDs
3. **Sin Duplicados**: Control automático de documentos únicos
4. **Procesamiento Eficiente**: Desde JSON sin dependencias externas
5. **Colección Separada**: No interfiere con implementación anterior
6. **Endpoints Específicos**: API dedicada para BAAI

## 🔧 Mantenimiento

### Verificar Estado de la Colección
```bash
curl http://localhost:8000/baai-search/stats
```

### Procesar Nuevos Documentos
```bash
curl -X POST http://localhost:8000/baai-search/process \
  -H "Content-Type: application/json" \
  -d '{"process_all": true, "limit": 100}'
```

### Búsqueda de Prueba
```bash
curl -X POST http://localhost:8000/baai-search/search \
  -H "Content-Type: application/json" \
  -d '{"query_text": "steamout resteam", "limit": 5}'
```

## 📝 Notas Importantes

1. **Primera Ejecución**: El modelo BAAI/bge-m3 se descargará automáticamente (~1GB)
2. **Memoria**: El modelo requiere más memoria que el anterior
3. **Rendimiento**: Embeddings de 1024 dimensiones son más precisos pero más lentos
4. **Compatibilidad**: No modifica la implementación existente
5. **Escalabilidad**: La colección separada permite crecimiento independiente

## 🎯 Próximos Pasos

1. **Monitoreo**: Implementar métricas de rendimiento
2. **Optimización**: Ajustar parámetros de chunking
3. **Caché**: Implementar caché de embeddings
4. **Batch Processing**: Procesamiento en lotes más grandes
5. **Compresión**: Optimizar almacenamiento de vectores 