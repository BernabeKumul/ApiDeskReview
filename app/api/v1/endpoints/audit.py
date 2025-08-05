"""
Endpoints para la gestión de auditorías.
Proporciona endpoints específicos para consulta de documentos de auditoría.
"""
from fastapi import APIRouter, HTTPException, Path
import logging

from app.services.audit_service import audit_service
from app.schemas.audit import (
    AuditDocumentsListResponse,
    AuditDocumentResponse
)

# Configurar logging
logger = logging.getLogger(__name__) 

# Crear router
router = APIRouter(prefix="/audit", tags=["Audit"])


def convert_model_to_response(document) -> AuditDocumentResponse:
    """Convierte un modelo de documento de auditoría a esquema de respuesta."""
    return AuditDocumentResponse(
        document_id=document.document_id,
        activity_category_id=document.activity_category_id,
        type_name=document.type_name,
        author_title=document.author_title,
        document_url=document.document_url,
        file_name=document.file_name,
        compliance_grid_id=document.compliance_grid_id,
        relation_question_id=document.relation_question_id,
        short_name=document.short_name,
        used_reference=document.used_reference
    )


@router.get(
    "/documents/{audit_header_id}",
    response_model=AuditDocumentsListResponse,
    summary="Obtener documentos adjuntos a la auditoría",
    description="Recupera todos los documentos asociados a una auditoría específica"
)
async def get_audit_documents(
    audit_header_id: int = Path(
        ..., 
        description="ID del header de auditoría", 
        gt=0
    )
):
    """
    Obtiene todos los documentos adjuntos a una auditoría específica.
    
    Ejecuta el stored procedure: AuditHeader_Get_AvailableActivityDocumentsAzzuleAI
    
    Parámetros:
    - audit_header_id: ID del header de auditoría (requerido)
    
    Respuesta:
    - Lista de documentos con toda la información especificada
    """
    try:
        logger.info(
            f"Obteniendo documentos para audit_header_id={audit_header_id}"
        )
        
        # Obtener documentos del servicio (question_id por defecto es 0)
        documents = await audit_service.get_audit_documents(
            audit_header_id=audit_header_id,
            question_id=0
        )
        
        # Convertir a esquemas de respuesta
        response_data = [convert_model_to_response(doc) for doc in documents]
        
        return AuditDocumentsListResponse(
            success=True,
            message=f"Se encontraron {len(documents)} documentos para la auditoría {audit_header_id}",
            data=response_data,
            total_count=len(documents),
            audit_header_id=audit_header_id
        )
        
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error de validación: {str(e)}"
        )
    except RuntimeError as e:
        logger.error(f"Error del servicio: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error inesperado al obtener documentos de auditoría: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


