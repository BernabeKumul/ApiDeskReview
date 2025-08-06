"""
Servicio mejorado para Qdrant con funcionalidades avanzadas.
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
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Servicio para operaciones con Qdrant vector database.
    """
    
    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.collection_name = "AIDocumentsTest"  # Colección específica
        self.vector_size = 384  # Tamaño del modelo all-MiniLM-L6-v2
        
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
        """Crea la colección AIDocumentsTest si no existe."""
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
        IMPORTANTE: Verifica por DocumentId, no por chunk individual.
        
        Args:
            document_id: ID del documento (DocumentId)
            
        Returns:
            True si existe, False si no
        """
        try:
            # Crear un vector dummy para la búsqueda
            dummy_vector = [0.0] * self.vector_size
            
            # Buscar cualquier chunk que tenga este DocumentId
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=dummy_vector,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="metadata.DocumentId",
                            match=MatchValue(value=document_id)
                        )
                    ]
                ),
                limit=1
            )
            
            exists = len(search_result) > 0
            if exists:
                logger.info(f"Documento {document_id} ya existe en Qdrant")
                print(f"🔄 Documento {document_id} ya existe en Qdrant")
            else:
                logger.info(f"Documento {document_id} no existe en Qdrant")
                print(f"📄 Documento {document_id} no existe en Qdrant")
            
            return exists
            
        except Exception as e:
            logger.error(f"Error verificando existencia de documento {document_id}: {e}")
            return False
    
    async def insert_document_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Inserta chunks de un documento en Qdrant.
        
        Args:
            chunks: Lista de chunks con embeddings y metadatos
            
        Returns:
            True si se insertó correctamente
        """
        try:
            if not chunks:
                logger.warning("No hay chunks para insertar")
                return False
            
            # Verificar que todos los chunks tienen el mismo DocumentId
            document_id = chunks[0]['document_id']
            for chunk in chunks:
                if chunk['document_id'] != document_id:
                    raise ValueError(f"Todos los chunks deben tener el mismo DocumentId: {document_id}")
            
            # Crear puntos para Qdrant
            points = []
            for chunk in chunks:
                # Generar ID numérico único
                point_id = self._generate_point_id(document_id, chunk['metadata']['chunk_index'])
                
                point = PointStruct(
                    id=point_id,  # ID numérico único
                    vector=chunk['embedding'],
                    payload=chunk['metadata']
                )
                points.append(point)
            
            # Insertar en batch
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"✅ Insertados {len(points)} chunks para documento {document_id}")
            print(f"✅ Insertados {len(points)} chunks para documento {document_id}")
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
        Búsqueda híbrida: primero filtra por IDs, luego busca por similitud.
        
        Args:
            document_ids: Lista de IDs de documentos a buscar
            query_text: Texto de consulta
            limit: Límite de resultados
            
        Returns:
            Lista de resultados con score y metadatos
        """
        try:
            # Generar embedding para la consulta
            query_embedding = embedding_service.generate_embeddings([query_text])[0]
            
            # Crear filtro para los IDs de documentos
            document_filters = [
                FieldCondition(
                    key="metadata.DocumentId",
                    match=MatchValue(value=doc_id)
                ) for doc_id in document_ids
            ]
            
            # Buscar con filtro y similitud
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=Filter(
                    should=document_filters  # OR entre los IDs
                ),
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            # Formatear resultados
            results = []
            for point in search_result:
                results.append({
                    'id': point.id,
                    'score': point.score,
                    'text': point.payload.get('chunk_text', ''),
                    'metadata': point.payload
                })
            
            logger.info(f"Búsqueda híbrida: {len(results)} resultados para {len(document_ids)} documentos")
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda híbrida: {e}")
            raise
    
    async def search_similar(
        self, 
        query_text: str, 
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda por similitud general.
        
        Args:
            query_text: Texto de consulta
            limit: Límite de resultados
            score_threshold: Umbral mínimo de similitud
            
        Returns:
            Lista de resultados
        """
        try:
            # Generar embedding para la consulta
            query_embedding = embedding_service.generate_embeddings([query_text])[0]
            
            # Buscar
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            
            # Formatear resultados
            results = []
            for point in search_result:
                results.append({
                    'id': point.id,
                    'score': point.score,
                    'text': point.payload.get('chunk_text', ''),
                    'metadata': point.payload
                })
            
            logger.info(f"Búsqueda por similitud: {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda por similitud: {e}")
            raise
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la colección.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                'name': self.collection_name,
                'points_count': info.points_count,
                'vectors_count': info.vectors_count,
                'status': info.status
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
            logger.info(f"Buscando chunks para documento {document_id}")
            
            # Usar search con un vector dummy y filtro
            dummy_vector = [0.0] * self.vector_size
            
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=dummy_vector,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="DocumentId",
                            match=MatchValue(value=document_id)
                        )
                    ]
                ),
                limit=10000,
                with_payload=True,
                with_vectors=False
            )
            
            logger.info(f"Search result: {len(search_result)} puntos encontrados")
            
            chunks = []
            for point in search_result:
                chunks.append({
                    'id': point.id,
                    'text': point.payload.get('chunk_text', ''),
                    'metadata': point.payload
                })
            
            # Ordenar por chunk_index
            chunks.sort(key=lambda x: x['metadata'].get('chunk_index', 0))
            
            logger.info(f"Obtenidos {len(chunks)} chunks para documento {document_id}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error obteniendo chunks del documento {document_id}: {e}")
            raise

# Instancia global
vector_store_service = VectorStoreService()