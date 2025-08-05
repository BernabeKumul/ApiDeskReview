from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class AIDocumentModel(BaseModel):
    """
    Modelo para documentos de IA almacenados en MongoDB.
    """
    id: Optional[str] = Field(alias="_id", default=None)
    document_id: int = Field(alias="DocumentId")
    file_name: str = Field(alias="FileName")
    document_type: str = Field(alias="DocumentType")
    content: str = Field(alias="Content")
    total_reading: int = Field(alias="TotalReading")
    created_at: datetime = Field(alias="CreatedAt")
    updated_at: datetime = Field(alias="UpdatedAt")
    inactive: bool = Field(alias="Inactive", default=False)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

    @classmethod
    def from_mongo(cls, data: dict):
        """Convierte datos de MongoDB al modelo Pydantic."""
        if data is None:
            return None
        
        # Convierte ObjectId a string si existe
        if "_id" in data and isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
        
        return cls(**data)

    def to_mongo(self) -> dict:
        """Convierte el modelo a formato MongoDB."""
        data = self.dict(by_alias=True, exclude_unset=True)
        
        # Remueve el id si es None para permitir auto-generación
        if data.get("_id") is None:
            data.pop("_id", None)
        
        return data


class AIDocumentFilterModel(BaseModel):
    """
    Modelo para filtros de búsqueda de documentos de IA.
    """
    document_id: Optional[int] = Field(alias="DocumentId", default=None)
    file_name: Optional[str] = Field(alias="FileName", default=None)
    document_type: Optional[str] = Field(alias="DocumentType", default=None)
    inactive: Optional[bool] = Field(alias="Inactive", default=None)
    
    class Config:
        populate_by_name = True

    def to_mongo_filter(self) -> dict:
        """Convierte los filtros a formato MongoDB."""
        filters = {}
        
        if self.document_id is not None:
            filters["DocumentId"] = self.document_id
        
        if self.file_name is not None:
            # Búsqueda exacta o con regex para coincidencia parcial
            filters["FileName"] = self.file_name
        
        if self.document_type is not None:
            filters["DocumentType"] = self.document_type
        
        if self.inactive is not None:
            filters["Inactive"] = self.inactive
        
        return filters


class AIDocumentCreateModel(BaseModel):
    """
    Modelo para crear nuevos documentos de IA.
    """
    document_id: int = Field(alias="DocumentId")
    file_name: str = Field(alias="FileName")
    document_type: str = Field(alias="DocumentType")
    content: str = Field(alias="Content")
    total_reading: int = Field(alias="TotalReading", default=0)
    inactive: bool = Field(alias="Inactive", default=False)

    class Config:
        populate_by_name = True

    def to_mongo(self) -> dict:
        """Convierte el modelo a formato MongoDB para inserción."""
        data = self.dict(by_alias=True)
        now = datetime.utcnow()
        data["CreatedAt"] = now
        data["UpdatedAt"] = now
        return data


class AIDocumentUpdateModel(BaseModel):
    """
    Modelo para actualizar documentos de IA existentes.
    """
    file_name: Optional[str] = Field(alias="FileName", default=None)
    document_type: Optional[str] = Field(alias="DocumentType", default=None)
    content: Optional[str] = Field(alias="Content", default=None)
    total_reading: Optional[int] = Field(alias="TotalReading", default=None)
    inactive: Optional[bool] = Field(alias="Inactive", default=None)

    class Config:
        populate_by_name = True

    def to_mongo_update(self) -> dict:
        """Convierte el modelo a formato MongoDB para actualización."""
        data = self.dict(by_alias=True, exclude_unset=True, exclude_none=True)
        
        if data:  # Solo agregar UpdatedAt si hay datos para actualizar
            data["UpdatedAt"] = datetime.utcnow()
        
        return {"$set": data} if data else {}