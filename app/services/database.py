"""
Database service - MongoDB connection and operations.
Servicio genérico para operaciones con MongoDB usando Motor.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from typing import Dict, List, Optional, Any, TypeVar, Generic
from pymongo.errors import ConnectionFailure, PyMongoError
from bson import ObjectId
from bson.errors import InvalidId
import logging
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

T = TypeVar('T')


class GenericMongoRepository(Generic[T]):
    """
    Repositorio genérico para operaciones CRUD con MongoDB.
    Puede ser usado con cualquier colección.
    """
    
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str):
        self.database = database
        self.collection: AsyncIOMotorCollection = database[collection_name]
        self.collection_name = collection_name
    
    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Busca un documento por filtros.
        
        Args:
            filter_dict: Diccionario con los filtros de búsqueda
            
        Returns:
            Documento encontrado o None
        """
        try:
            result = await self.collection.find_one(filter_dict)
            return result
        except PyMongoError as e:
            logger.error(f"Error al buscar documento en {self.collection_name}: {e}")
            raise
    
    async def find_one_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca un documento por su ID.
        
        Args:
            document_id: ID del documento (string)
            
        Returns:
            Documento encontrado o None
        """
        try:
            # Convertir string a ObjectId
            object_id = ObjectId(document_id)
            result = await self.collection.find_one({"_id": object_id})
            return result
        except InvalidId:
            logger.error(f"ID inválido: {document_id}")
            return None
        except PyMongoError as e:
            logger.error(f"Error al buscar documento por ID en {self.collection_name}: {e}")
            raise
    
    async def find_many(
        self, 
        filter_dict: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: Optional[int] = None,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca múltiples documentos con filtros opcionales.
        
        Args:
            filter_dict: Diccionario con los filtros de búsqueda
            skip: Número de documentos a saltar
            limit: Límite de documentos a retornar
            sort: Lista de tuplas (campo, dirección) para ordenamiento
            
        Returns:
            Lista de documentos encontrados
        """
        try:
            if filter_dict is None:
                filter_dict = {}
            
            cursor = self.collection.find(filter_dict)
            
            if skip > 0:
                cursor = cursor.skip(skip)
            
            if limit is not None:
                cursor = cursor.limit(limit)
            
            if sort:
                cursor = cursor.sort(sort)
            
            results = await cursor.to_list(length=None)
            return results
        except PyMongoError as e:
            logger.error(f"Error al buscar documentos en {self.collection_name}: {e}")
            raise
    
    async def count_documents(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta documentos que coinciden con los filtros.
        
        Args:
            filter_dict: Diccionario con los filtros de búsqueda
            
        Returns:
            Número de documentos que coinciden
        """
        try:
            if filter_dict is None:
                filter_dict = {}
            
            count = await self.collection.count_documents(filter_dict)
            return count
        except PyMongoError as e:
            logger.error(f"Error al contar documentos en {self.collection_name}: {e}")
            raise
    
    async def insert_one(self, document: Dict[str, Any]) -> str:
        """
        Inserta un nuevo documento.
        
        Args:
            document: Documento a insertar
            
        Returns:
            ID del documento insertado
        """
        try:
            result = await self.collection.insert_one(document)
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Error al insertar documento en {self.collection_name}: {e}")
            raise
    
    async def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Inserta múltiples documentos.
        
        Args:
            documents: Lista de documentos a insertar
            
        Returns:
            Lista de IDs de los documentos insertados
        """
        try:
            result = await self.collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        except PyMongoError as e:
            logger.error(f"Error al insertar documentos en {self.collection_name}: {e}")
            raise
    
    async def update_one(
        self, 
        filter_dict: Dict[str, Any], 
        update_dict: Dict[str, Any]
    ) -> bool:
        """
        Actualiza un documento.
        
        Args:
            filter_dict: Filtros para encontrar el documento
            update_dict: Datos de actualización
            
        Returns:
            True si se actualizó un documento, False si no se encontró
        """
        try:
            result = await self.collection.update_one(filter_dict, update_dict)
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error al actualizar documento en {self.collection_name}: {e}")
            raise
    
    async def update_many(
        self, 
        filter_dict: Dict[str, Any], 
        update_dict: Dict[str, Any]
    ) -> int:
        """
        Actualiza múltiples documentos.
        
        Args:
            filter_dict: Filtros para encontrar los documentos
            update_dict: Datos de actualización
            
        Returns:
            Número de documentos actualizados
        """
        try:
            result = await self.collection.update_many(filter_dict, update_dict)
            return result.modified_count
        except PyMongoError as e:
            logger.error(f"Error al actualizar documentos en {self.collection_name}: {e}")
            raise
    
    async def delete_one(self, filter_dict: Dict[str, Any]) -> bool:
        """
        Elimina un documento.
        
        Args:
            filter_dict: Filtros para encontrar el documento
            
        Returns:
            True si se eliminó un documento, False si no se encontró
        """
        try:
            result = await self.collection.delete_one(filter_dict)
            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"Error al eliminar documento en {self.collection_name}: {e}")
            raise
    
    async def delete_many(self, filter_dict: Dict[str, Any]) -> int:
        """
        Elimina múltiples documentos.
        
        Args:
            filter_dict: Filtros para encontrar los documentos
            
        Returns:
            Número de documentos eliminados
        """
        try:
            result = await self.collection.delete_many(filter_dict)
            return result.deleted_count
        except PyMongoError as e:
            logger.error(f"Error al eliminar documentos en {self.collection_name}: {e}")
            raise


class DatabaseService:
    """
    Servicio principal de base de datos MongoDB.
    Maneja la conexión y proporciona acceso a repositorios genéricos.
    """
    
    def __init__(self):
        self.mongodb_url = settings.mongodb_url
        self.database_name = settings.mongodb_database
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._repositories: Dict[str, GenericMongoRepository] = {}
    
    async def connect(self):
        """Conecta a la base de datos MongoDB."""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            # Verificar conexión
            await self.client.admin.command('ping')
            self.database = self.client[self.database_name]
            logger.info(f"📊 Conectado exitosamente a MongoDB: {self.mongodb_url}")
            print(f"📊 MongoDB conectado a: {self.mongodb_url}")
        except ConnectionFailure as e:
            logger.error(f"Error al conectar con MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al conectar con MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Desconecta de la base de datos MongoDB."""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self._repositories.clear()
            logger.info("📊 Desconectado de MongoDB")
            print("📊 MongoDB desconectado")
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        """
        Obtiene la instancia de la base de datos.
        
        Returns:
            Instancia de la base de datos MongoDB
        """
        if self.database is None:
            raise RuntimeError("Base de datos no conectada. Ejecute connect() primero.")
        return self.database
    
    def get_repository(self, collection_name: str) -> GenericMongoRepository:
        """
        Obtiene un repositorio genérico para una colección específica.
        
        Args:
            collection_name: Nombre de la colección
            
        Returns:
            Repositorio genérico para la colección
        """
        if self.database is None:
            raise RuntimeError("Base de datos no conectada. Ejecute connect() primero.")
        
        if collection_name not in self._repositories:
            self._repositories[collection_name] = GenericMongoRepository(
                self.database, collection_name
            )
        
        return self._repositories[collection_name]
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud de la conexión a MongoDB.
        
        Returns:
            Diccionario con el estado de la conexión
        """
        try:
            if not self.client:
                return {"status": "disconnected", "message": "No hay conexión activa"}
            
            # Ping a la base de datos
            await self.client.admin.command('ping')
            
            # Obtener información del servidor
            server_info = await self.client.admin.command("buildInfo")
            
            return {
                "status": "connected",
                "message": "Conexión exitosa",
                "database": self.database_name,
                "server_version": server_info.get("version", "unknown")
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error de conexión: {str(e)}"
            }


# Instancia global del servicio de base de datos
database_service = DatabaseService()