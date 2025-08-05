"""
Schemas para audit - Modelos de respuesta y validación.
Esquemas Pydantic para las auditorías y documentos relacionados.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union
from datetime import datetime
from app.schemas.base import BaseSchema


class AuditDocumentResponse(BaseSchema):
    """Schema para un documento de auditoría."""
    
    document_id: int = Field(..., description="ID del documento")
    activity_category_id: Optional[int] = Field(None, description="ID de la categoría de actividad")
    type_name: Optional[str] = Field(None, description="Nombre del tipo de documento")
    author_title: Optional[str] = Field(None, description="Título del autor")
    document_url: Optional[str] = Field(None, description="URL del documento")
    file_name: Optional[str] = Field(None, description="Nombre del archivo")
    compliance_grid_id: Optional[int] = Field(None, description="ID de la grilla de cumplimiento")
    relation_question_id: Optional[int] = Field(None, description="ID de la pregunta relacionada")
    short_name: Optional[str] = Field(None, description="Nombre corto")
    used_reference: Optional[str] = Field(None, description="Referencia utilizada")
    
    @field_validator('used_reference', mode='before')
    @classmethod
    def convert_used_reference_to_string(cls, v):
        """Convierte used_reference a string si es un número."""
        if v is not None and not isinstance(v, str):
            return str(v)
        return v
    
    @field_validator('type_name', 'author_title', 'document_url', 'file_name', 'short_name', mode='before')
    @classmethod
    def convert_fields_to_string(cls, v):
        """Convierte campos a string si no son None."""
        if v is not None and not isinstance(v, str):
            return str(v)
        return v


class AuditDocumentsListResponse(BaseSchema):
    """Schema para respuesta de lista de documentos de auditoría."""
    
    success: bool = Field(True, description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo de la respuesta")
    data: List[AuditDocumentResponse] = Field([], description="Lista de documentos de auditoría")
    total_count: int = Field(0, description="Número total de documentos encontrados")
    audit_header_id: int = Field(..., description="ID del header de auditoría consultado")


class AuditDocumentsRequest(BaseSchema):
    """Schema para solicitud de documentos de auditoría."""
    
    audit_header_id: int = Field(..., description="ID del header de auditoría", gt=0)
    question_id: Optional[int] = Field(0, description="ID de la pregunta (opcional, por defecto 0)")


class AuditDocumentsSingleResponse(BaseSchema):
    """Schema para respuesta de un solo documento de auditoría."""
    
    success: bool = Field(True, description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo de la respuesta")
    data: Optional[AuditDocumentResponse] = Field(None, description="Documento de auditoría encontrado")


class ErrorResponse(BaseSchema):
    """Schema para respuestas de error."""
    
    success: bool = Field(False, description="Indica que la operación falló")
    message: str = Field(..., description="Mensaje de error")
    detail: Optional[str] = Field(None, description="Detalle adicional del error")
    error_code: Optional[str] = Field(None, description="Código de error específico")


class HealthCheckResponse(BaseSchema):
    """Schema para respuesta de health check del servicio SQL Server."""
    
    status: str = Field(..., description="Estado de la conexión (connected, disconnected, error)")
    message: str = Field(..., description="Mensaje descriptivo del estado")
    server: Optional[str] = Field(None, description="Servidor SQL Server")
    database: Optional[str] = Field(None, description="Base de datos SQL Server")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la verificación")