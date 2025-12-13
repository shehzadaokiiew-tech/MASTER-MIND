import streamlit as st
import threading, time, hashlib, uuid, requests
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# --------- Session State ---------
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0

# --------- Utilities ---------
def get_indian_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")

def log(msg):
    timestamp = get_indian_time()
    st.session_state.logs.append(f"[{timestamp}] {msg}")

def setup_browser():
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    driver = uc.Chrome(options=options)
    driver.set_window_size(1920,1080)
    return driver

def find_message_input(driver):
    selectors = [
        'div[contenteditable="true"][role="textbox"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea', 'input[type="text"]'
    ]
    for sel in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, sel)
        for el in elements:
            if el.is_enabled() and el.is_displayed():
                return el
    return None

def send_messages(chat_id, messages, delay):
    st.session_state.automation_running = True
    st.session_state.message_count = 0
    driver = None
    try:
        log("Starting browser...")
        driver = setup_browser()
        log(f"Opening conversation {chat_id}...")
        driver.get(f"https://www.facebook.com/messages/t/{chat_id}")
        time.sleep(10)

        input_box = find_message_input(driver)
        if not input_box:
            log("Message input not found!")
            return

        idx = 0
        while st.session_state.automation_running:
            msg = messages[idx % len(messages)]
            driver.execute_script("arguments[0].textContent=arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", input_box, msg)
            driver.execute_script("""
                const btns = document.querySelectorAll('[aria-label*="Send"]');
                if(btns.length>0){btns[0].click();}
            """)
            idx += 1
            st.session_state.message_count += 1
            log(f"Sent: {msg[:50]}")
            time.sleep(delay)
    except Exception as e:
        log(f"Error: {e}")
    finally:
        if driver:
            driver.quit()
        st.session_state.automation_running = False
        log("Automation stopped.")

# --------- UI ---------
st.title("⚡ LORD DEVIL Facebook E2EE Automation")

chat_id = st.text_input("Facebook Chat ID", placeholder="e.g., 1362400298935018")
messages_file = st.file_uploader("Upload Messages (.txt)", type=['txt'])
delay = st.number_input("Delay (seconds)", min_value=1, max_value=300, value=5)

messages_content = []
if messages_file:
    messages_content = messages_file.getvalue().decode("utf-8").splitlines()
    messages_content = [m for m in messages_content if m.strip()]

col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Start Automation", disabled=st.session_state.automation_running):
        if chat_id and messages_content:
            threading.Thread(target=send_messages, args=(chat_id, messages_content, delay), daemon=True).start()
        else:
            st.warning("Chat ID and messages required!")

with col2:
    if st.button("⏹️ Stop Automation", disabled=not st.session_state.automation_running):
        st.session_state.automation_running = False

st.markdown("### 📜 Logs")
if st.session_state.logs:
    logs_html = '<div style="background:#1e1e1e;color:#87CEEB;padding:10px;border-radius:8px;height:300px;overflow:auto">'
    for log_msg in st.session_state.logs[-50:]:
        logs_html += f"<div>{log_msg}</div>"
    logs_html += "</div>"
    st.markdown(logs_html, unsafe_allow_html=True)
else:
    st.info("Logs will appear here after starting automation.")

st.metric("Messages Sent", st.session_state.message_count)
