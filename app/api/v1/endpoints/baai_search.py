"""
Endpoints para búsqueda y procesamiento con BAAI/bge-m3.
Proporciona endpoints específicos para embeddings y búsqueda vectorial con BAAI.
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List
import logging

from app.services.baai_vector_store import baai_vector_store_service
from app.services.baai_document_processor import baai_document_processor
from app.schemas.baai_search import (
    BAAISearchRequest,
    BAAISearchResponse,
    BAAISearchResult,
    BAAIProcessRequest,
    BAAIProcessResponse,
    BAAIStatsResponse,
    BAAICollectionStats
)

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/baai-search", tags=["BAAI Search"])


@router.post(
    "/search",
    response_model=BAAISearchResponse,
    summary="Búsqueda híbrida con BAAI/bge-m3",
    description="Realiza búsqueda híbrida: primero por IDs específicos, luego por similitud de texto"
)
async def search_with_baai(request: BAAISearchRequest):
    """
    Realiza búsqueda híbrida usando BAAI/bge-m3.
    Primero busca en documentos específicos por ID, luego por similitud de texto.
    """
    try:
        logger.info(f"Búsqueda BAAI iniciada: query='{request.query_text}', document_ids={request.document_ids}")
        
        # Conectar a la base vectorial
        await baai_vector_store_service.connect()
        
        # Realizar búsqueda híbrida
        results = await baai_vector_store_service.hybrid_search(
            document_ids=request.document_ids or [],
            query_text=request.query_text,
            limit=request.limit,
            score_threshold=request.score_threshold
        )
        
        # Desconectar de la base vectorial
        await baai_vector_store_service.disconnect()
        
        # Convertir resultados a esquemas
        search_results = []
        for result in results:
            search_result = BAAISearchResult(
                score=result["score"],
                document_id=result["document_id"],
                file_name=result["file_name"],
                document_type=result["document_type"],
                content=result["content"],
                chunk_index=result["chunk_index"],
                total_chunks=result["total_chunks"],
                created_at=result["created_at"],
                total_reading=result["total_reading"]
            )
            search_results.append(search_result)
        
        # Determinar tipo de búsqueda
        search_type = "hybrid"
        if request.document_ids:
            search_type = "hybrid_with_ids"
        else:
            search_type = "similarity_only"
        
        return BAAISearchResponse(
            success=True,
            message=f"Búsqueda completada exitosamente. {len(search_results)} resultados encontrados.",
            results=search_results,
            total_results=len(search_results),
            search_type=search_type
        )
        
    except Exception as e:
        logger.error(f"Error en búsqueda BAAI: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda BAAI: {str(e)}"
        )


@router.get(
    "/search/similar",
    response_model=BAAISearchResponse,
    summary="Búsqueda por similitud con BAAI/bge-m3",
    description="Busca documentos similares por texto de consulta"
)
async def search_similar_baai(
    query_text: str = Query(..., description="Texto de consulta"),
    limit: int = Query(10, ge=1, le=100, description="Límite de resultados"),
    score_threshold: float = Query(0.7, ge=0.0, le=1.0, description="Umbral de similitud mínimo")
):
    """
    Busca documentos similares usando BAAI/bge-m3.
    """
    try:
        logger.info(f"Búsqueda por similitud BAAI: query='{query_text}'")
        
        # Conectar a la base vectorial
        await baai_vector_store_service.connect()
        
        # Realizar búsqueda por similitud
        results = await baai_vector_store_service.search_similar(
            query_text=query_text,
            limit=limit,
            score_threshold=score_threshold
        )
        
        # Desconectar de la base vectorial
        await baai_vector_store_service.disconnect()
        
        # Convertir resultados a esquemas
        search_results = []
        for result in results:
            search_result = BAAISearchResult(
                score=result["score"],
                document_id=result["document_id"],
                file_name=result["file_name"],
                document_type=result["document_type"],
                content=result["content"],
                chunk_index=result["chunk_index"],
                total_chunks=result["total_chunks"],
                created_at=result["created_at"],
                total_reading=result["total_reading"]
            )
            search_results.append(search_result)
        
        return BAAISearchResponse(
            success=True,
            message=f"Búsqueda por similitud completada. {len(search_results)} resultados encontrados.",
            results=search_results,
            total_results=len(search_results),
            search_type="similarity"
        )
        
    except Exception as e:
        logger.error(f"Error en búsqueda por similitud BAAI: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda por similitud: {str(e)}"
        )


@router.get(
    "/search/by-ids",
    response_model=BAAISearchResponse,
    summary="Búsqueda por IDs específicos con BAAI/bge-m3",
    description="Busca en documentos específicos por sus IDs"
)
async def search_by_ids_baai(
    document_ids: List[int] = Query(..., description="IDs de documentos a buscar"),
    query_text: str = Query(..., description="Texto de consulta"),
    limit: int = Query(10, ge=1, le=100, description="Límite de resultados")
):
    """
    Busca en documentos específicos por sus IDs usando BAAI/bge-m3.
    """
    try:
        logger.info(f"Búsqueda por IDs BAAI: document_ids={document_ids}, query='{query_text}'")
        
        # Conectar a la base vectorial
        await baai_vector_store_service.connect()
        
        # Realizar búsqueda por IDs
        results = await baai_vector_store_service.search_by_document_ids(
            document_ids=document_ids,
            query_text=query_text,
            limit=limit
        )
        
        # Desconectar de la base vectorial
        await baai_vector_store_service.disconnect()
        
        # Convertir resultados a esquemas
        search_results = []
        for result in results:
            search_result = BAAISearchResult(
                score=result["score"],
                document_id=result["document_id"],
                file_name=result["file_name"],
                document_type=result["document_type"],
                content=result["content"],
                chunk_index=result["chunk_index"],
                total_chunks=result["total_chunks"],
                created_at=result["created_at"],
                total_reading=result["total_reading"]
            )
            search_results.append(search_result)
        
        return BAAISearchResponse(
            success=True,
            message=f"Búsqueda por IDs completada. {len(search_results)} resultados encontrados.",
            results=search_results,
            total_results=len(search_results),
            search_type="by_ids"
        )
        
    except Exception as e:
        logger.error(f"Error en búsqueda por IDs BAAI: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda por IDs: {str(e)}"
        )


@router.post(
    "/process",
    response_model=BAAIProcessResponse,
    summary="Procesar documentos para embeddings BAAI/bge-m3",
    description="Procesa documentos desde JSON y crea embeddings con BAAI/bge-m3"
)
async def process_documents_baai(request: BAAIProcessRequest):
    """
    Procesa documentos desde JSON y crea embeddings con BAAI/bge-m3.
    Evita duplicados automáticamente.
    """
    try:
        logger.info(f"Procesamiento BAAI iniciado: document_ids={request.document_ids}, limit={request.limit}, process_all={request.process_all}")
        
        if request.process_all:
            # Procesar todos los documentos
            result = await baai_document_processor.process_all_documents(limit=request.limit)
        elif request.document_ids:
            # Procesar documentos específicos
            result = await baai_document_processor.process_documents_by_ids(request.document_ids)
        else:
            raise HTTPException(
                status_code=400,
                detail="Debe especificar document_ids o process_all=True"
            )
        
        return BAAIProcessResponse(
            success=result["success"],
            message=result["message"],
            processed=result["processed"],
            skipped=result["skipped"],
            errors=result["errors"],
            total_documents=result["total_documents"],
            collection_stats=result.get("collection_stats")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en procesamiento BAAI: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en procesamiento BAAI: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=BAAIStatsResponse,
    summary="Obtener estadísticas de la colección BAAI",
    description="Obtiene estadísticas de la colección vectorial BAAI"
)
async def get_baai_stats():
    """
    Obtiene estadísticas de la colección vectorial BAAI.
    """
    try:
        logger.info("Obteniendo estadísticas de la colección BAAI")
        
        # Conectar a la base vectorial
        await baai_vector_store_service.connect()
        
        # Obtener estadísticas
        stats = await baai_vector_store_service.get_collection_stats()
        
        # Desconectar de la base vectorial
        await baai_vector_store_service.disconnect()
        
        if stats:
            collection_stats = BAAICollectionStats(
                collection_name=stats["collection_name"],
                vector_size=stats["vector_size"],
                points_count=stats["points_count"],
                segments_count=stats["segments_count"],
                status=stats["status"]
            )
            
            return BAAIStatsResponse(
                success=True,
                message="Estadísticas obtenidas exitosamente",
                stats=collection_stats
            )
        else:
            return BAAIStatsResponse(
                success=False,
                message="No se pudieron obtener estadísticas",
                stats=None
            )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas BAAI: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


@router.get(
    "/document/{document_id}/chunks",
    summary="Obtener chunks de un documento específico",
    description="Obtiene todos los chunks de un documento específico"
)
async def get_document_chunks_baai(
    document_id: int = Path(..., description="ID del documento")
):
    """
    Obtiene todos los chunks de un documento específico.
    """
    try:
        logger.info(f"Obteniendo chunks del documento {document_id}")
        
        # Conectar a la base vectorial
        await baai_vector_store_service.connect()
        
        # Obtener chunks del documento
        chunks = await baai_vector_store_service.get_document_chunks(document_id)
        
        # Desconectar de la base vectorial
        await baai_vector_store_service.disconnect()
        
        return {
            "success": True,
            "message": f"Chunks obtenidos para documento {document_id}",
            "document_id": document_id,
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo chunks del documento {document_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo chunks: {str(e)}"
        ) 