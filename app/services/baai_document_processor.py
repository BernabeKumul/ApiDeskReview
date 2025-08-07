"""
Servicio de procesamiento de documentos para BAAI/bge-m3.
Lee documentos desde JSON y los procesa para embeddings.
"""
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.services.baai_embedding_service import baai_embedding_service
from app.services.baai_vector_store import baai_vector_store_service

logger = logging.getLogger(__name__)

class BAAIDocumentProcessor:
    """
    Servicio para procesar documentos desde JSON y crear embeddings con BAAI/bge-m3.
    """
    
    def __init__(self, json_file_path: str = "JSON/AzzuleAI.AIDocuments.json"):
        self.json_file_path = json_file_path
        self.processed_documents = set()  # Para evitar duplicados
        
    def load_documents_from_json(self) -> List[Dict[str, Any]]:
        """
        Carga documentos desde el archivo JSON.
        
        Returns:
            Lista de documentos del JSON
        """
        try:
            json_path = Path(self.json_file_path)
            if not json_path.exists():
                logger.error(f"Archivo JSON no encontrado: {self.json_file_path}")
                return []
            
            with open(json_path, 'r', encoding='utf-8') as file:
                documents = json.load(file)
            
            logger.info(f"Cargados {len(documents)} documentos desde JSON")
            return documents
            
        except Exception as e:
            logger.error(f"Error cargando documentos desde JSON: {e}")
            return []
    
    async def process_single_document(self, document: Dict[str, Any]) -> bool:
        """
        Procesa un documento individual.
        
        Args:
            document: Documento a procesar
            
        Returns:
            True si se procesó correctamente, False en caso contrario
        """
        try:
            document_id = document.get("DocumentId")
            if not document_id:
                logger.warning("Documento sin DocumentId, saltando...")
                return False
            
            # Verificar si el documento ya existe en la base vectorial
            exists = await baai_vector_store_service.document_exists(document_id)
            if exists:
                logger.info(f"Documento {document_id} ya existe en la base vectorial, saltando...")
                return False
            
            # Extraer contenido y metadatos
            content = document.get("Content", "")
            if not content:
                logger.warning(f"Documento {document_id} sin contenido, saltando...")
                return False
            
            # Preparar metadatos
            metadata = {
                "DocumentId": document_id,
                "FileName": document.get("FileName", ""),
                "DocumentType": document.get("DocumentType", ""),
                "CreatedAt": document.get("CreatedAt", ""),
                "TotalReading": document.get("TotalReading", 0)
            }
            
            # Procesar documento con embeddings
            chunks = baai_embedding_service.process_document(content, metadata)
            
            if not chunks:
                logger.warning(f"No se pudieron generar chunks para el documento {document_id}")
                return False
            
            # Insertar chunks en la base vectorial
            success = await baai_vector_store_service.insert_document_chunks(chunks)
            
            if success:
                self.processed_documents.add(document_id)
                logger.info(f"✅ Documento {document_id} procesado exitosamente: {len(chunks)} chunks")
                return True
            else:
                logger.error(f"❌ Error insertando chunks para documento {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error procesando documento {document.get('DocumentId', 'unknown')}: {e}")
            return False
    
    async def process_all_documents(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Procesa todos los documentos del JSON.
        
        Args:
            limit: Límite opcional de documentos a procesar
            
        Returns:
            Estadísticas del procesamiento
        """
        try:
            # Cargar documentos desde JSON
            documents = self.load_documents_from_json()
            
            if not documents:
                logger.error("No se pudieron cargar documentos desde JSON")
                return {
                    "success": False,
                    "message": "No se pudieron cargar documentos desde JSON",
                    "processed": 0,
                    "skipped": 0,
                    "errors": 0
                }
            
            # Conectar a la base vectorial
            await baai_vector_store_service.connect()
            await baai_vector_store_service.create_collection()
            
            # Procesar documentos
            processed_count = 0
            skipped_count = 0
            error_count = 0
            
            # Aplicar límite si se especifica
            if limit:
                documents = documents[:limit]
            
            total_documents = len(documents)
            logger.info(f"Iniciando procesamiento de {total_documents} documentos...")
            
            for i, document in enumerate(documents, 1):
                try:
                    success = await self.process_single_document(document)
                    if success:
                        processed_count += 1
                    else:
                        skipped_count += 1
                        
                    # Log de progreso cada 10 documentos
                    if i % 10 == 0:
                        logger.info(f"Progreso: {i}/{total_documents} documentos procesados")
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error procesando documento {i}: {e}")
            
            # Desconectar de la base vectorial
            await baai_vector_store_service.disconnect()
            
            # Obtener estadísticas finales
            stats = await baai_vector_store_service.get_collection_stats()
            
            result = {
                "success": True,
                "message": f"Procesamiento completado: {processed_count} procesados, {skipped_count} saltados, {error_count} errores",
                "processed": processed_count,
                "skipped": skipped_count,
                "errors": error_count,
                "total_documents": total_documents,
                "collection_stats": stats
            }
            
            logger.info(f"✅ Procesamiento completado: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error en procesamiento masivo: {e}")
            return {
                "success": False,
                "message": f"Error en procesamiento: {str(e)}",
                "processed": 0,
                "skipped": 0,
                "errors": 1
            }
    
    async def process_documents_by_ids(self, document_ids: List[int]) -> Dict[str, Any]:
        """
        Procesa documentos específicos por sus IDs.
        
        Args:
            document_ids: Lista de IDs de documentos a procesar
            
        Returns:
            Estadísticas del procesamiento
        """
        try:
            # Cargar documentos desde JSON
            documents = self.load_documents_from_json()
            
            if not documents:
                logger.error("No se pudieron cargar documentos desde JSON")
                return {
                    "success": False,
                    "message": "No se pudieron cargar documentos desde JSON",
                    "processed": 0,
                    "skipped": 0,
                    "errors": 0
                }
            
            # Filtrar documentos por IDs
            target_documents = [
                doc for doc in documents 
                if doc.get("DocumentId") in document_ids
            ]
            
            if not target_documents:
                logger.warning(f"No se encontraron documentos con los IDs especificados: {document_ids}")
                return {
                    "success": False,
                    "message": f"No se encontraron documentos con los IDs: {document_ids}",
                    "processed": 0,
                    "skipped": 0,
                    "errors": 0
                }
            
            # Conectar a la base vectorial
            await baai_vector_store_service.connect()
            await baai_vector_store_service.create_collection()
            
            # Procesar documentos específicos
            processed_count = 0
            skipped_count = 0
            error_count = 0
            
            total_documents = len(target_documents)
            logger.info(f"Procesando {total_documents} documentos específicos...")
            
            for i, document in enumerate(target_documents, 1):
                try:
                    success = await self.process_single_document(document)
                    if success:
                        processed_count += 1
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error procesando documento {document.get('DocumentId')}: {e}")
            
            # Desconectar de la base vectorial
            await baai_vector_store_service.disconnect()
            
            result = {
                "success": True,
                "message": f"Procesamiento de documentos específicos completado: {processed_count} procesados, {skipped_count} saltados, {error_count} errores",
                "processed": processed_count,
                "skipped": skipped_count,
                "errors": error_count,
                "total_documents": total_documents,
                "target_ids": document_ids
            }
            
            logger.info(f"✅ Procesamiento de documentos específicos completado: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error en procesamiento de documentos específicos: {e}")
            return {
                "success": False,
                "message": f"Error en procesamiento: {str(e)}",
                "processed": 0,
                "skipped": 0,
                "errors": 1
            }

# Instancia global del procesador
baai_document_processor = BAAIDocumentProcessor() 