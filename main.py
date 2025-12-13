import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pathlib import Path
import threading, time

# ----- Session State -----
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'messages_sent' not in st.session_state:
    st.session_state.messages_sent = 0

# ----- Custom CSS -----
custom_css = """
<style>
body {background: #1e1e2f; color: white;}
.stButton>button {background: linear-gradient(135deg, #667eea, #764ba2); color:white; border-radius:10px; padding:10px 20px; font-weight:600;}
input, textarea {border-radius:10px; padding:8px; background:#111; color:white; border:2px solid #667eea;}
.log-container {background:#111; padding:10px; border-radius:10px; max-height:300px; overflow-y:auto; font-family:'Courier New', monospace;}
.log-entry {color:#00ffcc; margin:2px 0; font-weight:500;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ----- Logging function -----
def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {msg}")

# ----- Selenium browser setup -----
def setup_browser(cookies=None):
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    chromium_path = '/usr/bin/chromium'
    if Path(chromium_path).exists():
        chrome_options.binary_location = chromium_path

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920,1080)

    if cookies:
        driver.get('https://www.facebook.com/')
        for cookie in cookies.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=',1)
                try:
                    driver.add_cookie({'name':name, 'value':value, 'domain':'.facebook.com','path':'/'})
                except:
                    continue
    return driver

# ----- Find message input -----
def find_message_input(driver):
    selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'textarea',
        'input[type="text"]',
        '[contenteditable="true"]'
    ]
    for sel in selectors:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            return el
        except:
            continue
    return None

# ----- Automation function -----
def send_messages(chat_id, messages, prefix, delay, cookies=None):
    st.session_state.automation_running = True
    driver = setup_browser(cookies)
    driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
    time.sleep(8)

    input_field = find_message_input(driver)
    if not input_field:
        log("❌ Message input not found!")
        st.session_state.automation_running = False
        driver.quit()
        return

    st.session_state.messages_sent = 0
    while st.session_state.automation_running:
        for msg in messages:
            full_msg = f"{prefix} {msg}" if prefix else msg
            try:
                driver.execute_script("arguments[0].focus(); arguments[0].textContent=arguments[1];", input_field, full_msg)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles:true}));", input_field)
                driver.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', bubbles:true}));", input_field)
                st.session_state.messages_sent += 1
                log(f"✅ Sent: {full_msg[:50]}...")
                time.sleep(delay)
                if not st.session_state.automation_running:
                    break
            except Exception as e:
                log(f"❌ Error sending message: {e}")
                st.session_state.automation_running = False
                break
    driver.quit()
    log("⏹️ Automation stopped.")

# ----- Streamlit UI -----
st.markdown('<h1 style="text-align:center; color:#667eea;">⚡ LORD DEVIL E2EE Facebook Automation Tool</h1>', unsafe_allow_html=True)

chat_id = st.text_input("Chat/Conversation ID")
prefix = st.text_input("Message Prefix (optional)")
delay = st.number_input("Delay between messages (seconds)", 1, 300, 5)
uploaded_file = st.file_uploader("Upload Messages (.txt)")
cookies = st.text_area("Facebook Cookies (optional)")

messages = []
if uploaded_file:
    messages = [line.strip() for line in uploaded_file.getvalue().decode("utf-8").splitlines() if line.strip()]

col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Start Automation", disabled=st.session_state.automation_running):
        if chat_id and messages:
            threading.Thread(target=send_messages, args=(chat_id, messages, prefix, delay, cookies), daemon=True).start()
        else:
            st.error("⚠️ Chat ID aur Messages required hain!")

with col2:
    if st.button("⏹️ Stop Automation", disabled=not st.session_state.automation_running):
        st.session_state.automation_running = False

st.markdown("### 📜 Live Logs")
logs_html = '<div class="log-container">'
for log_entry in st.session_state.logs[-20:]:
    logs_html += f'<div class="log-entry">{log_entry}</div>'
logs_html += '</div>'
st.markdown(logs_html, unsafe_allow_html=True)

st.metric("Messages Sent", st.session_state.messages_sent)
