#!/bin/bash
# Setup script for MCP Server

echo "🚀 Setting up MCP Server..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed  
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. Frontend setup will be skipped."
    SKIP_FRONTEND=true
fi

echo "📦 Setting up Python backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# Copy environment file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Environment file created. Please update with your API keys."
fi

cd ..

# Setup frontend if Node.js is available
if [ "$SKIP_FRONTEND" != true ]; then
    echo "🎨 Setting up Next.js frontend..."
    cd frontend/next-app
    
    npm install
    echo "✅ Node.js dependencies installed"
    
    if [ ! -f ".env.local" ]; then
        cp .env.local.example .env.local
        echo "📝 Frontend environment file created"
    fi
    
    cd ../..
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update backend/.env with your API keys:"
echo "   - OPENAI_API_KEY (get from https://platform.openai.com/api-keys)"
echo "   - SENDGRID_API_KEY (get from https://app.sendgrid.com/settings/api_keys)"
echo "   - FROM_EMAIL (your verified sender email)"
echo ""
echo "2. Start the backend server:"
echo "   cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo ""
if [ "$SKIP_FRONTEND" != true ]; then
    echo "3. (Optional) Start the frontend:"
    echo "   cd frontend/next-app && npm run dev"
    echo ""
fi
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "📖 See DEVELOPMENT.md for detailed instructions"
