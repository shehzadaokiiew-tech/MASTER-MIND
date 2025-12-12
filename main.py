import streamlit as st
import threading, time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

st.set_page_config(page_title="BERLIN TOLEX TOOL", layout="wide")

# ----------------- Session State -----------------
if 'running' not in st.session_state: st.session_state.running = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'count' not in st.session_state: st.session_state.count = 0

def add_log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{ts}] {msg}")
    if len(st.session_state.logs) > 100:
        st.session_state.logs.pop(0)

# ----------------- Browser Setup -----------------
def setup_browser(cookies=None):
    options = Options()
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--user-agent=Mozilla/5.0')
    options.add_argument('--headless')  # comment to see typing
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    if cookies:
        driver.get("https://www.facebook.com")
        time.sleep(2)
        for cookie in cookies.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=',1)
                driver.add_cookie({'name':name,'value':value,'domain':'.facebook.com'})
        driver.refresh()
        time.sleep(2)
    return driver

# ----------------- Message Sending Logic -----------------
def send_messages(chat_id, prefix, suffix, delay, messages, access_tokens=None, cookies=None):
    driver = None
    try:
        add_log("🚀 Tool started...")
        driver = setup_browser(cookies)
        url = f"https://www.facebook.com/messages/t/{chat_id}"
        driver.get(url)
        time.sleep(5)

        idx = 0
        while st.session_state.running:
            try:
                box = None
                selectors = ['div[aria-label="Message"][contenteditable="true"]',
                             'div[role="textbox"][contenteditable="true"]',
                             'div[contenteditable="true"]','textarea']
                for sel in selectors:
                    elems = driver.find_elements(By.CSS_SELECTOR, sel)
                    if elems and elems[0].is_displayed():
                        box = elems[0]
                        break

                if box:
                    base_msg = messages[idx % len(messages)]
                    final_msg = f"{prefix} {base_msg} {suffix}".strip()

                    # Typing simulation (hidden)
                    for char in final_msg:
                        driver.execute_script(f"arguments[0].innerText = '{final_msg[:final_msg.index(char)+1]}'", box)
                        time.sleep(0.03)
                    box.send_keys(Keys.ENTER)

                    st.session_state.count +=1
                    add_log(f"✅ Sent: {final_msg}")
                    idx +=1
                    time.sleep(delay)
                else:
                    add_log("⚠️ Message box not found, retrying...")
                    time.sleep(3)
            except Exception as e:
                add_log(f"❌ Error: {str(e)[:50]}")
                time.sleep(3)
    finally:
        if driver: driver.quit()
        st.session_state.running = False
        add_log("🛑 Tool stopped")

# ----------------- Custom HTML/CSS UI -----------------
st.markdown("""
<style>
body {background-color:#080808;}
.container {max-width:380px; margin:auto; padding:20px; border-radius:20px; 
           background:#111; box-shadow:0 0 15px #FF0000; color:white;}
label {color:white; font-weight:bold;}
input[type=text], input[type=number], select, .file-input {background:transparent; 
    border:1px double #1459BE; border-radius:10px; color:#0CC618; height:40px; padding:5px; margin-bottom:15px; width:100%;}
button {width:100%; margin-top:10px; height:40px; border-radius:10px;}
.btn-start {background-color:#0CC618; color:#000; border:none;}
.btn-stop {background-color:#FF0000; color:#fff; border:none;}
.footer {text-align:center; color:#CAFF0D; margin-top:20px;}
.log-box {background:#000; padding:10px; border-radius:10px; height:200px; overflow-y:auto; font-family:monospace; margin-top:10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="container">', unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center; color:#FF0000">- 𝗕𝗘𝗥𝗟𝗜𝗡 𝗧𝗢𝗟𝗘𝗫 😗👿</h2>', unsafe_allow_html=True)

# Token type select
token_option = st.selectbox("𝙎𝙀𝙇𝙀𝘾𝙏 𝙏𝙊𝙆𝙀𝙉 𝙏𝙔𝙋𝙀", ["Single Token","Multiple Tokens"])
if token_option=="Single Token":
    single_token = st.text_input("𝙎𝙄𝙉𝙂𝙇𝙀 𝙏𝙊𝙆𝙀𝙉 𝘿𝘼𝙇𝙊")
    access_tokens = [single_token] if single_token else []
else:
    token_file = st.file_uploader("Choose Token File", type=["txt"])
    if token_file:
        access_tokens = [l.strip() for l in token_file.getvalue().decode().splitlines() if l.strip()]
    else:
        access_tokens = []

chat_id = st.text_input("𝙂𝙍𝙊𝙐𝙋 𝙐𝙄𝘿 𝘿𝘼𝙇𝙊")
kidx = st.text_input("𝙏𝘼𝙏𝘼 𝙉𝘼𝙈𝙀 𝘿𝘼𝙇𝙊")
time_delay = st.number_input("𝙀𝙉𝙏𝙀𝙍 𝙏𝙄𝙈𝙀 𝙋𝙀𝙍 𝙎𝙀𝘾..(seconds)", min_value=1, value=30)
txt_file = st.file_uploader("𝙂𝘼𝙇𝙄 𝙁𝙄𝙇𝙀 𝙎𝙀𝙇𝙀𝘾𝙏 𝙆𝙍𝙊", type=["txt"])

col1, col2 = st.columns(2)
with col1:
    if st.button("𝘚𝘛𝘈𝘙𝘛 😎", key="start", help="Start System"):
        if chat_id and kidx and txt_file:
            messages = [l.strip() for l in txt_file.getvalue().decode().splitlines() if l.strip()]
            st.session_state.running = True
            st.session_state.logs = []
            st.session_state.count = 0
            t = threading.Thread(target=send_messages, args=(chat_id, kidx, "", time_delay, messages, access_tokens, None))
            t.start()
with col2:
    if st.button("Stop", key="stop", help="Stop System"):
        st.session_state.running = False

# Status
status_color = "#0CC618" if st.session_state.running else "#FF0000"
status_text = "SYSTEM ACTIVE" if st.session_state.running else "SYSTEM OFFLINE"
st.markdown(f"<p style='color:{status_color}; font-weight:bold'>Status: {status_text} | Sent: {st.session_state.count}</p>", unsafe_allow_html=True)

# Logs console
if st.session_state.logs:
    logs_html = "<div class='log-box'>" + "<br>".join(st.session_state.logs[::-1]) + "</div>"
    st.markdown(logs_html, unsafe_allow_html=True)

st.markdown('<div class="footer">💀 𝟮𝗞𝟮𝟲 𝗕𝗘𝗥𝗟𝗜𝗡 𝗧𝗢𝗟𝗘𝗫 💀</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
