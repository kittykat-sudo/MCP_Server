# MCP Server Development Guide

## Setup Instructions

### Prerequisites

- Python 3.8+ installed
- Node.js 18+ installed
- Git installed

### Backend Setup

1. **Navigate to backend directory:**

   ```bash
   cd backend
   ```

2. **Create virtual environment (recommended):**

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   - Copy `.env.example` to `.env`
   - Fill in your API keys:
     - Get OpenAI API key from: https://platform.openai.com/api-keys
     - Get SendGrid API key from: https://app.sendgrid.com/settings/api_keys

5. **Run the FastAPI server:**

   ```bash
   uvicorn main:app --reload
   ```

   Server will be available at: http://localhost:8000

### Frontend Setup (Optional)

1. **Navigate to frontend directory:**

   ```bash
   cd frontend/next-app
   ```

2. **Install Node.js dependencies:**

   ```bash
   npm install
   ```

3. **Set up environment variables:**

   - Copy `.env.local.example` to `.env.local`
   - Update `NEXT_PUBLIC_BACKEND_URL` if needed

4. **Run the development server:**

   ```bash
   npm run dev
   ```

   Frontend will be available at: http://localhost:3000

## PowerShell Execution Policy (Windows)

If you encounter PowerShell execution policy errors, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## API Endpoints

### Backend API (FastAPI)

- `GET /` - Health check
- `POST /chat` - Chat with AI about CV
- `POST /send-email` - Send email notification
- `POST /upload-resume` - Upload and parse resume
- `GET /docs` - API documentation (Swagger UI)

### Testing the API

1. **Upload a resume:**

   ```bash
   curl -X POST "http://localhost:8000/upload-resume" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@your_resume.pdf"
   ```

2. **Chat about your CV:**

   ```bash
   curl -X POST "http://localhost:8000/chat" \
        -H "Content-Type: application/json" \
        -d '{"message": "What are my key skills?"}'
   ```

3. **Send an email:**
   ```bash
   curl -X POST "http://localhost:8000/send-email" \
        -H "Content-Type: application/json" \
        -d '{
          "recipient": "test@example.com",
          "subject": "Test Email",
          "body": "This is a test email from MCP Server"
        }'
   ```

## Debugging

### Check if services are running:

- Backend: Visit http://localhost:8000/health
- Frontend: Visit http://localhost:3000

### Common Issues:

1. **Import errors for Python packages:**

   - Make sure virtual environment is activated
   - Reinstall requirements: `pip install -r requirements.txt`

2. **API key errors:**

   - Verify `.env` file exists and has correct keys
   - Check OpenAI quota/billing status

3. **Email sending fails:**

   - Verify SendGrid API key is valid
   - Check FROM_EMAIL is a verified sender

4. **Frontend can't connect to backend:**
   - Ensure backend is running on port 8000
   - Check CORS settings in main.py

## Development Workflow

1. Start the backend server first
2. Upload a resume to load CV context
3. Test chat functionality
4. Test email functionality
5. Use the frontend for a complete experience

## Deployment

### Backend (Render/Heroku/Fly.io):

- Set environment variables on the platform
- Deploy from the `backend/` directory
- Use `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel/Netlify):

- Deploy from the `frontend/next-app/` directory
- Set `NEXT_PUBLIC_BACKEND_URL` to your backend URL

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI       │    │   OpenAI        │
│   Frontend      │───▶│   Backend       │───▶│   GPT-4         │
│   (Optional)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   SendGrid      │
                       │   Email API     │
                       └─────────────────┘
```

## Features

- ✅ **AI Chat**: GPT-4 integration for CV discussions
- ✅ **Email Notifications**: SendGrid integration
- ✅ **Resume Parsing**: PDF/DOCX support
- ✅ **Function Calling**: Natural language email commands
- ✅ **Frontend UI**: Optional web interface
- ✅ **CORS Enabled**: Ready for deployment
