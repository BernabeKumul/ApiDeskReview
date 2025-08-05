# Controlador de Auditorías - Documentación API

## Descripción General

El controlador de Auditorías proporciona endpoints para extraer información de auditorías desde una base de datos SQL Server. Está diseñado para ser genérico y reutilizable para otros stored procedures.

## Configuración

### 1. Dependencias

Las siguientes dependencias han sido agregadas al proyecto:

```
pyodbc>=4.0.39
aiodbc>=0.4.0
```

### 2. Configuración de SQL Server

En `app/core/config.py`:

```python
# SQL Server Configuration
sqlserver_server: str = "10.10.50.30"
sqlserver_database: str = "PrimusGFS"
sqlserver_username: str = "ApplicationUser_"
sqlserver_password: str = "Dev23InAzz$"
sqlserver_driver: str = "ODBC Driver 17 for SQL Server"
sqlserver_trusted_connection: bool = False
```

## Arquitectura

### Componentes Implementados

1. **Servicio SQL Server Genérico** (`app/services/sqlserver_service.py`)
   - Conexión a SQL Server usando aiodbc
   - Métodos genéricos para ejecutar queries y stored procedures
   - Pool de conexiones para mejor rendimiento

2. **Servicio de Auditoría** (`app/services/audit_service.py`)
   - Lógica específica para auditorías
   - Métodos especializados para obtener documentos de auditoría

3. **Modelos de Datos** (`app/models/audit.py`)
   - Clases de datos para documentos de auditoría
   - Mapeo desde/hacia diccionarios

4. **Esquemas de Validación** (`app/schemas/audit.py`)
   - Validación de entrada y salida usando Pydantic
   - Esquemas de respuesta estandarizados

5. **Endpoints** (`app/api/v1/endpoints/audit.py`)
   - Controladores REST para auditorías
   - Documentación automática con OpenAPI

## Endpoints Disponibles

### 1. Obtener Documentos de Auditoría

**GET** `/api/v1/audit/documents/{audit_header_id}`

Obtiene todos los documentos adjuntos a una auditoría específica.

#### Parámetros:
- `audit_header_id` (path, required): ID del header de auditoría

#### Ejemplo de Uso:
```bash
curl -X GET "http://localhost:8000/api/v1/audit/documents/123"
```

#### Respuesta:
```json
{
  "success": true,
  "message": "Se encontraron 5 documentos para la auditoría 123",
  "data": [
    {
      "document_id": 1001,
      "activity_category_id": 2,
      "type_name": "Policy Document",
      "author_title": "Risk Manager",
      "document_url": "https://example.com/doc1.pdf",
      "file_name": "policy_v1.pdf",
      "compliance_grid_id": 501,
      "relation_question_id": 10,
      "short_name": "POL001",
      "used_reference": "Reference A"
    }
  ],
  "total_count": 5,
  "audit_header_id": 123
}
```

### 2. Obtener Documento Específico

**GET** `/api/v1/audit/documents/{audit_header_id}/{document_id}`

Obtiene un documento específico de una auditoría.

#### Parámetros:
- `audit_header_id` (path, required): ID del header de auditoría
- `document_id` (path, required): ID del documento específico
- `question_id` (query, optional): ID de la pregunta (por defecto: 0)

### 3. Filtrar por Categoría de Actividad

**GET** `/api/v1/audit/documents/{audit_header_id}/category/{activity_category_id}`

Obtiene documentos filtrados por categoría de actividad.

### 4. Filtrar por Tipo de Documento

**GET** `/api/v1/audit/documents/{audit_header_id}/type/{type_name}`

Obtiene documentos filtrados por tipo de documento.

### 5. Health Check

**GET** `/api/v1/audit/health`

Verifica el estado de la conexión a SQL Server.

## Stored Procedure

### AuditHeader_Get_AvailableActivityDocumentsAzzuleAI

Este stored procedure debe existir en la base de datos SQL Server con la siguiente firma:

```sql
EXEC AuditHeader_Get_AvailableActivityDocumentsAzzuleAI 
    @Auditheaderid INT,
    @QuestionID INT = 0
```

#### Columnas Esperadas en la Respuesta:
- `DocumentID` (int): ID único del documento
- `ActivityCategoryId` (int, nullable): ID de la categoría de actividad
- `TypeName` (string, nullable): Nombre del tipo de documento
- `AuthorTitle` (string, nullable): Título del autor
- `DocumentURL` (string, nullable): URL del documento
- `FileName` (string, nullable): Nombre del archivo
- `ComplianceGridID` (int, nullable): ID de la grilla de cumplimiento
- `RelationQuestionID` (int, nullable): ID de la pregunta relacionada
- `ShortName` (string, nullable): Nombre corto
- `UsedReference` (string, nullable): Referencia utilizada

## Uso del Servicio SQL Server Genérico

El servicio SQL Server es completamente genérico y puede ser utilizado para otros stored procedures:

```python
from app.services.sqlserver_service import sqlserver_service

# Ejecutar cualquier stored procedure
results = await sqlserver_service.execute_stored_procedure(
    procedure_name="MiStoredProcedure",
    parameters={
        "parametro1": "valor1",
        "parametro2": 123
    }
)

# Ejecutar query directo
results = await sqlserver_service.execute_query(
    query="SELECT * FROM MiTabla WHERE campo = ?",
    parameters=["valor"]
)

# Obtener valor único
valor = await sqlserver_service.execute_scalar(
    query="SELECT COUNT(*) FROM MiTabla"
)
```

## Manejo de Errores

El API implementa manejo robusto de errores:

- **400 Bad Request**: Parámetros inválidos
- **500 Internal Server Error**: Errores de base de datos o internos

Todos los errores incluyen mensajes descriptivos en español.

## Logging

El sistema incluye logging completo para facilitar el debugging:

```python
import logging
logger = logging.getLogger(__name__)
```

Los logs incluyen:
- Parámetros de entrada
- Resultados de stored procedures
- Errores detallados
- Métricas de rendimiento

## Extensibilidad

Para agregar nuevos stored procedures:

1. Crear modelos en `app/models/`
2. Crear esquemas en `app/schemas/`
3. Agregar métodos al servicio específico
4. Crear endpoints en `app/api/v1/endpoints/`
5. Registrar en `app/api/v1/api.py`

El servicio SQL Server genérico no requiere modificaciones.

## Testing

Para probar la implementación:

1. Asegurar que SQL Server esté accesible
2. Verificar que el stored procedure existe
3. Iniciar la aplicación: `python run.py`
4. Acceder a la documentación: `http://localhost:8000/docs`
5. Probar los endpoints desde la interfaz Swagger

## Notas Importantes

- La conexión SQL Server usa pool de conexiones para mejor rendimiento
- Todas las operaciones son asíncronas
- Los parámetros de conexión pueden ser configurados via variables de entorno
- El sistema maneja automáticamente la reconexión en caso de pérdida de conexión