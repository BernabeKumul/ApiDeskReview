"""
Servicio mejorado para Qdrant con funcionalidades avanzadas para BAAI/bge-m3.
"""
from typing import List, Dict, Any, Optional
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, 
    Filter, FieldCondition, MatchValue,
    SearchRequest, FilterSelector
)
import numpy as np
import hashlib

from app.core.config import settings
from app.services.baai_embedding_service import baai_embedding_service

logger = logging.getLogger(__name__)

class BAAIVectorStoreService:
    """
    Servicio para operaciones con Qdrant vector database usando BAAI/bge-m3.
    """
    
    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.collection_name = settings.qdrant_BAAI_collection_name  # Colección específica para BAAI
        self.vector_size = 1024  # Tamaño del modelo BAAI/bge-m3
        
    def _generate_point_id(self, document_id: int, chunk_index: int) -> int:
        """
        Genera un ID numérico único para el punto basado en DocumentId y chunk_index.
        
        Args:
            document_id: ID del documento
            chunk_index: Índice del chunk
            
        Returns:
            ID numérico único
        """
        # Crear un hash único combinando DocumentId y chunk_index
        unique_string = f"{document_id}_{chunk_index}"
        hash_object = hashlib.md5(unique_string.encode())
        # Convertir a entero usando los primeros 8 bytes
        return int(hash_object.hexdigest()[:16], 16)
    
    async def connect(self):
        """Conecta a Qdrant."""
        try:
            # Configurar cliente Qdrant con HTTP
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key if settings.qdrant_api_key else None,
                https=settings.qdrant_https
            )
            
            # Verificar conexión
            self.client.get_collections()
            logger.info(f"✅ Conectado a Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
            print(f"✅ Conectado a Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
            
        except Exception as e:
            logger.error(f"❌ Error conectando a Qdrant: {e}")
            raise
    
    async def disconnect(self):
        """Desconecta de Qdrant."""
        if self.client:
            self.client.close()
            logger.info("✅ Desconectado de Qdrant")
            print("✅ Desconectado de Qdrant")
    
    async def create_collection(self):
        """Crea la colección BAAI si no existe."""
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Colección '{self.collection_name}' creada")
                print(f"✅ Colección '{self.collection_name}' creada")
            else:
                logger.info(f"✅ Colección '{self.collection_name}' ya existe")
                print(f"✅ Colección '{self.collection_name}' ya existe")
                
        except Exception as e:
            logger.error(f"❌ Error creando colección: {e}")
            raise
    
    async def document_exists(self, document_id: int) -> bool:
        """
        Verifica si un documento ya existe en la base vectorial.
        
        Args:
            document_id: ID del documento a verificar
            
        Returns:
            True si el documento existe, False en caso contrario
        """
        try:
            # Buscar puntos con el DocumentId específico
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="DocumentId",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
            
            # Realizar búsqueda con límite 1 para verificar existencia
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=[0.0] * self.vector_size,  # Vector dummy
                query_filter=filter_condition,
                limit=1
            )
            
            return len(search_result) > 0
            
        except Exception as e:
            logger.error(f"Error verificando existencia del documento {document_id}: {e}")
            return False
    
    async def insert_document_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Inserta chunks de un documento en la base vectorial.
        
        Args:
            chunks: Lista de chunks con embeddings y metadatos
            
        Returns:
            True si se insertaron correctamente, False en caso contrario
        """
        try:
            if not chunks:
                logger.warning("No hay chunks para insertar")
                return False
            
            # Preparar puntos para inserción
            points = []
            for chunk in chunks:
                metadata = chunk["metadata"]
                document_id = metadata["DocumentId"]
                chunk_index = metadata["chunk_index"]
                
                # Generar ID único para el punto
                point_id = self._generate_point_id(document_id, chunk_index)
                
                # Crear punto
                point = PointStruct(
                    id=point_id,
                    vector=chunk["embedding"],
                    payload={
                        "DocumentId": document_id,
                        "FileName": metadata.get("FileName", ""),
                        "DocumentType": metadata.get("DocumentType", ""),
                        "Content": chunk["content"],
                        "ChunkIndex": chunk_index,
                        "TotalChunks": metadata.get("total_chunks", 1),
                        "CreatedAt": metadata.get("CreatedAt", ""),
                        "TotalReading": metadata.get("TotalReading", 0)
                    }
                )
                points.append(point)
            
            # Insertar puntos en batch
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"✅ Insertados {len(points)} chunks para documento {chunks[0]['metadata']['DocumentId']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error insertando chunks: {e}")
            return False
    
    async def search_by_document_ids(
        self, 
        document_ids: List[int], 
        query_text: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos específicos por IDs y luego por similitud de texto.
        
        Args:
            document_ids: Lista de IDs de documentos a buscar
            query_text: Texto de consulta para búsqueda por similitud
            limit: Límite de resultados
            
        Returns:
            Lista de resultados ordenados por relevancia
        """
        try:
            # Generar embedding para el texto de consulta
            query_embedding = baai_embedding_service.generate_embeddings([query_text])[0]
            
            # Crear filtro para los DocumentIds específicos
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="DocumentId",
                        match=MatchValue(value=doc_id)
                    ) for doc_id in document_ids
                ]
            )
            
            # Realizar búsqueda vectorial
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=filter_condition,
                limit=limit
            )
            
            # Procesar resultados
            results = []
            for point in search_result:
                result = {
                    "score": point.score,
                    "document_id": point.payload["DocumentId"],
                    "file_name": point.payload["FileName"],
                    "document_type": point.payload["DocumentType"],
                    "content": point.payload["Content"],
                    "chunk_index": point.payload["ChunkIndex"],
                    "total_chunks": point.payload["TotalChunks"],
                    "created_at": point.payload["CreatedAt"],
                    "total_reading": point.payload["TotalReading"]
                }
                results.append(result)
            
            logger.info(f"Búsqueda por IDs {document_ids}: {len(results)} resultados encontrados")
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda por IDs: {e}")
            return []
    
    async def search_similar(
        self, 
        query_text: str, 
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos similares por texto de consulta.
        
        Args:
            query_text: Texto de consulta
            limit: Límite de resultados
            score_threshold: Umbral de similitud mínimo
            
        Returns:
            Lista de resultados ordenados por relevancia
        """
        try:
            # Generar embedding para el texto de consulta
            query_embedding = baai_embedding_service.generate_embeddings([query_text])[0]
            
            # Realizar búsqueda vectorial
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Procesar resultados
            results = []
            for point in search_result:
                result = {
                    "score": point.score,
                    "document_id": point.payload["DocumentId"],
                    "file_name": point.payload["FileName"],
                    "document_type": point.payload["DocumentType"],
                    "content": point.payload["Content"],
                    "chunk_index": point.payload["ChunkIndex"],
                    "total_chunks": point.payload["TotalChunks"],
                    "created_at": point.payload["CreatedAt"],
                    "total_reading": point.payload["TotalReading"]
                }
                results.append(result)
            
            logger.info(f"Búsqueda por similitud: {len(results)} resultados encontrados")
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda por similitud: {e}")
            return []
    
    async def hybrid_search(
        self,
        document_ids: List[int],
        query_text: str,
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda híbrida: primero por IDs específicos, luego por similitud de texto.
        
        Args:
            document_ids: Lista de IDs de documentos a buscar primero
            query_text: Texto de consulta para búsqueda por similitud
            limit: Límite de resultados
            score_threshold: Umbral de similitud mínimo
            
        Returns:
            Lista de resultados ordenados por relevancia
        """
        try:
            results = []
            
            # 1. Primero buscar por IDs específicos
            if document_ids:
                id_results = await self.search_by_document_ids(document_ids, query_text, limit)
                results.extend(id_results)
                logger.info(f"Búsqueda por IDs: {len(id_results)} resultados")
            
            # 2. Si no hay suficientes resultados, buscar por similitud
            remaining_limit = limit - len(results)
            if remaining_limit > 0:
                # Excluir documentos ya encontrados por ID
                exclude_doc_ids = [r["document_id"] for r in results]
                
                # Buscar por similitud excluyendo los ya encontrados
                similar_results = await self.search_similar(query_text, remaining_limit, score_threshold)
                
                # Filtrar resultados que no estén en la lista de IDs específicos
                filtered_results = [
                    r for r in similar_results 
                    if r["document_id"] not in exclude_doc_ids
                ]
                
                results.extend(filtered_results)
                logger.info(f"Búsqueda por similitud: {len(filtered_results)} resultados adicionales")
            
            # Ordenar por score y eliminar duplicados
            unique_results = {}
            for result in results:
                key = f"{result['document_id']}_{result['chunk_index']}"
                if key not in unique_results or result['score'] > unique_results[key]['score']:
                    unique_results[key] = result
            
            final_results = list(unique_results.values())
            final_results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"Búsqueda híbrida completada: {len(final_results)} resultados únicos")
            return final_results[:limit]
            
        except Exception as e:
            logger.error(f"Error en búsqueda híbrida: {e}")
            return []
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la colección.
        
        Returns:
            Diccionario con estadísticas de la colección
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            collection_stats = self.client.get_collection(self.collection_name)
            
            return {
                "collection_name": self.collection_name,
                "vector_size": self.vector_size,
                "points_count": collection_stats.points_count,
                "segments_count": collection_stats.segments_count,
                "status": collection_info.status
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    async def get_document_chunks(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los chunks de un documento específico.
        
        Args:
            document_id: ID del documento
            
        Returns:
            Lista de chunks del documento
        """
        try:
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="DocumentId",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
            
            # Buscar todos los chunks del documento
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=100  # Límite alto para obtener todos los chunks
            )
            
            chunks = []
            for point in search_result[0]:  # scroll retorna (points, next_page_offset)
                chunk = {
                    "document_id": point.payload["DocumentId"],
                    "file_name": point.payload["FileName"],
                    "content": point.payload["Content"],
                    "chunk_index": point.payload["ChunkIndex"],
                    "total_chunks": point.payload["TotalChunks"],
                    "created_at": point.payload["CreatedAt"],
                    "total_reading": point.payload["TotalReading"]
                }
                chunks.append(chunk)
            
            # Ordenar por chunk_index
            chunks.sort(key=lambda x: x["chunk_index"])
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error obteniendo chunks del documento {document_id}: {e}")
            return []

# Instancia global del servicio
baai_vector_store_service = BAAIVectorStoreService() 