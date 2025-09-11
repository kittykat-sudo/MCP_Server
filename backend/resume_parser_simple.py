"""
Simplified resume parser without PyMuPDF dependency
"""
import json
from typing import Dict, Any

def parse_resume_file(file_path: str) -> Dict[str, Any]:
    """
    Simplified resume parser - returns sample data for now
    In production, you could integrate with cloud-based parsing services
    """
    return get_sample_resume_data()

def get_sample_resume_data() -> Dict[str, Any]:
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

def load_resume_context(parsed_data: Dict[str, Any]) -> str:
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