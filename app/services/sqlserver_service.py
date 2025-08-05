"""
SQL Server service - Conexión y operaciones genéricas con SQL Server.
Servicio genérico para operaciones con SQL Server usando pyodbc con asyncio.
"""
import pyodbc
import asyncio
from typing import Dict, List, Optional, Any, Union
import logging
from concurrent.futures import ThreadPoolExecutor
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)


class SQLServerService:
    """
    Servicio genérico para operaciones con SQL Server.
    Maneja la conexión y proporciona métodos genéricos para ejecutar queries y stored procedures.
    """
    
    def __init__(self):
        self.connection_string = self._build_connection_string()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._connection_pool = []
        self._max_connections = 10
        self._is_connected = False
    
    def _build_connection_string(self) -> str:
        """
        Construye la cadena de conexión para SQL Server.
        
        Returns:
            Cadena de conexión formateada
        """
        if settings.sqlserver_trusted_connection:
            # Autenticación de Windows
            conn_str = (
                f"DRIVER={{{settings.sqlserver_driver}}};"
                f"SERVER={settings.sqlserver_server};"
                f"DATABASE={settings.sqlserver_database};"
                f"Trusted_Connection=yes;"
            )
        else:
            # Autenticación SQL Server
            conn_str = (
                f"DRIVER={{{settings.sqlserver_driver}}};"
                f"SERVER={settings.sqlserver_server};"
                f"DATABASE={settings.sqlserver_database};"
                f"UID={settings.sqlserver_username};"
                f"PWD={settings.sqlserver_password};"
            )
        
        return conn_str
    
    async def connect(self) -> None:
        """
        Establece la conexión a SQL Server.
        """
        try:
            # Probar la conexión
            await self._test_connection()
            self._is_connected = True
            logger.info(f"🗄️ Conexión SQL Server establecida exitosamente")
            print(f"🗄️ SQL Server conectado a: {settings.sqlserver_server}")
        except Exception as e:
            logger.error(f"Error al conectar con SQL Server: {e}")
            raise
    
    async def disconnect(self) -> None:
        """
        Cierra las conexiones.
        """
        if self._is_connected:
            self.executor.shutdown(wait=True)
            self._connection_pool.clear()
            self._is_connected = False
            logger.info("🗄️ Conexiones SQL Server cerradas")
            print("🗄️ SQL Server desconectado")
    
    def _execute_query_sync(self, query: str, parameters: Optional[Union[List, Dict]] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL de manera síncrona.
        """
        conn = None
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            if parameters:
                if isinstance(parameters, dict):
                    # Convertir dict a lista en el orden correcto
                    cursor.execute(query, list(parameters.values()))
                else:
                    cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            
            # Obtener nombres de columnas
            columns = [column[0] for column in cursor.description] if cursor.description else []
            
            # Obtener todas las filas
            rows = cursor.fetchall()
            
            # Convertir a lista de diccionarios
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return result
            
        finally:
            if conn:
                conn.close()

    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Union[List, Dict]] = None
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL y retorna los resultados.
        
        Args:
            query: Consulta SQL a ejecutar
            parameters: Parámetros para la consulta
            
        Returns:
            Lista de diccionarios con los resultados
        """
        if not self._is_connected:
            raise RuntimeError("Conexión no inicializada. Ejecute connect() primero.")
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._execute_query_sync, 
                query, 
                parameters
            )
            return result
        except Exception as e:
            logger.error(f"Error al ejecutar query: {e}")
            raise
    
    def _execute_stored_procedure_sync(self, procedure_name: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta un stored procedure de manera síncrona.
        """
        conn = None
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Construir la llamada al stored procedure
            if parameters:
                # Crear placeholders para los parámetros
                placeholders = ', '.join(['?' for _ in parameters.values()])
                call = f"EXEC {procedure_name} {placeholders}"
                cursor.execute(call, list(parameters.values()))
            else:
                call = f"EXEC {procedure_name}"
                cursor.execute(call)
            
            # Obtener nombres de columnas
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                
                # Obtener todas las filas
                rows = cursor.fetchall()
                
                # Convertir a lista de diccionarios
                result = []
                for row in rows:
                    result.append(dict(zip(columns, row)))
                
                return result
            else:
                # El stored procedure no retorna resultados
                return []
                
        finally:
            if conn:
                conn.close()

    async def execute_stored_procedure(
        self, 
        procedure_name: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta un stored procedure y retorna los resultados.
        
        Args:
            procedure_name: Nombre del stored procedure
            parameters: Parámetros del stored procedure
            
        Returns:
            Lista de diccionarios con los resultados
        """
        if not self._is_connected:
            raise RuntimeError("Conexión no inicializada. Ejecute connect() primero.")
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._execute_stored_procedure_sync, 
                procedure_name, 
                parameters
            )
            return result
        except Exception as e:
            logger.error(f"Error al ejecutar stored procedure {procedure_name}: {e}")
            raise
    
    def _execute_scalar_sync(self, query: str, parameters: Optional[Union[List, Dict]] = None) -> Any:
        """
        Ejecuta una consulta que retorna un valor único de manera síncrona.
        """
        conn = None
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            if parameters:
                if isinstance(parameters, dict):
                    cursor.execute(query, list(parameters.values()))
                else:
                    cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            
            row = cursor.fetchone()
            return row[0] if row else None
            
        finally:
            if conn:
                conn.close()

    async def execute_scalar(
        self, 
        query: str, 
        parameters: Optional[Union[List, Dict]] = None
    ) -> Any:
        """
        Ejecuta una consulta que retorna un valor único.
        
        Args:
            query: Consulta SQL a ejecutar
            parameters: Parámetros para la consulta
            
        Returns:
            Valor único retornado por la consulta
        """
        if not self._is_connected:
            raise RuntimeError("Conexión no inicializada. Ejecute connect() primero.")
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._execute_scalar_sync, 
                query, 
                parameters
            )
            return result
        except Exception as e:
            logger.error(f"Error al ejecutar query scalar: {e}")
            raise
    
    def _execute_non_query_sync(self, query: str, parameters: Optional[Union[List, Dict]] = None) -> int:
        """
        Ejecuta una consulta que no retorna resultados de manera síncrona.
        """
        conn = None
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            if parameters:
                if isinstance(parameters, dict):
                    cursor.execute(query, list(parameters.values()))
                else:
                    cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            
            rowcount = cursor.rowcount
            conn.commit()
            return rowcount
            
        finally:
            if conn:
                conn.close()

    async def execute_non_query(
        self, 
        query: str, 
        parameters: Optional[Union[List, Dict]] = None
    ) -> int:
        """
        Ejecuta una consulta que no retorna resultados (INSERT, UPDATE, DELETE).
        
        Args:
            query: Consulta SQL a ejecutar
            parameters: Parámetros para la consulta
            
        Returns:
            Número de filas afectadas
        """
        if not self._is_connected:
            raise RuntimeError("Conexión no inicializada. Ejecute connect() primero.")
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                self._execute_non_query_sync, 
                query, 
                parameters
            )
            return result
        except Exception as e:
            logger.error(f"Error al ejecutar non-query: {e}")
            raise
    
    async def _test_connection(self) -> None:
        """
        Prueba la conexión a SQL Server.
        """
        conn = None
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        finally:
            if conn:
                conn.close()

    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud de la conexión a SQL Server.
        
        Returns:
            Diccionario con el estado de la conexión
        """
        try:
            if not self._is_connected:
                return {"status": "disconnected", "message": "No hay conexión activa"}
            
            # Ejecutar una consulta simple para verificar la conexión
            result = await self.execute_scalar("SELECT 1")
            
            if result == 1:
                return {
                    "status": "connected",
                    "message": "Conexión exitosa",
                    "server": settings.sqlserver_server,
                    "database": settings.sqlserver_database
                }
            else:
                return {
                    "status": "error",
                    "message": "Respuesta inesperada del servidor"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error de conexión: {str(e)}"
            }


# Instancia global del servicio SQL Server
sqlserver_service = SQLServerService()