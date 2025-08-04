"""
Tests for configuration module.
"""
import pytest
from app.core.config import Settings


def test_settings_creation():
    """Test that settings can be created with default values."""
    settings = Settings()
    assert settings.app_name == "FastAPI Backend"
    assert settings.app_version == "1.0.0"
    assert settings.debug is True
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000


def test_settings_with_custom_values():
    """Test that settings can be overridden."""
    settings = Settings(
        app_name="Custom App",
        debug=False,
        port=9000
    )
    assert settings.app_name == "Custom App"
    assert settings.debug is False
    assert settings.port == 9000


def test_mongodb_settings():
    """Test MongoDB configuration settings."""
    settings = Settings()
    assert settings.mongodb_url == "mongodb://localhost:27017"
    assert settings.mongodb_database == "fastapi_db"


def test_qdrant_settings():
    """Test Qdrant configuration settings."""
    settings = Settings()
    assert settings.qdrant_host == "localhost"
    assert settings.qdrant_port == 6333
    assert settings.qdrant_collection_name == "documents"


def test_openai_settings():
    """Test OpenAI configuration settings."""
    settings = Settings()
    assert settings.openai_model == "gpt-3.5-turbo"
    assert settings.openai_max_tokens == 1000