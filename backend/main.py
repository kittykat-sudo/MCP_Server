import os
import json
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Simplified AI Provider imports - only Gemini for now
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from backend.email_sender_huge import send_email

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
        "https://mcp-server-virid.vercel.app",  # Your Vercel domain
        "https://*.vercel.app",  # All Vercel domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI clients
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
gemini_model = None

# Initialize Gemini (primary free option)
if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Global variable for resume content
resume_context = ""

def get_sample_resume_data():
    """Sample resume data for demonstration"""
    return {
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1 (555) 123-4567",
            "location": "San Francisco, CA"
        },
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "duration": "2021-2024",
                "description": "Led development of scalable web applications using Python and React"
            },
            {
                "title": "Software Engineer",
                "company": "StartupXYZ",
                "duration": "2019-2021",
                "description": "Developed REST APIs and microservices"
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Technology",
                "graduation_year": "2019"
            }
        ],
        "skills": [
            "Python", "JavaScript", "React", "FastAPI", "PostgreSQL", 
            "Docker", "AWS", "Git", "REST APIs", "Microservices"
        ],
        "certifications": [
            "AWS Certified Developer",
            "Google Cloud Professional"
        ]
    }

def load_resume_context(parsed_data):
    """Convert parsed resume data to context string"""
    context_parts = []
    
    # Personal information
    if "personal_info" in parsed_data:
        personal = parsed_data["personal_info"]
        context_parts.append(f"**Personal Information:**")
        context_parts.append(f"Name: {personal.get('name', 'N/A')}")
        context_parts.append(f"Email: {personal.get('email', 'N/A')}")
        context_parts.append(f"Phone: {personal.get('phone', 'N/A')}")
        context_parts.append(f"Location: {personal.get('location', 'N/A')}")
        context_parts.append("")
    
    # Experience
    if "experience" in parsed_data and parsed_data["experience"]:
        context_parts.append("**Work Experience:**")
        for exp in parsed_data["experience"]:
            context_parts.append(f"• {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')} ({exp.get('duration', 'N/A')})")
            context_parts.append(f"  {exp.get('description', 'N/A')}")
        context_parts.append("")
    
    # Education
    if "education" in parsed_data and parsed_data["education"]:
        context_parts.append("**Education:**")
        for edu in parsed_data["education"]:
            context_parts.append(f"• {edu.get('degree', 'N/A')} from {edu.get('institution', 'N/A')} ({edu.get('graduation_year', 'N/A')})")
        context_parts.append("")
    
    # Skills
    if "skills" in parsed_data and parsed_data["skills"]:
        context_parts.append("**Technical Skills:**")
        context_parts.append(f"• {', '.join(parsed_data['skills'])}")
        context_parts.append("")
    
    # Certifications
    if "certifications" in parsed_data and parsed_data["certifications"]:
        context_parts.append("**Certifications:**")
        for cert in parsed_data["certifications"]:
            context_parts.append(f"• {cert}")
        context_parts.append("")
    
    return "\n".join(context_parts)

class AIProvider:
    """Unified AI provider interface"""
    
    @staticmethod
    def generate_response(message: str, system_prompt: str) -> str:
        """Generate response using available AI provider"""
        
        if AI_PROVIDER == "gemini" and gemini_model:
            return AIProvider._generate_gemini_response(message, system_prompt)
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
    def _generate_fallback_response(message: str) -> str:
        """Generate basic response when no AI provider is available"""
        return """🤖 **AI Provider Configuration Needed**
        
To get AI-powered responses, please configure an AI provider in your environment variables:
1. **For Gemini (FREE)**: Get key from https://makersuite.google.com/app/apikey

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
        "platform": "Render",
        "version": "minimal"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "resume_loaded": bool(resume_context),
        "ai_provider": AI_PROVIDER,
        "ai_configured": bool(AI_PROVIDER == "gemini" and gemini_model)
    }

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse a resume file - simplified version"""
    global resume_context
    
    try:
        # For now, use sample data
        # In production, integrate with cloud parsing services
        parsed_data = get_sample_resume_data()
        resume_context = load_resume_context(parsed_data)
        
        return {
            "message": "Resume processed successfully (using sample data for demo)",
            "filename": file.filename,
            "parsed_data": parsed_data,
            "note": "Full PDF parsing will be added in future updates"
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
        
        system_prompt = f"""You are an AI assistant that helps people discuss their CV/resume. 
        You have access to the following resume information:
        
        {resume_context}
        
        You can also help with career advice and answer questions about the resume.
        Be helpful, professional, and knowledgeable about career-related topics.
        """
        
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