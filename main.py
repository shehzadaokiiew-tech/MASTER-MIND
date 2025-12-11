import streamlit as st
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime

# --- IMPORT FOR FIXING THREAD ERROR ---
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

# Session States Initialization
if 'running' not in st.session_state: st.session_state.running = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'count' not in st.session_state: st.session_state.count = 0

# --- SAFE LOGGING FUNCTION ---
def add_log(msg):
    # Safety check: Agar session state access nahi ho raha to crash na kare
    try:
        if 'logs' not in st.session_state:
            st.session_state.logs = []
            
        ts = datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.append(f"[{ts}] {msg}")
        
        if len(st.session_state.logs) > 100:
            st.session_state.logs.pop(0)
    except Exception:
        pass # Ignore errors in logging to keep bot running

# --- BROWSER SETUP ---
def setup_browser():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    return webdriver.Chrome(options=options)

# --- AUTOMATION LOGIC ---
def start_process(chat_id, prefix, delay, cookies, messages):
    driver = None
    try:
        add_log("🚀 Starting Process...")
        driver = setup_browser()
        
        add_log("🌐 Opening Facebook...")
        driver.get("https://www.facebook.com")
        time.sleep(3)
        
        # Cookies
        add_log("🍪 Setting Cookies...")
        try:
            for cookie in cookies.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com'})
        except:
            add_log("❌ Cookie Error!")

        # Chat
        url = f"https://www.facebook.com/messages/t/{chat_id}"
        add_log(f"💬 Going to Chat: {chat_id}")
        driver.get(url)
        time.sleep(10)
        
        idx = 0
        while st.session_state.running:
            try:
                box = None
                selectors = ['div[contenteditable="true"]', 'textarea', 'div[aria-label="Message"]']
                
                for s in selectors:
                    try:
                        found = driver.find_elements(By.CSS_SELECTOR, s)
                        if found: box = found[0]; break
                    except: continue
                
                if box:
                    msg = messages[idx % len(messages)]
                    final_msg = f"{prefix} {msg}" if prefix else msg
                    
                    driver.execute_script("arguments[0].focus();", box)
                    box.send_keys(final_msg)
                    time.sleep(0.5)
                    box.send_keys(Keys.ENTER)
                    
                    st.session_state.count += 1
                    add_log(f"✅ Sent: {final_msg}")
                    idx += 1
                    time.sleep(delay)
                else:
                    add_log("⚠️ Box not found. Refreshing...")
                    driver.refresh()
                    time.sleep(10)
                    
            except Exception as e:
                add_log(f"❌ Error: {str(e)[:30]}")
                time.sleep(5)
                
    except Exception as e:
        add_log(f"🛑 FATAL ERROR: {str(e)}")
    finally:
        if driver: driver.quit()
        st.session_state.running = False

# --- GUI ---
st.markdown('<div class="main-container"><div class="header-title">LORD DEVIL CLOUD</div></div>', unsafe_allow_html=True)

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
            
            # --- FIX: ATTACH CONTEXT TO THREAD ---
            t = threading.Thread(target=start_process, args=(chat_id, prefix, delay, cookies, msgs))
            add_script_run_ctx(t) # YEH LINE ERROR SOLVE KAREGI
            t.start()
            
            st.rerun()
        else:
            st.warning("Cookies & Chat ID Required!")

with c2:
    if st.button("⏹ STOP", disabled=not st.session_state.running):
        st.session_state.running = False
        st.rerun()

# Logs Display
st.markdown(f"**Status:** {'RUNNING' if st.session_state.running else 'STOPPED'} | **Sent:** {st.session_state.count}")

# Safe Log Display
try:
    if 'logs' in st.session_state:
        logs_html = '<div class="terminal-window">'
        for log in reversed(st.session_state.logs):
            logs_html += f'<div class="log-line">{log}</div>'
        logs_html += '</div>'
        st.markdown(logs_html, unsafe_allow_html=True)
except:
    st.markdown("Logs initializing...")

if st.session_state.running:
    time.sleep(1)
    st.rerun()    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # Streamlit Cloud par driver automatic detect ho jata hai
    return webdriver.Chrome(options=options)

# --- AUTOMATION FUNCTION ---
def start_process(chat_id, prefix, delay, cookies, messages):
    driver = None
    try:
        add_log("🚀 Starting Process...")
        driver = setup_browser()
        
        add_log("🌐 Opening Facebook...")
        driver.get("https://www.facebook.com")
        time.sleep(3)
        
        # Cookies Logic
        add_log("🍪 Setting Cookies...")
        try:
            for cookie in cookies.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com'})
        except:
            add_log("❌ Cookie Error!")

        # Chat Navigation
        url = f"https://www.facebook.com/messages/t/{chat_id}"
        add_log(f"💬 Going to Chat: {chat_id}")
        driver.get(url)
        time.sleep(10)
        
        idx = 0
        while st.session_state.running:
            try:
                box = None
                selectors = ['div[contenteditable="true"]', 'textarea', 'div[aria-label="Message"]']
                
                for s in selectors:
                    try:
                        found = driver.find_elements(By.CSS_SELECTOR, s)
                        if found: box = found[0]; break
                    except: continue
                
                if box:
                    msg = messages[idx % len(messages)]
                    final_msg = f"{prefix} {msg}" if prefix else msg
                    
                    driver.execute_script("arguments[0].focus();", box)
                    box.send_keys(final_msg)
                    time.sleep(0.5)
                    box.send_keys(Keys.ENTER)
                    
                    st.session_state.count += 1
                    add_log(f"✅ Sent: {final_msg}")
                    idx += 1
                    time.sleep(delay)
                else:
                    add_log("⚠️ Box not found. Refreshing...")
                    driver.refresh()
                    time.sleep(10)
                    
            except Exception as e:
                add_log(f"❌ Error: {str(e)[:30]}")
                time.sleep(5)
                
    except Exception as e:
        add_log(f"🛑 FATAL ERROR: {str(e)}")
    finally:
        if driver: driver.quit()
        st.session_state.running = False

# --- UI ---
st.markdown('<div class="main-container"><div class="header-title">LORD DEVIL CLOUD</div></div>', unsafe_allow_html=True)

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
            t.daemon = True
            t.start()
            st.rerun()
        else:
            st.warning("Cookies & Chat ID Required!")

with c2:
    if st.button("⏹ STOP", disabled=not st.session_state.running):
        st.session_state.running = False
        st.rerun()

# Logs Display
st.markdown(f"**Status:** {'RUNNING' if st.session_state.running else 'STOPPED'} | **Sent:** {st.session_state.count}")
logs_html = '<div class="terminal-window">'
for log in reversed(st.session_state.logs):
    logs_html += f'<div class="log-line">{log}</div>'
logs_html += '</div>'
st.markdown(logs_html, unsafe_allow_html=True)

if st.session_state.running:
    time.sleep(1)
    st.rerun()
