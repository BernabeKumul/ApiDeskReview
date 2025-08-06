"""
Esquemas para búsqueda vectorial.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SearchResult(BaseModel):
    """Resultado individual de búsqueda."""
    id: int  # Cambiado de str a int para coincidir con Qdrant
    score: float
    text: str
    document_id: int
    file_name: str
    chunk_index: int
    total_chunks: int

class DocumentChunk(BaseModel):
    """Fragmento de documento."""
    id: int
    text: str
    metadata: Dict[str, Any]

class HybridSearchRequest(BaseModel):
    """Request para búsqueda híbrida."""
    document_ids: List[int] = Field(..., description="IDs de documentos a buscar")
    query_text: str = Field(..., description="Texto de consulta")
    limit: int = Field(10, ge=1, le=100, description="Límite de resultados")

class HybridSearchResponse(BaseModel):
    """Response para búsqueda híbrida."""
    success: bool
    message: str
    results: List[SearchResult]
    query_text: str
    document_ids: List[int]
    all_chunks: Dict[int, List[DocumentChunk]] = Field(..., description="Todos los fragmentos de cada documento encontrado")

class SimilaritySearchRequest(BaseModel):
    """Request para búsqueda por similitud."""
    query_text: str = Field(..., description="Texto de consulta")
    limit: int = Field(10, ge=1, le=100, description="Límite de resultados")
    score_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Umbral mínimo de similitud")

class SimilaritySearchResponse(BaseModel):
    """Response para búsqueda por similitud."""
    success: bool
    message: str
    results: List[SearchResult]
    query_text: str 