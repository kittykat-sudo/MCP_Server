import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
from dotenv import load_dotenv
import json
from email_sender import send_email
from resume_parser import parse_resume_file, load_resume_context

# Load environment variables
load_dotenv()

app = FastAPI(
    title="MCP Server - CV Chat & Email",
    description="AI-powered chat about your CV with email notification capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Global variable to store resume context
resume_context = ""

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

# Function definitions for OpenAI function calling
email_function = {
    "name": "send_email",
    "description": "Send an email to a recipient",
    "parameters": {
        "type": "object",
        "properties": {
            "recipient": {
                "type": "string",
                "description": "Email address of the recipient"
            },
            "subject": {
                "type": "string",
                "description": "Email subject line"
            },
            "body": {
                "type": "string",
                "description": "Email body content"
            }
        },
        "required": ["recipient", "subject", "body"]
    }
}

@app.get("/")
async def root():
    return {"message": "MCP Server - CV Chat & Email API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "resume_loaded": bool(resume_context)}

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
        # System prompt with resume context
        system_prompt = f"""You are an AI assistant that helps people discuss their CV/resume. 
        You have access to the following resume information:
        
        {resume_context}
        
        You can also send emails when requested. Use the send_email function when the user asks you to send an email.
        Be helpful, professional, and knowledgeable about career-related topics.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": chat_request.message}
        ]
        
        # Make OpenAI API call with function calling
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            functions=[email_function],
            function_call="auto",
            temperature=0.7,
            max_tokens=1000
        )
        
        message = response.choices[0].message
        
        # Check if function call was made
        function_call_result = None
        if message.function_call:
            function_name = message.function_call.name
            function_args = json.loads(message.function_call.arguments)
            
            if function_name == "send_email":
                try:
                    email_result = send_email(
                        function_args["recipient"],
                        function_args["subject"],
                        function_args["body"]
                    )
                    function_call_result = {
                        "function": "send_email",
                        "result": email_result,
                        "args": function_args
                    }
                except Exception as e:
                    function_call_result = {
                        "function": "send_email",
                        "result": f"Error sending email: {str(e)}",
                        "args": function_args
                    }
        
        return ChatResponse(
            response=message.content or "Function called successfully",
            conversation_id=chat_request.conversation_id or "default",
            function_call=function_call_result
        )
        
    except Exception as e:
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
