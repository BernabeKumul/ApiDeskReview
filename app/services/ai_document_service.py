"""
Servicio específico para documentos de IA.
Maneja todas las operaciones relacionadas con la colección AIDocuments.
"""
from typing import List, Optional, Dict, Any
import logging
from pymongo import ASCENDING, DESCENDING

from app.services.database import database_service, GenericMongoRepository
from app.models.ai_document import (
    AIDocumentModel, 
    AIDocumentFilterModel, 
    AIDocumentCreateModel, 
    AIDocumentUpdateModel
)

# Configurar logging
logger = logging.getLogger(__name__)

class AIDocumentService:
    """
    Servicio para operaciones con documentos de IA.
    Utiliza el repositorio genérico de MongoDB para operaciones CRUD.
    """
    
    def __init__(self):
        self.collection_name = "AIDocuments"
        self._repository: Optional[GenericMongoRepository] = None
    
    @property
    def repository(self) -> GenericMongoRepository:
        """Obtiene el repositorio de la colección AIDocuments."""
        if self._repository is None:
            self._repository = database_service.get_repository(self.collection_name)
        return self._repository
    
    async def get_document_by_filters(
        self, 
        file_name: Optional[str] = None, 
        document_id: Optional[int] = None
    ) -> Optional[AIDocumentModel]:
        """
        Recupera un documento por FileName y/o DocumentId.
        
        Args:
            file_name: Nombre del archivo a buscar
            document_id: ID del documento a buscar
            
        Returns:
            Documento encontrado o None
        """
        try:
            # Crear filtros
            filters = {}
            
            if file_name is not None:
                filters["FileName"] = file_name
                
            if document_id is not None:
                filters["DocumentId"] = document_id
            
            # Si no hay filtros, retornar None
            if not filters:
                logger.warning("No se proporcionaron filtros para la búsqueda")
                return None
            
            logger.info(f"Buscando documento con filtros: {filters}")
            
            # Buscar documento
            result = await self.repository.find_one(filters)
            
            if result:
                logger.info(f"Documento encontrado con ID: {result.get('_id')}")
                return AIDocumentModel.from_mongo(result)
            else:
                logger.info("No se encontró ningún documento con los filtros especificados")
                return None
                
        except Exception as e:
            logger.error(f"Error al buscar documento por filtros: {e}")
            raise
    
    async def get_document_by_id(self, document_id: str) -> Optional[AIDocumentModel]:
        """
        Recupera un documento por su ID de MongoDB.
        
        Args:
            document_id: ID del documento en MongoDB
            
        Returns:
            Documento encontrado o None
        """
        try:
            logger.info(f"Buscando documento por ID: {document_id}")
            
            result = await self.repository.find_one_by_id(document_id)
            
            if result:
                logger.info(f"Documento encontrado: {result.get('FileName')}")
                return AIDocumentModel.from_mongo(result)
            else:
                logger.info(f"No se encontró documento con ID: {document_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error al buscar documento por ID: {e}")
            raise
    
    async def get_all_documents(
        self, 
        filters: Optional[AIDocumentFilterModel] = None,
        skip: int = 0,
        limit: Optional[int] = None,
        sort_by: str = "CreatedAt",
        sort_order: int = DESCENDING
    ) -> List[AIDocumentModel]:
        """
        Recupera todos los documentos con filtros opcionales.
        
        Args:
            filters: Filtros de búsqueda opcional
            skip: Número de documentos a saltar para paginación
            limit: Límite de documentos a retornar
            sort_by: Campo por el cual ordenar (por defecto CreatedAt)
            sort_order: Orden de clasificación (ASCENDING o DESCENDING)
            
        Returns:
            Lista de documentos encontrados
        """
        try:
            # Crear filtros de búsqueda
            search_filters = {}
            if filters:
                search_filters = filters.to_mongo_filter()
            
            logger.info(f"Buscando documentos con filtros: {search_filters}")
            
            # Configurar ordenamiento
            sort_criteria = [(sort_by, sort_order)]
            
            # Buscar documentos
            results = await self.repository.find_many(
                filter_dict=search_filters,
                skip=skip,
                limit=limit,
                sort=sort_criteria
            )
            
            # Convertir a modelos Pydantic
            documents = [AIDocumentModel.from_mongo(result) for result in results]
            
            logger.info(f"Se encontraron {len(documents)} documentos")
            return documents
            
        except Exception as e:
            logger.error(f"Error al obtener todos los documentos: {e}")
            raise
    
    async def get_documents_count(
        self, 
        filters: Optional[AIDocumentFilterModel] = None
    ) -> int:
        """
        Cuenta el número total de documentos que coinciden con los filtros.
        
        Args:
            filters: Filtros de búsqueda opcional
            
        Returns:
            Número total de documentos
        """
        try:
            # Crear filtros de búsqueda
            search_filters = {}
            if filters:
                search_filters = filters.to_mongo_filter()
            
            count = await self.repository.count_documents(search_filters)
            logger.info(f"Total de documentos encontrados: {count}")
            
            return count
            
        except Exception as e:
            logger.error(f"Error al contar documentos: {e}")
            raise
    
    async def create_document(self, document_data: AIDocumentCreateModel) -> str:
        """
        Crea un nuevo documento.
        
        Args:
            document_data: Datos del documento a crear
            
        Returns:
            ID del documento creado
        """
        try:
            # Verificar si ya existe un documento con el mismo DocumentId
            existing = await self.get_document_by_filters(
                document_id=document_data.document_id
            )
            
            if existing:
                raise ValueError(f"Ya existe un documento con DocumentId: {document_data.document_id}")
            
            # Convertir a formato MongoDB
            mongo_data = document_data.to_mongo()
            
            logger.info(f"Creando nuevo documento: {document_data.file_name}")
            
            # Insertar documento
            document_id = await self.repository.insert_one(mongo_data)
            
            logger.info(f"Documento creado exitosamente con ID: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Error al crear documento: {e}")
            raise
    
    async def update_document(
        self, 
        document_id: str, 
        update_data: AIDocumentUpdateModel
    ) -> bool:
        """
        Actualiza un documento existente.
        
        Args:
            document_id: ID del documento a actualizar
            update_data: Datos de actualización
            
        Returns:
            True si se actualizó, False si no se encontró
        """
        try:
            # Verificar que el documento existe
            existing = await self.get_document_by_id(document_id)
            if not existing:
                logger.warning(f"No se encontró documento con ID: {document_id}")
                return False
            
            # Convertir a formato MongoDB
            mongo_update = update_data.to_mongo_update()
            
            if not mongo_update.get("$set"):
                logger.warning("No hay datos para actualizar")
                return False
            
            logger.info(f"Actualizando documento con ID: {document_id}")
            
            from bson import ObjectId
            
            # Actualizar documento
            success = await self.repository.update_one(
                {"_id": ObjectId(document_id)}, 
                mongo_update
            )
            
            if success:
                logger.info(f"Documento actualizado exitosamente: {document_id}")
            else:
                logger.warning(f"No se pudo actualizar el documento: {document_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error al actualizar documento: {e}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Elimina un documento.
        
        Args:
            document_id: ID del documento a eliminar
            
        Returns:
            True si se eliminó, False si no se encontró
        """
        try:
            from bson import ObjectId
            
            logger.info(f"Eliminando documento con ID: {document_id}")
            
            # Eliminar documento
            success = await self.repository.delete_one({"_id": ObjectId(document_id)})
            
            if success:
                logger.info(f"Documento eliminado exitosamente: {document_id}")
            else:
                logger.warning(f"No se encontró documento para eliminar: {document_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error al eliminar documento: {e}")
            raise
    
    async def soft_delete_document(self, document_id: str) -> bool:
        """
        Marca un documento como inactivo (eliminación lógica).
        
        Args:
            document_id: ID del documento a marcar como inactivo
            
        Returns:
            True si se actualizó, False si no se encontró
        """
        try:
            update_data = AIDocumentUpdateModel(inactive=True)
            return await self.update_document(document_id, update_data)
            
        except Exception as e:
            logger.error(f"Error al realizar eliminación lógica: {e}")
            raise
    
    async def search_documents_by_content(
        self, 
        search_term: str, 
        skip: int = 0, 
        limit: Optional[int] = None
    ) -> List[AIDocumentModel]:
        """
        Busca documentos por contenido utilizando expresiones regulares.
        
        Args:
            search_term: Término de búsqueda
            skip: Número de documentos a saltar
            limit: Límite de documentos a retornar
            
        Returns:
            Lista de documentos que contienen el término de búsqueda
        """
        try:
            import re
            
            # Crear filtro de búsqueda con regex (insensible a mayúsculas)
            search_filter = {
                "Content": {"$regex": re.escape(search_term), "$options": "i"}
            }
            
            logger.info(f"Buscando documentos que contengan: '{search_term}'")
            
            # Buscar documentos
            results = await self.repository.find_many(
                filter_dict=search_filter,
                skip=skip,
                limit=limit,
                sort=[("CreatedAt", DESCENDING)]
            )
            
            # Convertir a modelos Pydantic
            documents = [AIDocumentModel.from_mongo(result) for result in results]
            
            logger.info(f"Se encontraron {len(documents)} documentos con el término '{search_term}'")
            return documents
            
        except Exception as e:
            logger.error(f"Error al buscar documentos por contenido: {e}")
            raise


# Instancia global del servicio
ai_document_service = AIDocumentService()