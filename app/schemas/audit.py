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
    
    document_id: int = Field(..., alias="DocumentId", description="ID del documento")
    activity_category_id: Optional[int] = Field(None, alias="ActivityCategoryId", description="ID de la categoría de actividad")
    type_name: Optional[str] = Field(None, alias="TypeName", description="Nombre del tipo de documento")
    author_title: Optional[str] = Field(None, alias="AuthorTitle", description="Título del autor")
    document_url: Optional[str] = Field(None, alias="DocumentUrl", description="URL del documento")
    file_name: Optional[str] = Field(None, alias="FileName", description="Nombre del archivo")
    compliance_grid_id: Optional[int] = Field(None, alias="ComplianceGridId", description="ID de la grilla de cumplimiento")
    relation_question_id: Optional[int] = Field(None, alias="RelationQuestionId", description="ID de la pregunta relacionada")
    short_name: Optional[str] = Field(None, alias="ShortName", description="Nombre corto")
    used_reference: Optional[str] = Field(None, alias="UsedReference", description="Referencia utilizada")
    
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
    
    success: bool = Field(True, alias="Success", description="Indica si la operación fue exitosa")
    message: str = Field(..., alias="Message", description="Mensaje descriptivo de la respuesta")
    data: List[AuditDocumentResponse] = Field([], alias="Data", description="Lista de documentos de auditoría")
    total_count: int = Field(0, alias="TotalCount", description="Número total de documentos encontrados")
    audit_header_id: int = Field(..., alias="AuditHeaderId", description="ID del header de auditoría consultado")


class AuditDocumentsRequest(BaseSchema):
    """Schema para solicitud de documentos de auditoría."""
    
    audit_header_id: int = Field(..., description="ID del header de auditoría", gt=0)
    question_id: Optional[int] = Field(0, description="ID de la pregunta (opcional, por defecto 0)")


class AuditDocumentsSingleResponse(BaseSchema):
    """Schema para respuesta de un solo documento de auditoría."""
    
    success: bool = Field(True, alias="Success", description="Indica si la operación fue exitosa")
    message: str = Field(..., alias="Message", description="Mensaje descriptivo de la respuesta")
    data: Optional[AuditDocumentResponse] = Field(None, alias="Data", description="Documento de auditoría encontrado")


class ErrorResponse(BaseSchema):
    """Schema para respuestas de error."""
    
    success: bool = Field(False, alias="Success", description="Indica que la operación falló")
    message: str = Field(..., alias="Message", description="Mensaje de error")
    detail: Optional[str] = Field(None, alias="Detail", description="Detalle adicional del error")
    error_code: Optional[str] = Field(None, alias="ErrorCode", description="Código de error específico")


class AuditHeaderResponse(BaseSchema):
    """Schema para un header de auditoría."""
    
    audit_header_id: int = Field(..., alias="AuditHeaderId", description="ID del header de auditoría")
    org_id: int = Field(..., alias="OrgId", description="ID de la organización")
    org_name: Optional[str] = Field(None, alias="OrgName", description="Nombre de la organización")
    oper_id: Optional[int] = Field(None, alias="OperId", description="ID de la operación")
    oper_name: Optional[str] = Field(None, alias="OperName", description="Nombre de la operación")
    products: Optional[str] = Field(None, alias="Products", description="Productos asociados")


class AuditHeadersListResponse(BaseSchema):
    """Schema para respuesta de lista de headers de auditoría."""
    
    success: bool = Field(True, alias="Success", description="Indica si la operación fue exitosa")
    message: str = Field(..., alias="Message", description="Mensaje descriptivo de la respuesta")
    data: List[AuditHeaderResponse] = Field([], alias="Data", description="Lista de headers de auditoría")
    total_count: int = Field(0, alias="TotalCount", description="Número total de auditorías encontradas")


class HealthCheckResponse(BaseSchema):
    """Schema para respuesta de health check del servicio SQL Server."""
    
    status: str = Field(..., alias="Status", description="Estado de la conexión (connected, disconnected, error)")
    message: str = Field(..., alias="Message", description="Mensaje descriptivo del estado")
    server: Optional[str] = Field(None, alias="Server", description="Servidor SQL Server")
    database: Optional[str] = Field(None, alias="Database", description="Base de datos SQL Server")
    timestamp: datetime = Field(default_factory=datetime.now, alias="Timestamp", description="Timestamp de la verificación")