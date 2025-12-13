import streamlit as st
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re
import threading
import queue
import random
from datetime import datetime
import pytz
import base64
from pathlib import Path

# Global variables for automation control
automation_running = False
automation_thread = None
log_queue = queue.Queue()
task_id = None
message_count = 0

# CSS for VIP dark theme styling
VIP_CSS = """
<style>
/* Main container styling */
.stApp {
    background: linear-gradient(135deg, #080808 0%, #1a1a1a 100%);
    color: #0CC618;
}

/* Custom CSS for glowing inputs and buttons */
.glow-input {
    background: #1a1a1a !important;
    border: 2px solid #0CC618 !important;
    border-radius: 10px !important;
    color: #0CC618 !important;
    font-family: 'Courier New', monospace !important;
    padding: 12px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 10px rgba(12, 198, 24, 0.3) !important;
}

.glow-input:focus {
    border-color: #ff0040 !important;
    box-shadow: 0 0 20px rgba(255, 0, 64, 0.5), 0 0 30px rgba(12, 198, 24, 0.3) !important;
    outline: none !important;
}

.red-glow {
    border-color: #ff0040 !important;
    box-shadow: 0 0 15px rgba(255, 0, 64, 0.4) !important;
}

.blue-glow {
    border-color: #0080ff !important;
    box-shadow: 0 0 15px rgba(0, 128, 255, 0.4) !important;
}

/* VIP Button styling */
.vip-button {
    background: linear-gradient(45deg, #1a1a1a, #2a2a2a) !important;
    border: 2px solid #0CC618 !important;
    color: #0CC618 !important;
    font-weight: bold !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    font-family: 'Courier New', monospace !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

.vip-button:hover {
    background: linear-gradient(45deg, #0CC618, #00ff40) !important;
    color: #000000 !important;
    box-shadow: 0 0 20px rgba(12, 198, 24, 0.6) !important;
    transform: translateY(-2px) !important;
}

.stop-button {
    border-color: #ff0040 !important;
    color: #ff0040 !important;
}

.stop-button:hover {
    background: linear-gradient(45deg, #ff0040, #ff4080) !important;
    color: #ffffff !important;
    box-shadow: 0 0 20px rgba(255, 0, 64, 0.6) !important;
}

/* Console styling */
.console-container {
    background: #0a0a0a !important;
    border: 2px solid #0CC618 !important;
    border-radius: 10px !important;
    padding: 15px !important;
    height: 400px !important;
    overflow-y: auto !important;
    font-family: 'Courier New', monospace !important;
    font-size: 12px !important;
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5) !important;
}

.console-log {
    color: #0CC618 !important;
    margin: 2px 0 !important;
    padding: 2px 5px !important;
    border-left: 2px solid #0CC618 !important;
    padding-left: 10px !important;
}

.error-log {
    color: #ff0040 !important;
    border-left-color: #ff0040 !important;
}

.success-log {
    color: #00ff40 !important;
    border-left-color: #00ff40 !important;
}

.warning-log {
    color: #ffaa00 !important;
    border-left-color: #ffaa00 !important;
}

/* Header styling */
.main-header {
    text-align: center;
    font-size: 2.5em;
    font-weight: bold;
    color: #0CC618;
    text-shadow: 0 0 10px rgba(12, 198, 24, 0.8);
    margin-bottom: 20px;
    animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
    from { text-shadow: 0 0 10px rgba(12, 198, 24, 0.8); }
    to { text-shadow: 0 0 20px rgba(12, 198, 24, 1), 0 0 30px rgba(12, 198, 24, 0.6); }
}

/* Section headers */
.section-header {
    color: #0CC618;
    font-size: 1.3em;
    font-weight: bold;
    margin: 20px 0 10px 0;
    border-bottom: 2px solid #0CC618;
    padding-bottom: 5px;
}

/* Hide default streamlit elements */
.stDeployButton {
    display: none;
}

/* Custom scrollbar */
.console-container::-webkit-scrollbar {
    width: 8px;
}

.console-container::-webkit-scrollbar-track {
    background: #1a1a1a;
}

.console-container::-webkit-scrollbar-thumb {
    background: #0CC618;
    border-radius: 4px;
}

.console-container::-webkit-scrollbar-thumb:hover {
    background: #00ff40;
}

/* Status indicator */
.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
    animation: pulse 1.5s infinite;
}

.status-running {
    background: #00ff40;
    box-shadow: 0 0 10px rgba(0, 255, 64, 0.8);
}

.status-stopped {
    background: #ff0040;
    box-shadow: 0 0 10px rgba(255, 0, 64, 0.8);
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}
</style>
"""

def get_pakistan_time():
    """Get current Pakistan time"""
    pakistan_tz = pytz.timezone('Asia/Karachi')
    return datetime.now(pakistan_tz)

def generate_task_id():
    """Generate unique task ID"""
    return f"TASK-{int(time.time())}-{random.randint(1000, 9999)}"

def add_log(message, log_type="info"):
    """Add log message to queue"""
    timestamp = get_pakistan_time().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "message": message,
        "type": log_type,
        "task_id": task_id,
        "message_count": message_count
    }
    log_queue.put(log_entry)

def parse_cookies(cookie_string):
    """Parse cookie string into list of dictionaries"""
    cookies = []
    if not cookie_string.strip():
        return cookies
    
    # Handle file format (multiple cookies)
    if cookie_string.count('c_user') > 1:
        # Split by cookie boundary if multiple cookies
        cookie_entries = re.split(r'(c_user=\d+)', cookie_string)
        current_cookie = ""
        
        for i, entry in enumerate(cookie_entries):
            if entry.startswith('c_user'):
                if current_cookie:
                    cookies.append(current_cookie.strip())
                current_cookie = entry
            else:
                current_cookie += entry
        
        if current_cookie:
            cookies.append(current_cookie.strip())
    else:
        cookies.append(cookie_string.strip())
    
    return cookies

def setup_driver():
    """Setup Chrome WebDriver with options"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # For Termux compatibility
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except:
        # Fallback for Termux or environments where webdriver-manager fails
        driver = webdriver.Chrome(options=chrome_options)
    
    return driver

def apply_cookies(driver, cookie_string):
    """Apply cookies to WebDriver"""
    try:
        # Navigate to Facebook first
        driver.get("https://www.facebook.com")
        time.sleep(2)
        
        # Parse cookie string
        cookie_pairs = cookie_string.split(';')
        for pair in cookie_pairs:
            if '=' in pair:
                name, value = pair.strip().split('=', 1)
                # Add cookie
                driver.add_cookie({
                    'name': name,
                    'value': value,
                    'domain': '.facebook.com'
                })
        
        # Refresh to apply cookies
        driver.refresh()
        time.sleep(3)
        
        # Check if login successful by looking for user menu
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Account'] | //div[@role='button' and contains(., 'Account')]"))
            )
            return True
        except:
            return False
            
    except Exception as e:
        add_log(f"Cookie application failed: {str(e)}", "error")
        return False

def send_facebook_message(driver, thread_uid, message, prefix="", suffix=""):
    """Send message to Facebook thread"""
    try:
        # Navigate to the thread
        thread_url = f"https://www.facebook.com/messages/t/{thread_uid}"
        driver.get(thread_url)
        time.sleep(3)
        
        # Wait for message box to be available
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'] | //div[@role='textbox'] | //textarea[@placeholder='Message...']"))
        )
        
        # Format message
        full_message = f"{prefix}{message}{suffix}"
        
        # Click on message box and type
        message_box.click()
        time.sleep(1)
        
        # Clear any existing content
        message_box.clear()
        
        # Type message
        message_box.send_keys(full_message)
        time.sleep(2)
        
        # Find and click send button
        send_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Press enter to send'] | //button[@aria-label='Send'] | //div[contains(@class, 'send')]"))
        )
        send_button.click()
        
        time.sleep(2)  # Wait for message to send
        
        return True
        
    except TimeoutException:
        add_log(f"Timeout: Could not find message box for thread {thread_uid}", "error")
        return False
    except NoSuchElementException as e:
        add_log(f"Element not found in thread {thread_uid}: {str(e)}", "error")
        return False
    except Exception as e:
        add_log(f"Error sending message to thread {thread_uid}: {str(e)}", "error")
        return False

def automation_worker():
    """Main automation worker thread"""
    global automation_running, message_count
    
    # Get parameters from session state
    cookie_string = st.session_state.get('cookies', '')
    thread_uid = st.session_state.get('thread_uid', '')
    prefix = st.session_state.get('prefix', '')
    suffix = st.session_state.get('suffix', '')
    delay = float(st.session_state.get('delay', 5))
    message_file = st.session_state.get('message_file', None)
    
    if not cookie_string or not thread_uid or not message_file:
        add_log("Missing required parameters", "error")
        automation_running = False
        return
    
    # Read messages from file
    try:
        with open(message_file, 'r', encoding='utf-8') as f:
            messages = [line.strip() for line in f if line.strip()]
    except Exception as e:
        add_log(f"Error reading message file: {str(e)}", "error")
        automation_running = False
        return
    
    if not messages:
        add_log("No messages found in file", "error")
        automation_running = False
        return
    
    # Parse cookies
    cookies = parse_cookies(cookie_string)
    if not cookies:
        add_log("No valid cookies found", "error")
        automation_running = False
        return
    
    add_log(f"Starting automation with {len(cookies)} cookie(s) and {len(messages)} messages", "success")
    
    driver = None
    try:
        # Setup driver
        driver = setup_driver()
        add_log("WebDriver initialized successfully", "success")
        
        # Apply cookies and check login
        if not apply_cookies(driver, cookies[0]):  # Use first cookie for now
            add_log("Login failed with cookies", "error")
            automation_running = False
            return
        
        add_log("Successfully logged into Facebook", "success")
        
        # Start sending messages
        message_index = 0
        while automation_running and message_index < len(messages):
            message = messages[message_index]
            
            add_log(f"Sending message {message_index + 1}/{len(messages)}: {message[:50]}...", "info")
            
            if send_facebook_message(driver, thread_uid, message, prefix, suffix):
                message_count += 1
                add_log(f"✓ Message sent successfully (Total: {message_count})", "success")
            else:
                add_log(f"✗ Failed to send message {message_index + 1}", "error")
            
            message_index += 1
            
            # Wait for delay (but check if stopped)
            wait_time = 0
            while wait_time < delay and automation_running:
                time.sleep(1)
                wait_time += 1
        
        if automation_running:
            add_log(f"Automation completed. Total messages sent: {message_count}", "success")
        else:
            add_log(f"Automation stopped by user. Total messages sent: {message_count}", "warning")
            
    except Exception as e:
        add_log(f"Automation error: {str(e)}", "error")
    finally:
        if driver:
            driver.quit()
        automation_running = False
        add_log("Automation stopped and resources cleaned up", "info")

def start_automation():
    """Start automation in separate thread"""
    global automation_running, automation_thread, task_id, message_count
    
    if automation_running:
        add_log("Automation is already running", "warning")
        return
    
    automation_running = True
    task_id = generate_task_id()
    message_count = 0
    add_log(f"Starting new automation session - {task_id}", "success")
    
    automation_thread = threading.Thread(target=automation_worker, daemon=True)
    automation_thread.start()

def stop_automation():
    """Stop automation"""
    global automation_running
    if automation_running:
        automation_running = False
        add_log("Stop command sent - waiting for current message to complete...", "warning")
    else:
        add_log("Automation is not running", "info")

def clear_logs():
    """Clear log queue"""
    global task_id, message_count
    while not log_queue.empty():
        log_queue.get()
    task_id = None
    message_count = 0
    add_log("Console cleared", "info")

def main():
    st.set_page_config(
        page_title="Facebook Automation Tool",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Inject custom CSS
    st.markdown(VIP_CSS, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<div class="main-header">🚀 Facebook Automation Tool</div>', unsafe_allow_html=True)
    
    # Main container
    with st.container():
        # Status indicator
        status_class = "status-running" if automation_running else "status-stopped"
        status_text = "RUNNING" if automation_running else "STOPPED"
        st.markdown(f'<span class="status-indicator {status_class}"></span><strong>Status: {status_text}</strong>', unsafe_allow_html=True)
        
        # Configuration section
        st.markdown('<div class="section-header">⚙️ Configuration</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cookies input
            st.markdown("**🍪 Facebook Cookies**")
            cookies = st.text_area(
                "Enter cookies (single string or file with multiple cookies):",
                height=100,
                key="cookies",
                help="Paste your Facebook cookies here. For multiple cookies, separate them with the c_user parameter."
            )
            
            # Thread UID input
            thread_uid = st.text_input(
                "**📱 Thread/Chat UID**",
                key="thread_uid",
                help="Enter the Facebook thread UID or user ID"
            )
            
            # Time delay
            delay = st.number_input(
                "**⏱️ Time Delay (seconds)**",
                min_value=1,
                max_value=300,
                value=5,
                key="delay"
            )
        
        with col2:
            # Prefix and suffix
            prefix = st.text_input(
                "**📝 Message Prefix**",
                key="prefix",
                help="Text to add before each message"
            )
            
            suffix = st.text_input(
                "**📝 Message Suffix**",
                key="suffix",
                help="Text to add after each message"
            )
            
            # Message file upload
            st.markdown("**📄 Message File (.txt)**")
            message_file = st.file_uploader(
                "Upload text file with messages (one per line)",
                type=['txt'],
                key="message_file"
            )
            
            if message_file:
                # Save uploaded file
                file_path = f"uploaded_messages_{int(time.time())}.txt"
                with open(file_path, 'wb') as f:
                    f.write(message_file.getbuffer())
                st.session_state['message_file'] = file_path
                st.success(f"File uploaded: {message_file.name}")
        
        # Control buttons
        st.markdown('<div class="section-header">🎮 Control Panel</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 START AUTOMATION", key="start_btn", help="Start the Facebook automation"):
                start_automation()
        
        with col2:
            if st.button("⏹️ STOP AUTOMATION", key="stop_btn", help="Stop the current automation"):
                stop_automation()
        
        with col3:
            if st.button("🗑️ CLEAR LOGS", key="clear_btn", help="Clear console logs"):
                clear_logs()
        
        # Console/Log section
        st.markdown('<div class="section-header">📊 Console Logs</div>', unsafe_allow_html=True)
        
        # Create console container
        console_container = st.empty()
        
        # Process logs and update console
        logs_html = '<div class="console-container">'
        
        # Get all logs from queue
        temp_logs = []
        while not log_queue.empty():
            temp_logs.append(log_queue.get())
        
        # Put logs back and display them
        for log in temp_logs:
            log_queue.put(log)
            
            log_class = f"console-log {log['type']}-log"
            logs_html += f'''
            <div class="{log_class}">
                [{log['timestamp']}] [{log.get('task_id', 'N/A')}] [Msgs: {log.get('message_count', 0)}] {log['message']}
            </div>
            '''
        
        logs_html += '</div>'
        console_container.markdown(logs_html, unsafe_allow_html=True)
        
        # Auto-refresh
        if automation_running:
            time.sleep(1)
            st.rerun()

if __name__ == "__main__":
    main()