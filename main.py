import streamlit as st
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta
# Use try-except for webdriver_manager as it might not be needed/available on all systems
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.core.os_manager import ChromeType
    _WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    _WEBDRIVER_MANAGER_AVAILABLE = False
    st.warning("`webdriver-manager` not found. Ensure ChromeDriver is in PATH or provide path manually.")

# For Streamlit's session state in threads
from streamlit.runtime.scriptrunner import add_script_run_ctx

# --- Global Flags and Session State Initialization ---
st.set_page_config(page_title="SNAKE XD TOOL", layout="wide", initial_sidebar_state="expanded")

if 'running' not in st.session_state: st.session_state.running = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'count' not in st.session_state: st.session_state.count = 0
if 'start_time' not in st.session_state: st.session_state.start_time = None # For uptime
if 'log_area_placeholder' not in st.session_state: st.session_state.log_area_placeholder = None

# --- Custom CSS for VIP Styling ---
st.markdown("""
    <style>
    /* General Body Styling */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #e0e0e0;
        background-color: #1a1a1a;
    }

    /* Main Container for overall layout */
    .main-container {
        padding: 20px;
        max-width: 1200px;
        margin: auto;
    }

    /* Title Box */
    .title-box {
        background: linear-gradient(90deg, #1f1f1f, #2a2a2a, #1f1f1f);
        border: 2px solid #00FFFF; /* Cyan border */
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.4); /* Cyan glow */
    }
    .vip-title {
        color: #00FFFF; /* Cyan */
        font-size: 3.5em;
        font-weight: bold;
        text-shadow: 0 0 10px #00FFFF;
        margin: 0;
    }
    .vip-subtitle {
        color: #00FF00; /* Green */
        font-size: 1.2em;
        letter-spacing: 2px;
        margin-top: 5px;
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 8px 15px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 1.1em;
        margin: 5px;
        text-transform: uppercase;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }

    /* Terminal Window for Logs */
    .terminal-window {
        background-color: #0d0d0d;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
        min-height: 250px;
        max-height: 500px; /* Limit height for scrolling */
        overflow-y: auto; /* Enable vertical scrolling */
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.9em;
        line-height: 1.4;
        color: #00FF00; /* Green text */
        margin-top: 30px;
        box-shadow: inset 0 0 10px rgba(0,255,0,0.2); /* Inner glow */
    }
    .log-line {
        white-space: pre-wrap; /* Preserve whitespace and wrap text */
        word-break: break-all; /* Break long words */
        margin-bottom: 2px;
    }
    /* Specific log message colors */
    .log-line.info { color: #ADD8E6; } /* Light Blue */
    .log-line.success { color: #00FF00; } /* Green */
    .log-line.warning { color: #FFFF00; } /* Yellow */
    .log-line.error { color: #FF0000; } /* Red */
    .log-line.system { color: #00FFFF; } /* Cyan */

    /* Streamlit widgets styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stFileUploader>div>div>button {
        background-color: #2a2a2a;
        color: #e0e0e0;
        border: 1px solid #444;
        border-radius: 5px;
    }
    .stButton>button {
        background-color: #00FFFF; /* Cyan */
        color: black;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        transition: background-color 0.3s, color 0.3s;
    }
    .stButton>button:hover {
        background-color: #00FF00; /* Green on hover */
        color: black;
    }
    .stButton>button:disabled {
        background-color: #555;
        color: #aaa;
    }
    label {
        color: #00FFFF !important; /* Cyan for labels */
        font-weight: bold;
    }
    .css-1d391kg p { /* For st.info, st.warning etc. text */
        color: #e0e0e0 !important;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1em;
        color: #00FFFF; /* Cyan tab labels */
    }

    /* Uptime/Time Display */
    .time-status-box {
        background-color: #1f1f1f;
        border: 1px solid #00FFFF;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
    }
    .time-status-box h3 {
        color: #00FF00; /* Green */
        margin: 5px 0;
    }
    .time-status-box p {
        color: #e0e0e0;
        margin: 2px 0;
    }
    </style>
""", unsafe_allow_html=True)


# --- Utility Functions ---
def get_pakistan_time():
    now_utc = datetime.utcnow()
    pakistan_time = now_utc + timedelta(hours=5) # Pakistan Standard Time (PKT) is UTC+5
    return pakistan_time.strftime("%d %B, %Y %I:%M:%S %p PKT")

def format_uptime(start_time):
    if not start_time:
        return "Inactive"
    elapsed_time = datetime.now() - start_time
    hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def add_log(msg, level="info"):
    # Ensure logs is initialized if this is called before main UI setup
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    
    ts = datetime.now().strftime("[%H:%M:%S]")
    log_entry = f"<div class='log-line {level}'>{ts} {msg}</div>"
    st.session_state.logs.append(log_entry)
    if len(st.session_state.logs) > 100:
        st.session_state.logs.pop(0) # Keep log history limited

    # Update log area if placeholder is available
    if st.session_state.log_area_placeholder:
        with st.session_state.log_area_placeholder:
            st.markdown('<div class="terminal-window">', unsafe_allow_html=True)
            for log_item in reversed(st.session_state.logs): # Show latest first
                st.markdown(log_item, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


# --- BROWSER SETUP ---
@st.cache_resource
def setup_browser():
    options = Options()
    options.add_argument('--headless') # Run in background without GUI
    options.add_argument('--no-sandbox') # Essential for many cloud environments
    options.add_argument('--disable-dev-shm-usage') # Overcomes shared memory issues
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) # Hide automation detection
    options.add_experimental_option('useAutomationExtension', False)

    try:
        if _WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        else:
            # Fallback if webdriver_manager is not installed
            # User must ensure chromedriver is in PATH or provide path
            add_log("`webdriver-manager` not available. Assuming chromedriver is in PATH or configured.", level="warning")
            service = Service() # Assumes chromedriver is found in PATH
        
        driver = webdriver.Chrome(service=service, options=options)
        add_log("Browser setup complete.", level="success")
        return driver
    except Exception as e:
        add_log(f"Failed to set up browser: {e}", level="error")
        return None

# --- MAIN LOGIC ---
def start_process(chat_ids, prefix, suffix, delay_seconds, cookie_string, messages):
    driver = None
    try:
        add_log("🚀 SNAKE XD SYSTEM STARTED...", level="system")
        driver = setup_browser()
        if not driver:
            add_log("🛑 Browser could not be initialized. Aborting.", level="error")
            st.session_state.running = False
            return

        add_log("🌐 Opening Facebook to apply cookies...", level="info")
        driver.get("https://www.facebook.com")
        time.sleep(2) # Give page some time to load

        # Parse and add cookies
        parsed_cookies = {}
        for part in cookie_string.split(';'):
            if '=' in part:
                name, value = part.strip().split('=', 1)
                parsed_cookies[name] = value

        if not parsed_cookies:
            add_log("⚠️ No valid cookies found after parsing.", level="warning")
            # Attempt to add all parts as cookies if simple split failed
            for cookie_part in cookie_string.split(';'):
                cookie_part = cookie_part.strip()
                if cookie_part:
                    try:
                        driver.add_cookie({'name': cookie_part.split('=',1)[0], 'value': cookie_part.split('=',1)[1], 'domain': '.facebook.com'})
                    except Exception as e:
                        add_log(f"Failed to add part of cookie: {cookie_part[:20]}... Error: {e}", level="warning")
        else:
            for name, value in parsed_cookies.items():
                try:
                    driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com'})
                except Exception as e:
                    add_log(f"Failed to add cookie {name}: {e}", level="warning")
        
        driver.get("https://www.facebook.com") # Reload to ensure cookies are applied
        time.sleep(5) # Give time for cookies to take effect and redirect

        current_message_idx = 0
        total_uids = len(chat_ids)
        
        for i, chat_id in enumerate(chat_ids):
            if not st.session_state.running:
                add_log("🚫 Task stopped by user.", level="warning")
                break
            
            add_log(f"💬 Processing UID {i+1}/{total_uids}: {chat_id}", level="info")
            url = f"https://www.facebook.com/messages/t/{chat_id}"
            driver.get(url)
            time.sleep(7) # Wait for chat to load

            # Try to close any pop-ups (like "Use Facebook Lite")
            try:
                close_button = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Close"], a[role="button"][href="#"], button[aria-label*="Close"]')
                if close_button.is_displayed():
                    close_button.click()
                    add_log("Closed a pop-up.", level="info")
                    time.sleep(2)
            except:
                pass # No pop-up found or not clickable

            # Message sending loop for current chat_id
            for _ in range(st.session_state.messages_per_uid): # Send multiple messages per UID if needed
                if not st.session_state.running:
                    add_log("🚫 Task stopped by user.", level="warning")
                    break

                try:
                    box = None
                    selectors = [
                        'div[aria-label="Message"][contenteditable="true"]',
                        'div[role="textbox"][contenteditable="true"]',
                        'div[contenteditable="true"]',
                        'textarea' # Generic fallback
                    ]
                    
                    for s in selectors:
                        try:
                            found = driver.find_elements(By.CSS_SELECTOR, s)
                            # Ensure the element is visible and enabled
                            if found and found[0].is_displayed() and found[0].is_enabled():
                                box = found[0]
                                break
                        except:
                            continue
                    
                    if box:
                        if not messages:
                            add_log("⚠️ No messages loaded. Skipping message send.", level="warning")
                            break # Move to next UID or stop
                        
                        base_msg = messages[current_message_idx % len(messages)]
                        
                        # --- MESSAGE CONSTRUCTION ---
                        part1 = f"{prefix} " if prefix else ""
                        part3 = f" {suffix}" if suffix else ""
                        final_msg = f"{part1}{base_msg}{part3}"
                        
                        try:
                            # Using ActionChains for more robust interaction
                            actions = ActionChains(driver)
                            actions.move_to_element(box).click().perform() # Ensure box is focused
                            box.send_keys(final_msg) # Send keys directly
                            time.sleep(0.5) # Short pause before enter
                            actions.send_keys(Keys.ENTER).perform()
                            
                        except Exception as send_error:
                            add_log(f"Fallback send: Attempting JS-based send. Error: {send_error}", level="warning")
                            # Fallback to JavaScript if send_keys/ActionChains has issues
                            driver.execute_script("arguments[0].focus();", box)
                            driver.execute_script(f"arguments[0].innerText = '{final_msg}';", box)
                            box.send_keys(Keys.ENTER) # Still try to use Selenium ENTER for consistency

                        st.session_state.count += 1
                        add_log(f"✅ Sent to {chat_id}: {final_msg[:50]}...", level="success")
                        current_message_idx += 1
                        
                        time.sleep(delay_seconds) # Respect the user-defined delay
                    else:
                        add_log(f"⚠️ Message box not found or not interactable for {chat_id}. Skipping to next.", level="warning")
                        break # Move to next UID
                except Exception as e:
                    add_log(f"❌ Error during message send to {chat_id}: {str(e)[:100]}", level="error")
                    break # Move to next UID on error
        
        if st.session_state.running: # If not stopped by user explicitly
            add_log("✅ All tasks completed successfully.", level="system")

    except Exception as e:
        add_log(f"🛑 Critical Automation Crash: {str(e)[:150]}", level="error")
    finally:
        if driver: 
            try: 
                driver.quit()
                add_log("Browser closed.", level="info")
            except Exception as e:
                add_log(f"Error closing browser: {e}", level="error")
        st.session_state.running = False
        st.session_state.start_time = None
        st.rerun() # Ensure UI updates after task completion/crash

# --- Uptime and Pakistan Time Updater Thread ---
def update_time_display():
    while True:
        try:
            # Need to get a reference to the placeholder from session_state
            if 'time_status_placeholder' in st.session_state and st.session_state.time_status_placeholder:
                with st.session_state.time_status_placeholder.container():
                    st.markdown('<div class="time-status-box">', unsafe_allow_html=True)
                    st.markdown(f"<h3>🇵🇰 Live Pakistan Time:</h3><p>{get_pakistan_time()}</p>", unsafe_allow_html=True)
                    st.markdown(f"<h3>⏳ System Uptime:</h3><p>{format_uptime(st.session_state.start_time)}</p>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            # Handle cases where session_state might be reset or UI elements are gone
            # For a daemon thread, it's okay to let it die silently if Streamlit context is gone
            pass
        time.sleep(1)

# Start the time updater thread only once
if 'time_thread_started' not in st.session_state:
    time_thread = threading.Thread(target=update_time_display, daemon=True)
    add_script_run_ctx(time_thread) # Important for Streamlit context
    time_thread.start()
    st.session_state.time_thread_started = True


# --- UI LAYOUT ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# 1. Title
st.markdown('<div class="title-box"><h1 class="vip-title">SNAKE XD</h1><div class="vip-subtitle">PREMIUM AUTOMATION</div></div>', unsafe_allow_html=True)

# 2. Pakistan Time & Uptime Display (Placeholder)
st.session_state.time_status_placeholder = st.empty() # Create a placeholder for time/uptime

# 3. Inputs Section
st.subheader("⚙️ Automation Settings")
tab1, tab2 = st.tabs(["🔑 Cookies & Chat IDs", "📝 Message & Speed"])

with tab1:
    st.markdown("### Facebook Cookies")
    cookie_input_method = st.radio(
        "Select Cookie Input Method:",
        ("Paste Cookie String", "Upload Cookie File (.txt)"),
        key="cookie_method"
    )
    cookie_data = ""
    if cookie_input_method == "Paste Cookie String":
        cookie_data = st.text_area("Paste your Facebook ID Cookie string here (e.g., 'c_user=xxx; xs=yyy;')", height=100, key="cookie_string_input", placeholder="Paste approved cookies...")
    else:
        cookie_file = st.file_uploader("Upload your Cookies file (.txt)", type=["txt"], key="cookie_file_uploader")
        if cookie_file is not None:
            cookie_data = cookie_file.read().decode("utf-8")
            st.success("Cookies file uploaded.")
    
    st.markdown("---")
    st.markdown("### Messenger Group / Thread UIDs")
    uid_input_method = st.radio(
        "Select UID Input Method:",
        ("Paste UIDs (comma/newline separated)", "Upload UID File (.txt)"),
        key="uid_method"
    )
    chat_ids = []
    if uid_input_method == "Paste UIDs (comma/newline separated)":
        raw_uids = st.text_area("Enter Messenger Group UIDs (one per line, or comma-separated)", height=150, key="uid_string_input", placeholder="1000..., 1000..., 1000...\nOr one per line...")
        chat_ids = [uid.strip() for uid in raw_uids.replace('\n', ',').split(',') if uid.strip()]
    else:
        uid_file = st.file_uploader("Upload UID File (.txt)", type=["txt"], key="uid_file_uploader")
        if uid_file is not None:
            chat_ids = [line.strip() for line in uid_file.read().decode("utf-8").splitlines() if line.strip()]
    st.info(f"Loaded {len(chat_ids)} Unique Messenger UIDs.")

with tab2:
    st.markdown("### Message Content")
    file_uploader_msg = st.file_uploader("Upload Message File (.TXT)", type="txt", key="msg_file_uploader")
    messages = []
    if file_uploader_msg:
        messages = [l.strip() for l in file_uploader_msg.getvalue().decode('utf-8').split('\n') if l.strip()]
        st.success(f"Loaded {len(messages)} messages.")
    else:
        st.warning("No message file uploaded. Using default test message 'SNAKE XD TESTING'.")
        messages = ["SNAKE XD TESTING"] # Default message if no file

    col_prefix, col_suffix = st.columns(2)
    with col_prefix:
        prefix = st.text_input("NAME (PREFIX)", placeholder="e.g., 'Dear', 'Hello'", key="prefix_input")
    with col_suffix:
        suffix = st.text_input("HERE NAME (SUFFIX)", placeholder="e.g., 'friend', 'sir'", key="suffix_input")

    col_delay, col_msgs_per_uid = st.columns(2)
    with col_delay:
        delay_seconds = st.number_input("TIME DELAY (SECONDS) PER MESSAGE", value=60, min_value=1, key="delay_input")
    with col_msgs_per_uid:
        # Added an option for multiple messages per UID
        st.session_state.messages_per_uid = st.number_input("MESSAGES PER UID (Loop through message file)", value=1, min_value=1, key="msgs_per_uid_input")


st.markdown("<br>", unsafe_allow_html=True) # Spacer

# 4. Control Buttons
c1, c2 = st.columns(2)
with c1:
    if st.button("🚀 ACTIVATE SNAKE XD", use_container_width=True, disabled=st.session_state.running):
        if not cookie_data:
            st.error("COOKIES KAHA HAIN BOSS?")
        elif not chat_ids:
            st.error("CHAT ID KAHA HAIN BOSS?")
        else:
            st.session_state.running = True
            st.session_state.logs = [] # Clear previous logs
            st.session_state.count = 0
            st.session_state.start_time = datetime.now() # Set start time
            
            # Start automation in a separate thread
            t = threading.Thread(target=start_process, args=(chat_ids, prefix, suffix, delay_seconds, cookie_data, messages))
            add_script_run_ctx(t) # Crucial for Streamlit session state in thread
            t.start()
            add_log("Automation task initiated...", level="system")
            st.rerun() # Force a rerun to update UI state

with c2:
    if st.button("🛑 STOP SYSTEM", use_container_width=True, disabled=not st.session_state.running):
        st.session_state.running = False
        add_log("Stop signal sent. Please wait for current task to finish.", level="warning")
        st.rerun() # Force a rerun to update UI state

# 5. Status & Logs
status_color = "#00c853" if st.session_state.running else "#d50000"
status_text = "SYSTEM ACTIVE" if st.session_state.running else "SYSTEM OFFLINE"

st.markdown(f"""
    <div style="text-align:center; margin-top:20px;">
        <span class="status-badge" style="border: 2px solid {status_color}; color: {status_color};">
            {status_text}
        </span>
        <span class="status-badge" style="border: 2px solid #00FFFF; color: #00FFFF; margin-left:10px;">
            MESSAGES SENT: {st.session_state.count}
        </span>
    </div>
""", unsafe_allow_html=True)

# Logs Terminal (Using placeholder for dynamic updates)
st.markdown("### 📄 Live Console Updates", unsafe_allow_html=True)
st.session_state.log_area_placeholder = st.empty() # Assign placeholder here

# Initial log display
with st.session_state.log_area_placeholder:
    if not st.session_state.logs:
        st.markdown('<div class="terminal-window"><div class="log-line info">Waiting for tasks...</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="terminal-window">', unsafe_allow_html=True)
        for log_item in reversed(st.session_state.logs):
            st.markdown(log_item, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


st.markdown('</div>', unsafe_allow_html=True) # End Main Container

# Auto-rerun to update logs and status if automation is running
if st.session_state.running:
    time.sleep(1) # Rerun every second
    st.rerun()
