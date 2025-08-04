from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BaseSchema(BaseModel):
    """Base schema with common fields."""
    
    class Config:
        from_attributes = True


class ResponseSchema(BaseSchema):
    """Standard response schema."""
    
    success: bool = True
    message: str
    data: Optional[dict] = None


class HealthResponse(BaseSchema):
    """Health check response schema."""
    
    status: str
    message: str
    version: str
    timestamp: datetime = datetime.now()