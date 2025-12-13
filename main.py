import streamlit as st
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random
from datetime import datetime
import pytz
import os
from webdriver_manager.chrome import ChromeDriverManager

# Initialize session state variables
if 'running' not in st.session_state:
    st.session_state.running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'task_id' not in st.session_state:
    st.session_state.task_id = ""
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0

# Custom CSS for VIP dark design with glowing elements
def apply_custom_css():
    st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #080808;
        color: #0CC618;
    }
    
    /* Glowing input boxes */
    input, textarea, div.stTextArea textarea, div.stSelectbox div, div.stNumberInput input {
        background-color: #111111 !important;
        border: 2px solid;
        border-radius: 8px;
        color: #0CC618 !important;
        box-shadow: 0 0 10px #ff0080, 0 0 20px #0088ff inset;
        transition: box-shadow 0.3s ease-in-out;
    }
    
    input:focus, textarea:focus, div.stTextArea textarea:focus {
        box-shadow: 0 0 15px #ff0080, 0 0 25px #0088ff inset;
        outline: none;
    }
    
    /* Glowing buttons */
    .stButton button {
        background: linear-gradient(45deg, #ff0080, #0088ff);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        box-shadow: 0 0 15px #ff0080, 0 0 25px #0088ff;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        box-shadow: 0 0 20px #ff0080, 0 0 30px #0088ff;
        transform: translateY(-2px);
    }
    
    /* Console styling */
    .console-container {
        background-color: #111111;
        border: 2px solid #0088ff;
        border-radius: 8px;
        padding: 15px;
        height: 300px;
        overflow-y: auto;
        box-shadow: 0 0 10px #0088ff inset;
        font-family: 'Courier New', monospace;
    }
    
    .console-line {
        margin: 5px 0;
        animation: fadeIn 0.5s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #0CC618;
        text-shadow: 0 0 10px #0088ff;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #080808;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(#ff0080, #0088ff);
        border-radius: 10px;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background-color: #111111;
        border: 2px dashed #0088ff;
        border-radius: 8px;
        box-shadow: 0 0 10px #0088ff;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to log messages with timestamp in Pakistan time
def log_message(message, msg_type="INFO"):
    pakistan_tz = pytz.timezone('Asia/Karachi')
    timestamp = datetime.now(pakistan_tz).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{msg_type}] [{st.session_state.task_id}] {message}"
    st.session_state.logs.append(log_entry)
    # Keep only the last 1000 logs to prevent memory issues
    if len(st.session_state.logs) > 1000:
        st.session_state.logs = st.session_state.logs[-1000:]

# Function to initialize Chrome WebDriver
def init_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Remove if you want to see the browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        return driver
    except Exception as e:
        log_message(f"Error initializing WebDriver: {str(e)}", "ERROR")
        return None

# Function to login to Facebook using cookies
def login_with_cookies(driver, cookies_str):
    try:
        driver.get("https://www.facebook.com/")
        
        # Add cookies to the driver
        cookies_list = []
        if '\n' in cookies_str:
            # Multiple cookies from file
            cookie_lines = cookies_str.strip().split('\n')
            for line in cookie_lines:
                if ':' in line:
                    parts = line.split(':')
                    cookies_list.append({
                        "name": parts[0].strip(),
                        "value": parts[1].strip()
                    })
        else:
            # Single cookie string
            if ':' in cookies_str:
                parts = cookies_str.split(':')
                cookies_list.append({
                    "name": parts[0].strip(),
                    "value": parts[1].strip()
                })
        
        for cookie in cookies_list:
            driver.add_cookie(cookie)
        
        # Refresh to apply cookies
        driver.refresh()
        
        # Wait for page to load after login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-pagelet='ChatTab']"))
        )
        
        log_message("Successfully logged in to Facebook using cookies")
        return True
    except TimeoutException:
        log_message("Timeout while logging in. Please check your cookies", "ERROR")
        return False
    except Exception as e:
        log_message(f"Error during login: {str(e)}", "ERROR")
        return False

# Function to send a single message
def send_message(driver, chat_uid, message):
    try:
        # Navigate to the chat
        driver.get(f"https://www.facebook.com/messages/t/{chat_uid}")
        
        # Wait for the message input field
        message_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
        )
        
        # Type the message
        message_box.send_keys(message)
        
        # Find and click the send button
        send_button = driver.find_element(By.XPATH, "//div[@aria-label='Press enter to send']")
        send_button.click()
        
        return True
    except TimeoutException:
        log_message(f"Timeout while sending message to chat {chat_uid}", "ERROR")
        return False
    except NoSuchElementException:
        log_message(f"Could not find message input for chat {chat_uid}", "ERROR")
        return False
    except Exception as e:
        log_message(f"Error sending message: {str(e)}", "ERROR")
        return False

# Main automation function
def run_automation(cookies, chat_uid, prefix, suffix, delay, messages):
    driver = init_webdriver()
    if not driver:
        log_message("Failed to initialize WebDriver. Aborting task.", "ERROR")
        return
    
    # Login with cookies
    if not login_with_cookies(driver, cookies):
        driver.quit()
        return
    
    # Send messages
    try:
        for message in messages:
            if not st.session_state.running:
                break
                
            formatted_message = f"{prefix}{message}{suffix}"
            
            if send_message(driver, chat_uid, formatted_message):
                st.session_state.message_count += 1
                log_message(f"Sent message ({st.session_state.message_count}): {formatted_message}")
            else:
                log_message(f"Failed to send message: {formatted_message}", "ERROR")
            
            # Delay between messages
            time.sleep(delay)
    finally:
        driver.quit()
        if st.session_state.running:
            log_message(f"Task completed. Total messages sent: {st.session_state.message_count}")
        else:
            log_message(f"Task stopped by user. Messages sent: {st.session_state.message_count}")
        st.session_state.running = False

# Main Streamlit app
def main():
    apply_custom_css()
    
    st.title("VIP Facebook Messenger Bot")
    st.markdown("---")
    
    # Sidebar for task info
    with st.sidebar:
        st.header("Task Information")
        if st.session_state.task_id:
            st.markdown(f"**Task ID:** `{st.session_state.task_id}`")
            st.markdown(f"**Messages Sent:** `{st.session_state.message_count}`")
        else:
            st.markdown("**Task ID:** `Not running`")
            st.markdown("**Messages Sent:** `0`")
        
        pakistan_tz = pytz.timezone('Asia/Karachi')
        current_time = datetime.now(pakistan_tz).strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"**Pakistan Time:** `{current_time}`")
        
        # Status indicator
        if st.session_state.running:
            st.markdown("🔴 **Status:** Running")
        else:
            st.markdown("🟢 **Status:** Idle")
    
    # Input section
    st.header("Configuration")
    
    # Cookies input
    st.subheader("Facebook Cookies")
    cookies_option = st.radio("Cookie Input Method:", ["Single Cookie String", "Cookies File"])
    
    cookies = ""
    if cookies_option == "Single Cookie String":
        cookies = st.text_area("Enter your Facebook cookies (name:value)", height=100, 
                               placeholder="c_user:1234567890\nxs:abcdefghijk1234567890...")
    else:
        cookies_file = st.file_uploader("Upload cookies file", type=['txt'])
        if cookies_file:
            cookies = cookies_file.read().decode('utf-8')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Chat Configuration")
        chat_uid = st.text_input("Thread/Chat UID", placeholder="Enter chat ID")
        delay = st.number_input("Delay Between Messages (seconds)", min_value=1, value=5)
    
    with col2:
        st.subheader("Message Formatting")
        prefix = st.text_input("Message Prefix", placeholder="Enter prefix")
        suffix = st.text_input("Message Suffix", placeholder="Enter suffix")
    
    st.subheader("Message Content")
    messages_file = st.file_uploader("Upload Messages File (.txt)", type=['txt'])
    
    messages = []
    if messages_file:
        content = messages_file.read().decode('utf-8')
        messages = [msg.strip() for msg in content.split('\n') if msg.strip()]
        st.success(f"Loaded {len(messages)} messages from file")
    
    # Control buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Start Messaging", use_container_width=True):
            if not cookies:
                st.error("Please provide Facebook cookies")
            elif not chat_uid:
                st.error("Please enter a Chat UID")
            elif not messages:
                st.error("Please upload a messages file")
            else:
                st.session_state.running = True
                st.session_state.task_id = f"TASK-{random.randint(1000, 9999)}"
                st.session_state.message_count = 0
                st.session_state.logs = []
                log_message("Starting messaging task...")
                
                # Run automation in a separate thread
                thread = threading.Thread(target=run_automation, 
                                          args=(cookies, chat_uid, prefix, suffix, delay, messages))
                thread.start()
                st.experimental_rerun()
    
    with col2:
        if st.button("⏹️ Stop Messaging", use_container_width=True):
            if st.session_state.running:
                st.session_state.running = False
                log_message("Stopping messaging task...")
                st.experimental_rerun()
            else:
                st.warning("No task is currently running")
    
    with col3:
        if st.button("🧹 Clear Logs", use_container_width=True):
            st.session_state.logs = []
            st.experimental_rerun()
    
    # Console/logs section
    st.markdown("---")
    st.header("Live Console")
    
    # Scrollable log container
    log_container = st.container()
    with log_container:
        st.markdown('<div class="console-container">', unsafe_allow_html=True)
        for log in st.session_state.logs[-100:]:  # Show last 100 logs
            st.markdown(f'<div class="console-line">{log}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto-refresh for live logs
    if st.session_state.running:
        time.sleep(1)
        st.experimental_rerun()

if __name__ == "__main__":
    main()
