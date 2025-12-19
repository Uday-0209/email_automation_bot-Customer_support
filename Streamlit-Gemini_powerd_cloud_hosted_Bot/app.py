
import os
import time
import queue

import streamlit as st
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

from email_worker import start_worker, stop_worker

# ------------------------------------
# Load environment variables
# ------------------------------------
load_dotenv()

# ------------------------------------
# Streamlit Page Settings
# ------------------------------------
st.set_page_config(
    page_title="Email Automation Dashboard",
    page_icon="📧",
    layout="wide"
)

# ------------------------------------
# SESSION STATE INITIALIZATION
# ------------------------------------
if "automation_running" not in st.session_state:
    st.session_state.automation_running = False

if "logs" not in st.session_state:
    st.session_state.logs = []

# IMPORTANT:
# We create a Queue ONCE and then capture it in the logger closure.
# The worker thread ONLY talks to this queue (no Streamlit APIs!)
if "log_queue" not in st.session_state:
    st.session_state.log_queue = queue.Queue()

log_queue: queue.Queue = st.session_state.log_queue


# ------------------------------------
# THREAD-SAFE LOGGER (NO st.* INSIDE)
# ------------------------------------
def logger(message: str):
    """
    This function is passed to email_worker.start_worker(...).

    It is called from the BACKGROUND worker thread, so it MUST NOT
    use any Streamlit APIs (no st.session_state, no st.* at all).

    We only push messages into a plain Python queue, which is safe.
    """
    try:
        log_queue.put(str(message).strip())
    except Exception as e:
        # As a last resort, print to console
        print("[LOGGER ERROR]", e, "while logging:", message)


# ------------------------------------
# HELPER FUNCTIONS
# ------------------------------------
def save_uploaded_file(uploaded_file, filename):
    if uploaded_file:
        with open(filename, "wb") as f:
            f.write(uploaded_file.getvalue())
        return True
    return False


def update_env_file(gemini_key: str):
    env_data = {}

    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env_data[k.strip()] = v.strip()

    if gemini_key:
        env_data["GEMINI_API_KEY"] = gemini_key

    with open(".env", "w") as f:
        for k, v in env_data.items():
            f.write(f"{k}={v}\n")


# ------------------------------------
# HEADER
# ------------------------------------
st.markdown(
    """
    <h1 style='text-align:center; color:#4ADE80;'>
        📧 Email Automation Dashboard
    </h1>
    <h4 style='text-align:center; color:#94A3B8;'>
        Gmail + Gemini powered automatic tech support system
    </h4>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ------------------------------------
# CONFIGURATION PANEL
# ------------------------------------
st.subheader("🔧 Configuration")

config_col1, config_col2 = st.columns(2)

with config_col1:
    gmail_id = st.text_input(
        "Gmail Account (used for automation)",
        placeholder="example@gmail.com"
    )
    poll_interval = st.number_input(
        "Polling Interval (seconds)",
        min_value=5,
        max_value=300,
        value=10,
        step=1
    )

with config_col2:
    gemini_key = st.text_input(
        "Gemini API Key",
        placeholder="Enter your Gemini API Key",
        type="password"
    )

st.markdown(
    """
    <div style='padding:10px; margin-top:10px; border-radius:8px;
                background-color:#1A1D23; color:#E2E8F0;'>
        ℹ️ <strong>Note:</strong> Your Gemini API key will be stored securely in <code>.env</code>.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ------------------------------------
# FILE UPLOADS
# ------------------------------------
st.subheader("📁 Upload Required JSON Files")

cred_file = st.file_uploader("credentials.json", type=["json"])
token_read = st.file_uploader("token_read.json", type=["json"])
token_send = st.file_uploader("token_send.json", type=["json"])
error_db = st.file_uploader("possible_error.json", type=["json"])

if st.button("💾 Save All Files"):
    ok = True

    if cred_file:
        save_uploaded_file(cred_file, "credentials.json")
        logger("Saved credentials.json")
    else:
        ok = False
        st.warning("Missing: credentials.json")

    if token_read:
        save_uploaded_file(token_read, "token_read.json")
        logger("Saved token_read.json")
    else:
        ok = False
        st.warning("Missing: token_read.json")

    if token_send:
        save_uploaded_file(token_send, "token_send.json")
        logger("Saved token_send.json")
    else:
        ok = False
        st.warning("Missing: token_send.json")

    if error_db:
        save_uploaded_file(error_db, "possible_error.json")
        logger("Saved possible_error.json")
    else:
        ok = False
        st.warning("Missing: possible_error.json")

    if gemini_key:
        update_env_file(gemini_key)
        logger("GEMINI_API_KEY updated.")

    if ok:
        st.success("All files saved successfully 🎉")
    else:
        st.error("Some files are missing. Please upload again.")

st.markdown("---")

# ------------------------------------
# CONTROL PANEL
# ------------------------------------
st.subheader("🎛️ Control Panel")

c1, c2 = st.columns(2)

with c1:
    start_btn = st.button("🚀 Start Automation", use_container_width=True)

with c2:
    stop_btn = st.button("⛔ Stop Automation", use_container_width=True)

# ---------- START ----------
if start_btn:
    if not gmail_id:
        st.warning("Enter Gmail ID.")
    elif not gemini_key and "GEMINI_API_KEY" not in os.environ:
        st.warning("Enter Gemini API Key.")
    elif not os.path.exists("credentials.json"):
        st.warning("Upload credentials.json.")
    elif not os.path.exists("token_read.json"):
        st.warning("Upload token_read.json.")
    elif not os.path.exists("token_send.json"):
        st.warning("Upload token_send.json.")
    elif not os.path.exists("possible_error.json"):
        st.warning("Upload possible_error.json.")
    else:
        # Persist key if provided
        if gemini_key:
            update_env_file(gemini_key)
            logger("GEMINI_API_KEY updated in .env")

        os.environ["AUTOMATION_GMAIL"] = gmail_id

        # Start background worker
        start_worker(
            poll_interval=int(poll_interval),
            logger=logger
        )

        st.session_state.automation_running = True
        st.success("Automation Running 🚀")
        logger("✅ Automation started from UI")

# ---------- STOP ----------
if stop_btn:
    stop_worker()
    st.session_state.automation_running = False
    st.error("Automation Stopped ⛔")
    logger("❌ Automation stopped from UI")

st.markdown("---")

# ------------------------------------
# STATUS & LIVE LOGS
# ------------------------------------
st.subheader("📊 System Status & Live Logs")

status_col1, status_col2, status_col3 = st.columns([2, 1, 1])

with status_col1:
    status = (
        "<span style='color:#4ADE80;'>🟢 Running</span>"
        if st.session_state.automation_running
        else "<span style='color:#F87171;'>🔴 Stopped</span>"
    )
    st.markdown(f"### Status: {status}", unsafe_allow_html=True)

with status_col2:
    # Show current queue size
    queue_size = log_queue.qsize()
    st.metric("Pending Log Queue", queue_size)

with status_col3:
    if st.button("🔄 Manual Refresh", use_container_width=True):
        st.experimental_rerun()

st.markdown("#### 📜 Live Logs")

# Auto-refresh ONLY when automation is running
if st.session_state.automation_running:
    st_autorefresh(interval=2000, key="auto_refresh_logs")

# Pull logs from queue into session_state.logs
logs_pulled = 0
while True:
    try:
        entry = log_queue.get_nowait()
    except queue.Empty:
        break
    st.session_state.logs.append(entry)
    logs_pulled += 1

if logs_pulled > 0:
    st.caption(f"🔄 Pulled {logs_pulled} new log entries")

# Display logs
if st.session_state.logs:
    recent_logs = st.session_state.logs[-200:]
    logs_text = "\n".join(recent_logs)

    st.text_area(
        "Logs Output",
        value=logs_text,
        height=500,
        disabled=True
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"📊 Total Logs Stored: {len(st.session_state.logs)}")
    with col2:
        st.caption(f"👁️ Displaying Last: {len(recent_logs)}")
    with col3:
        st.caption(f"⏰ Last Update: {time.strftime('%H:%M:%S')}")
else:
    st.info("📭 No logs yet. Start automation to see activity.")
    st.caption(f"Current log queue size: {log_queue.qsize()}")
