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
    qdrant_api_key: str = ""  # Sin API key para desarrollo local
    qdrant_collection_name: str = "AIDocumentsTest"  # Colección específica para testing
    qdrant_https: bool = False  # Usar HTTP para desarrollo local
    
    # OpenAI Configuration
    openai_api_key: str = "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"  # Placeholder key to be updated
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.3
    
    # SQL Server Configuration
    sqlserver_server: str = "10.10.50.30"  # Actualizar con el servidor real
    sqlserver_database: str = "PrimusGFS"  # Actualizar con la base de datos real
    sqlserver_username: str = "ApplicationUser_"  # Actualizar con el usuario real
    sqlserver_password: str = "Dev23InAzz$"  # Actualizar con la contraseña real
    sqlserver_driver: str = "ODBC Driver 17 for SQL Server"
    sqlserver_trusted_connection: bool = False
    
    # CORS Configuration
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()