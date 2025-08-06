"""
Endpoints para búsqueda vectorial híbrida.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging

from app.services.vector_store import vector_store_service
from app.schemas.vector_search import (
    HybridSearchRequest,
    HybridSearchResponse,
    SimilaritySearchRequest,
    SimilaritySearchResponse,
    SearchResult,
    DocumentChunk
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vector-search", tags=["Vector Search"])

@router.post(
    "/hybrid",
    response_model=HybridSearchResponse,
    summary="Búsqueda híbrida por IDs y similitud",
    description="Primero filtra por IDs de documentos, luego busca por similitud de contenido"
)
async def hybrid_search(request: HybridSearchRequest):
    """
    Búsqueda híbrida: filtra por IDs de documentos y luego busca por similitud.
    """
    try:
        if not request.document_ids:
            raise HTTPException(
                status_code=400,
                detail="Se requiere al menos un DocumentId"
            )
        
        if not request.query_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Se requiere texto de consulta"
            )
        
        logger.info(f"Búsqueda híbrida: {len(request.document_ids)} documentos, query: '{request.query_text}'")
        
        # Realizar búsqueda híbrida
        results = await vector_store_service.search_by_document_ids(
            document_ids=request.document_ids,
            query_text=request.query_text,
            limit=request.limit
        )
        
        # Obtener todos los fragmentos de cada documento solicitado
        all_document_chunks = {}
        for doc_id in request.document_ids:
            # Obtener todos los fragmentos del documento
            chunks = await vector_store_service.get_document_chunks(doc_id)
            # Convertir a DocumentChunk schema
            all_document_chunks[doc_id] = [
                DocumentChunk(id=c['id'], text=c['text'], metadata=c['metadata']) for c in chunks
            ]
        
        # Convertir a esquema de respuesta
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                id=result['id'],
                score=result['score'],
                text=result['text'],
                document_id=result['metadata']['DocumentId'],
                file_name=result['metadata']['FileName'],
                chunk_index=result['metadata']['chunk_index'],
                total_chunks=result['metadata']['total_chunks']
            ))
        
        return HybridSearchResponse(
            success=True,
            message=f"Búsqueda completada: {len(search_results)} resultados",
            results=search_results,
            query_text=request.query_text,
            document_ids=request.document_ids,
            all_chunks=all_document_chunks  # Agregar todos los fragmentos
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en búsqueda híbrida: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post(
    "/similarity",
    response_model=SimilaritySearchResponse,
    summary="Búsqueda por similitud general",
    description="Busca en toda la base vectorial por similitud de contenido"
)
async def similarity_search(request: SimilaritySearchRequest):
    """
    Búsqueda por similitud en toda la base vectorial.
    """
    try:
        if not request.query_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Se requiere texto de consulta"
            )
        
        logger.info(f"Búsqueda por similitud: '{request.query_text}'")
        
        # Realizar búsqueda por similitud
        results = await vector_store_service.search_similar(
            query_text=request.query_text,
            limit=request.limit,
            score_threshold=request.score_threshold
        )
        
        # Convertir a esquema de respuesta
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                id=result['id'],
                score=result['score'],
                text=result['text'],
                document_id=result['metadata']['DocumentId'],
                file_name=result['metadata']['FileName'],
                chunk_index=result['metadata']['chunk_index'],
                total_chunks=result['metadata']['total_chunks']
            ))
        
        return SimilaritySearchResponse(
            success=True,
            message=f"Búsqueda completada: {len(search_results)} resultados",
            results=search_results,
            query_text=request.query_text
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en búsqueda por similitud: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get(
    "/stats",
    summary="Estadísticas de la colección vectorial",
    description="Obtiene estadísticas de la base vectorial"
)
async def get_vector_stats():
    """
    Obtiene estadísticas de la colección vectorial.
    """
    try:
        stats = await vector_store_service.get_collection_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        ) 