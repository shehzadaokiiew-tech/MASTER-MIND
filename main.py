import streamlit as st
import threading, time, uuid, hashlib
from datetime import datetime
import requests
import undetected_chromedriver as uc

# ----------------------
# Session State Init
# ----------------------
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'messages_rotation_index' not in st.session_state:
    st.session_state.messages_rotation_index = 0
if 'messages_content' not in st.session_state:
    st.session_state.messages_content = ""

# ----------------------
# Helper Functions
# ----------------------
def get_indian_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")

def log(msg):
    timestamp = get_indian_time()
    formatted = f"[{timestamp}] {msg}"
    st.session_state.logs.append(formatted)

def get_next_message():
    messages = st.session_state.messages_content.splitlines()
    messages = [m.strip() for m in messages if m.strip()]
    if not messages:
        return "Hello!"
    idx = st.session_state.messages_rotation_index % len(messages)
    st.session_state.messages_rotation_index += 1
    return messages[idx]

def setup_browser():
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--window-size=1920,1080')
    options.add_argument("--log-level=3")
    
    driver = uc.Chrome(options=options)
    driver.set_window_size(1920,1080)
    return driver

def send_messages(chat_id, delay, prefix=""):
    driver = None
    try:
        st.session_state.automation_running = True
        driver = setup_browser()
        log("Chrome browser started")

        driver.get(f"https://www.facebook.com/messages/t/{chat_id}")
        log(f"Navigated to conversation {chat_id}")
        time.sleep(10)

        # Message input selector
        input_selector = 'div[contenteditable="true"][role="textbox"], textarea, input[type="text"]'
        message_input = driver.find_element("css selector", input_selector)
        log("Message input located")

        sent_count = 0
        while st.session_state.automation_running:
            msg = prefix + get_next_message()
            driver.execute_script("""
                const element = arguments[0];
                const message = arguments[1];
                element.focus();
                element.innerHTML = message;
                element.dispatchEvent(new Event('input', { bubbles: true }));
            """, message_input, msg)
            time.sleep(1)

            # Send via Enter
            driver.execute_script("""
                const e = new KeyboardEvent('keydown', {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true});
                arguments[0].dispatchEvent(e);
            """, message_input)

            sent_count += 1
            st.session_state.message_count = sent_count
            log(f"Message sent: {msg[:30]}...")
            time.sleep(delay)
    except Exception as e:
        log(f"Error: {str(e)}")
    finally:
        st.session_state.automation_running = False
        if driver:
            try:
                driver.quit()
                log("Browser closed")
            except:
                pass

def start_automation(chat_id, delay, prefix=""):
    if st.session_state.automation_running:
        st.warning("Automation already running!")
        return
    thread = threading.Thread(target=send_messages, args=(chat_id, delay, prefix))
    thread.daemon = True
    thread.start()

def stop_automation():
    st.session_state.automation_running = False

# ----------------------
# Streamlit UI
# ----------------------
st.title("🚀 LORD DEVIL E2EE Facebook Automation")
st.markdown("Simple tool to send messages automatically to a Facebook conversation.")

# Configuration
st.subheader("⚙️ Configuration")
chat_id = st.text_input("Facebook Chat/Conversation ID", placeholder="e.g., 1362400298935018")
prefix = st.text_input("Message Prefix (optional)", placeholder="e.g., [E2EE]")
delay = st.number_input("Delay between messages (seconds)", min_value=1, max_value=300, value=5)
uploaded_file = st.file_uploader("Upload Messages (.txt, one per line)", type=['txt'])

if uploaded_file:
    st.session_state.messages_content = uploaded_file.getvalue().decode("utf-8")

# Automation Controls
st.subheader("🚀 Automation Control")
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Start E2EE", disabled=st.session_state.automation_running):
        if chat_id and st.session_state.messages_content.strip():
            start_automation(chat_id, delay, prefix)
        else:
            st.error("Please provide chat ID and messages file.")
with col2:
    if st.button("⏹️ Stop E2EE", disabled=not st.session_state.automation_running):
        stop_automation()

# Live Metrics
st.subheader("📊 Live Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Messages Sent", st.session_state.message_count)
with col2:
    status = "🟢 Running" if st.session_state.automation_running else "🔴 Stopped"
    st.metric("Status", status)
with col3:
    st.metric("Total Logs", len(st.session_state.logs))

# Live Logs
st.subheader("📜 Live Logs")
if st.session_state.logs:
    logs_html = '<div style="background:#111;color:#0f0;padding:10px;height:300px;overflow:auto;font-family:monospace;">'
    for log_entry in st.session_state.logs[-50:]:
        logs_html += f"<div>{log_entry}</div>"
    logs_html += "</div>"
    st.markdown(logs_html, unsafe_allow_html=True)
else:
    st.info("No logs yet. Start automation to see logs here.")
