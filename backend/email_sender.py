import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to_email: str, subject: str, body: str) -> dict:
    """
    Send email using SendGrid
    """
    try:
        # Get SendGrid API key from environment
        api_key = os.getenv('SENDGRID_API_KEY')
        from_email = os.getenv('FROM_EMAIL', 'ytream.RX4@gmail.com')
        
        if not api_key:
            raise Exception("SENDGRID_API_KEY not found in environment variables")
        
        # Create the email message
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=body
        )
        
        # Send the email
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        return {
            "status": "success",
            "status_code": response.status_code,
            "message": "Email sent successfully"
        }
        
    except Exception as e:
        print(f"Email sending error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to send email: {str(e)}"
        }