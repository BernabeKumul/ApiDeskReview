"""
Setup script for FastAPI Backend project.
Facilitates environment setup and dependency installation.
Compatible with Python 3.13+
"""
import subprocess
import sys
import os


def run_command(command: str) -> bool:
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing: {command}")
        print(f"Error: {e.stderr}")
        return False


def create_virtual_environment():
    """Create a virtual environment."""
    print("🐍 Creating virtual environment...")
    return run_command(f"{sys.executable} -m venv venv")


def install_dependencies():
    """Install project dependencies."""
    print("📦 Installing dependencies...")
    
    # Determine the correct python executable path
    if os.name == 'nt':  # Windows
        python_path = "venv\\Scripts\\python"
        pip_path = "venv\\Scripts\\pip"
    else:  # Linux/Mac
        python_path = "venv/bin/python"
        pip_path = "venv/bin/pip"
    
    # Upgrade pip first
    success = run_command(f"{python_path} -m pip install --upgrade pip")
    if not success:
        return False
    
    # Install requirements
    return run_command(f"{pip_path} install -r requirements.txt")


def create_env_file():
    """Create .env file if it doesn't exist."""
    if not os.path.exists('.env'):
        print("📄 Creating .env file...")
        env_content = """# Application Configuration
APP_NAME=FastAPI Backend
APP_VERSION=1.0.0
DEBUG=True
HOST=127.0.0.1
PORT=8000

# Security
SECRET_KEY=your-super-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=fastapi_db

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=documents

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
ALLOWED_METHODS=["GET", "POST", "PUT", "DELETE"]
ALLOWED_HEADERS=["*"]"""
        
        try:
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ .env file created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("✅ .env file already exists")
        return True


def main():
    """Main setup function."""
    print("🚀 Setting up FastAPI Backend project...\n")
    
    steps = [
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Creating environment file", create_env_file),
    ]
    
    all_success = True
    for step_name, step_function in steps:
        print(f"\n{step_name}...")
        success = step_function()
        if not success:
            all_success = False
            print(f"❌ Failed: {step_name}")
        else:
            print(f"✅ Completed: {step_name}")
    
    print("\n" + "="*50)
    if all_success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Activate virtual environment:")
        if os.name == 'nt':  # Windows
            print("   venv\\Scripts\\activate")
        else:  # Linux/Mac
            print("   source venv/bin/activate")
        print("2. Update .env file with your actual API keys")
        print("3. Run the application:")
        print("   python run.py")
        print("4. Visit http://127.0.0.1:8000/docs for API documentation")
    else:
        print("❌ Setup completed with errors. Please check the output above.")
    print("="*50)


if __name__ == "__main__":
    main()