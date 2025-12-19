import base64
import os
import re
import threading
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from email_generator import send_email
from gemini_llm_response import run_generator

# Scopes
SCOPES_send = ["https://www.googleapis.com/auth/gmail.send"]
SCOPES_read = ["https://www.googleapis.com/auth/gmail.readonly"]

# Globals
seen_ids = set()
worker_running = False
log_callback = None


# ============================================
# LOGGING (THREAD-SAFE)
# ============================================
def log(msg: str):
    """Logs to terminal AND safely queues for Streamlit."""
    print(msg)  # Always print to console
    if log_callback:
        try:
            # Use callback (which pushes to queue) - this is thread-safe
            log_callback(msg)
        except Exception as e:
            print(f"[LOG ERROR] {e}")


# ============================================
# CLEANING + PROCESSING FUNCTIONS
# ============================================
def get_clean_text(body: str) -> str:
    body = re.sub(r'https?://\S+', '', body)
    body = re.sub(r'<.*?>', '', body)
    body = re.sub(r'\s+', ' ', body).strip()
    return body


def get_email_body(msg):
    payload = msg.get("payload", {})

    if "parts" in payload:
        for part in payload["parts"]:
            mime = part.get("mimeType", "")
            data = part.get("body", {}).get("data")

            if data:
                decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                if mime in ("text/plain", "text/html"):
                    return decoded

    # Single part
    data = payload.get("body", {}).get("data")
    if data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    return "(No body found)"


KEYWORDS = [
    "support",
    "tech support",
    "error",
    "not working",
    "assistance",
]


def subject_matches(subject: str) -> bool:
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
    "promo",
    "offer",
    "delivered",
]


def is_purchase_or_spam(subject: str, sender: str, body: str) -> bool:
    text = (subject + " " + sender + " " + body).lower()
    return any(word in text for word in PURCHASE_SPAM_KEYWORDS)


def process_new_message(service, msg_id):
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()

    headers = msg.get("payload", {}).get("headers", [])
    sender = subject = "(unknown)"

    for h in headers:
        if h["name"] == "From":
            sender = h["value"]
        if h["name"] == "Subject":
            subject = h["value"]

    raw_body = get_email_body(msg)
    body = get_clean_text(raw_body)

    # Check conditions
    if not subject_matches(subject):
        log(f"⏭️ Skipping (Not tech-related): {subject}")
        return None

    if is_purchase_or_spam(subject, sender, body):
        log(f"⏭️ Skipping (Purchase/Spam): {subject}")
        return None

    # Print details
    log("=" * 50)
    log("🚨 TECH SUPPORT EMAIL DETECTED")
    log(f"📧 From: {sender}")
    log(f"📋 Subject: {subject}")
    log(f"💬 Body: {body[:200]}...")  # First 200 chars
    log("=" * 50)

    return [sender, subject, body]


def error_code_getter(body: str):
    pattern = r'[A-Za-z]+\s*[:\- ]\s*(\d+)'
    match = re.search(pattern, body)
    return match.group(1) if match else None


# ============================================
# AUTHENTICATION
# ============================================
def authenticate():
    """Authenticate Gmail API with proper error handling."""
    creds_read = None
    creds_send = None
    
    if not os.path.exists("credentials.json"):
        raise FileNotFoundError("credentials.json not found. Please upload it first.")
    
    # READ credentials
    try:
        if os.path.exists("token_read.json"):
            log("📂 Loading token_read.json...")
            creds_read = Credentials.from_authorized_user_file("token_read.json", SCOPES_read)

        if not creds_read or not creds_read.valid:
            if creds_read and creds_read.expired and creds_read.refresh_token:
                log("🔄 Refreshing expired read token...")
                creds_read.refresh(Request())
                with open("token_read.json", "w") as f:
                    f.write(creds_read.to_json())
            else:
                raise Exception("Valid token_read.json required. Run OAuth flow manually first.")
    
    except Exception as e:
        log(f"❌ Error with read credentials: {e}")
        raise

    # SEND credentials
    try:
        if os.path.exists("token_send.json"):
            log("📂 Loading token_send.json...")
            creds_send = Credentials.from_authorized_user_file("token_send.json", SCOPES_send)

        if not creds_send or not creds_send.valid:
            if creds_send and creds_send.expired and creds_send.refresh_token:
                log("🔄 Refreshing expired send token...")
                creds_send.refresh(Request())
                with open("token_send.json", "w") as f:
                    f.write(creds_send.to_json())
            else:
                raise Exception("Valid token_send.json required. Run OAuth flow manually first.")
    
    except Exception as e:
        log(f"❌ Error with send credentials: {e}")
        raise

    log("✅ Authentication successful!")
    return [creds_read, creds_send]


# ============================================
# WORKER LOOP (BACKGROUND THREAD)
# ============================================
def worker_loop(poll_interval: int):
    global worker_running

    log("🔐 Authenticating Gmail services...")

    try:
        creds = authenticate()
        service_read = build("gmail", "v1", credentials=creds[0])
        service_send = build("gmail", "v1", credentials=creds[1])
    except Exception as e:
        log(f"❌ Authentication failed: {e}")
        log("")
        log("📋 Fix: Ensure all JSON files are uploaded and valid")
        worker_running = False
        return

    log(f"✅ Gmail monitoring active (poll interval: {poll_interval}s)")
    
    # Signal to UI that worker is ready
    if log_callback:
        try:
            log_callback("WORKER_READY_SIGNAL")
        except:
            pass

    log("⏸️  Press STOP in UI to halt automation")
    log("")

    email_count = 0

    while worker_running:
        try:
            results = service_read.users().messages().list(
                userId="me", q="is:unread", maxResults=5
            ).execute()

            msgs = results.get("messages", [])

            if not msgs:
                # Reduced noise - only log occasionally
                if email_count == 0:
                    log("📭 No unread emails. Monitoring...")
            
            for item in msgs:
                msg_id = item["id"]
                if msg_id in seen_ids:
                    continue

                seen_ids.add(msg_id)
                log("")
                log("🔥 NEW MESSAGE DETECTED")

                out = process_new_message(service_read, msg_id)
                if out is None:
                    continue

                Sender, Subject, Body = out

                log("🔍 Extracting error code from email body...")
                err = error_code_getter(Body)

                if err is None:
                    log("⚠️ No valid error code found. Skipping this email.")
                    continue

                log(f"✅ Error code identified: {err}")
                log("🤖 Generating AI-powered response via Gemini...")
                
                reply_msg = run_generator.generate_email(int(err), Body)

                log("📤 Sending automated reply...")
                send_email(service_send, Sender, "Reply for error", reply_msg)

                email_count += 1

                log("")
                log("=" * 50)
                log("📨 EMAIL SENT SUCCESSFULLY")
                log(f"   To: {Sender}")
                log(f"   Subject: Reply for error")
                log(f"   Error Code: {err}")
                log(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                log(f"   Total Processed: {email_count}")
                log("=" * 50)
                log("")

        except Exception as e:
            log(f"⚠️ Worker error: {e}")

        time.sleep(poll_interval)

    log("🛑 Worker loop terminated.")


# ============================================
# CONTROL (CALLED FROM STREAMLIT)
# ============================================
def start_worker(poll_interval: int, logger=None):
    """Start background worker thread."""
    global worker_running, log_callback

    if worker_running:
        if logger:
            logger("⚠️ Worker already running.")
        return

    log_callback = logger
    worker_running = True

    t = threading.Thread(target=worker_loop, args=(poll_interval,), daemon=True)
    t.start()

    log("🚀 Background worker thread started")


def stop_worker():
    """Stop background worker thread."""
    global worker_running
    if worker_running:
        worker_running = False
        log("🛑 Stop signal sent - worker will halt after current cycle")
    else:
        log("ℹ️ Worker is not currently running")
