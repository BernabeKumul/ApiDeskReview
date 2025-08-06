"""
Servicio optimizado para embeddings de documentos.
Usa modelos eficientes y procesamiento por párrafos.
"""
import re
from typing import List, Dict, Any
import logging
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Servicio optimizado para generar embeddings de documentos.
    Usa modelos eficientes y procesamiento por párrafos.
    """
    
    def __init__(self):
        # Modelo optimizado para embeddings - más eficiente que OpenAI
        # text-embedding-ada-002 equivalente pero local y más barato
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensiones, muy eficiente
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
        Genera embeddings para una lista de textos.
        
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
            logger.error(f"Error generando embeddings: {e}")
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
            logger.warning(f"Documento {metadata.get('DocumentId')} no tiene contenido procesable")
            return []
        
        # Generar embeddings para todos los párrafos
        embeddings = self.generate_embeddings(paragraphs)
        
        # Crear chunks con metadatos
        chunks = []
        document_id = metadata.get('DocumentId')
        
        for i, (paragraph, embedding) in enumerate(zip(paragraphs, embeddings)):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_index': i,
                'total_chunks': len(paragraphs),
                'chunk_text': paragraph[:100] + "..." if len(paragraph) > 100 else paragraph
            })
            
            # ID único para cada chunk: DocumentId_chunk_index
            chunk_id = f"{document_id}_{i}"
            
            chunks.append({
                'id': chunk_id,  # ID único del chunk
                'document_id': document_id,  # DocumentId compartido
                'text': paragraph,
                'embedding': embedding,
                'metadata': chunk_metadata
            })
        
        logger.info(f"Procesado documento {document_id}: {len(chunks)} chunks")
        return chunks

# Instancia global
embedding_service = EmbeddingService() 