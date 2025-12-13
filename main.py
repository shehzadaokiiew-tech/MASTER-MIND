import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

# Custom CSS for dark theme
def apply_custom_css():
    st.markdown("""
    <style>
    .stApp {
        background-color: #0f0f0f;
        color: #00ff00;
    }
    h1, h2, h3 {
        color: #00ff00;
    }
    .stButton button {
        background-color: #1a1a1a;
        color: #00ff00;
        border: 1px solid #00ff00;
    }
    textarea, input {
        background-color: #1a1a1a;
        color: #00ff00;
        border: 1px solid #00ff00;
    }
    .console-box {
        background-color: #111;
        border: 1px solid #00ff00;
        padding: 10px;
        height: 300px;
        overflow-y: auto;
        font-family: monospace;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# Simple logging function
def log_to_console(message):
    if 'console_logs' not in st.session_state:
        st.session_state.console_logs = []
    st.session_state.console_logs.append(f"[{time.strftime('%H:%M:%S')}] {message}")
    # Keep only last 100 entries
    if len(st.session_state.console_logs) > 100:
        st.session_state.console_logs = st.session_state.console_logs[-100:]

# Initialize WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        log_to_console(f"WebDriver error: {str(e)}")
        return None

# Login function
def login_to_facebook(driver, cookies_str):
    try:
        log_to_console("Navigating to Facebook...")
        driver.get("https://www.facebook.com/")
        time.sleep(3)
        
        # Add cookies
        cookies = [line.strip() for line in cookies_str.split('\n') if ':' in line]
        for cookie in cookies:
            name, value = cookie.split(':', 1)
            driver.add_cookie({
                "name": name.strip(),
                "value": value.strip(),
                "domain": ".facebook.com"
            })
        
        log_to_console("Refreshing page after adding cookies...")
        driver.refresh()
        time.sleep(5)
        
        # Check if logged in
        if "facebook.com/" in driver.current_url and "login" not in driver.current_url:
            log_to_console("Login successful!")
            return True
        else:
            log_to_console("Login failed - check your cookies")
            return False
    except Exception as e:
        log_to_console(f"Login error: {str(e)}")
        return False

# Send single message
def send_message_to_chat(driver, chat_id, message):
    try:
        log_to_console(f"Opening chat: {chat_id}")
        driver.get(f"https://www.facebook.com/messages/t/{chat_id}")
        time.sleep(5)
        
        # Find message input - try multiple selectors
        selectors = [
            "//div[@role='textbox' and @data-testid='message-input']",
            "//div[@role='textbox']",
            "//div[@aria-label='Message']",
            "//div[@aria-label='Type a message...']"
        ]
        
        message_input = None
        for selector in selectors:
            try:
                message_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                if message_input:
                    break
            except TimeoutException:
                continue
        
        if not message_input:
            log_to_console("Could not find message input")
            return False
            
        log_to_console("Sending message...")
        message_input.clear()
        message_input.send_keys(message)
        message_input.send_keys(u'\ue007')  # Enter key
        
        time.sleep(2)
        log_to_console("Message sent successfully")
        return True
    except Exception as e:
        log_to_console(f"Error sending message: {str(e)}")
        return False

# Main app
def main():
    apply_custom_css()
    st.title("🔧 Simple Facebook Messenger Tool")
    
    # Initialize session state
    if 'console_logs' not in st.session_state:
        st.session_state.console_logs = []
    
    with st.expander("⚠️ Important Instructions", expanded=True):
        st.markdown("""
        1. **Get your Facebook cookies:**
           - Login to Facebook in your browser
           - Open Dev Tools (F12) → Application → Cookies → https://www.facebook.com
           - Copy `c_user` and `xs` cookie values
           - Format as: `c_user:VALUE\nxs:VALUE`
        
        2. **Get chat ID:**
           - Open Facebook chat
           - URL will be like: `https://www.facebook.com/messages/t/CHAT_ID`
        
        3. **Note:** This is a simplified demo. For full automation, 
           you'd need more sophisticated error handling.
        """)
    
    st.subheader("Configuration")
    
    # Cookie input
    cookies = st.text_area(
        "Facebook Cookies (name:value format)",
        placeholder="c_user:100001234567890\nxs:abcdef123456789...",
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        chat_id = st.text_input("Chat ID", placeholder="Enter chat ID from URL")
    with col2:
        delay = st.number_input("Delay (seconds)", min_value=1, value=3)
    
    message = st.text_area("Message to Send", placeholder="Enter your message here...")
    
    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Send Single Message", use_container_width=True):
            if not cookies or not chat_id or not message:
                st.error("Please fill all fields")
            else:
                # Clear logs
                st.session_state.console_logs = []
                log_to_console("Starting process...")
                
                # Initialize driver
                driver = init_driver()
                if not driver:
                    st.error("Failed to initialize browser")
                    return
                
                try:
                    # Login
                    if login_to_facebook(driver, cookies):
                        # Send message
                        send_message_to_chat(driver, chat_id, message)
                    else:
                        log_to_console("Login failed")
                finally:
                    driver.quit()
                    log_to_console("Process completed")
    
    with col2:
        if st.button("🧹 Clear Console", use_container_width=True):
            st.session_state.console_logs = []
    
    # Console output
    st.markdown("---")
    st.subheader("Console Output")
    console_content = "\n".join(st.session_state.console_logs) if st.session_state.console_logs else "No logs yet..."
    st.markdown(f'<div class="console-box">{console_content}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
