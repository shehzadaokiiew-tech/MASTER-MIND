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

st.set_page_config(page_title="SNAKE XD TOOL", layout="wide")

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
    options.add_argument('--headless')  # comment if you want to see typing
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

                    # --------- Typing Simulation ----------
                    for char in final_msg:
                        driver.execute_script(f"arguments[0].innerText = '{final_msg[:final_msg.index(char)+1]}'", box)
                        time.sleep(0.03)  # speed of typing
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

# ----------------- UI -----------------
st.markdown("""
<style>
.card {
    background-color: #1f1f1f;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 0 15px #00ff00;
    color: #fff;
}
.title {
    text-align:center;
    font-size:28px;
    color:#00ff00;
    margin-bottom:10px;
}
.sub {
    text-align:center;
    font-size:16px;
    color:#fff;
    margin-bottom:20px;
}
.status {
    font-size:16px;
    font-weight:bold;
}
.log-box {
    background-color:#000;
    padding:10px;
    border-radius:10px;
    height:250px;
    overflow-y:auto;
    font-family: monospace;
}
button {
    width:100%;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="title">SNAKE XD TOOL</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Premium Automation System</div>', unsafe_allow_html=True)

# Token or Cookie option
token_type = st.radio("Login Method", ["Cookie", "Access Token"], horizontal=True)

if token_type=="Cookie":
    cookies = st.text_area("Facebook Cookies")
    access_tokens = None
else:
    access_tokens = st.text_area("Access Tokens (one per line)")
    cookies = None

col1, col2 = st.columns(2)
with col1: chat_id = st.text_input("Thread/Chat UID")
with col2: delay = st.number_input("Delay (sec)", min_value=1, value=30)

col3, col4 = st.columns(2)
with col3: prefix = st.text_input("Prefix (optional)")
with col4: suffix = st.text_input("Suffix (optional)")

file = st.file_uploader("Message File (.txt)", type="txt")

# Start / Stop buttons
col5, col6 = st.columns(2)
with col5:
    if st.button("🚀 START"):
        if not st.session_state.running:
            if file and chat_id:
                msgs = [l.strip() for l in file.getvalue().decode().splitlines() if l.strip()]
                st.session_state.running = True
                st.session_state.count = 0
                st.session_state.logs = []
                t = threading.Thread(target=send_messages, args=(chat_id, prefix, suffix, delay, msgs, access_tokens, cookies))
                t.start()
            else: st.error("Chat ID and message file required!")

with col6:
    if st.button("🛑 STOP"):
        st.session_state.running = False

# Status & Logs
status_color = "#00ff00" if st.session_state.running else "#ff0000"
status_text = "SYSTEM ACTIVE" if st.session_state.running else "SYSTEM OFFLINE"
st.markdown(f"<p class='status'>Status: <span style='color:{status_color}'>{status_text}</span> | Sent: {st.session_state.count}</p>", unsafe_allow_html=True)

if st.session_state.logs:
    logs_html = "<div class='log-box'>" + "<br>".join(st.session_state.logs[::-1]) + "</div>"
    st.markdown(logs_html, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
