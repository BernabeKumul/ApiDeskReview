#!/usr/bin/env python3
"""
Python 3.13 Compatibility Checker for FastAPI Backend Project.
Verifies that all dependencies are compatible with Python 3.13+.
"""
import sys
import subprocess
import pkg_resources
from typing import List, Dict, Tuple


def check_python_version() -> Tuple[bool, str]:
    """Check if current Python version is 3.13+."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 13:
        return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"❌ Python {version.major}.{version.minor}.{version.micro} (Requires Python 3.13+)"


def check_dependencies() -> Dict[str, bool]:
    """Check if key dependencies can be imported."""
    dependencies = {
        'fastapi': 'FastAPI framework',
        'uvicorn': 'ASGI server',
        'pydantic': 'Data validation',
        'pydantic_settings': 'Settings management',
        'pymongo': 'MongoDB driver',
        'motor': 'Async MongoDB driver',
        'qdrant_client': 'Qdrant vector database',
        'openai': 'OpenAI API client',
        'pytest': 'Testing framework',
        'httpx': 'HTTP client'
    }
    
    results = {}
    
    for dep, description in dependencies.items():
        try:
            __import__(dep)
            results[f"{dep} ({description})"] = True
        except ImportError:
            results[f"{dep} ({description})"] = False
    
    return results


def check_installed_packages() -> List[str]:
    """Get list of installed packages."""
    try:
        installed_packages = [d.project_name for d in pkg_resources.working_set]
        return installed_packages
    except Exception as e:
        print(f"Warning: Could not check installed packages: {e}")
        return []


def run_compatibility_tests() -> bool:
    """Run basic compatibility tests."""
    print("🧪 Running Python 3.13 compatibility tests...\n")
    
    # Check Python version
    python_ok, python_msg = check_python_version()
    print(f"Python Version: {python_msg}")
    
    if not python_ok:
        print("\n❌ Python 3.13+ is required for this project.")
        return False
    
    print("\n📦 Checking key dependencies:")
    dependencies = check_dependencies()
    
    all_deps_ok = True
    for dep, status in dependencies.items():
        if status:
            print(f"✅ {dep}")
        else:
            print(f"❌ {dep} - Not installed or incompatible")
            all_deps_ok = False
    
    # Test basic FastAPI functionality
    print("\n🚀 Testing FastAPI basic functionality:")
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        # Create a simple test app
        test_app = FastAPI()
        
        @test_app.get("/test")
        def test_endpoint():
            return {"status": "ok", "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"}
        
        client = TestClient(test_app)
        response = client.get("/test")
        
        if response.status_code == 200:
            print("✅ FastAPI basic functionality works")
        else:
            print(f"❌ FastAPI test failed with status {response.status_code}")
            all_deps_ok = False
            
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        all_deps_ok = False
    
    # Test Pydantic
    print("\n📋 Testing Pydantic:")
    try:
        from pydantic import BaseModel
        
        class TestModel(BaseModel):
            name: str
            value: int
        
        test_data = TestModel(name="test", value=42)
        if test_data.name == "test" and test_data.value == 42:
            print("✅ Pydantic models work correctly")
        else:
            print("❌ Pydantic test failed")
            all_deps_ok = False
            
    except Exception as e:
        print(f"❌ Pydantic test failed: {e}")
        all_deps_ok = False
    
    return all_deps_ok


def main():
    """Main compatibility check function."""
    print("="*60)
    print("🐍 Python 3.13 Compatibility Check for FastAPI Backend")
    print("="*60)
    
    success = run_compatibility_tests()
    
    print("\n" + "="*60)
    if success:
        print("🎉 All compatibility checks passed!")
        print("✅ Your FastAPI project is ready for Python 3.13!")
        print("\nNext steps:")
        print("1. Run: python run.py")
        print("2. Visit: http://127.0.0.1:8000/docs")
    else:
        print("❌ Some compatibility issues found.")
        print("💡 Try running: pip install -r requirements.txt")
        print("   Or: python setup.py")
    print("="*60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())