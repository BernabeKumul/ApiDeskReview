"""
Esquemas para búsqueda y respuestas de BAAI/bge-m3.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BAAISearchResult(BaseModel):
    """Resultado individual de búsqueda BAAI."""
    score: float = Field(..., description="Score de similitud")
    document_id: int = Field(..., description="ID del documento")
    file_name: str = Field(..., description="Nombre del archivo")
    document_type: str = Field(..., description="Tipo de documento")
    content: str = Field(..., description="Contenido del chunk")
    chunk_index: int = Field(..., description="Índice del chunk")
    total_chunks: int = Field(..., description="Total de chunks del documento")
    created_at: str = Field(..., description="Fecha de creación")
    total_reading: int = Field(..., description="Total de lecturas")


class BAAISearchRequest(BaseModel):
    """Solicitud de búsqueda BAAI."""
    query_text: str = Field(..., description="Texto de consulta")
    document_ids: Optional[List[int]] = Field(None, description="IDs específicos de documentos a buscar primero")
    limit: int = Field(10, ge=1, le=100, description="Límite de resultados")
    score_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Umbral de similitud mínimo")


class BAAISearchResponse(BaseModel):
    """Respuesta de búsqueda BAAI."""
    success: bool = Field(..., description="Indica si la búsqueda fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    results: List[BAAISearchResult] = Field(..., description="Lista de resultados")
    total_results: int = Field(..., description="Total de resultados encontrados")
    search_type: str = Field(..., description="Tipo de búsqueda realizada")


class BAAIProcessRequest(BaseModel):
    """Solicitud de procesamiento BAAI."""
    document_ids: Optional[List[int]] = Field(None, description="IDs específicos de documentos a procesar")
    limit: Optional[int] = Field(None, ge=1, description="Límite de documentos a procesar")
    process_all: bool = Field(False, description="Procesar todos los documentos del JSON")


class BAAIProcessResponse(BaseModel):
    """Respuesta de procesamiento BAAI."""
    success: bool = Field(..., description="Indica si el procesamiento fue exitoso")
    message: str = Field(..., description="Mensaje descriptivo")
    processed: int = Field(..., description="Número de documentos procesados")
    skipped: int = Field(..., description="Número de documentos saltados")
    errors: int = Field(..., description="Número de errores")
    total_documents: int = Field(..., description="Total de documentos procesados")
    collection_stats: Optional[Dict[str, Any]] = Field(None, description="Estadísticas de la colección")


class BAAICollectionStats(BaseModel):
    """Estadísticas de la colección BAAI."""
    collection_name: str = Field(..., description="Nombre de la colección")
    vector_size: int = Field(..., description="Tamaño del vector")
    points_count: int = Field(..., description="Número de puntos en la colección")
    segments_count: int = Field(..., description="Número de segmentos")
    status: str = Field(..., description="Estado de la colección")


class BAAIStatsResponse(BaseModel):
    """Respuesta de estadísticas BAAI."""
    success: bool = Field(..., description="Indica si la consulta fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo")
    stats: Optional[BAAICollectionStats] = Field(None, description="Estadísticas de la colección") 