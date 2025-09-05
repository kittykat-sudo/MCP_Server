# MCP Server - CV Chat & Email Notifications

A Model Context Protocol (MCP) server that provides AI-powered chat about your CV/resume and email notification capabilities, with an optional Next.js frontend playground.

## Features

- 🤖 **AI Chat**: Chat with GPT-4 about your CV/resume
- 📧 **Email Notifications**: Send email notifications via SendGrid/SMTP
- 🎮 **Frontend Playground**: Optional Next.js frontend interface
- 📄 **Resume Parsing**: Parse and structure resume data
- 🔌 **Function Calling**: Natural language commands for email sending

## Architecture

```
mcp-server/
├── backend/           # FastAPI server
│   ├── main.py       # Main FastAPI application
│   ├── resume_parser.py
│   ├── email_sender.py
│   └── requirements.txt
├── frontend/         # Next.js playground (optional)
│   └── next-app/
└── README.md
```

## Quick Start

### Backend Setup

1. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

2. Set environment variables:

```bash
OPENAI_API_KEY=your_openai_api_key
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=your_email@example.com
```

3. Run the server:

```bash
uvicorn main:app --reload
```

### Frontend Setup (Optional)

1. Install dependencies:

```bash
cd frontend/next-app
npm install
```

2. Run the development server:

```bash
npm run dev
```

## API Endpoints

- `POST /chat` - Chat with AI about your CV
- `POST /send-email` - Send email notifications
- `POST /upload-resume` - Upload and parse resume
- `GET /health` - Health check

## Environment Variables

| Variable           | Description                      | Required |
| ------------------ | -------------------------------- | -------- |
| `OPENAI_API_KEY`   | OpenAI API key for GPT-4         | Yes      |
| `SENDGRID_API_KEY` | SendGrid API key for emails      | Yes      |
| `FROM_EMAIL`       | Email address for sending emails | Yes      |

## Deployment

- **Backend**: Deploy to Render, Fly.io, or Heroku
- **Frontend**: Deploy to Vercel or Netlify

## Technology Stack

- **Backend**: FastAPI (Python)
- **AI Model**: OpenAI GPT-4o
- **Email**: SendGrid
- **Frontend**: Next.js (React)
- **Parsing**: PyMuPDF, python-docx

## License

MIT License
"# MCP_Server" 
