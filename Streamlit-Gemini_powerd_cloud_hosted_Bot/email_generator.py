import base64
from email.mime.text import MIMEText

def send_email(service, to_email, subject, body):
    # Create MIME message
    #message = MIMEText(body)
    if not isinstance(body, str):
        body = "".join(body)

    message = MIMEText(body)
    message["to"] = to_email
    message["from"] = "me"
    message["subject"] = subject

    # Encode message to base64
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Send email via Gmail API
    return service.users().messages().send(
        userId="me",
        body={"raw": raw_message}
    ).execute()
