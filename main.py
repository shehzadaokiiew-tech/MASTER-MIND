# --- FILE NAME: main.py ---

import streamlit as st
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from streamlit.runtime.scriptrunner import add_script_run_ctx

st.set_page_config(page_title="SNAKE XD TOOL", layout="wide")

# --- DESIGN LOAD KARNA (Ye zaroori hai) ---
def load_design():
    try:
        with open('design.html', 'r') as f:
            st.markdown(f.read(), unsafe_allow_html=True)
    except:
        st.warning("design.html file nahi mili! Design load nahi hua.")

load_design() # Design Apply Ho Gaya

# --- SESSION STATES ---
if 'running' not in st.session_state: st.session_state.running = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'count' not in st.session_state: st.session_state.count = 0

def add_log(msg):
    try:
        ts = datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.append(f"[{ts}] {msg}")
        if len(st.session_state.logs) > 100: st.session_state.logs.pop(0)
    except: pass

# --- BROWSER SETUP (NO CHANGE) ---
def setup_browser():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    try:
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        return webdriver.Chrome(service=service, options=options)
    except:
        return webdriver.Chrome(options=options)

# --- MAIN LOGIC (NO CHANGE) ---
def start_process(chat_id, prefix, suffix, delay, cookies, messages):
    driver = None
    try:
        add_log("🚀 SNAKE XD SYSTEM STARTED...")
        driver = setup_browser()
        
        add_log("🌐 Opening Facebook...")
        driver.get("https://www.facebook.com")
        time.sleep(4)
        
        try:
            for cookie in cookies.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com'})
        except: pass

        url = f"https://www.facebook.com/messages/t/{chat_id}"
        add_log(f"💬 Opening Chat: {chat_id}")
        driver.get(url)
        time.sleep(10)
        
        try: driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Close"]').click()
        except: pass
        
        idx = 0
        while st.session_state.running:
            try:
                box = None
                selectors = [
                    'div[aria-label="Message"][contenteditable="true"]',
                    'div[role="textbox"][contenteditable="true"]',
                    'div[contenteditable="true"]',
                    'textarea'
                ]
                
                for s in selectors:
                    try:
                        found = driver.find_elements(By.CSS_SELECTOR, s)
                        if found and found[0].is_displayed():
                            box = found[0]; break
                    except: continue
                
                if box:
                    base_msg = messages[idx % len(messages)]
                    part1 = f"{prefix} " if prefix else ""
                    part3 = f" {suffix}" if suffix else ""
                    final_msg = f"{part1}{base_msg}{part3}"
                    
                    try:
                        actions = ActionChains(driver)
                        actions.move_to_element(box).click().send_keys(final_msg).perform()
                        time.sleep(0.5)
                        actions.send_keys(Keys.ENTER).perform()
                    except:
                        driver.execute_script("arguments[0].focus();", box)
                        driver.execute_script(f"arguments[0].innerText = '{final_msg}';", box)
                        box.send_keys(Keys.ENTER)

                    st.session_state.count += 1
                    add_log(f"✅ Sent: {final_msg}")
                    idx += 1
                    time.sleep(delay)
                else:
                    add_log("⚠️ Box hidden. Waiting...")
                    time.sleep(5)
            except Exception as e:
                add_log(f"❌ Error: {str(e)[:20]}")
                time.sleep(5)
    except Exception as e:
        add_log(f"🛑 Crash: {str(e)[:40]}")
    finally:
        if driver: 
            try: driver.quit()
            except: pass
        st.session_state.running = False

# --- INPUT UI (Iska Design HTML file se aayega) ---
# Sirf Layout thoda clean kiya hai taake HTML style achay se baithe

cookies = st.text_area("FACEBOOK COOKIES (VIP)", height=100)

col1, col2 = st.columns(2)
with col1:
    chat_id = st.text_input("THREAD / CHAT UID")
with col2:
    delay = st.number_input("TIME DELAY (SEC)", value=60, min_value=1)

col3, col4 = st.columns(2)
with col3:
    prefix = st.text_input("NAME (PREFIX)")
with col4:
    suffix = st.text_input("HERE NAME (END)")

file = st.file_uploader("MESSAGE FILE (.TXT)", type="txt")

st.markdown("<br>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    if st.button("🚀 ACTIVATE SNAKE XD"):
        if not st.session_state.running:
            if cookies and chat_id:
                msgs = ["SNAKE XD TESTING"]
                if file: msgs = [l.strip() for l in file.getvalue().decode().split('\n') if l.strip()]
                
                st.session_state.running = True
                st.session_state.logs = []
                st.session_state.count = 0
                
                t = threading.Thread(target=start_process, args=(chat_id, prefix, suffix, delay, cookies, msgs))
                add_script_run_ctx(t)
                t.start()
                st.rerun()
            else:
                st.error("COOKIES AUR CHAT ID KAHA HAI BOSS?")

with c2:
    if st.button("🛑 STOP SYSTEM"):
        st.session_state.running = False
        st.rerun()

# --- LOGS DISPLAY (HTML Style Use Karega) ---
logs_html = '<div class="logs-container">'
if st.session_state.logs:
    for log in reversed(st.session_state.logs):
        logs_html += f'<div class="log-line">{log}</div>'
else:
    logs_html += '<div class="log-line" style="color:#666;">Waiting for start...</div>'
logs_html += '</div>'

st.markdown(logs_html, unsafe_allow_html=True)

if st.session_state.running:
    time.sleep(1)
    st.rerun()
