@echo off
echo 🚀 Setting up MCP Server...

rem Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    exit /b 1
)

echo 📦 Setting up Python backend...
cd backend

rem Create virtual environment
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
)

rem Activate virtual environment
call venv\Scripts\activate.bat

rem Install Python dependencies
pip install -r requirements.txt
echo ✅ Python dependencies installed

rem Copy environment file
if not exist ".env" (
    copy .env.example .env
    echo 📝 Environment file created. Please update with your API keys.
)

cd ..

rem Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js not found. Frontend setup will be skipped.
    goto :skip_frontend
)

echo 🎨 Setting up Next.js frontend...
cd frontend\next-app

npm install
echo ✅ Node.js dependencies installed

if not exist ".env.local" (
    copy .env.local.example .env.local
    echo 📝 Frontend environment file created
)

cd ..\..

:skip_frontend

echo.
echo 🎉 Setup complete!
echo.
echo 📋 Next steps:
echo 1. Update backend\.env with your API keys:
echo    - OPENAI_API_KEY (get from https://platform.openai.com/api-keys)
echo    - SENDGRID_API_KEY (get from https://app.sendgrid.com/settings/api_keys)
echo    - FROM_EMAIL (your verified sender email)
echo.
echo 2. Start the backend server:
echo    cd backend ^&^& venv\Scripts\activate ^&^& uvicorn main:app --reload
echo.
echo 3. (Optional) Start the frontend:
echo    cd frontend\next-app ^&^& npm run dev
echo.
echo 4. Visit http://localhost:8000/docs for API documentation
echo.
echo 📖 See DEVELOPMENT.md for detailed instructions

pause
