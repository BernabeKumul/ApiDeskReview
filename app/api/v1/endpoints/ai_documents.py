"""
Endpoints para la gestión de documentos de IA.
Proporciona endpoints específicos para búsqueda y listado de la colección AIDocuments.
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
from pymongo import ASCENDING, DESCENDING
import logging

from app.services.ai_document_service import ai_document_service
from app.models.ai_document import AIDocumentFilterModel
from app.schemas.ai_document import (
    AIDocumentListResponse,
    AIDocumentSingleResponse,
    AIDocumentResponse
)

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/ai-documents", tags=["AI Documents"])


def convert_model_to_response(document) -> AIDocumentResponse:
    """Convierte un modelo de documento a esquema de respuesta."""
    return AIDocumentResponse(
        id=document.id,
        document_id=document.document_id,
        file_name=document.file_name,
        document_type=document.document_type,
        content=document.content,
        total_reading=document.total_reading,
        created_at=document.created_at,
        updated_at=document.updated_at,
        inactive=document.inactive
    )


@router.get(
    "/search",
    response_model=AIDocumentSingleResponse,
    summary="Buscar documento por FileName y/o DocumentId",
    description="Recupera un documento específico utilizando filtros de FileName y DocumentId"
)
async def search_document_by_filters(
    file_name: Optional[str] = Query(None, description="Nombre del archivo a buscar"),
    document_id: Optional[int] = Query(None, description="ID del documento a buscar")
):
    """
    Busca un documento específico por FileName y/o DocumentId.
    Al menos uno de los filtros debe ser proporcionado.
    """
    try:
        # Validar que al menos un filtro esté presente
        if file_name is None and document_id is None:
            raise HTTPException(
                status_code=400,
                detail="Al menos uno de los filtros (file_name o document_id) debe ser proporcionado"
            )
        
        logger.info(f"Buscando documento con file_name='{file_name}', document_id={document_id}")
        
        # Buscar documento
        document = await ai_document_service.get_document_by_filters(
            file_name=file_name,
            document_id=document_id
        )
        
        if document is None:
            return AIDocumentSingleResponse(
                success=False,
                message="No se encontró ningún documento con los filtros especificados",
                data=None
            )
        
        # Convertir a esquema de respuesta
        response_data = convert_model_to_response(document)
        
        return AIDocumentSingleResponse(
            success=True,
            message="Documento encontrado exitosamente",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al buscar documento por filtros: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/search/document-id/{document_id}",
    response_model=AIDocumentSingleResponse,
    summary="Buscar documento por DocumentId",
    description="Recupera un documento específico utilizando solo el DocumentId"
)
async def search_document_by_document_id(
    document_id: int = Path(..., description="ID del documento a buscar")
):
    """
    Busca un documento específico por DocumentId únicamente.
    """
    try:
        logger.info(f"Buscando documento con document_id={document_id}")
        
        # Buscar documento por DocumentId
        document = await ai_document_service.get_document_by_filters(
            file_name=None,
            document_id=document_id
        )
        
        if document is None:
            return AIDocumentSingleResponse(
                success=False,
                message=f"No se encontró ningún documento con DocumentId: {document_id}",
                data=None
            )
        
        # Convertir a esquema de respuesta
        response_data = convert_model_to_response(document)
        
        return AIDocumentSingleResponse(
            success=True,
            message="Documento encontrado exitosamente",
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"Error al buscar documento por DocumentId: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/",
    response_model=AIDocumentListResponse,
    summary="Obtener todos los documentos",
    description="Recupera todos los documentos con filtros y paginación opcionales"
)
async def get_all_documents(
    # Filtros opcionales
    document_id: Optional[int] = Query(None, description="Filtrar por ID del documento"),
    file_name: Optional[str] = Query(None, description="Filtrar por nombre de archivo"),
    document_type: Optional[str] = Query(None, description="Filtrar por tipo de documento"),
    inactive: Optional[bool] = Query(None, description="Filtrar por estado (activo/inactivo)"),
    
    # Paginación
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    
    # Ordenamiento
    sort_by: str = Query("CreatedAt", description="Campo por el cual ordenar"),
    sort_order: str = Query("desc", description="Orden de clasificación (asc/desc)")
):
    """
    Obtiene todos los documentos con filtros opcionales, paginación y ordenamiento.
    """
    try:
        logger.info(f"Obteniendo documentos - página {page}, tamaño {page_size}")
        
        # Crear filtros
        filters = None
        if any([document_id, file_name, document_type, inactive is not None]):
            filters = AIDocumentFilterModel(
                document_id=document_id,
                file_name=file_name,
                document_type=document_type,
                inactive=inactive
            )
        
        # Configurar paginación
        skip = (page - 1) * page_size
        
        # Configurar ordenamiento
        sort_direction = DESCENDING if sort_order.lower() == "desc" else ASCENDING
        
        # Obtener documentos
        documents = await ai_document_service.get_all_documents(
            filters=filters,
            skip=skip,
            limit=page_size,
            sort_by=sort_by,
            sort_order=sort_direction
        )
        
        # Obtener conteo total para paginación
        total_count = await ai_document_service.get_documents_count(filters)
        
        # Convertir a esquemas de respuesta
        response_data = [convert_model_to_response(doc) for doc in documents]
        
        return AIDocumentListResponse(
            success=True,
            message=f"Se encontraron {len(documents)} documentos",
            data=response_data,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error al obtener todos los documentos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

