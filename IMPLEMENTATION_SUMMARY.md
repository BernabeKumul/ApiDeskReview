# Implementación de Prompts Dinámicos - Resumen

## 🎯 Objetivo Completado

Se ha implementado exitosamente la funcionalidad de **prompts dinámicos** que permite:

1. **Cargar prompts desde JSON**: Los prompts se cargan dinámicamente desde `JSON/AzzuleAI.AIDynamicPrompts.json`
2. **Procesamiento por QuestionID**: Cada QuestionID en los parámetros se busca por su `NameSection` correspondiente
3. **Múltiples peticiones a GPT**: Cada QuestionID genera una petición separada a OpenAI
4. **Lista de respuestas**: Se retorna una lista con la respuesta de cada QuestionID

## 📁 Archivos Modificados

### 1. `app/services/ai_service.py`
- ✅ Agregado método `_load_dynamic_prompts()` para cargar el JSON
- ✅ Nuevo método `_create_dynamic_prompt()` que busca por NameSection
- ✅ Nuevo método `process_multiple_questions()` para manejar múltiples QuestionID
- ✅ Métodos auxiliares para OpenAI con QuestionID
- ✅ Mantenida compatibilidad con métodos legacy

### 2. `app/services/ai_process_service.py`
- ✅ Nuevo método `process_audit()` que extrae QuestionIDs y procesa múltiples preguntas
- ✅ Método `_extract_question_ids()` para obtener IDs únicos del request
- ✅ Método legacy `process_audit_legacy()` para compatibilidad hacia atrás

### 3. `app/schemas/ai_process.py`
- ✅ Nuevo schema `QuestionResponse` para respuesta individual
- ✅ Nuevo schema `MultipleQuestionsResponse` para lista de respuestas
- ✅ Mantenido schema original `AuditProcessResponse` para compatibilidad

### 4. `app/api/v1/endpoints/ai_process.py`
- ✅ Endpoint principal `/ai-process/audit` modificado para retornar múltiples respuestas
- ✅ Nuevo endpoint `/ai-process/audit-legacy` para compatibilidad
- ✅ Documentación actualizada

## 🔄 Flujo de Funcionamiento

### Nuevo Flujo (Múltiples QuestionID):
```
1. Request llega con múltiples QuestionDocument
2. Se extraen los QuestionID únicos [4346, 4347, 4348, etc.]
3. Para cada QuestionID:
   a. Se busca el prompt en JSON por NameSection
   b. Se crea prompt dinámico específico
   c. Se envía petición individual a OpenAI
   d. Se recibe respuesta con QuestionID incluido
4. Se retorna lista completa de respuestas
```

### Formato de Respuesta:
```json
{
  "success": true,
  "message": "Successfully processed 3 questions for audit 12345",
  "data": [
    {
      "ComplianceLevel": 2,
      "Comments": "Assessment for Question 9.01.01...",
      "FilesSearch": [...],
      "QuestionID": "4346"
    },
    {
      "ComplianceLevel": 2,
      "Comments": "Assessment for Question 9.01.02...",
      "FilesSearch": [...],
      "QuestionID": "4347"
    }
  ],
  "total_questions": 2
}
```

## 📋 Mapeo de QuestionID a NameSection

Según `JSON/AzzuleAI.AIDynamicPrompts.json`:

| QuestionID | NameSection | Descripción |
|------------|-------------|-------------|
| 4346 | "4346" | ¿Tiene plan IPM documentado? |
| 4347 | "4347" | ¿Evidencia de implementación de IPM? |
| 4348 | "4348" | ¿Monitorea efectividad de métodos no químicos? |
| 4349 | "4349" | ¿Evalúa riesgo de pesticidas? |
| 4350 | "4350" | ¿Aplicaciones con justificación documentada? |

## 🧪 Pruebas y Validación

### Request de Ejemplo:
```json
{
  "AuditID": 12345,
  "OrgID": 67890,
  "Operation": "Strawberry Farm Operations",
  "Products": "Fresh Strawberries",
  "Documents": [
    {
      "QuestionID": 4346,
      "DocumentsId": [
        {"DocumentId": 1, "URL": "http://example.com/ipm_plan.pdf"}
      ]
    },
    {
      "QuestionID": 4347,
      "DocumentsId": [
        {"DocumentId": 2, "URL": "http://example.com/implementation.pdf"}
      ]
    }
  ]
}
```

### Endpoints Disponibles:

1. **Principal**: `POST /api/v1/ai-process/audit`
   - Retorna: `MultipleQuestionsResponse` con lista de respuestas
   - Un response por cada QuestionID único

2. **Legacy**: `POST /api/v1/ai-process/audit-legacy`
   - Retorna: `AuditProcessResponse` (formato original)
   - Para compatibilidad hacia atrás

## ✅ Funcionalidades Implementadas

- [x] Carga dinámica de prompts desde JSON
- [x] Búsqueda por NameSection correspondiente a QuestionID
- [x] Procesamiento de múltiples QuestionID en paralelo
- [x] Una petición a GPT por cada QuestionID
- [x] Lista de respuestas con QuestionID identificado
- [x] Manejo de errores por QuestionID individual
- [x] Compatibilidad hacia atrás con endpoint legacy
- [x] Validación y logging completo

## 🚀 Uso

El sistema ahora es completamente dinámico. Para agregar nuevas preguntas:

1. Agregar entrada en `JSON/AzzuleAI.AIDynamicPrompts.json`
2. Usar el NameSection como QuestionID en el request
3. El sistema automáticamente cargará y usará el prompt correspondiente

**¡La implementación está completa y lista para usar!** 🎉