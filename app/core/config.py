from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Application Configuration
    app_name: str = "FastAPI Backend"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Security
    secret_key: str = "your-super-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://ApplicationUser_:Mong0dev%2424@10.10.50.76:27017/"  # Actualizar con credenciales reales
    mongodb_database: str = "AzzuleAI"
    
    # Qdrant Configuration
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str = "your-qdrant-api-key"
    qdrant_collection_name: str = "documents"
    
    # OpenAI Configuration
    openai_api_key: str = "your-openai-api-key-here"
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 1000
    
    # CORS Configuration
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()