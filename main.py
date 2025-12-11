import streamlit as st
import time
import threading
import os
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

st.set_page_config(page_title="CLOUD E2EE", layout="wide")

def load_html():
    try:
        with open('index.html', 'r') as f: return f.read()
    except: return ""

st.markdown(load_html(), unsafe_allow_html=True)

if 'running' not in st.session_state: st.session_state.running = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'count' not in st.session_state: st.session_state.count = 0

def add_log(msg):
    try:
        if 'logs' not in st.session_state: st.session_state.logs = []
        ts = datetime.now().strftime("%H:%M:%S")
        st.session_state.logs.append(f"[{ts}] {msg}")
        if len(st.session_state.logs) > 100: st.session_state.logs.pop(0)
    except: pass

# --- BROWSER SETUP WITH POPUP BLOCKER ---
def setup_browser():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-notifications') # Block Notifications
    options.add_argument('--disable-popup-blocking') # Block Popups
    
    # User Agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    try:
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        return webdriver.Chrome(service=service, options=options)
    except:
        return webdriver.Chrome(options=options)

def start_process(chat_id, prefix, delay, cookies, messages):
    driver = None
    try:
        add_log("🚀 Starting Process...")
        driver = setup_browser()
        
        add_log("🌐 Opening Facebook...")
        driver.get("https://www.facebook.com")
        time.sleep(4)
        
        # Cookie Injection
        try:
            for cookie in cookies.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com'})
        except: pass

        url = f"https://www.facebook.com/messages/t/{chat_id}"
        add_log(f"💬 Opening Chat...")
        driver.get(url)
        time.sleep(10)
        
        # Try to dismiss popups if any
        try:
            driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Close"]').click()
        except: pass
        
        idx = 0
        while st.session_state.running:
            try:
                box = None
                # Updated Selectors
                selectors = [
                    'div[aria-label="Message"][contenteditable="true"]',
                    'div[role="textbox"][contenteditable="true"]',
                    'div[contenteditable="true"]',
                    'textarea'
                ]
                
                for s in selectors:
                    try:
                        found = driver.find_elements(By.CSS_SELECTOR, s)
                        if found:
                            # Verify if visible
                            if found[0].is_displayed():
                                box = found[0]
                                break
                    except: continue
                
                if box:
                    msg = messages[idx % len(messages)]
                    final_msg = f"{prefix} {msg}" if prefix else msg
                    
                    try:
                        # METHOD 1: Action Chains (Best for Headless)
                        actions = ActionChains(driver)
                        actions.move_to_element(box).click().send_keys(final_msg).perform()
                        time.sleep(0.5)
                        actions.send_keys(Keys.ENTER).perform()
                    except:
                        try:
                            # METHOD 2: Direct JS Injection (Fallback)
                            driver.execute_script("arguments[0].focus();", box)
                            driver.execute_script(f"arguments[0].innerText = '{final_msg}';", box)
                            box.send_keys(Keys.ENTER)
                        except Exception as e:
                            # Agar fail ho to thoda ruk kar retry kare (Spam nahi karega)
                            add_log(f"⚠️ Type Error. Waiting 5s...")
                            time.sleep(5)
                            continue

                    st.session_state.count += 1
                    add_log(f"✅ Sent: {final_msg}")
                    idx += 1
                    time.sleep(delay)
                else:
                    add_log("⚠️ Box hidden/loading...")
                    time.sleep(5)
                    
            except Exception as e:
                add_log(f"❌ Loop Error: {str(e)[:20]}")
                time.sleep(5)
                
    except Exception as e:
        add_log(f"🛑 Crash: {str(e)[:40]}")
    finally:
        if driver: 
            try: driver.quit()
            except: pass
        st.session_state.running = False

# --- UI ---
st.markdown('<div class="main-container"><div class="header-title">LORD DEVIL FIX</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    chat_id = st.text_input("Chat ID", placeholder="1000...")
    prefix = st.text_input("Prefix", placeholder="Optional")
    delay = st.number_input("Delay", value=60, min_value=1)

with col2:
    cookies = st.text_area("Cookies", height=130)
    file = st.file_uploader("Message File", type="txt")

st.markdown("---")

c1, c2 = st.columns(2)
with c1:
    if st.button("▶ START", disabled=st.session_state.running):
        if cookies and chat_id:
            msgs = ["Hello"]
            if file: msgs = [l.strip() for l in file.getvalue().decode().split('\n') if l.strip()]
            
            st.session_state.running = True
            st.session_state.logs = []
            st.session_state.count = 0
            
            t = threading.Thread(target=start_process, args=(chat_id, prefix, delay, cookies, msgs))
            add_script_run_ctx(t)
            t.start()
            st.rerun()

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
