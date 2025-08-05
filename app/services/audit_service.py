"""
Servicio específico para auditorías.
Maneja todas las operaciones relacionadas con auditorías y documentos asociados.
"""
from typing import List, Optional
import logging
from app.services.sqlserver_service import sqlserver_service
from app.models.audit import AuditDocument, StoredProcedureParameters

# Configurar logging
logger = logging.getLogger(__name__)


class AuditService:
    """
    Servicio específico para operaciones de auditoría.
    Proporciona métodos de alto nivel para trabajar con auditorías.
    """
    
    def __init__(self):
        self.sqlserver_service = sqlserver_service
    
    async def get_audit_documents(
        self, 
        audit_header_id: int, 
        question_id: Optional[int] = 0
    ) -> List[AuditDocument]:
        """
        Obtiene los documentos asociados a una auditoría específica.
        
        Args:
            audit_header_id: ID del header de auditoría
            question_id: ID de la pregunta (opcional, por defecto 0)
            
        Returns:
            Lista de documentos de auditoría
            
        Raises:
            ValueError: Si el audit_header_id no es válido
            RuntimeError: Si hay problemas con la conexión a la base de datos
        """
        try:
            # Validar parámetros
            if audit_header_id <= 0:
                raise ValueError("audit_header_id debe ser mayor a 0")
            
            # Crear parámetros para el stored procedure
            sp_params = StoredProcedureParameters(
                audit_header_id=audit_header_id,
                question_id=question_id or 0
            )
            
            logger.info(
                f"Ejecutando SP {sp_params.procedure_name} con parámetros: "
                f"Auditheaderid={audit_header_id}, QuestionID={question_id or 0}"
            )
            
            # Ejecutar stored procedure
            results = await self.sqlserver_service.execute_stored_procedure(
                procedure_name=sp_params.procedure_name,
                parameters=sp_params.get_parameters()
            )
            
            # Convertir resultados a modelos de datos
            documents = []
            for row in results:
                try:
                    document = AuditDocument.from_dict(row)
                    documents.append(document)
                except Exception as e:
                    logger.warning(f"Error al procesar fila: {row}. Error: {e}")
                    continue
            
            logger.info(f"Se encontraron {len(documents)} documentos para audit_header_id={audit_header_id}")
            return documents
            
        except ValueError:
            # Re-lanzar errores de validación
            raise
        except Exception as e:
            logger.error(f"Error al obtener documentos de auditoría: {e}")
            raise RuntimeError(f"Error interno al obtener documentos de auditoría: {str(e)}")
    
    async def get_audit_document_by_id(
        self, 
        audit_header_id: int, 
        document_id: int,
        question_id: Optional[int] = 0
    ) -> Optional[AuditDocument]:
        """
        Obtiene un documento específico de una auditoría.
        
        Args:
            audit_header_id: ID del header de auditoría
            document_id: ID del documento específico
            question_id: ID de la pregunta (opcional, por defecto 0)
            
        Returns:
            Documento de auditoría encontrado o None si no existe
        """
        try:
            # Obtener todos los documentos de la auditoría
            documents = await self.get_audit_documents(audit_header_id, question_id)
            
            # Buscar el documento específico
            for document in documents:
                if document.document_id == document_id:
                    return document
            
            return None
            
        except Exception as e:
            logger.error(f"Error al obtener documento específico: {e}")
            raise
    
    async def count_audit_documents(
        self, 
        audit_header_id: int, 
        question_id: Optional[int] = 0
    ) -> int:
        """
        Cuenta el número de documentos asociados a una auditoría.
        
        Args:
            audit_header_id: ID del header de auditoría
            question_id: ID de la pregunta (opcional, por defecto 0)
            
        Returns:
            Número de documentos encontrados
        """
        try:
            documents = await self.get_audit_documents(audit_header_id, question_id)
            return len(documents)
        except Exception as e:
            logger.error(f"Error al contar documentos de auditoría: {e}")
            raise
    
    async def validate_audit_header_exists(self, audit_header_id: int) -> bool:
        """
        Valida si existe un header de auditoría específico.
        
        Args:
            audit_header_id: ID del header de auditoría
            
        Returns:
            True si existe, False si no existe
        """
        try:
            # Intentar obtener documentos para validar si el header existe
            documents = await self.get_audit_documents(audit_header_id, 0)
            # Si no lanza excepción, el header probablemente existe
            # (aunque puede no tener documentos asociados)
            return True
        except ValueError:
            # Error de validación de parámetros
            return False
        except Exception:
            # Cualquier otro error, asumimos que no existe o hay problemas
            return False
    
    async def get_audit_documents_by_category(
        self, 
        audit_header_id: int, 
        activity_category_id: int,
        question_id: Optional[int] = 0
    ) -> List[AuditDocument]:
        """
        Obtiene documentos de auditoría filtrados por categoría de actividad.
        
        Args:
            audit_header_id: ID del header de auditoría
            activity_category_id: ID de la categoría de actividad
            question_id: ID de la pregunta (opcional, por defecto 0)
            
        Returns:
            Lista de documentos filtrados por categoría
        """
        try:
            # Obtener todos los documentos
            all_documents = await self.get_audit_documents(audit_header_id, question_id)
            
            # Filtrar por categoría de actividad
            filtered_documents = [
                doc for doc in all_documents 
                if doc.activity_category_id == activity_category_id
            ]
            
            logger.info(
                f"Filtrados {len(filtered_documents)} documentos por category_id={activity_category_id}"
            )
            return filtered_documents
            
        except Exception as e:
            logger.error(f"Error al filtrar documentos por categoría: {e}")
            raise
    
    async def get_audit_documents_by_type(
        self, 
        audit_header_id: int, 
        type_name: str,
        question_id: Optional[int] = 0
    ) -> List[AuditDocument]:
        """
        Obtiene documentos de auditoría filtrados por tipo de documento.
        
        Args:
            audit_header_id: ID del header de auditoría
            type_name: Nombre del tipo de documento
            question_id: ID de la pregunta (opcional, por defecto 0)
            
        Returns:
            Lista de documentos filtrados por tipo
        """
        try:
            # Obtener todos los documentos
            all_documents = await self.get_audit_documents(audit_header_id, question_id)
            
            # Filtrar por tipo de documento (case-insensitive)
            filtered_documents = [
                doc for doc in all_documents 
                if doc.type_name and doc.type_name.lower() == type_name.lower()
            ]
            
            logger.info(
                f"Filtrados {len(filtered_documents)} documentos por type_name='{type_name}'"
            )
            return filtered_documents
            
        except Exception as e:
            logger.error(f"Error al filtrar documentos por tipo: {e}")
            raise


# Instancia global del servicio de auditoría
audit_service = AuditService()