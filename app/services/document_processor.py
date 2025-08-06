"""
Procesador para documentos JSON de AzzuleAI.
"""
import json
import logging
from typing import List, Dict, Any
from pathlib import Path

from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store_service

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Procesa documentos JSON y los inserta en Qdrant.
    """
    
    def __init__(self):
        self.processed_count = 0
        self.skipped_count = 0
        self.error_count = 0
    
    async def process_json_file(self, file_path: str) -> Dict[str, int]:
        """
        Procesa un archivo JSON completo.
        
        Args:
            file_path: Ruta al archivo JSON
            
        Returns:
            Estadísticas del procesamiento
        """
        try:
            # Cargar archivo JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            logger.info(f"📄 Procesando {len(documents)} documentos de {file_path}")
            print(f"📄 Procesando {len(documents)} documentos de {file_path}")
            
            # Procesar cada documento
            for i, doc in enumerate(documents, 1):
                print(f"Procesando documento {i}/{len(documents)}: {doc.get('DocumentId', 'N/A')}")
                await self._process_single_document(doc)
            
            return {
                'processed': self.processed_count,
                'skipped': self.skipped_count,
                'errors': self.error_count,
                'total': len(documents)
            }
            
        except Exception as e:
            logger.error(f"Error procesando archivo {file_path}: {e}")
            raise
    
    async def _process_single_document(self, doc: Dict[str, Any]):
        """
        Procesa un documento individual.
        
        Args:
            doc: Documento a procesar
        """
        try:
            document_id = doc.get('DocumentId')
            if not document_id:
                logger.warning("Documento sin DocumentId, saltando...")
                self.skipped_count += 1
                return
            
            # 🔄 VERIFICACIÓN CLAVE: Verificar si el documento ya existe
            if await vector_store_service.document_exists(document_id):
                logger.info(f"🔄 Documento {document_id} ya existe en Qdrant, saltando...")
                print(f"🔄 Documento {document_id} ya existe en Qdrant, saltando...")
                self.skipped_count += 1
                return
            
            # Extraer metadatos
            metadata = {
                'DocumentId': document_id,
                'FileName': doc.get('FileName', ''),
                'DocumentType': doc.get('DocumentType', ''),
                'TotalReading': doc.get('TotalReading', 0),
                'CreatedAt': doc.get('CreatedAt', ''),
                'UpdatedAt': doc.get('UpdatedAt', ''),
                'Inactive': doc.get('Inactive', False)
            }
            
            # Procesar contenido
            content = doc.get('Content', '')
            if not content:
                logger.warning(f"Documento {document_id} sin contenido, saltando...")
                self.skipped_count += 1
                return
            
            # Generar chunks con embeddings
            chunks = embedding_service.process_document(content, metadata)
            
            if not chunks:
                logger.warning(f"Documento {document_id} no generó chunks válidos")
                self.skipped_count += 1
                return
            
            # Insertar en Qdrant
            success = await vector_store_service.insert_document_chunks(chunks)
            
            if success:
                self.processed_count += 1
                logger.info(f"✅ Documento {document_id} procesado: {len(chunks)} chunks")
                print(f"✅ Documento {document_id} procesado: {len(chunks)} chunks")
            else:
                self.error_count += 1
                logger.error(f"❌ Error procesando documento {document_id}")
                print(f"❌ Error procesando documento {document_id}")
                
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error procesando documento: {e}")
            print(f"❌ Error procesando documento: {e}")
    
    async def process_specific_documents(
        self, 
        file_path: str, 
        document_ids: List[int]
    ) -> Dict[str, int]:
        """
        Procesa solo documentos específicos por ID.
        
        Args:
            file_path: Ruta al archivo JSON
            document_ids: Lista de IDs a procesar
            
        Returns:
            Estadísticas del procesamiento
        """
        try:
            # Cargar archivo JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            # Filtrar documentos por ID
            filtered_docs = [
                doc for doc in documents 
                if doc.get('DocumentId') in document_ids
            ]
            
            logger.info(f"📄 Procesando {len(filtered_docs)} documentos específicos")
            print(f"📄 Procesando {len(filtered_docs)} documentos específicos")
            
            # Procesar documentos filtrados
            for doc in filtered_docs:
                await self._process_single_document(doc)
            
            return {
                'processed': self.processed_count,
                'skipped': self.skipped_count,
                'errors': self.error_count,
                'total': len(filtered_docs)
            }
            
        except Exception as e:
            logger.error(f"Error procesando documentos específicos: {e}")
            raise
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de procesamiento.
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'processed': self.processed_count,
            'skipped': self.skipped_count,
            'errors': self.error_count,
            'total': self.processed_count + self.skipped_count + self.error_count
        }

# Instancia global
document_processor = DocumentProcessor() 