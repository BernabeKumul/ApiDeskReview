#!/bin/bash

echo "🚀 Starting FastAPI Backend..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.py first."
    echo "   python setup.py"
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
d. Creating default .env file..."if [ ! -f ".env" ]; then
    echo "⚠️  .env file not foun
    cat > .env << EOF
APP_NAME=FastAPI Backend
DEBUG=True
HOST=127.0.0.1
PORT=8000
SECRET_KEY=your-super-secret-key-here
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=fastapi_db
OPENAI_API_KEY=your-openai-api-key-here
EOF
    echo "✅ Default .env file created. Please update it with your actual values."
fi

# Start the application
echo "🚀 Starting FastAPI application..."
echo "📍 Server will be available at: http://127.0.0.1:8000"
echo "📚 API Documentation: http://127.0.0.1:8000/docs"
echo
echo "Press Ctrl+C to stop the server"
echo

python run.py