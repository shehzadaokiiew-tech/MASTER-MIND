import streamlit as st
import os
import json
import time
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import uuid
from typing import List

# --- CONFIGURATION FILE PATHS (Only for reading initial messages) ---
MESSAGES_PATH = Path(__file__).parent / 'NP.txt'

# --- Global State for Multiple Task Management ---
if 'active_tasks' not in st.session_state:
    st.session_state.active_tasks = {} # {task_id: {'thread': thread, 'running': bool, 'logs': list, 'count': int, 'config': dict}}
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = ["[SYSTEM]: Welcome to SNAKE XWD Cookie Tool. Ready to run!"]

# --- Custom Logger Function for Streamlit ---
def log(message, task_id=None, type='INFO'):
    """Logs messages globally and to a specific task."""
    timestamp = time.strftime("[%H:%M:%S]")
    log_entry = f"{timestamp} [{task_id if task_id else 'SYSTEM'} / {type.upper()}]: {message}"
    
    # 1. Global Log
    if len(st.session_state.log_messages) >= 50:
        st.session_state.log_messages.pop(0)
    st.session_state.log_messages.append(log_entry)
    
    # 2. Task-specific Log 
    if task_id and task_id in st.session_state.active_tasks:
        task_logs = st.session_state.active_tasks[task_id]['logs']
        if len(task_logs) >= 50:
            task_logs.pop(0)
        task_logs.append(log_entry)
    
    # Force rerun to update the logs/UI (Streamlit's way to update UI from thread)
    st.rerun() 

# --- CONFIGURATION & UTILITY FUNCTIONS ---

def get_next_message(messages: List[str], task_id: str):
    """Rotates through the message list for a specific task."""
    task_state = st.session_state.active_tasks[task_id]
    
    if 'rotation_index' not in task_state:
        task_state['rotation_index'] = 0
        
    if not messages:
        return 'Hello! Default message.'
    
    message = messages[task_state['rotation_index'] % len(messages)]
    task_state['rotation_index'] += 1
    st.session_state.active_tasks[task_id]['rotation_index'] = task_state['rotation_index']
    return message

def read_messages_from_file():
    """Reads messages from the local NP.txt file."""
    messages = ['Hello! Default message from deployment']
    if MESSAGES_PATH.exists():
        try:
            messages_content = MESSAGES_PATH.read_text(encoding='utf-8')
            messages = [line.strip() for line in messages_content.split('\n') if line.strip()]
        except Exception as error:
            log(f'Error reading local messages file: {error}', type='ERROR')
    return messages

# --- SELENIUM AUTOMATION LOGIC (Working Core is retained) ---

def setup_browser(task_id):
    """Sets up Chrome with required options."""
    log(f'[🔧] Setting up Chrome browser for Task {task_id}...', task_id, 'SETUP')
    # ... (Rest of setup_browser function is unchanged) ...
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)
    log(f'[✅] Chrome browser setup completed.', task_id, 'SUCCESS')
    return driver

def send_facebook_messages_core(task_id: str, cookies_json_str: str, chat_id: str, haters_name: str, last_name: str, delay_time: str, messages: List[str]):
    """The main logic for navigating and sending messages, running in a thread."""
    
    task_state = st.session_state.active_tasks[task_id]
    driver = None
    
    try:
        driver = setup_browser(task_id)
        
        # 1. Add cookies (Retaining the original JSON handling logic)
        log(f'[🍪] Adding cookies to session...', task_id)
        
        cookies_data = json.loads(cookies_json_str)
            
        driver.get('https://www.facebook.com/')
        time.sleep(3)

        for c in cookies_data:
            # Need to handle potential KeyError if essential fields are missing (Original logic)
            if 'name' in c and 'value' in c and 'domain' in c: 
                driver.add_cookie(c)
        log('[✅] Cookies added.', task_id, 'SUCCESS')

        # 2. Navigate to conversation page
        driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        time.sleep(8)
        
        # 3. Find message input
        message_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][role="textbox"]'))
        )
        log('[✅] Message input field found.', task_id, 'SUCCESS')

        # 4. Message sending loop
        float_delay = float(delay_time)
        while task_state['running']:
            base_message = get_next_message(messages, task_id)
            
            # --- CUSTOM MESSAGE FORMAT (Using all fields) ---
            current_message = f'{haters_name} {last_name} {base_message}' 
            
            # Send the message
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(driver).send_keys_to_element(message_input, current_message).perform()
            ActionChains(driver).send_keys(Keys.ENTER).perform()
            
            st.session_state.active_tasks[task_id]['count'] += 1
            log(f'[✅] Msg {st.session_state.active_tasks[task_id]["count"]} sent. Waiting {float_delay}s.', task_id, 'SUCCESS')
            
            time.sleep(float_delay)
            
    except Exception as e:
        log(f'[❌] Critical error: {e}', task_id, 'CRITICAL_ERROR')
    finally:
        st.session_state.active_tasks[task_id]['running'] = False
        if driver:
            try:
                driver.quit()
                log('[ℹ️] Browser closed.', task_id, 'INFO')
            except Exception:
                pass
        
        log(f"Task {task_id} Stopped. Total Sent: {st.session_state.active_tasks[task_id]['count']}", 'SYSTEM', 'FINISHED')
        st.rerun() 

def start_new_task(cookie_json_str, chat_id, haters_name, last_name, delay_time):
    """Initializes and starts a new task in a background thread."""
    if not cookie_json_str or not chat_id or not haters_name or not delay_time:
        log("All required fields must be filled: Cookie (JSON), Target UID, Name, and Speed.", 'SYSTEM', 'ERROR')
        return

    messages = read_messages_from_file()
    if not messages:
        log("Message file (NP.txt) is empty. Cannot start task.", 'SYSTEM', 'ERROR')
        return

    task_id = f"T-SNAKE-{uuid.uuid4().hex[:4].upper()}"
    log(f"Task ID {task_id} generated. Starting process...", 'SYSTEM', 'RUNNING')

    # Initialize task state
    st.session_state.active_tasks[task_id] = {
        'running': True,
        'logs': [f"Task {task_id} created."],
        'count': 0,
        'start_time': time.time(),
        'config': {'uid': chat_id, 'name': haters_name, 'speed': delay_time, 'last_name': last_name}
    }

    # Start the core function in a new thread
    thread = threading.Thread(
        target=send_facebook_messages_core, 
        args=(task_id, cookie_json_str, chat_id, haters_name, last_name, delay_time, messages), 
        daemon=True
    )
    st.session_state.active_tasks[task_id]['thread'] = thread
    thread.start()
    
    st.rerun() 

def stop_task_by_id(task_id):
    """Sends a stop signal to a specific task."""
    if task_id in st.session_state.active_tasks:
        if st.session_state.active_tasks[task_id]['running']:
            st.session_state.active_tasks[task_id]['running'] = False
            log(f"Stop signal sent to Task ID {task_id}.", 'SYSTEM', 'COMMAND')
            st.rerun()
        else:
            log(f"Task ID {task_id} is already stopped.", 'SYSTEM', 'WARNING')
    else:
        log(f"Task ID {task_id} not found.", 'SYSTEM', 'ERROR')


# --- STREAMLIT UI (Single Page Design) ---

st.set_page_config(
    page_title="SNAKE XWD Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling for SNAKE XWD Theme (Refined for better visibility)
st.markdown("""
<style>
/* SNAKE XWD Theme */
.stApp { 
    background-color: #000000; 
    color: #FFFFFF; 
    font-family: 'Arial', sans-serif; 
}

/* Titles and Headers */
h1 { color: #FFD700; text-align: center; text-shadow: 0 0 8px #FFD700; font-size: 2.5em; text-transform: uppercase; border-bottom: 2px solid #B22222; padding-bottom: 5px; }
h3 { color: #FFD700; text-transform: uppercase; font-size: 1.5em; }

/* Input Fields & Selects */
.stTextInput > div > div > input, .stSelectbox > div > div, .stTextArea > div > div {
    background-color: #000;
    color: #FFF;
    border: 2px solid #FFD700; /* Yellow border for input */
    border-radius: 4px;
    padding: 10px;
    text-transform: uppercase;
}
label { font-weight: bold; color: #FFF; text-transform: uppercase; }

/* Buttons */
.stButton button {
    background-color: #B22222; /* Red Button */
    color: white;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 15px 20px;
    font-size: 1.1em;
    text-transform: uppercase;
    box-shadow: 0 4px #8B0000;
}
.stButton button:hover {
    background-color: #8B0000;
    box-shadow: 0 2px #6B0000;
}
.stButton button:active {
    box-shadow: none;
    transform: translateY(2px);
}

/* Console/Log */
.stCode {
    background-color: #0A0A0A;
    border: 1px solid #333;
    color: #00FF00; /* Green terminal text */
    font-family: 'Consolas', monospace;
    font-size: 0.9em;
    padding: 10px;
    height: 250px;
    overflow-y: scroll;
}

/* Task Info Box - Custom Styling */
.task-box {
    background-color: #1A1A1A; /* Darker than background */
    border: 2px solid #B22222;
    padding: 10px;
    margin-bottom: 15px;
    border-radius: 8px;
}
.task-box h4 {
    color: #FFD700;
    margin-bottom: 5px;
}
.task-box .status-running {
    color: #00FF00;
    font-weight: bold;
}
.task-box .status-stopped {
    color: #B22222;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# --- UI START ---

st.markdown("<h1>👑 SNAKE XWD COOKIE WEB 👑</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- 1. INPUT & PARAMETERS SECTION ---
st.markdown("<h3>⚙️ INPUT & PARAMETERS</h3>", unsafe_allow_html=True)

col_input1, col_input2 = st.columns([1, 1])

with col_input1:
    # 1. COOKIE PASTE BOX (Accepts JSON Array String)
    cookie_json_input = st.text_area(
        "COOKIE PASTE BOX (SINGLE TOKEN DALO - JSON FORMAT)",
        placeholder="PASTE YOUR COOKIE JSON ARRAY STRING HERE...",
        height=100
    )
    # 2. 1ST HATERS NAME
    haters_name_input = st.text_input(
        "1ST HATERS NAME",
        placeholder="[END TO END PRINCE HERE]"
    )

with col_input2:
    # 3. GROUP UID BOX
    chat_id_input = st.text_input(
        "TARGET UID BOX (GROUP/INBOX UID)",
        placeholder="9874135895969256"
    )
    # 4. LAST HERE NAME BOX
    last_name_input = st.text_input(
        "LAST HERE NAME BOX",
        placeholder="SECOND PREFIX NAME"
    )
    # 5. SPEED BOX
    speed_input = st.text_input(
        "SPEED BOX (ENTER TIME ⏰ SECONDS)",
        placeholder="10",
        value="10"
    )

# 6. MESSAGE FILE OPTION (Show Preview)
st.markdown("---")
st.markdown("<h3>MSG FILE (NP.TXT) PREVIEW</h3>", unsafe_allow_html=True)
messages_list = read_messages_from_file()
if messages_list:
    st.success(f"MSG FILE (NP.TXT) Loaded: {len(messages_list)} messages.")
else:
    st.error("MSG FILE (NP.TXT) Empty or Missing.")

st.markdown("---")

# --- 2. START CONTROL ---
st.markdown("<h3>🚀 TASK CONTROL</h3>", unsafe_allow_html=True)

if st.button("START RUN ✅", use_container_width=True):
    start_new_task(cookie_json_input, chat_id_input, haters_name_input, last_name_input, speed_input)

st.markdown("---")

# --- 3. MULTIPLE TASK MANAGEMENT (Task Boxes) ---
st.markdown("<h3>📊 ACTIVE TASKS</h3>", unsafe_allow_html=True)

# Stop Task by ID input (as requested for manual stop)
stop_id_input = st.text_input("ENTER STOP TASK 💥", placeholder="ENTER TASK ID TO STOP MANUALLY (E.G., T-SNAKE-A1B2)")
if st.button("STOP TASK BY ID", key="manual_stop", type="secondary"):
    stop_task_by_id(stop_id_input.strip())

st.markdown("---")

if st.session_state.active_tasks:
    
    # Sort tasks by running status first
    sorted_tasks = dict(sorted(st.session_state.active_tasks.items(), key=lambda item: item[1]['running'], reverse=True))

    for task_id, task_state in sorted_tasks.items():
        running = task_state['running']
        
        with st.container():
            col_t1, col_t2, col_t3 = st.columns([1, 2, 1])
            
            with col_t1:
                st.markdown(f"**{task_id}**")
                
            with col_t2:
                status_class = "status-running" if running else "status-stopped"
                status_text = "RUNNING" if running else "STOPPED"
                
                elapsed_time = time.time() - task_state['start_time']
                time_display = time.strftime('%M:%S', time.gmtime(elapsed_time))
                
                st.markdown(f"""
                <div class="task-box">
                    <p style='margin:0;'>Status: <span class="{status_class}">{status_text}</span></p>
                    <p style='margin:0;'>Sent: <span style='color:#FFD700;'>{task_state['count']}</span> | Time: <span style='color:#FFD700;'>{time_display}</span></p>
                    <p style='margin:0;'>UID: {task_state['config']['uid'][:8]}... | Name: {task_state['config']['name'][:10]}...</p>
                </div>
                """, unsafe_allow_html=True)

            with col_t3:
                if running:
                    # STOP button for individual task
                    st.button("STOP", key=f"stop_{task_id}", on_click=stop_task_by_id, args=(task_id,), type="primary")
                else:
                    # Placeholder for Delete/Restart buttons
                    st.button("DELETE", key=f"delete_{task_id}", disabled=True)
            
            # --- TASK-SPECIFIC CONSOLE ---
            if running:
                st.markdown(f"**Live Console for {task_id}:**", unsafe_allow_html=True)
                st.code('\n'.join(task_state['logs'][-10:]), language='text', height=150)
                st.markdown("---")
else:
    st.info("No active tasks running.")


# --- 4. GLOBAL CONSOLE ---
st.markdown("---")
st.markdown("<h3>📜 GLOBAL ACTIVITY CONSOLE</h3>", unsafe_allow_html=True)
st.code('\n'.join(st.session_state.log_messages), language='text')

