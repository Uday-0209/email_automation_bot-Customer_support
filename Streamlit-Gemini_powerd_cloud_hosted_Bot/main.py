
"""
Simple Gmail Monitor - Poll for unread messages every 15 seconds
Prints new emails when they arrive.
"""
import base64
import time
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import re
from email_generator import send_email
from gemini_llm_response import run_generator
from dotenv import load_dotenv

load_dotenv()

SCOPES_send = ["https://www.googleapis.com/auth/gmail.send"]
SCOPES_read= ['https://www.googleapis.com/auth/gmail.readonly']
POLL_INTERVAL = 15  # seconds
seen_ids = set()  # to avoid processing the same mail again

def get_clean_text(body):
    body = re.sub(r'https?://\S+', '', body)

    # remove HTML tags
    body = re.sub(r'<.*?>', '', body)

    # remove extra spaces
    body = re.sub(r'\s+', ' ', body).strip()

    return body   


def get_email_body(msg):
    payload = msg.get("payload", {})

    # If multiple parts
    parts = payload.get("parts")
    if parts:
        for part in parts:
            mime_type = part.get("mimeType")
            data = part.get("body", {}).get("data")

            if data:
                decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

                if mime_type == "text/plain":
                    return decoded
                if mime_type == "text/html":
                    return decoded

    # Single-part email
    data = payload.get("body", {}).get("data")
    if data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    return "(No body found)"

def process_new_message(service, msg_id):
    msg = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="full"
    ).execute()

    headers = msg.get("payload", {}).get("headers", [])
    sender = subject = "(unknown)"

    for h in headers:
        if h["name"] == "From":
            sender = h["value"]
        if h["name"] == "Subject":
            subject = h["value"]

    raw_body = get_email_body(msg)

    # 1. Check if subject matches technical keywords
    if not subject_matches(subject):
        #print(f"Skipping (Not tech-related): {subject}")
        return

    # 2. Skip purchase/spam/marketing mails
    if is_purchase_or_spam(subject, sender, raw_body):
        #print(f"Skipping (Purchase/Spam): {subject}")
        return

    # 3. Clean body text
    body = get_clean_text(raw_body)

    # print("\n========== TECH ALERT EMAIL ==========")
    # print("From:", sender)
    # print("Subject:", subject)
    # print("Body:\n", body)
    # print("=======================================\n")
    return [sender, subject, body]

def error_code_getter(body):
    pattern = r'[A-Za-z]+\s*[:\- ]\s*(\d+)'
    match = re.search(pattern, body)
    if match:
        return match.group(1)
    # for t in body:
    #     match = re.search(pattern, t)
    #     if match:
    #         return match.group(1)

KEYWORDS = [
    "support",
    "tech support",
    "error",
    "not working",
    "assistance"
]

def subject_matches(subject):
    subject_lower = subject.lower()
    return any(keyword in subject_lower for keyword in KEYWORDS)

PURCHASE_SPAM_KEYWORDS = [
    "order",
    "purchased",
    "purchase",
    "invoice",
    "receipt",
    "payment",
    "subscription",
    "discount",
    "offer",
    "save",
    "sale",
    "deal",
    "promo",
    "amazon",
    "flipkart",
    "myntra",
    "ajio",
    "ebay",
    "shop",
    "shipment",
    "delivered",
    "delivery",
]

def is_purchase_or_spam(subject, sender, body):
    text = (subject + " " + sender + " " + body).lower()
    return any(word in text for word in PURCHASE_SPAM_KEYWORDS)

# --------------------------
# FUNCTION: authenticate
# --------------------------
def authenticate():
    creds_read = None
    creds_send = None
    if os.path.exists('token_read.json'):
        creds_read = Credentials.from_authorized_user_file('token_read.json', SCOPES_read)

    if not creds_read or not creds_read.valid:
        if creds_read and creds_read.expired and creds_read.refresh_token:
            creds_read.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES_read
            )
            creds_read = flow.run_local_server(port=0)

        with open("token_read.json", "w") as f:
            f.write(creds_read.to_json())
            
            
    if os.path.exists('token_send.json'):
        creds_send = Credentials.from_authorized_user_file('token_send.json', SCOPES_send)

    if not creds_send or not creds_send.valid:
        if creds_send and creds_send.expired and creds_send.refresh_token:
            creds_send.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES_send
            )
            creds_send = flow.run_local_server(port=1)

        with open("token_send.json", "w") as f:
            f.write(creds_send.to_json())

    return [creds_read, creds_send]


# --------------------------
# MAIN MONITOR LOOP
# --------------------------
def main():
    creds = authenticate()
    service_read = build("gmail", "v1", credentials=creds[0])
    service_send = build("gmail", "v1", credentials=creds[1])

    print("Monitoring Gmail... (checking every 15 seconds)")
    print("Press CTRL + C to stop.\n")

    while True:
        # list unread emails
        results = service_read.users().messages().list(
            userId="me",
            q="is:unread",
            maxResults=2
        ).execute()

        messages = results.get("messages", [])

        for m in messages:
            msg_id = m["id"]
            
            output = None
            if msg_id not in seen_ids:
                seen_ids.add(msg_id)
                print('\nNew message getting processed.......')
                output = process_new_message(service_read, msg_id)
                if output is not None:
                    print('\nExtracting sender, subject and body details')
                    Sender = output[0]
                    Subject = output[1]
                    Body = output[2]
                    print('\nExtracting the error code from email body')
                    k = error_code_getter(Body)
                    if k is None:
                        print("No valid error code found. Skipping email.")
                        continue
                    print('\nThe reply email is generating via Gemini')
                    mail = run_generator.generate_email(int(k))
                    # mail = ''
                    # for gen in llm_generation:
                    #     mail = mail+gen

                    print('\n....Final step.....')

                    print('\nSending Email.....')
                    send_email(service_send, Sender, 'Reply for error', mail)
                    print('Successfully email sent to the customer')
                    
                #print(output)

        time.sleep(POLL_INTERVAL)
    


if __name__ == "__main__":
    main()
