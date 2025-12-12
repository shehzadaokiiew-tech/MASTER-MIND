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
    #st.warning("`webdriver-manager` not found. Ensure ChromeDriver is in PATH or provide path manually.") # Removed for VIP clean look
    pass

# For Streamlit's session state in threads
from streamlit.runtime.scriptrunner import add_script_run_ctx

# --- Global Flags and Session State Initialization ---
# Set page config with a custom title and wide layout
st.set_page_config(page_title="SNAKE XD: Elite Automation", layout="wide", initial_sidebar_state="collapsed")

if 'running' not in st.session_state: st.session_state.running = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'count' not in st.session_state: st.session_state.count = 0
if 'start_time' not in st.session_state: st.session_state.start_time = None # For uptime
if 'log_area_placeholder' not in st.session_state: st.session_state.log_area_placeholder = None
if 'time_status_placeholder' not in st.session_state: st.session_state.time_status_placeholder = None


# --- Custom CSS for VIP Styling ---
st.markdown("""
    <style>
    /* General Body Styling */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #e0e0e0;
        background-color: #0f0f0f; /* Very dark background */
    }

    /* Main Container for overall layout */
    .main-container {
        padding: 20px;
        max-width: 1300px; /* Slightly wider */
        margin: auto;
    }

    /* Streamlit's main content area */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Title Box */
    .title-box {
        background: linear-gradient(90deg, #181818, #2a2a2a, #181818); /* Dark metallic gradient */
        border: 2px solid #00FFFF; /* Cyan border */
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.5); /* Stronger cyan glow */
    }
    .vip-title {
        color: #00FFFF; /* Cyan */
        font-size: 4em; /* Larger title */
        font-weight: 900; /* Extra bold */
        text-shadow: 0 0 15px #00FFFF, 0 0 25px #00FFFF; /* Intense cyan glow */
        margin: 0;
        letter-spacing: 2px;
        animation: pulseTitle 2s infinite alternate; /* Subtle breathing effect */
    }
    .vip-subtitle {
        color: #00FF00; /* Neon Green */
        font-size: 1.3em;
        letter-spacing: 4px; /* Wider spacing */
        margin-top: 10px;
        text-transform: uppercase;
        font-weight: bold;
        text-shadow: 0 0 8px #00FF00;
    }

    @keyframes pulseTitle {
        from { transform: scale(1); opacity: 0.9; }
        to { transform: scale(1.02); opacity: 1; }
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.2em;
        margin: 8px;
        text-transform: uppercase;
        box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        transition: all 0.3s ease-in-out;
    }
    .status-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.7);
    }

    /* Terminal Window for Logs */
    .terminal-window {
        background-color: #000000; /* Pure black for terminal */
        border: 1px solid #00FF00; /* Green border */
        border-radius: 10px;
        padding: 20px;
        min-height: 300px; /* Taller */
        max-height: 550px; /* Limit height for scrolling */
        overflow-y: auto; /* Enable vertical scrolling */
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 1em; /* Slightly larger font */
        line-height: 1.5;
        color: #00FF00; /* Neon Green text */
        margin-top: 40px;
        box-shadow: inset 0 0 15px rgba(0,255,0,0.4); /* Stronger inner green glow */
    }
    .log-line {
        white-space: pre-wrap;
        word-break: break-all;
        margin-bottom: 5px;
        animation: fadeInLog 0.5s ease-out;
    }
    @keyframes fadeInLog {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    /* Specific log message colors */
    .log-line.info { color: #87CEEB; } /* Sky Blue */
    .log-line.success { color: #00FF00; font-weight: bold; } /* Neon Green */
    .log-line.warning { color: #FFFF00; } /* Yellow */
    .log-line.error { color: #FF0000; font-weight: bold; } /* Red */
    .log-line.system { color: #00FFFF; font-weight: bold; } /* Cyan */

    /* Streamlit widgets styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stFileUploader>div>div>button, .stNumberInput>div>div>input {
        background-color: #1a1a1a;
        color: #e0e0e0;
        border: 1px solid #00FFFF; /* Cyan border for inputs */
        border-radius: 7px;
        padding: 10px;
        box-shadow: 0 0 5px rgba(0, 255, 255, 0.2);
        transition: all 0.3s;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus, .stNumberInput>div>div>input:focus {
        border-color: #00FF00; /* Green focus border */
        box-shadow: 0 0 8px rgba(0, 255, 0, 0.4);
        outline: none;
    }
    
    /* File Uploader custom button style */
    .stFileUploader label span {
        background-color: #00FFFF;
        color: black;
        border-radius: 5px;
        padding: 8px 15px;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .stFileUploader label span:hover {
        background-color: #00FF00;
        color: black;
    }

    .stButton>button {
        background-color: #00FFFF; /* Cyan */
        color: black;
        border: none;
        padding: 12px 25px; /* Larger buttons */
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.1em;
        transition: background-color 0.3s, color 0.3s, transform 0.2s;
        box-shadow: 0 4px 15px rgba(0, 255, 255, 0.4);
    }
    .stButton>button:hover {
        background-color: #00FF00; /* Neon Green on hover */
        color: black;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 255, 0, 0.6);
    }
    .stButton>button:disabled {
        background-color: #333;
        color: #666;
        box-shadow: none;
        transform: none;
        cursor: not-allowed;
    }
    
    /* Labels for all input types */
    label, .st-b3, .st-b6, .st-emotion-cache-nahz7x p { /* More specific targeting for labels */
        color: #00FFFF !important; /* Cyan for all labels */
        font-weight: bold !important;
        font-size: 1.05em !important;
        margin-bottom: 5px !important;
    }
    /* Streamlit info/warning/error messages */
    .stAlert {
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    }
    .stAlert > div {
        color: #e0e0e0 !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #1a1a1a;
        color: #00FFFF;
        border: 1px solid #00FFFF;
        border-radius: 8px 8px 0 0;
        font-weight: bold;
        font-size: 1.1em;
        padding: 10px 20px;
        margin-right: 5px;
        transition: all 0.3s;
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        background-color: #00FFFF;
        color: #000000;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #00FFFF;
        color: #000000;
        border-bottom-color: #00FFFF;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.7);
    }
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #1a1a1a;
        border: 1px solid #00FFFF;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 20px;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
    }


    /* Uptime/Time Display */
    .time-status-box {
        background-color: #1f1f1f;
        border: 1px solid #00FFFF;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 12px rgba(0, 255, 255, 0.3);
    }
    .time-status-box h3 {
        color: #00FF00; /* Neon Green */
        margin: 5px 0;
        font-size: 1.4em;
        text-shadow: 0 0 5px #00FF00;
    }
    .time-status-box p {
        color: #e0e0e0;
        margin: 2px 0;
        font-size: 1.1em;
        letter-spacing: 1px;
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
    return f"{hours:02}h {minutes:02}m {seconds:02}s"

def add_log(msg, level="info"):
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
        add_log("🚀 SNAKE XD SYSTEM INITIATED...", level="system")
        driver = setup_browser()
        if not driver:
            add_log("🛑 Browser could not be initialized. Aborting automation.", level="error")
            st.session_state.running = False
            return

        add_log("🌐 Navigating to Facebook for cookie injection...", level="info")
        driver.get("https://www.facebook.com")
        time.sleep(3) # Give page some time to load

        # Parse and add cookies
        # Attempt a more robust cookie parsing
        try:
            for cookie_part in cookie_string.split(';'):
                cookie_part = cookie_part.strip()
                if '=' in cookie_part:
                    name, value = cookie_part.split('=', 1)
                    driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com'})
            add_log("Cookies injected. Reloading Facebook to apply...", level="info")
        except Exception as e:
            add_log(f"⚠️ Error injecting cookies: {e}", level="error")
            add_log("Attempting to proceed, but login may fail.", level="warning")
            
        driver.get("https://www.facebook.com") # Reload to ensure cookies are applied
        time.sleep(7) # Give time for cookies to take effect and redirect

        # Verify if logged in (basic check)
        if "login.php" in driver.current_url.lower() or "checkpoint" in driver.current_url.lower():
            add_log("🛑 Cookies are invalid or expired. Login failed. Please provide fresh cookies.", level="error")
            st.session_state.running = False
            driver.quit()
            return
        add_log("Facebook login successful via cookies.", level="success")

        current_message_idx = 0
        total_uids = len(chat_ids)
        
        for i, chat_id in enumerate(chat_ids):
            if not st.session_state.running:
                add_log("🚫 Automation paused by user.", level="warning")
                break
            
            add_log(f"💬 Targeting UID {i+1}/{total_uids}: {chat_id}", level="system")
            url = f"https://www.facebook.com/messages/t/{chat_id}/"
            driver.get(url)
            time.sleep(8) # Wait for chat to load

            # Try to close any pop-ups (like "Use Facebook Lite")
            try:
                # Look for common close button selectors
                close_buttons = driver.find_elements(By.CSS_SELECTOR, 'div[aria-label="Close"], a[role="button"][href="#"], button[aria-label*="Close"], div[aria-label*="Dismiss"]')
                for btn in close_buttons:
                    if btn.is_displayed():
                        btn.click()
                        add_log("Closed a detected pop-up.", level="info")
                        time.sleep(2)
                        break
            except:
                pass # No pop-up found or not clickable

            # Message sending loop for current chat_id
            for msg_num in range(st.session_state.messages_per_uid):
                if not st.session_state.running:
                    add_log("🚫 Automation paused by user.", level="warning")
                    break

                try:
                    box = None
                    # Attempt to find the message input box using multiple robust selectors
                    selectors = [
                        'div[aria-label="Message"][contenteditable="true"]',
                        'div[role="textbox"][contenteditable="true"]',
                        'div[data-testid="post-create"] div[contenteditable="true"]', # Sometimes used
                        'textarea[placeholder*="message"]',
                        'div[contenteditable="true"][tabindex="0"]'
                    ]
                    
                    for s in selectors:
                        try:
                            found = driver.find_elements(By.CSS_SELECTOR, s)
                            if found and found[0].is_displayed() and found[0].is_enabled():
                                box = found[0]
                                break
                        except:
                            continue
                    
                    if box:
                        if not messages:
                            add_log("⚠️ No messages loaded from file. Cannot send message.", level="warning")
                            break # Move to next UID or stop
                        
                        base_msg = messages[current_message_idx % len(messages)]
                        
                        # --- MESSAGE CONSTRUCTION ---
                        part1 = f"{prefix} " if prefix else ""
                        part3 = f" {suffix}" if suffix else ""
                        final_msg = f"{part1}{base_msg}{part3}"
                        
                        try:
                            # Use ActionChains for robust interaction
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
                        add_log(f"✅ Sent message {msg_num+1} to {chat_id}: '{final_msg[:50]}...' (Total Sent: {st.session_state.count})", level="success")
                        current_message_idx += 1
                        
                        time.sleep(delay_seconds) # Respect the user-defined delay
                    else:
                        add_log(f"⚠️ Message box not found or not interactable for UID {chat_id}. Skipping this UID.", level="warning")
                        break # Move to next UID
                except Exception as e:
                    add_log(f"❌ Error during message send to UID {chat_id}: {str(e)[:100]}", level="error")
                    break # Move to next UID on error
        
        if st.session_state.running: # If not stopped by user explicitly
            add_log("✅ All automation tasks completed successfully for all UIDs.", level="system")

    except Exception as e:
        add_log(f"🛑 CRITICAL AUTOMATION CRASH: {str(e)[:150]}", level="error")
    finally:
        if driver: 
            try: 
                driver.quit()
                add_log("Browser instance closed.", level="info")
            except Exception as e:
                add_log(f"Error closing browser: {e}", level="warning")
        st.session_state.running = False
        st.session_state.start_time = None # Reset uptime
        st.rerun() # Ensure UI updates after task completion/crash

# --- Uptime and Pakistan Time Updater Thread ---
def update_time_display():
    while True:
        try:
            if st.session_state.time_status_placeholder:
                with st.session_state.time_status_placeholder.container():
                    st.markdown('<div class="time-status-box">', unsafe_allow_html=True)
                    st.markdown(f"<h3>🇵🇰 Live Pakistan Time:</h3><p>{get_pakistan_time()}</p>", unsafe_allow_html=True)
                    st.markdown(f"<h3>⏳ System Uptime:</h3><p>{format_uptime(st.session_state.start_time)}</p>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        except Exception:
            # Handle cases where session_state might be reset or UI elements are gone
            # For a daemon thread, it's generally okay to let it die silently if Streamlit context is gone
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
st.markdown('<div class="title-box"><h1 class="vip-title">SNAKE XD</h1><div class="vip-subtitle">ELITE AUTOMATION SYSTEM</div></div>', unsafe_allow_html=True)

# 2. Pakistan Time & Uptime Display (Placeholder)
st.session_state.time_status_placeholder = st.empty() # Assign placeholder here


# 3. Inputs Section with Tabs
st.markdown("## ⚙️ Configuration Module")
tab1, tab2 = st.tabs(["🔑 Access Credentials", "📝 Message & Schedule"])

with tab1:
    st.markdown("### Facebook Account Cookies")
    cookie_input_method = st.radio(
        "Select Cookie Input Method:",
        ("Paste Raw Cookie String", "Upload Cookie File (.txt)"),
        key="cookie_method"
    )
    cookie_data = ""
    if cookie_input_method == "Paste Raw Cookie String":
        cookie_data = st.text_area("Paste your full Facebook ID Cookie string here:", height=100, key="cookie_string_input", placeholder="e.g., c_user=12345; xs=abcdefgh; fr=123...")
    else:
        cookie_file = st.file_uploader("Upload your Cookie file (.txt)", type=["txt"], key="cookie_file_uploader")
        if cookie_file is not None:
            cookie_data = cookie_file.read().decode("utf-8")
            st.success("Cookie file loaded successfully.")
    
    st.markdown("---")
    st.markdown("### Messenger Group / Thread UIDs")
    uid_input_method = st.radio(
        "Select Target UID Method:",
        ("Paste UIDs (comma/newline separated)", "Upload UID List (.txt)"),
        key="uid_method"
    )
    chat_ids = []
    if uid_input_method == "Paste UIDs (comma/newline separated)":
        raw_uids = st.text_area("Enter Messenger Group/Thread UIDs (e.g., 1000..., 1000...)", height=150, key="uid_string_input", placeholder="1000..., 1000..., 1000...\nOr one UID per line...")
        chat_ids = [uid.strip() for uid in raw_uids.replace('\n', ',').split(',') if uid.strip()]
    else:
        uid_file = st.file_uploader("Upload UID List File (.txt)", type=["txt"], key="uid_file_uploader")
        if uid_file is not None:
            chat_ids = [line.strip() for line in uid_file.read().decode("utf-8").splitlines() if line.strip()]
    st.info(f"Targeting **{len(chat_ids)}** Unique Messenger UIDs for automation.")

with tab2:
    st.markdown("### Message Content & Personalization")
    file_uploader_msg = st.file_uploader("Upload Message Bank File (.TXT)", type="txt", key="msg_file_uploader")
    messages = []
    if file_uploader_msg:
        messages = [l.strip() for l in file_uploader_msg.getvalue().decode('utf-8').split('\n') if l.strip()]
        st.success(f"Loaded **{len(messages)}** unique messages into bank.")
    else:
        st.warning("No message bank uploaded. Using default system message: 'SNAKE XD INITIATING PROTOCOL'.")
        messages = ["SNAKE XD INITIATING PROTOCOL"] # Default message if no file

    col_prefix, col_suffix = st.columns(2)
    with col_prefix:
        prefix = st.text_input("Message Prefix (e.g., 'Hello,', 'Dear')", placeholder="e.g., 'Greetings, '", key="prefix_input")
    with col_suffix:
        suffix = st.text_input("Message Suffix (e.g., 'Team', 'Friend')", placeholder="e.g., ' -Team XD'", key="suffix_input")

    col_delay, col_msgs_per_uid = st.columns(2)
    with col_delay:
        delay_seconds = st.number_input("Delay Between Messages (Seconds)", value=60, min_value=5, key="delay_input", help="Set a higher delay to reduce risk of detection. Minimum 5 seconds recommended.")
    with col_msgs_per_uid:
        st.session_state.messages_per_uid = st.number_input("Messages Per UID (Loops through message bank)", value=1, min_value=1, key="msgs_per_uid_input", help="How many messages to send to each UID before moving to the next.")


st.markdown("<br>", unsafe_allow_html=True) # Spacer

# 4. Control Buttons
c1, c2 = st.columns(2)
with c1:
    if st.button("🚀 ACTIVATE SNAKE XD PROTOCOL", use_container_width=True, disabled=st.session_state.running):
        if not cookie_data:
            st.error("ERROR: ACCESS COOKIES REQUIRED. Please provide your Facebook ID Cookies.")
        elif not chat_ids:
            st.error("ERROR: TARGET UIDs REQUIRED. Please specify Messenger Group/Thread UIDs.")
        elif not messages:
             st.error("ERROR: MESSAGE BANK EMPTY. Please upload a message file or provide default messages.")
        else:
            st.session_state.running = True
            st.session_state.logs = [] # Clear previous logs for new task
            st.session_state.count = 0
            st.session_state.start_time = datetime.now() # Record start time for uptime
            
            # Start automation in a separate thread
            t = threading.Thread(target=start_process, args=(chat_ids, prefix, suffix, delay_seconds, cookie_data, messages))
            add_script_run_ctx(t) # Crucial for Streamlit session state in thread
            t.start()
            add_log("SNAKE XD PROTOCOL ACTIVATED. Monitoring operations...", level="system")
            st.rerun() # Force a rerun to update UI state

with c2:
    if st.button("🛑 INITIATE SHUTDOWN PROTOCOL", use_container_width=True, disabled=not st.session_state.running):
        st.session_state.running = False
        add_log("SHUTDOWN PROTOCOL INITIATED. System will halt operations shortly...", level="warning")
        st.rerun() # Force a rerun to update UI state

# 5. Status & Logs
status_color = "#00FF00" if st.session_state.running else "#FF0000" # Green for active, Red for offline
status_text = "SYSTEM ACTIVE" if st.session_state.running else "SYSTEM OFFLINE"

st.markdown(f"""
    <div style="text-align:center; margin-top:30px;">
        <span class="status-badge" style="border: 2px solid {status_color}; color: {status_color};">
            {status_text}
        </span>
        <span class="status-badge" style="border: 2px solid #00FFFF; color: #00FFFF; margin-left:15px;">
            MESSAGES DISPATCHED: {st.session_state.count}
        </span>
    </div>
""", unsafe_allow_html=True)

# Logs Terminal (Using placeholder for dynamic updates)
st.markdown("## 📄 Live Operational Log", unsafe_allow_html=True)
st.session_state.log_area_placeholder = st.empty() # Assign placeholder here

# Initial log display (or during rerun)
with st.session_state.log_area_placeholder:
    if not st.session_state.logs:
        st.markdown('<div class="terminal-window"><div class="log-line info">Awaiting protocol activation...</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="terminal-window">', unsafe_allow_html=True)
        for log_item in reversed(st.session_state.logs): # Show latest first
            st.markdown(log_item, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


st.markdown('</div>', unsafe_allow_html=True) # End Main Container

# Auto-rerun to update logs and status if automation is running
if st.session_state.running:
    time.sleep(1) # Rerun every second to refresh logs and time displays
    st.rerun()
