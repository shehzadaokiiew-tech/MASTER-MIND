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
import psutil
import sys
import uuid
import base64
from typing import List

# --- CONFIGURATION FILE PATHS ---
# Note: In Streamlit, we will primarily use session_state for user input, 
# but these files are used for core data/messages.
TIME_PATH = Path(__file__).parent / 'time.txt'
HATERS_NAME_PATH = Path(__file__).parent / 'hatersname.txt'
CONVO_PATH = Path(__file__).parent / 'convo.txt'
MESSAGES_PATH = Path(__file__).parent / 'NP.txt'
COOKIES_JSON_PATH = Path(__file__).parent / 'cookies.json'

# Global state for process management (for Flask was active_processes)
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'process_thread' not in st.session_state:
    st.session_state.process_thread = None
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []

# --- Custom Logger Function for Streamlit ---
def log(message):
    timestamp = time.strftime("[%H:%M:%S]")
    st.session_state.log_messages.append(f"{timestamp} {message}")
    # Force rerun to update the log display
    st.session_state.log_messages_placeholder.empty()
    with st.session_state.log_messages_placeholder:
        st.code('\n'.join(st.session_state.log_messages[-20:]), language='text')

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
        log(f'Error reading local files: {error}')
        config.update({
            'delay': '30',
            'haters_name': '',
            'chat_id': '',
            'messages': ['Hello! Default message from deployment']
        })
    return config

# --- SELENIUM AUTOMATION LOGIC (Simplified and Adapted) ---

# (Check_vps_only logic is removed as Streamlit is often run locally or on platforms that handle this)

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
    
    # Optional: Add service argument for chromium-driver path if needed for Render/VPS
    # try:
    #     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # except:
    driver = webdriver.Chrome(options=chrome_options) # Fallback to default
    driver.set_window_size(1920, 1080)
    log('[✅] Chrome browser setup completed')
    return driver

def send_facebook_messages_core(cookies_json_str: str, chat_id: str, haters_name: str, delay_time: str, messages: List[str]):
    """The main logic for navigating and sending messages, running in a thread."""
    
    if not st.session_state.automation_running:
        log("Automation cancelled before start.")
        return

    driver = None
    message_count = 0
    
    try:
        driver = setup_browser()
        
        # 1. Add stealth settings
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
        
        # 2. Navigate to Facebook main page
        driver.get('https://www.facebook.com/')
        time.sleep(5)
        
        # 3. Add cookies
        log(f'[🍪] Adding cookies to session...')
        try:
            cookies_data = json.loads(cookies_json_str)
            for cookie in cookies_data:
                # Need to handle potential KeyError if essential fields are missing
                if 'name' in cookie and 'value' in cookie and 'domain' in cookie:
                    driver.add_cookie(cookie)
            log('[✅] Cookies added.')
        except json.JSONDecodeError:
            log('[❌] Error: Invalid JSON in Cookies input.')
            raise Exception("Invalid Cookies format")
        except Exception as e:
            log(f'[❌] Error adding cookies: {e}')
            raise Exception(f"Cookie setup failed: {e}")

        # 4. Navigate to conversation page
        driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        time.sleep(10)
        
        # 5. Dismiss pop-ups (simplified)
        try:
            driver.execute_script("document.querySelectorAll('[aria-label=\"Close\"], [aria-label=\"Not Now\"]').forEach(btn => btn.click());")
        except Exception:
            pass

        # 6. Find message input
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

        # 7. Message sending loop
        float_delay = float(delay_time)
        while st.session_state.automation_running and message_count < 50: # Safety limit
            base_message = get_next_message(messages)
            
            # --- CUSTOM MESSAGE FORMAT ---
            # Haters Name + Last Name (file content) + Message
            # Note: Since we don't know what "Last Name" refers to in the original file, 
            # we'll assume the entire 'haters_name' content is the name prefix.
            
            # Use the entire haters_name file content as the prefix
            current_message = f'{haters_name} {base_message}' 
            
            # Send the message
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(driver).send_keys_to_element(message_input, current_message).perform()
            
            # Send ENTER key
            ActionChains(driver).send_keys(Keys.ENTER).perform()
            
            message_count += 1
            log(f'[✅] Message {message_count} sent: "{current_message[:30]}..." Waiting {float_delay}s.')
            
            # Update status in Streamlit
            st.session_state.log_messages_placeholder.empty()
            with st.session_state.log_messages_placeholder:
                st.code('\n'.join(st.session_state.log_messages[-20:]), language='text')
                st.info(f"**Messages Sent:** {message_count}")
                
            time.sleep(float_delay)
            
        if message_count >= 50:
            log("[🛑] Safety limit (50 messages) reached. Stopping.")

    except Exception as e:
        log(f'[❌] Critical error: {e}')
    finally:
        st.session_state.automation_running = False
        if driver:
            try:
                driver.quit()
                log('[ℹ️] Browser closed.')
            except Exception:
                pass
        
        # Final status update
        st.session_state.log_messages_placeholder.empty()
        with st.session_state.log_messages_placeholder:
            st.code('\n'.join(st.session_state.log_messages[-20:]), language='text')
            st.error(f"**Automation Stopped.** Total Sent: {message_count}")
        st.session_state.process_thread = None
        # Rerun Streamlit to update button state
        st.rerun() 

def start_automation_thread(cookies_json_str, chat_id, haters_name, delay_time, messages):
    """Starts the automation in a background thread and updates state"""
    if st.session_state.automation_running:
        log("Automation is already running.")
        return

    st.session_state.log_messages = []
    log("Starting automation process...")
    st.session_state.automation_running = True
    
    # Start the core function in a new thread
    thread = threading.Thread(
        target=send_facebook_messages_core, 
        args=(cookies_json_str, chat_id, haters_name, delay_time, messages), 
        daemon=True
    )
    st.session_state.process_thread = thread
    thread.start()
    
    st.rerun() # Rerun Streamlit to show the running state

def stop_automation():
    """Stops the automation process"""
    if st.session_state.automation_running:
        st.session_state.automation_running = False
        log("Stop signal sent. Waiting for browser to close...")
        if st.session_state.process_thread and st.session_state.process_thread.is_alive():
            # The thread's finally block will handle cleanup
            pass
        st.rerun() # Rerun to update button state
    else:
        log("Automation is not running.")


# --- STREAMLIT UI (Single Page Design) ---

st.set_page_config(
    page_title="Facebook Automation Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling (Thoda behtar design ke liye)
st.markdown("""
<style>
.css-1d391kg { padding-top: 2rem; } /* Main area top padding */
.css-1avcm0n { background-color: #0b1e42; } /* Sidebar background if used */
h1, h2, h3, h4 { color: #1E90FF; } /* Blue headings */
.stButton>button {
    background-color: #4CAF50;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 10px 20px;
}
.stButton>button:hover {
    background-color: #45a049;
}
</style>
""", unsafe_allow_html=True)


st.title("🚀 Facebook Message Automation Tool")
st.markdown("---")

# 1. Configuration Files (Read data from files)
config_data = read_config_from_files()

# --- INPUT SECTION (Cookie Input Upar Aagaya) ---
st.header("1. Core Setup (Required Files Data)")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🍪 Facebook Cookies (`cookies.json`)")
    # File Uploader
    uploaded_cookies = st.file_uploader(
        "Upload your cookies.json file", 
        type=["json"], 
        help="Please upload the cookies file for login."
    )
    if uploaded_cookies:
        try:
            cookies_data = json.load(uploaded_cookies)
            st.session_state.cookies_json_str = json.dumps(cookies_data)
            st.success("Cookies file uploaded successfully!")
        except Exception:
            st.error("Invalid cookies.json file format.")
            st.session_state.cookies_json_str = ""
    elif COOKIES_JSON_PATH.exists():
        try:
            with open(COOKIES_JSON_PATH, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
                st.session_state.cookies_json_str = json.dumps(cookies_data)
                st.info("Using cookies from local `cookies.json` file.")
        except Exception:
            st.warning("`cookies.json` file is present but could not be loaded.")
            st.session_state.cookies_json_str = ""
    else:
        st.session_state.cookies_json_str = ""

with col2:
    st.markdown("### 🆔 Target & Timing")
    
    # Target Chat ID
    chat_id = st.text_input(
        "Target Chat ID (from `convo.txt`)",
        value=config_data['chat_id'],
        help="The unique ID of the Facebook chat thread (e.g., 1000123456789)."
    )
    
    # Delay Time
    delay_time = st.text_input(
        "Delay (Seconds) (from `time.txt`)",
        value=config_data['delay'],
        help="Wait time between sending each message."
    )
    
    # Haters Name / Prefix
    haters_name = st.text_input(
        "Message Prefix (from `hatersname.txt`)",
        value=config_data['haters_name'],
        help="This text will be prepended to every message sent."
    )

st.markdown("---")

# --- MESSAGE PREVIEW SECTION ---
st.header("2. Message Content Preview (`NP.txt`)")

# Display messages for confirmation
messages_list = config_data['messages']
if messages_list:
    st.text_area("List of Messages:", value='\n'.join(messages_list), height=150, disabled=True)
    st.info(f"Total {len(messages_list)} messages loaded.")
    st.caption(f"**Final Message Format:** `{haters_name}` + `[One Message from List]`")
else:
    st.error("NP.txt file is empty or missing. Please ensure it contains messages.")

st.markdown("---")


# --- CONTROL SECTION (Start/Stop Buttons) ---
st.header("3. Automation Control")

if st.session_state.automation_running:
    # RUNNING STATE
    st.session_state.log_placeholder = st.empty()
    st.error("Automation is currently RUNNING...")
    
    stop_button = st.button("🔴 Stop Automation", on_click=stop_automation, use_container_width=True)
    
    # Check if thread finished unexpectedly
    if st.session_state.process_thread and not st.session_state.process_thread.is_alive():
        st.session_state.automation_running = False
        st.warning("Automation stopped unexpectedly. Check logs for error.")
        st.rerun()

else:
    # STOPPED STATE
    st.session_state.log_placeholder = st.empty()
    if st.session_state.cookies_json_str and chat_id and delay_time and messages_list:
        start_button = st.button(
            "🟢 Start Automation", 
            on_click=start_automation_thread, 
            args=(st.session_state.cookies_json_str, chat_id, haters_name, delay_time, messages_list), 
            use_container_width=True
        )
    else:
        st.warning("Please ensure Cookies, Chat ID, and Messages are loaded before starting.")
        st.button("🟢 Start Automation", disabled=True, use_container_width=True)

st.markdown("---")

# --- LOGS SECTION ---
st.header("4. Live Automation Logs")
st.session_state.log_messages_placeholder = st.empty()

# Initialize log display on first run
if not st.session_state.log_messages:
    with st.session_state.log_messages_placeholder:
        st.info("Press 'Start Automation' to view real-time logs here.")

