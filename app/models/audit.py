"""
Modelos para audit - Clases de datos para auditorías.
Modelos que representan los datos de auditorías y documentos relacionados.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class AuditDocument:
    """
    Modelo de datos para un documento de auditoría.
    Representa los datos retornados por el stored procedure.
    """
    
    document_id: int
    activity_category_id: Optional[int] = None
    type_name: Optional[str] = None
    author_title: Optional[str] = None
    document_url: Optional[str] = None
    file_name: Optional[str] = None
    compliance_grid_id: Optional[int] = None
    relation_question_id: Optional[int] = None
    short_name: Optional[str] = None
    used_reference: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AuditDocument':
        """
        Crea una instancia de AuditDocument desde un diccionario.
        
        Args:
            data: Diccionario con los datos del documento
            
        Returns:
            Instancia de AuditDocument
        """
        return cls(
            document_id=data.get('DocumentID'),
            activity_category_id=data.get('ActivityCategoryId'),
            type_name=data.get('TypeName'),
            author_title=data.get('AuthorTitle'),
            document_url=data.get('DocumentURL'),
            file_name=data.get('FileName'),
            compliance_grid_id=data.get('ComplianceGridID'),
            relation_question_id=data.get('RelationQuestionID'),
            short_name=data.get('ShortName'),
            used_reference=data.get('UsedReference')
        )
    
    def to_dict(self) -> dict:
        """
        Convierte la instancia a diccionario.
        
        Returns:
            Diccionario con los datos del documento
        """
        return {
            'DocumentID': self.document_id,
            'ActivityCategoryId': self.activity_category_id,
            'TypeName': self.type_name,
            'AuthorTitle': self.author_title,
            'DocumentURL': self.document_url,
            'FileName': self.file_name,
            'ComplianceGridID': self.compliance_grid_id,
            'RelationQuestionID': self.relation_question_id,
            'ShortName': self.short_name,
            'UsedReference': self.used_reference
        }


@dataclass
class AuditDocumentFilter:
    """
    Modelo para filtros de búsqueda de documentos de auditoría.
    """
    
    audit_header_id: int
    question_id: Optional[int] = 0
    
    def to_dict(self) -> dict:
        """
        Convierte los filtros a diccionario para uso en stored procedures.
        
        Returns:
            Diccionario con los parámetros de filtro
        """
        return {
            'Auditheaderid': self.audit_header_id,
            'QuestionID': self.question_id or 0
        }


@dataclass
class AuditHeader:
    """
    Modelo de datos para un header de auditoría.
    Representa los datos retornados por el stored procedure GetDemoAuditAzzuleAI_Alias_jbk.
    """
    
    audit_header_id: int
    org_id: int
    org_name: Optional[str] = None
    oper_id: Optional[int] = None
    oper_name: Optional[str] = None
    products: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AuditHeader':
        """
        Crea una instancia de AuditHeader desde un diccionario.
        
        Args:
            data: Diccionario con los datos del header
            
        Returns:
            Instancia de AuditHeader
        """
        return cls(
            audit_header_id=data.get('AuditHeaderID'),
            org_id=data.get('OrgID'),
            org_name=data.get('OrgName'),
            oper_id=data.get('OperID'),
            oper_name=data.get('OperName'),
            products=data.get('Products')
        )
    
    def to_dict(self) -> dict:
        """
        Convierte la instancia a diccionario.
        
        Returns:
            Diccionario con los datos del header
        """
        return {
            'AuditHeaderID': self.audit_header_id,
            'OrgID': self.org_id,
            'OrgName': self.org_name,
            'OperID': self.oper_id,
            'OperName': self.oper_name,
            'Products': self.products
        }


@dataclass
class StoredProcedureParameters:
    """
    Modelo para parámetros de stored procedures de auditoría.
    """
    
    audit_header_id: int
    question_id: int = 0
    
    @property
    def procedure_name(self) -> str:
        """Retorna el nombre del stored procedure para documentos de auditoría."""
        return "AuditHeader_Get_AvailableActivityDocumentsAzzuleAI"
    
    def get_parameters(self) -> dict:
        """
        Obtiene los parámetros formateados para el stored procedure.
        
        Returns:
            Diccionario con los parámetros del stored procedure
        """
        return {
            'Auditheaderid': self.audit_header_id,
            'QuestionID': self.question_id
        }