# app.py
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import threading
import time
import pytz
from datetime import datetime

# =========================
# GUI STYLING
# =========================
st.set_page_config(page_title="Premium FB Message Tool", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #000000;
        color: #0CC618;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #111111;
        color: #0CC618;
        border: 2px solid red;
        border-radius: 5px;
    }
    .stButton>button {
        background-color: red;
        color: #ffffff;
        border-radius: 5px;
        height: 3em;
        width: 100%;
    }
    .stFileUploader>div>div>input {
        color: #0CC618;
    }
    .console-panel {
        background-color: #111111;
        color: #0CC618;
        height: 250px;
        overflow-y: scroll;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid red;
        font-family: monospace;
    }
    </style>
    """, unsafe_allow_html=True
)

# =========================
# INPUTS
# =========================
st.title("Premium Facebook Message Automation Tool")

cookies = st.text_area("Facebook Cookies", placeholder="Paste your cookies here", height=150)
token_option = st.radio("Token Option", ["Single Token", "Multiple Tokens (Upload File)"])
if token_option == "Single Token":
    access_token = st.text_input("Access Token")
else:
    token_file = st.file_uploader("Upload Token File (.txt)")

thread_uid = st.text_input("Thread/Chat UID")
prefix = st.text_input("Message Prefix")
suffix = st.text_input("Message Suffix")
delay = st.number_input("Delay per message (seconds)", min_value=1, value=3)
repeat_count = st.number_input("Number of repetitions", min_value=1, value=1)
message_file = st.file_uploader("Upload Message File (.txt)")

# =========================
# CONSOLE PANEL
# =========================
console = st.empty()

def log(msg):
    now = datetime.now(pytz.timezone("Asia/Karachi")).strftime("%H:%M:%S")
    console.markdown(f"<div class='console-panel'>[{now}] {msg}</div>", unsafe_allow_html=True)

# =========================
# SELENIUM MESSAGE SENDER
# =========================
stop_flag = False  # Global stop flag

def send_messages(cookies, thread_uid, messages, prefix, suffix, delay, task_id):
    global stop_flag

    # Setup Chrome Options
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--user-data-dir=selenium")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get("https://www.facebook.com")
        time.sleep(5)
        
        # Set cookies if provided
        if cookies:
            driver.delete_all_cookies()
            for cookie in cookies.split(";"):
                name, value = cookie.strip().split("=", 1)
                driver.add_cookie({"name": name, "value": value})
            driver.refresh()
            time.sleep(5)

        # Navigate to chat
        driver.get(f"https://www.facebook.com/messages/t/{thread_uid}")
        time.sleep(5)

        sent_count = 0

        for i in range(repeat_count):
            for msg in messages:
                if stop_flag:
                    log(f"Task {task_id} stopped manually.")
                    driver.quit()
                    return
                final_msg = f"{prefix} {msg} {suffix}".strip()
                try:
                    # Message input box
                    input_box = driver.find_element(By.XPATH, "//div[@aria-label='Message']")
                    input_box.send_keys(final_msg)
                    input_box.send_keys("\n")  # Send message
                    sent_count += 1
                    log(f"Task {task_id} | Sent ({sent_count}): {final_msg}")
                    time.sleep(delay)
                except Exception as e:
                    log(f"Task {task_id} | Failed to send: {final_msg} | Error: {e}")

        log(f"Task {task_id} completed. Total messages sent: {sent_count}")
    except Exception as e:
        log(f"Task {task_id} encountered an error: {e}")
    finally:
        driver.quit()

# =========================
# BUTTON ACTIONS
# =========================
if st.button("Start"):
    if not cookies:
        st.error("Please provide Facebook cookies!")
    elif not thread_uid:
        st.error("Please provide Thread/Chat UID!")
    elif not message_file:
        st.error("Please upload a message file!")
    else:
        messages = [line.strip() for line in message_file.getvalue().decode("utf-8").splitlines() if line.strip()]
        task_id = int(time.time())
        stop_flag = False
        threading.Thread(target=send_messages, args=(cookies, thread_uid, messages, prefix, suffix, delay, task_id), daemon=True).start()
        log(f"Task {task_id} started. Total messages to send: {len(messages) * repeat_count}")

if st.button("Stop"):
    stop_flag = True

if st.button("Clear Logs"):
    console.empty()
