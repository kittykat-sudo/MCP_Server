import fitz  # PyMuPDF
import docx
import json
from typing import Dict, Any
import os

def parse_pdf_resume(file_path: str) -> str:
    """Extract text from PDF resume"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")

def parse_docx_resume(file_path: str) -> str:
    """Extract text from DOCX resume"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error parsing DOCX: {str(e)}")

def parse_resume_file(file_path: str) -> Dict[str, Any]:
    """
    Parse resume file and extract structured information
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        Dict[str, Any]: Structured resume data
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Extract raw text based on file type
    if file_extension == '.pdf':
        raw_text = parse_pdf_resume(file_path)
    elif file_extension == '.docx':
        raw_text = parse_docx_resume(file_path)
    else:
        raise Exception(f"Unsupported file type: {file_extension}")
    
    # Basic text processing to structure the data
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    # Simple extraction logic (can be enhanced with NLP)
    resume_data = {
        "raw_text": raw_text,
        "extracted_info": {
            "name": extract_name(lines),
            "email": extract_email(raw_text),
            "phone": extract_phone(raw_text),
            "sections": identify_sections(lines),
            "skills": extract_skills(lines),
            "experience": extract_experience(lines),
            "education": extract_education(lines)
        },
        "file_info": {
            "filename": os.path.basename(file_path),
            "file_type": file_extension,
            "total_lines": len(lines)
        }
    }
    
    return resume_data

def extract_name(lines: list) -> str:
    """Extract name (usually the first line or two)"""
    if lines:
        # Simple heuristic: name is usually in the first few lines
        potential_names = []
        for i, line in enumerate(lines[:3]):
            # Skip lines that look like contact info
            if not any(keyword in line.lower() for keyword in ['@', 'phone', 'tel', 'email', 'linkedin']):
                if len(line.split()) <= 4 and len(line) > 2:  # Names usually 1-4 words
                    potential_names.append(line)
        
        return potential_names[0] if potential_names else lines[0]
    return "Unknown"

def extract_email(text: str) -> str:
    """Extract email address using regex"""
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Not found"

def extract_phone(text: str) -> str:
    """Extract phone number using regex"""
    import re
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890 or 123.456.7890
        r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',    # (123) 456-7890
        r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'  # +1-123-456-7890
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            return phones[0]
    return "Not found"

def identify_sections(lines: list) -> Dict[str, int]:
    """Identify major resume sections"""
    sections = {}
    section_keywords = {
        'experience': ['experience', 'work history', 'employment', 'professional experience'],
        'education': ['education', 'academic', 'degree', 'university', 'college'],
        'skills': ['skills', 'technical skills', 'competencies', 'technologies'],
        'projects': ['projects', 'personal projects', 'key projects'],
        'certifications': ['certifications', 'certificates', 'licenses'],
        'summary': ['summary', 'objective', 'profile', 'about']
    }
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        for section, keywords in section_keywords.items():
            if any(keyword in line_lower for keyword in keywords):
                sections[section] = i
                break
    
    return sections

def extract_skills(lines: list) -> list:
    """Extract skills from resume"""
    skills = []
    skill_indicators = ['skills', 'technologies', 'programming', 'software', 'tools']
    
    for i, line in enumerate(lines):
        if any(indicator in line.lower() for indicator in skill_indicators):
            # Look at the next few lines for actual skills
            for j in range(i + 1, min(i + 5, len(lines))):
                skill_line = lines[j].strip()
                if skill_line and not any(indicator in skill_line.lower() for indicator in skill_indicators):
                    # Split by common delimiters
                    potential_skills = []
                    for delimiter in [',', '•', '|', ';']:
                        if delimiter in skill_line:
                            potential_skills.extend([s.strip() for s in skill_line.split(delimiter)])
                    
                    if potential_skills:
                        skills.extend(potential_skills)
                    elif len(skill_line.split()) <= 3:  # Single skill
                        skills.append(skill_line)
    
    return list(set(skills))  # Remove duplicates

def extract_experience(lines: list) -> list:
    """Extract work experience"""
    experience = []
    exp_indicators = ['experience', 'work', 'employment', 'professional']
    
    for i, line in enumerate(lines):
        if any(indicator in line.lower() for indicator in exp_indicators):
            # Look for job entries in subsequent lines
            for j in range(i + 1, min(i + 10, len(lines))):
                exp_line = lines[j].strip()
                if exp_line and len(exp_line.split()) > 2:
                    # Common job title patterns
                    if any(title in exp_line.lower() for title in ['engineer', 'developer', 'manager', 'analyst', 'coordinator', 'specialist']):
                        experience.append(exp_line)
    
    return experience

def extract_education(lines: list) -> list:
    """Extract education information"""
    education = []
    edu_indicators = ['education', 'degree', 'university', 'college', 'bachelor', 'master', 'phd']
    
    for i, line in enumerate(lines):
        if any(indicator in line.lower() for indicator in edu_indicators):
            # Look for education entries
            for j in range(i, min(i + 5, len(lines))):
                edu_line = lines[j].strip()
                if edu_line and any(degree in edu_line.lower() for degree in ['bachelor', 'master', 'phd', 'bs', 'ms', 'ba', 'ma']):
                    education.append(edu_line)
    
    return education

def load_resume_context(resume_data: Dict[str, Any]) -> str:
    """
    Convert parsed resume data into a context string for AI
    
    Args:
        resume_data (Dict[str, Any]): Parsed resume data
        
    Returns:
        str: Formatted context string
    """
    extracted = resume_data.get('extracted_info', {})
    
    context = f"""
RESUME INFORMATION:

Name: {extracted.get('name', 'Unknown')}
Email: {extracted.get('email', 'Not found')}
Phone: {extracted.get('phone', 'Not found')}

SKILLS:
{', '.join(extracted.get('skills', []))}

EXPERIENCE:
{chr(10).join(extracted.get('experience', []))}

EDUCATION:
{chr(10).join(extracted.get('education', []))}

FULL RESUME TEXT:
{resume_data.get('raw_text', '')}
"""
    
    return context.strip()

# Sample resume data for testing (when no file is uploaded)
def get_sample_resume_data() -> Dict[str, Any]:
    """Return sample resume data for testing"""
    return {
        "raw_text": """John Doe
Software Engineer
Email: john.doe@email.com
Phone: (555) 123-4567

EXPERIENCE
Senior Software Engineer at Tech Corp (2020-Present)
- Developed web applications using Python and React
- Led a team of 5 developers

Software Engineer at StartupCo (2018-2020)
- Built REST APIs using FastAPI
- Implemented CI/CD pipelines

EDUCATION
Bachelor of Science in Computer Science
University of Technology (2014-2018)

SKILLS
Python, JavaScript, React, FastAPI, Docker, AWS, Git""",
        "extracted_info": {
            "name": "John Doe",
            "email": "john.doe@email.com", 
            "phone": "(555) 123-4567",
            "skills": ["Python", "JavaScript", "React", "FastAPI", "Docker", "AWS", "Git"],
            "experience": [
                "Senior Software Engineer at Tech Corp (2020-Present)",
                "Software Engineer at StartupCo (2018-2020)"
            ],
            "education": [
                "Bachelor of Science in Computer Science - University of Technology (2014-2018)"
            ]
        }
    }

# Load sample data by default for testing
if __name__ == "__main__":
    sample_data = get_sample_resume_data()
    context = load_resume_context(sample_data)
    print("Sample Resume Context:")
    print(context)
