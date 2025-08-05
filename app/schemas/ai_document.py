from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.base import BaseSchema


class AIDocumentResponse(BaseSchema):
    """Esquema de respuesta para un documento de IA."""
    
    id: str = Field(description="ID único del documento")
    document_id: int = Field(description="ID del documento")
    file_name: str = Field(description="Nombre del archivo")
    document_type: str = Field(description="Tipo de documento")
    content: str = Field(description="Contenido del documento")
    total_reading: int = Field(description="Total de lecturas")
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: datetime = Field(description="Fecha de última actualización")
    inactive: bool = Field(description="Estado del documento")


class AIDocumentListResponse(BaseSchema):
    """Esquema de respuesta para una lista de documentos de IA."""
    
    success: bool = True
    message: str = "Documentos obtenidos exitosamente"
    data: List[AIDocumentResponse] = Field(description="Lista de documentos")
    total_count: Optional[int] = Field(None, description="Total de documentos (para paginación)")
    page: Optional[int] = Field(None, description="Página actual")
    page_size: Optional[int] = Field(None, description="Tamaño de página")


class AIDocumentSingleResponse(BaseSchema):
    """Esquema de respuesta para un documento individual."""
    
    success: bool = True
    message: str = "Documento obtenido exitosamente"
    data: Optional[AIDocumentResponse] = Field(description="Documento encontrado")


class AIDocumentCreateRequest(BaseSchema):
    """Esquema de solicitud para crear un documento."""
    
    document_id: int = Field(description="ID único del documento")
    file_name: str = Field(description="Nombre del archivo")
    document_type: str = Field(description="Tipo de documento")
    content: str = Field(description="Contenido del documento")
    total_reading: int = Field(default=0, description="Total de lecturas")
    inactive: bool = Field(default=False, description="Estado del documento")


class AIDocumentUpdateRequest(BaseSchema):
    """Esquema de solicitud para actualizar un documento."""
    
    file_name: Optional[str] = Field(None, description="Nombre del archivo")
    document_type: Optional[str] = Field(None, description="Tipo de documento")
    content: Optional[str] = Field(None, description="Contenido del documento")
    total_reading: Optional[int] = Field(None, description="Total de lecturas")
    inactive: Optional[bool] = Field(None, description="Estado del documento")


class AIDocumentCreateResponse(BaseSchema):
    """Esquema de respuesta para la creación de un documento."""
    
    success: bool = True
    message: str = "Documento creado exitosamente"
    data: dict = Field(description="ID del documento creado")


class AIDocumentUpdateResponse(BaseSchema):
    """Esquema de respuesta para la actualización de un documento."""
    
    success: bool = True
    message: str = "Documento actualizado exitosamente"
    data: Optional[dict] = Field(None, description="Información adicional")


class AIDocumentDeleteResponse(BaseSchema):
    """Esquema de respuesta para la eliminación de un documento."""
    
    success: bool = True
    message: str = "Documento eliminado exitosamente"
    data: Optional[dict] = Field(None, description="Información adicional")


class AIDocumentSearchRequest(BaseSchema):
    """Esquema de solicitud para buscar documentos."""
    
    document_id: Optional[int] = Field(None, description="ID del documento")
    file_name: Optional[str] = Field(None, description="Nombre del archivo")
    document_type: Optional[str] = Field(None, description="Tipo de documento")
    inactive: Optional[bool] = Field(None, description="Estado del documento")
    search_content: Optional[str] = Field(None, description="Buscar en el contenido")
    page: int = Field(default=1, ge=1, description="Número de página")
    page_size: int = Field(default=10, ge=1, le=100, description="Tamaño de página")
    sort_by: str = Field(default="CreatedAt", description="Campo por el cual ordenar")
    sort_order: str = Field(default="desc", description="Orden de clasificación (asc/desc)")


class ErrorResponse(BaseSchema):
    """Esquema de respuesta para errores."""
    
    success: bool = False
    message: str = Field(description="Mensaje de error")
    error_code: Optional[str] = Field(None, description="Código de error")
    details: Optional[dict] = Field(None, description="Detalles adicionales del error")