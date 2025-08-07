"""
Servicio optimizado para embeddings de documentos usando BAAI/bge-m3.
Usa el modelo BAAI/bge-m3 para generar embeddings de alta calidad.
"""
import re
from typing import List, Dict, Any
import logging
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class BAAIEmbeddingService:
    """
    Servicio optimizado para generar embeddings de documentos usando BAAI/bge-m3.
    Usa el modelo BAAI/bge-m3 para embeddings de alta calidad.
    """
    
    def __init__(self):
        # Modelo BAAI/bge-m3 para embeddings de alta calidad
        self.model = SentenceTransformer('BAAI/bge-m3')  # 1024 dimensiones, alta calidad
        self.max_chunk_size = 512  # Tamaño óptimo de párrafo
        self.overlap_size = 50     # Overlap para mantener contexto
        
    def split_into_paragraphs(self, text: str) -> List[str]:
        """
        Divide el texto en párrafos optimizados para embeddings.
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de párrafos
        """
        # Limpiar texto
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Dividir por puntos y mantener contexto
        sentences = re.split(r'[.!?]+', text)
        paragraphs = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Si agregar esta oración excede el límite, guardar chunk actual
            if len(current_chunk) + len(sentence) > self.max_chunk_size:
                if current_chunk:
                    paragraphs.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Agregar último chunk
        if current_chunk:
            paragraphs.append(current_chunk.strip())
        
        # Si no hay párrafos, dividir por longitud
        if not paragraphs:
            paragraphs = [text[i:i+self.max_chunk_size] 
                        for i in range(0, len(text), self.max_chunk_size - self.overlap_size)]
        
        return paragraphs
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para una lista de textos usando BAAI/bge-m3.
        
        Args:
            texts: Lista de textos a procesar
            
        Returns:
            Lista de embeddings
        """
        try:
            # Generar embeddings en batch para eficiencia
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generando embeddings con BAAI/bge-m3: {e}")
            raise
    
    def process_document(self, content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Procesa un documento completo y retorna chunks con embeddings.
        
        Args:
            content: Contenido del documento
            metadata: Metadatos del documento (incluye DocumentId)
            
        Returns:
            Lista de chunks con embeddings y metadatos
        """
        # Dividir en párrafos
        paragraphs = self.split_into_paragraphs(content)
        
        if not paragraphs:
            logger.warning(f"No se pudieron generar párrafos para el documento {metadata.get('DocumentId')}")
            return []
        
        # Generar embeddings para todos los párrafos
        embeddings = self.generate_embeddings(paragraphs)
        
        # Crear chunks con embeddings
        chunks = []
        for i, (paragraph, embedding) in enumerate(zip(paragraphs, embeddings)):
            chunk = {
                "content": paragraph,
                "embedding": embedding,
                "metadata": {
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(paragraphs)
                }
            }
            chunks.append(chunk)
        
        logger.info(f"Procesado documento {metadata.get('DocumentId')}: {len(chunks)} chunks generados")
        return chunks

# Instancia global del servicio
baai_embedding_service = BAAIEmbeddingService() 