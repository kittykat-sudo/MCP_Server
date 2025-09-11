import os
import sendgrid
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

def send_email(recipient: str, subject: str, body: str) -> dict:
    """
    Send an email using SendGrid API
    
    Args:
        recipient (str): Email address of the recipient
        subject (str): Email subject
        body (str): Email body content
        
    Returns:
        dict: Result of the email sending operation
    """
    try:
        # Get environment variables
        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("FROM_EMAIL")
        
        if not sendgrid_api_key:
            raise Exception("SENDGRID_API_KEY not found in environment variables")
        
        if not from_email:
            raise Exception("FROM_EMAIL not found in environment variables")
        
        # Create SendGrid client
        sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
        
        # Create email message
        message = Mail(
            from_email=from_email,
            to_emails=recipient,
            subject=subject,
            html_content=body
        )
        
        # Send email
        response = sg.send(message)
        
        return {
            "status": "success",
            "status_code": response.status_code,
            "message": "Email sent successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def send_smtp_email(recipient: str, subject: str, body: str, 
                   smtp_server: str = "smtp.gmail.com", 
                   smtp_port: int = 587) -> dict:
    """
    Alternative email sending using SMTP (fallback option)
    
    Args:
        recipient (str): Email address of the recipient
        subject (str): Email subject
        body (str): Email body content
        smtp_server (str): SMTP server address
        smtp_port (int): SMTP server port
        
    Returns:
        dict: Result of the email sending operation
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        # Get environment variables
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")
        
        if not email_user or not email_password:
            raise Exception("EMAIL_USER and EMAIL_PASSWORD must be set for SMTP")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = recipient
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to server and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        
        text = msg.as_string()
        server.sendmail(email_user, recipient, text)
        server.quit()
        
        return {
            "status": "success",
            "message": "Email sent successfully via SMTP"
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e)
        }
