import os
import json
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# AI Provider imports
from openai import OpenAI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from backend.email_sender_huge import send_email
from resume_parser import parse_resume_file, load_resume_context, get_sample_resume_data

# Load environment variables
load_dotenv()

app = FastAPI(
    title="MCP Server - CV Chat & Email API",
    description="AI-powered chat about your CV with email notification capabilities",
    version="1.0.0"
)

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://mcp-server-virid.vercel.app",  # Your correct Vercel domain
        "https://*.vercel.app",  # All Vercel domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI clients
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
openai_client = None
gemini_model = None

# Initialize OpenAI (backup)
if os.getenv("OPENAI_API_KEY"):
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Gemini (primary free option)
if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Global variable for resume content
resume_context = ""

class AIProvider:
    """Unified AI provider interface"""
    
    @staticmethod
    def generate_response(message: str, system_prompt: str) -> str:
        """Generate response using available AI provider"""
        
        if AI_PROVIDER == "gemini" and gemini_model:
            return AIProvider._generate_gemini_response(message, system_prompt)
        elif AI_PROVIDER == "openai" and openai_client:
            return AIProvider._generate_openai_response(message, system_prompt)
        else:
            return AIProvider._generate_fallback_response(message)
    
    @staticmethod
    def _generate_gemini_response(message: str, system_prompt: str) -> str:
        """Generate response using Google Gemini"""
        try:
            full_prompt = f"{system_prompt}\n\nUser: {message}\nAssistant:"
            
            response = gemini_model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                )
            )
            
            return response.text
            
        except Exception as e:
            print(f"Gemini error: {e}")
            return f"Sorry, I'm experiencing technical difficulties with Gemini API. Error: {str(e)}"
    
    @staticmethod
    def _generate_openai_response(message: str, system_prompt: str) -> str:
        """Generate response using OpenAI (fallback)"""
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return f"Sorry, I'm experiencing technical difficulties with OpenAI API. Error: {str(e)}"
    
    @staticmethod
    def _generate_fallback_response(message: str) -> str:
        """Generate basic response when no AI provider is available"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['experience', 'work', 'job']):
            return "I can see your work experience in the uploaded resume. For detailed AI analysis, please configure an AI provider (Gemini or OpenAI) in your environment variables."
        
        elif any(word in message_lower for word in ['skills', 'technical']):
            return "Your technical skills are listed in your resume. For AI-powered insights, please set up an AI provider."
        
        elif any(word in message_lower for word in ['education', 'degree']):
            return "Your education information is available in your resume. AI analysis requires an API key."
        
        else:
            return """🤖 **AI Provider Configuration Needed**
            
To get AI-powered responses, please:
1. **For Gemini (FREE)**: Get key from https://makersuite.google.com/app/apikey
2. **For OpenAI**: Add billing at https://platform.openai.com/account/billing
3. Add your API key to the .env file

Currently showing basic resume information only."""

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class EmailRequest(BaseModel):
    recipient: str
    subject: str
    body: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    function_call: Optional[dict] = None

@app.get("/")
async def root():
    return {
        "message": "MCP Server - CV Chat & Email API", 
        "status": "running",
        "ai_provider": AI_PROVIDER,
        "gemini_available": GEMINI_AVAILABLE and bool(os.getenv("GEMINI_API_KEY")),
        "openai_available": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "resume_loaded": bool(resume_context),
        "ai_provider": AI_PROVIDER,
        "ai_configured": bool(
            (AI_PROVIDER == "gemini" and gemini_model) or 
            (AI_PROVIDER == "openai" and openai_client)
        )
    }

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse a resume file (PDF, DOCX)"""
    global resume_context
    
    try:
        # Save uploaded file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse the resume
        parsed_data = parse_resume_file(file_path)
        resume_context = load_resume_context(parsed_data)
        
        # Clean up temp file
        os.remove(file_path)
        
        return {
            "message": "Resume uploaded and parsed successfully",
            "filename": file.filename,
            "parsed_data": parsed_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_cv(chat_request: ChatMessage):
    """Chat with AI about your CV"""
    try:
        global resume_context
        if not resume_context:
            sample_data = get_sample_resume_data()
            resume_context = load_resume_context(sample_data)
        
        # System prompt with resume context
        system_prompt = f"""You are an AI assistant that helps people discuss their CV/resume. 
        You have access to the following resume information:
        
        {resume_context}
        
        You can also help with career advice and answer questions about the resume.
        Be helpful, professional, and knowledgeable about career-related topics.
        
        If the user asks about sending emails, let them know they can use the separate email endpoint.
        """
        
        # Generate response using configured AI provider
        ai_response = AIProvider.generate_response(chat_request.message, system_prompt)
        
        return ChatResponse(
            response=ai_response,
            conversation_id=chat_request.conversation_id or "default",
            function_call=None
        )
        
    except Exception as e:
        import traceback
        print(f"Chat error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

@app.post("/send-email")
async def send_email_endpoint(email_request: EmailRequest):
    """Send an email notification"""
    try:
        result = send_email(
            email_request.recipient,
            email_request.subject,
            email_request.body
        )
        return {"message": "Email sent successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)