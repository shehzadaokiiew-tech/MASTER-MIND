import streamlit as st
import time
import threading
import json
import os
import pytz
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from streamlit.runtime.scriptrunner import add_script_run_ctx

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MASTERO TOOL - VIP AUTOMATION",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS & HTML (THEME) ---
# This creates the "Mastero" dark/hacker look
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Mono:wght@400;700&display=swap');
    
    body { background-color: #0e0e0e; color: #00ff00; font-family: 'Roboto Mono', monospace; }
    .stApp { background-color: #050505; }
    
    /* TITLES */
    .mastero-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        text-align: center;
        background: -webkit-linear-gradient(#00ff00, #004d00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 20px rgba(0, 255, 0, 0.5);
        margin-bottom: 10px;
    }
    .vip-badge {
        text-align: center;
        color: #fff;
        background: #d32f2f;
        padding: 5px 15px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 20px;
        box-shadow: 0 0 10px #d32f2f;
    }

    /* INPUTS */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
        background-color: #111;
        color: #00ff00;
        border: 1px solid #333;
        border-radius: 5px;
    }
    .stTextInput>div>div>input:focus { border-color: #00ff00; box-shadow: 0 0 5px #00ff00; }
    
    /* BUTTONS */
    .stButton>button {
        background: #000;
        color: #00ff00;
        border: 2px solid #00ff00;
        width: 100%;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #00ff00;
        color: #000;
        box-shadow: 0 0 15px #00ff00;
    }

    /* CONSOLE */
    .console-box {
        background-color: #000;
        border: 1px solid #333;
        border-left: 4px solid #00ff00;
        padding: 15px;
        height: 400px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        margin-top: 20px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.9);
    }
    .log-entry { margin-bottom: 5px; border-bottom: 1px solid #111; padding-bottom: 2px; }
    .log-time { color: #888; margin-right: 10px; }
    .log-info { color: #00bcff; }
    .log-success { color: #00ff00; }
    .log-error { color: #ff0000; }
    .log-sys { color: #ffff00; }

    /* LAYOUT CONTAINERS */
    .box-container {
        background: #0a0a0a;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #222;
        margin-bottom: 20px;
    }
    
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #000; }
    ::-webkit-scrollbar-thumb { background: #004d00; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #00ff00; }
</style>

<div style="text-align:center;">
    <h1 class="mastero-title">MASTERO TOOL</h1>
    <span class="vip-badge">PREMIUM VERSION 9.0</span>
</div>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'tasks' not in st.session_state: st.session_state.tasks = {}
if 'console_logs' not in st.session_state: st.session_state.console_logs = []

# --- HELPER FUNCTIONS ---
def get_pk_time():
    tz = pytz.timezone('Asia/Karachi')
    return datetime.now(tz).strftime("%H:%M:%S")

def add_log(msg, type="info"):
    ts = get_pk_time()
    color_class = f"log-{type}"
    st.session_state.console_logs.append(f"<div class='log-entry'><span class='log-time'>[{ts}]</span> <span class='{color_class}'>{msg}</span></div>")
    if len(st.session_state.console_logs) > 200:
        st.session_state.console_logs.pop(0)

def parse_cookies(raw_data, method):
    """Parse various login inputs into a list of cookie dicts."""
    cookies_list = []
    try:
        if method == "AppState (JSON)":
            data = json.loads(raw_data)
            # Handle standard AppState format
            for item in data:
                cookie = {
                    'name': item.get('key') or item.get('name'),
                    'value': item.get('value'),
                    'domain': item.get('domain', '.facebook.com'),
                    'path': item.get('path', '/')
                }
                cookies_list.append(cookie)
        
        elif method in ["Cookie (Text)", "Token / Cookie"]:
            # Handle "name=value; name2=value2" format
            for pair in raw_data.split(';'):
                if '=' in pair:
                    name, value = pair.strip().split('=', 1)
                    cookies_list.append({'name': name, 'value': value, 'domain': '.facebook.com'})
    except Exception as e:
        add_log(f"Cookie Parsing Error: {e}", "error")
    return cookies_list

# --- BROWSER AUTOMATION ENGINE ---
def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-notifications')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    try:
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        driver = webdriver.Chrome(service=service, options=options)
    except:
        driver = webdriver.Chrome(options=options)
    return driver

def run_task(task_id, login_data, login_method, chat_id, messages, hater_name, here_name, delay):
    driver = None
    task_start_time = datetime.now()
    
    try:
        add_log(f"Task {task_id}: Initializing Engine...", "sys")
        driver = setup_driver()
        
        # 1. Login Phase
        add_log(f"Task {task_id}: Navigating to Facebook...", "info")
        driver.get("https://www.facebook.com")
        time.sleep(3)
        
        cookies = parse_cookies(login_data, login_method)
        if not cookies:
            add_log(f"Task {task_id}: Invalid Cookies/Data!", "error")
            return

        for cookie in cookies:
            try: driver.add_cookie(cookie)
            except: pass
            
        add_log(f"Task {task_id}: Cookies Injected. Refreshing...", "info")
        driver.refresh()
        time.sleep(5)
        
        # 2. Target Phase
        url = f"https://www.facebook.com/messages/t/{chat_id}"
        add_log(f"Task {task_id}: Targeting Chat {chat_id}...", "info")
        driver.get(url)
        time.sleep(10)
        
        # Popup closer
        try: driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Close"]').click()
        except: pass

        # 3. Messaging Loop
        msg_idx = 0
        sent_count = 0
        
        while st.session_state.tasks.get(task_id, {}).get('running', False):
            try:
                # Calculate Uptime
                now = datetime.now()
                uptime = str(now - task_start_time).split('.')[0]
                
                # Find Input Box
                box = None
                selectors = [
                    'div[aria-label="Message"][contenteditable="true"]',
                    'div[role="textbox"][contenteditable="true"]',
                    'div[contenteditable="true"]'
                ]
                
                for s in selectors:
                    found = driver.find_elements(By.CSS_SELECTOR, s)
                    if found and found[0].is_displayed():
                        box = found[0]; break
                
                if box:
                    # Construct Message
                    text_content = messages[msg_idx % len(messages)]
                    
                    # PREFIX (Hater Name) + MSG + SUFFIX (Here Name)
                    prefix = f"{hater_name} " if hater_name else ""
                    suffix = f" {here_name}" if here_name else ""
                    final_msg = f"{prefix}{text_content}{suffix}"
                    
                    # Send
                    try:
                        # Try natural typing first
                        actions = ActionChains(driver)
                        actions.move_to_element(box).click().send_keys(final_msg).perform()
                        time.sleep(0.5)
                        actions.send_keys(Keys.ENTER).perform()
                    except:
                        # Fallback to JS injection
                        driver.execute_script("arguments[0].focus();", box)
                        driver.execute_script(f"arguments[0].innerText = '{final_msg}';", box)
                        box.send_keys(Keys.ENTER)
                        
                    sent_count += 1
                    msg_idx += 1
                    
                    add_log(f"Task {task_id} | Sent: {sent_count} | Uptime: {uptime} | Msg: {final_msg}", "success")
                    
                    # Delay
                    time.sleep(delay)
                else:
                    add_log(f"Task {task_id}: Chatbox not found (Retrying...)", "error")
                    time.sleep(5)
                    driver.refresh()
                    time.sleep(10)
                    
            except Exception as e:
                add_log(f"Task {task_id} Error: {str(e)[:30]}", "error")
                time.sleep(5)

    except Exception as e:
        add_log(f"Task {task_id} CRITICAL FAILURE: {str(e)}", "error")
    finally:
        add_log(f"Task {task_id}: STOPPED.", "sys")
        if driver:
            try: driver.quit()
            except: pass
        # Update state to stopped
        if task_id in st.session_state.tasks:
            st.session_state.tasks[task_id]['running'] = False

# --- UI LAYOUT ---

# CONTAINER 1: CONFIGURATION
st.markdown('<div class="box-container">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🔐 LOGIN SYSTEM")
    login_method = st.selectbox("Select Login Method", 
                                ["Cookie (Text)", "Cookie (File)", "AppState (JSON)", "Token / Cookie"])
    
    login_data = ""
    if login_method == "Cookie (File)":
        uploaded_file = st.file_uploader("Upload Cookies File (.txt/.json)", type=['txt', 'json'])
        if uploaded_file:
            login_data = uploaded_file.getvalue().decode("utf-8")
    else:
        placeholder_txt = "Paste AppState JSON or Cookie String here..."
        login_data = st.text_area("Credentials Data", height=150, placeholder=placeholder_txt)

with col2:
    st.markdown("### 🎯 TARGET & MESSAGE")
    chat_id = st.text_input("Group / Chat UID", placeholder="e.g. 1000847...")
    
    c1, c2 = st.columns(2)
    with c1:
        hater_name = st.text_input("Hater Name (Prefix)", placeholder="Start msg with...")
    with c2:
        here_name = st.text_input("Here Name (Suffix)", placeholder="End msg with...")
    
    msg_file = st.file_uploader("Message List (.txt)", type="txt")
    
    c3, c4 = st.columns(2)
    with c3:
        delay = st.number_input("Speed (Seconds)", min_value=1, value=60)
    with c4:
        task_name = st.text_input("Task Name", value="Task-1")

st.markdown('</div>', unsafe_allow_html=True)

# CONTAINER 2: ACTIONS
c_act1, c_act2 = st.columns([1, 2])

with c_act1:
    st.markdown("### ⚡ CONTROLS")
    if st.button("🚀 START MASTERO"):
        if not login_data or not chat_id:
            st.error("❌ Missing Login Data or Chat ID!")
        else:
            # Prepare Messages
            msgs = ["MASTERO TOOL CHECKING"]
            if msg_file:
                raw_msgs = msg_file.getvalue().decode("utf-8").split('\n')
                msgs = [m.strip() for m in raw_msgs if m.strip()]
            
            # Create Task
            t_id = f"{task_name}_{int(time.time())}"
            st.session_state.tasks[t_id] = {'running': True, 'name': task_name}
            
            # Start Thread
            t = threading.Thread(target=run_task, args=(t_id, login_data, login_method, chat_id, msgs, hater_name, here_name, delay))
            add_script_run_ctx(t)
            t.start()
            
            st.success(f"Task {task_name} Started!")
            time.sleep(1)
            st.rerun()

with c_act2:
    st.markdown("### 📋 ACTIVE TASKS")
    if not st.session_state.tasks:
        st.info("No tasks running.")
    else:
        active_cols = st.columns(3)
        idx = 0
        for tid, tdata in st.session_state.tasks.items():
            if tdata['running']:
                with active_cols[idx % 3]:
                    st.markdown(f"**{tdata['name']}**")
                    if st.button(f"🛑 STOP", key=tid):
                        st.session_state.tasks[tid]['running'] = False
                        st.rerun()
                idx += 1

# CONTAINER 3: LIVE CONSOLE
st.markdown("### 🖥️ LIVE CONSOLE SYSTEM")
console_html = f"""
<div class="console-box">
    <div style="border-bottom: 1px dashed #333; padding-bottom: 5px; margin-bottom: 10px; color: #fff;">
        PK TIME: <span style="color:#00ff00">{get_pk_time()}</span> | 
        SYSTEM: <span style="color:#00bcff">ONLINE</span> | 
        LOCATION: <span style="color:#ffff00">PAKISTAN SERVER</span>
    </div>
    {''.join(reversed(st.session_state.console_logs))}
</div>
"""
st.markdown(console_html, unsafe_allow_html=True)

# Auto-refresh for real-time feel if tasks are running
if any(t['running'] for t in st.session_state.tasks.values()):
    time.sleep(2)
    st.rerun()
