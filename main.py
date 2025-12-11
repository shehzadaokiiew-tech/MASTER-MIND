import streamlit as st
import time
import threading
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# --- FIX THREADING ERROR ---
from streamlit.runtime.scriptrunner import add_script_run_ctx

st.set_page_config(page_title="CLOUD E2EE", layout="wide")

# Load HTML
def load_html():
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except:
        return ""

st.markdown(load_html(), unsafe_allow_html=True)

# Session States
if 'running' not in st.session_state: st.session_state.running = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'count' not in st.session_state: st.session_state.count = 0

# --- LOGGING ---
def add_log(msg):
    try:
        if 'logs' not in st.session_state: st.session_state.logs = []
        ts = datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.append(f"[{ts}] {msg}")
        if len(st.session_state.logs) > 100: st.session_state.logs.pop(0)
    except: pass

# --- ADVANCED BROWSER SETUP (CRASH FIX) ---
def setup_browser():
    options = Options()
    
    # Ye saare Flags zaroori hain hosting ke liye
    options.add_argument('--headless') # New mode hata diya, stability ke liye old use kiya
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--remote-debugging-port=9222')
    
    # User Agent Check
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Try 1: Automatic Driver Management (Best for Cloud)
    try:
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        return webdriver.Chrome(service=service, options=options)
    except:
        pass
        
    # Try 2: Manual Path Finding (Backup)
    try:
        paths = [
            "/usr/bin/chromium", 
            "/usr/bin/chromium-browser", 
            "/usr/bin/google-chrome"
        ]
        for p in paths:
            if os.path.exists(p):
                options.binary_location = p
                break
        return webdriver.Chrome(options=options)
    except Exception as e:
        add_log(f"Browser Setup Failed: {str(e)}")
        raise e

# --- PROCESS LOGIC ---
def start_process(chat_id, prefix, delay, cookies, messages):
    driver = None
    try:
        add_log("🚀 Starting Process (v2)...")
        driver = setup_browser()
        
        add_log("🌐 Opening Facebook...")
        driver.get("https://www.facebook.com")
        time.sleep(5) # Thoda time badhaya taaki crash na ho
        
        # Cookies
        add_log("🍪 Injecting Cookies...")
        try:
            for cookie in cookies.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com'})
        except:
            add_log("❌ Invalid Cookies!")

        url = f"https://www.facebook.com/messages/t/{chat_id}"
        add_log(f"💬 Opening Chat...")
        driver.get(url)
        time.sleep(15) # Wait for chat load
        
        idx = 0
        while st.session_state.running:
            try:
                box = None
                selectors = ['div[contenteditable="true"]', 'textarea', 'div[role="textbox"]']
                
                for s in selectors:
                    try:
                        found = driver.find_elements(By.CSS_SELECTOR, s)
                        if found: box = found[0]; break
                    except: continue
                
                if box:
                    msg = messages[idx % len(messages)]
                    final_msg = f"{prefix} {msg}" if prefix else msg
                    
                    try:
                        driver.execute_script("arguments[0].focus();", box)
                        box.send_keys(final_msg)
                        time.sleep(0.5)
                        box.send_keys(Keys.ENTER)
                        
                        st.session_state.count += 1
                        add_log(f"✅ Sent: {final_msg}")
                        idx += 1
                        time.sleep(delay)
                    except:
                        add_log("⚠️ Failed to type. Retrying...")
                else:
                    add_log("⚠️ Chat box not found. Refreshing...")
                    driver.refresh()
                    time.sleep(15)
                    
            except Exception as e:
                add_log(f"❌ Error: {str(e)[:40]}")
                time.sleep(5)
                
    except Exception as e:
        add_log(f"🛑 CRASH: {str(e)}")
    finally:
        if driver: 
            try: driver.quit()
            except: pass
        st.session_state.running = False

# --- UI ---
st.markdown('<div class="main-container"><div class="header-title">LORD DEVIL v2</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    chat_id = st.text_input("Chat ID", placeholder="1000...")
    prefix = st.text_input("Prefix", placeholder="Optional")
    delay = st.number_input("Delay", value=5, min_value=1)

with col2:
    cookies = st.text_area("Cookies", height=130, placeholder="Paste cookies here...")
    file = st.file_uploader("Message File (.txt)", type="txt")

st.markdown("---")

c1, c2 = st.columns(2)
with c1:
    if st.button("▶ START", disabled=st.session_state.running):
        if cookies and chat_id:
            msgs = ["Hello World"]
            if file:
                msgs = [l.strip() for l in file.getvalue().decode().split('\n') if l.strip()]
            
            st.session_state.running = True
            st.session_state.logs = []
            st.session_state.count = 0
            
            t = threading.Thread(target=start_process, args=(chat_id, prefix, delay, cookies, msgs))
            add_script_run_ctx(t)
            t.start()
            st.rerun()
        else:
            st.warning("Data Missing!")

with c2:
    if st.button("⏹ STOP", disabled=not st.session_state.running):
        st.session_state.running = False
        st.rerun()

st.markdown(f"**Status:** {'RUNNING' if st.session_state.running else 'STOPPED'} | **Sent:** {st.session_state.count}")

try:
    if 'logs' in st.session_state:
        logs_html = '<div class="terminal-window">'
        for log in reversed(st.session_state.logs):
            logs_html += f'<div class="log-line">{log}</div>'
        logs_html += '</div>'
        st.markdown(logs_html, unsafe_allow_html=True)
except: pass

if st.session_state.running:
    time.sleep(1)
    st.rerun()
