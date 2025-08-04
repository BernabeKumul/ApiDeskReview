@echo off
echo 🚀 Starting FastAPI Backend...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Virtual environment not found. Please run setup.py first.
    echo    python setup.py
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🐍 Activating virtual environment...
call venv\Scripts\activate

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating default .env file...
    copy NUL .env
    echo APP_NAME=FastAPI Backend >> .env
    echo DEBUG=True >> .env
    echo HOST=127.0.0.1 >> .env
    echo PORT=8000 >> .env
    echo SECRET_KEY=your-super-secret-key-here >> .env
    echo MONGODB_URL=mongodb://localhost:27017 >> .env
    echo MONGODB_DATABASE=fastapi_db >> .env
    echo OPENAI_API_KEY=your-openai-api-key-here >> .env
    echo.
    echo ✅ Default .env file created. Please update it with your actual values.
)

REM Start the application
echo 🚀 Starting FastAPI application...
echo 📍 Server will be available at: http://127.0.0.1:8000
echo 📚 API Documentation: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python run.py

pause