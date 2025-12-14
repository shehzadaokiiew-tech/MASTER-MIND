import streamlit as st
import os
import json
import time
import platform
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys
import uuid
from typing import List

# --- CONFIGURATION FILE PATHS ---
# Note: In Streamlit, we will primarily use session_state for user input, 
# but these files are used for core data/messages.
TIME_PATH = Path(__file__).parent / 'time.txt'
HATERS_NAME_PATH = Path(__file__).parent / 'hatersname.txt'
CONVO_PATH = Path(__file__).parent / 'convo.txt'
MESSAGES_PATH = Path(__file__).parent / 'NP.txt'
COOKIES_JSON_PATH = Path(__file__).parent / 'cookies.json'

# Global state for process management
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'process_thread' not in st.session_state:
    st.session_state.process_thread = None
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0
if 'task_id' not in st.session_state:
    st.session_state.task_id = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# --- Custom Logger Function for Streamlit ---
def log(message, type='INFO'):
    """Logs messages to the session state log array."""
    timestamp = time.strftime("[%H:%M:%S]")
    log_entry = f"{timestamp} [{type.upper()}]: {message}"
    
    # Ensure log_messages is limited to prevent memory issues
    if len(st.session_state.log_messages) >= 50:
        st.session_state.log_messages.pop(0)
        
    st.session_state.log_messages.append(log_entry)
    
    # Note: We rely on st.rerun() or background thread updating the UI periodically
    # The dedicated placeholder will be updated in the main UI loop.

# --- CONFIGURATION & UTILITY FUNCTIONS ---

def get_next_message(messages: List[str]):
    """Rotates through the message list"""
    if 'message_rotation_index' not in st.session_state:
        st.session_state.message_rotation_index = 0
        
    if not messages or len(messages) == 0:
        return 'Hello! Default message.'
    
    message = messages[st.session_state.message_rotation_index % len(messages)]
    st.session_state.message_rotation_index += 1
    return message

def read_config_from_files():
    """Reads configuration directly from local files"""
    config = {}
    try:
        # Read delay time from time.txt
        config['delay'] = TIME_PATH.read_text(encoding='utf-8').strip() or '30' if TIME_PATH.exists() else '30'

        # Read target name from hatersname.txt (Name Prefix)
        config['haters_name'] = HATERS_NAME_PATH.read_text(encoding='utf-8').strip() if HATERS_NAME_PATH.exists() else ''

        # Read chat_id from convo.txt
        config['chat_id'] = CONVO_PATH.read_text(encoding='utf-8').strip() if CONVO_PATH.exists() else ''

        # Read messages from NP.txt
        messages = ['Hello! Default message from deployment']
        if MESSAGES_PATH.exists():
            messages_content = MESSAGES_PATH.read_text(encoding='utf-8')
            messages = [line.strip() for line in messages_content.split('\n') if line.strip()]
        config['messages'] = messages
        
    except Exception as error:
        log(f'Error reading local files: {error}', 'ERROR')
        config.update({
            'delay': '30',
            'haters_name': '',
            'chat_id': '',
            'messages': ['Hello! Default message from deployment']
        })
    return config

# --- SELENIUM AUTOMATION LOGIC ---

def setup_browser():
    """Sets up Chrome with required options for headless cloud deployment"""
    log('[🔧] Setting up Chrome browser...')
    
    chrome_options = Options()
    # Use 'new' headless mode
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)
    log('[✅] Chrome browser setup completed.')
    return driver

def send_facebook_messages_core(cookies_json_str: str, chat_id: str, haters_name: str, delay_time: str, messages: List[str]):
    """The main logic for navigating and sending messages, running in a thread."""
    
    st.session_state.message_count = 0
    st.session_state.start_time = time.time()
    
    driver = None
    
    try:
        driver = setup_browser()
        
        # 1. Add stealth settings
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
        driver.get('https://www.facebook.com/')
        time.sleep(5)
        
        # 2. Add cookies
        log(f'[🍪] Adding cookies to session...')
        try:
            cookies_data = json.loads(cookies_json_str)
            for cookie in cookies_data:
                if 'name' in cookie and 'value' in cookie and 'domain' in cookie:
                    driver.add_cookie(cookie)
            log('[✅] Cookies added.')
        except Exception as e:
            log(f'[❌] Cookie setup failed: Invalid format or error: {e}', 'ERROR')
            raise Exception(f"Cookie setup failed: {e}")

        # 3. Navigate to conversation page
        driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        time.sleep(10)
        
        # 4. Find message input
        message_input = None
        message_input_selectors = [
            'div[contenteditable="true"][role="textbox"]', 
            '[role="textbox"][contenteditable="true"]',
        ]
        
        for selector in message_input_selectors:
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element.is_displayed():
                    message_input = element
                    break
            except TimeoutException:
                continue

        if not message_input:
            raise Exception('Could not locate message input field. Facebook layout changed.')
        
        log('[✅] Message input field found.')

        # 5. Message sending loop
        float_delay = float(delay_time)
        while st.session_state.automation_running:
            base_message = get_next_message(messages)
            
            # --- CUSTOM MESSAGE FORMAT ---
            current_message = f'{haters_name} {base_message}' 
            
            # Send the message
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(driver).send_keys_to_element(message_input, current_message).perform()
            
            # Send ENTER key
            ActionChains(driver).send_keys(Keys.ENTER).perform()
            
            st.session_state.message_count += 1
            log(f'[✅] Msg {st.session_state.message_count} sent. Waiting {float_delay}s.', 'SUCCESS')
            
            # Rerun Streamlit periodically to update the UI with new logs/counts
            time.sleep(1) # Small sleep before time.sleep(float_delay) to allow RERUN
            st.rerun() 
            time.sleep(float_delay - 1)
            
    except Exception as e:
        log(f'[❌] Critical error: {e}', 'CRITICAL_ERROR')
    finally:
        st.session_state.automation_running = False
        if driver:
            try:
                driver.quit()
                log('[ℹ️] Browser closed.', 'INFO')
            except Exception:
                pass
        
        log(f"**Automation Stopped.** Total Sent: {st.session_state.message_count}", 'FINISHED')
        st.session_state.process_thread = None
        # Final rerun to update button state
        st.rerun() 

def start_automation_thread(cookies_json_str, chat_id, haters_name, delay_time, messages):
    """Starts the automation in a background thread and updates state"""
    if st.session_state.automation_running:
        log("Automation is already running.", 'WARNING')
        return

    st.session_state.log_messages = []
    st.session_state.task_id = f"T-SNAKE-{uuid.uuid4().hex[:6].upper()}"
    log(f"Starting automation process with Task ID: {st.session_state.task_id}...", 'RUNNING')
    st.session_state.automation_running = True
    
    # Start the core function in a new thread
    thread = threading.Thread(
        target=send_facebook_messages_core, 
        args=(cookies_json_str, chat_id, haters_name, delay_time, messages), 
        daemon=True
    )
    st.session_state.process_thread = thread
    thread.start()
    
    st.rerun() 

def stop_automation():
    """Stops the automation process"""
    if st.session_state.automation_running:
        st.session_state.automation_running = False
        log("Stop signal sent. Waiting for browser to close...", 'COMMAND')
        # The thread's finally block handles cleanup and final log.
        st.rerun() 
    else:
        log("Automation is not running.", 'WARNING')

# --- STREAMLIT UI (Single Page Design) ---

st.set_page_config(
    page_title="SNAKE XWD Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling for SNAKE XWD Theme
st.markdown("""
<style>
/* SNAKE XWD Theme */
body { background-color: #000000; color: #FFFFFF; font-family: 'Arial', sans-serif; }
.stApp { 
    background-color: #000000; 
    color: #FFFFFF; 
    font-family: 'Arial', sans-serif; 
}

/* Titles and Headers */
h1 { color: #FFD700; text-align: center; text-shadow: 0 0 10px #FFD700; font-size: 2.5em; text-transform: uppercase; }
h2 { color: #B22222; text-transform: uppercase; border-bottom: 2px solid #B22222; padding-bottom: 5px; }
h3 { color: #FFD700; text-transform: uppercase; }

/* Input Fields & Selects */
.stTextInput > div > div > input, .stSelectbox > div > div {
    background-color: #000;
    color: #FFF;
    border: 2px solid #FFD700; /* Yellow border for input */
    border-radius: 4px;
    padding: 10px;
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
.task-info-box {
    background-color: #333333; /* Dark Grey for background */
    border: 2px solid #FFD700;
    padding: 15px;
    border-radius: 8px;
    color: #FFFFFF;
    font-family: 'Consolas', monospace;
}
.task-info-box p { margin: 5px 0; }
.task-info-box .value { color: #FFD700; font-weight: bold; }

</style>
""", unsafe_allow_html=True)


# --- UI START ---

st.markdown("<h1>👑 SNAKE XWD COOKIE WEB 👑</h1>", unsafe_allow_html=True)
st.markdown("---")

# 1. Configuration Files (Read data from files)
config_data = read_config_from_files()

# --- INPUT & PARAMETERS SECTION ---
st.header("⚙️ INPUT & PARAMETERS")

# Emulate the Input Fields from the original design (using placeholders for Last Here Name/Select Mode)
col_input1, col_input2 = st.columns([1, 1])

with col_input1:
    st.markdown("### 🍪 COOKIE DATA")
    # File Uploader
    uploaded_cookies = st.file_uploader(
        "UPLOAD COOKIE FILE (cookies.json)", 
        type=["json"]
    )
    # Target Chat ID
    chat_id = st.text_input(
        "TARGET UID DALO (from convo.txt)",
        value=config_data['chat_id']
    )
    # Haters Name / Prefix
    haters_name = st.text_input(
        "ENTER YOUR HEATER NAME (from hatersname.txt)",
        value=config_data['haters_name']
    )

with col_input2:
    st.markdown("### ⏲️ TIMING & PREFIX")
    # Delay Time
    delay_time = st.text_input(
        "ENTER TIME ⏰ (seconds)",
        value=config_data['delay']
    )
    # Placeholders to match the design fields
    st.selectbox("SELECT MODE", options=["SINGLE TOKEN", "MULTI TOKEN FILE"], disabled=True, index=0)
    st.text_input("SINGLE COOKIE DALO", placeholder="PASTE COOKIE HERE IF SINGLE MODE", disabled=True)
    st.text_input("ENTER LAST HERE NAME", placeholder="SECOND PREFIX (DISABLED)", disabled=True)
    

# --- MESSAGE PREVIEW (MSG FILE) ---
st.markdown("---")
st.header("MSG FILE (NP.TXT) PREVIEW")
messages_list = config_data['messages']
if messages_list:
    st.text_area("LIST OF MESSAGES:", value='\n'.join(messages_list), height=100, disabled=True)
    st.caption(f"**Total Messages Loaded:** {len(messages_list)}. **Final Format:** `{haters_name}` + `[Message]`")
else:
    st.error("NP.txt file is empty or missing. Messages cannot be sent.")

st.markdown("---")


# --- CONTROL SECTION (Start/Stop/Task Info) ---
st.header("3. 🚀 TASK CONTROL")

col_control1, col_control2 = st.columns([1, 1])

with col_control1:
    # START BUTTON LOGIC
    if st.session_state.automation_running:
        st.button("STOP TASK ⏸️", on_click=stop_automation, use_container_width=True)
    else:
        # Load cookies from uploader or file
        final_cookies_str = st.session_state.get('cookies_json_str', '')
        if uploaded_cookies and 'cookies_data' in locals():
             final_cookies_str = json.dumps(cookies_data)
        elif COOKIES_JSON_PATH.exists():
            final_cookies_str = config_data.get('cookies_json_str', '') # Already loaded in initial run

        
        if final_cookies_str and chat_id and delay_time and messages_list:
            st.button(
                "START RUN ✅", 
                on_click=start_automation_thread, 
                args=(final_cookies_str, chat_id, haters_name, delay_time, messages_list), 
                use_container_width=True
            )
        else:
            st.warning("Please ensure Cookies, Target UID, and Messages are loaded.")
            st.button("START RUN ✅", disabled=True, use_container_width=True)

with col_control2:
    # TASK INFORMATION BOX
    st.markdown("<h3>📊 TASK INFORMATION</h3>", unsafe_allow_html=True)
    if st.session_state.automation_running and st.session_state.start_time:
        
        elapsed_time = time.time() - st.session_state.start_time
        time_display = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
        
        st.markdown(f"""
        <div class="task-info-box">
            <p><strong>TASK ID:</strong> <span class="value">{st.session_state.task_id}</span></p>
            <p><strong>STATUS:</strong> <span class="value" style="color:#00FF00;">RUNNING</span></p>
            <p><strong>TIME RUN:</strong> <span class="value">{time_display}</span></p>
            <p><strong>MSGS SENT:</strong> <span class="value">{st.session_state.message_count}</span></p>
            <p><strong>TARGET:</strong> <span class="value">{chat_id}</span></p>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.message_count > 0:
        st.markdown(f"""
        <div class="task-info-box">
            <p><strong>STATUS:</strong> <span class="value" style="color:#B22222;">STOPPED/FINISHED</span></p>
            <p><strong>MSGS SENT:</strong> <span class="value">{st.session_state.message_count}</span></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Task will appear here upon START RUN.")


# --- LOGS SECTION (ACTIVITY CONSOLE) ---
st.markdown("---")
st.header("4. 📜 ACTIVITY CONSOLE (GLOBAL LOG)")

# Placeholders for the manual STOP TASK feature (as requested)
st.text_input("ENTER STOP TASK 💥", placeholder="NOT FUNCTIONAL IN STREAMLIT VERSION", disabled=True)

st.session_state.log_messages_placeholder = st.empty()

# Update the log display in the main UI loop
with st.session_state.log_messages_placeholder.container():
    st.code('\n'.join(st.session_state.log_messages), language='text')

# Check if thread finished unexpectedly
if st.session_state.process_thread and not st.session_state.process_thread.is_alive() and st.session_state.automation_running:
    st.session_state.automation_running = False
    log("Automation thread stopped unexpectedly. Check logs for critical error.", 'FATAL')
    st.rerun()

