import streamlit as st
import threading
import time
from datetime import datetime, timedelta
import random

# --- Page config ---
st.set_page_config(page_title="SNAKE XD TOOL", layout="wide")

# --- Session State ---
if 'running' not in st.session_state: st.session_state.running=False
if 'logs' not in st.session_state: st.session_state.logs=[]
if 'count' not in st.session_state: st.session_state.count=0
if 'task_id' not in st.session_state: st.session_state.task_id=None

# --- Custom CSS ---
st.markdown("""
<style>
body {background:#080808;}
.container {max-width:400px; margin:auto; padding:20px; border-radius:20px; background:#111; box-shadow:0 0 20px #FF0000;}
input, textarea {background:#000; color:#0CC618; border:1px double #1459BE; border-radius:10px; width:100%; padding:7px; margin-bottom:15px; height:40px;}
button {width:100%; height:40px; border-radius:10px; margin-top:10px; font-weight:bold; cursor:pointer;}
.btn-start {background:#0CC618; color:#000; border:none;}
.btn-stop {background:#FF0000; color:#fff; border:none;}
.log-box {background:#000; padding:10px; border-radius:10px; height:250px; overflow-y:auto; font-family:monospace; color:#0CC618; box-shadow:0 0 10px #0CC618;}
h1,h3 {margin:5px 0; color:#FFFFFF;}
.footer {text-align:center; color:#CAFF0D; margin-top:20px;}
</style>
""", unsafe_allow_html=True)

# --- Container ---
st.markdown('<div class="container">', unsafe_allow_html=True)
st.markdown("<h1>SNAKE XD TOOL 😎👿</h1>", unsafe_allow_html=True)

# --- Inputs ---
chat_id = st.text_input("THREAD / CHAT UID", placeholder="1000...")
prefix = st.text_input("PREFIX NAME", placeholder="Start msg with...")
suffix = st.text_input("SUFFIX NAME", placeholder="End msg with...")
delay = st.number_input("DELAY (SEC)", min_value=1, value=5)
cookies = st.text_area("COOKIES / TOKEN", height=100, placeholder="Paste cookies/token here...")
file = st.file_uploader("MESSAGE FILE (.TXT)", type="txt")

# --- Buttons ---
col1, col2 = st.columns(2)
with col1:
    start_clicked = st.button("🚀 START")
with col2:
    stop_clicked = st.button("🛑 STOP")

# --- Logs display ---
st.markdown("<h3>Console Logs</h3>", unsafe_allow_html=True)
log_box = st.empty()

# --- Functions ---
def add_log(msg):
    ts = (datetime.utcnow()+timedelta(hours=5)).strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{ts}] {msg}")
    if len(st.session_state.logs)>200: st.session_state.logs.pop(0)

def update_logs():
    log_box.markdown("<div class='log-box'>"+ "<br>".join(st.session_state.logs[::-1])+"</div>", unsafe_allow_html=True)

def start_task():
    if not file:
        add_log("❌ No message file uploaded!")
        return
    messages = [l.strip() for l in file.getvalue().decode().splitlines() if l.strip()]
    task_id = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
    st.session_state.task_id = task_id
    st.session_state.running=True
    add_log(f"🚀 Task #{task_id} started for chat {chat_id}")

    idx = 0
    while st.session_state.running:
        msg = messages[idx%len(messages)]
        final_msg = f"{prefix} {msg} {suffix}".strip()
        st.session_state.count+=1
        add_log(f"✅ [Task {task_id}] Sent: {final_msg}")
        idx+=1
        update_logs()
        time.sleep(delay)

# --- Start / Stop logic ---
if start_clicked and not st.session_state.running:
    t = threading.Thread(target=start_task)
    t.start()

if stop_clicked:
    st.session_state.running=False
    add_log(f"🛑 Task #{st.session_state.task_id} stopped")

# --- Status ---
status_color = "#00c853" if st.session_state.running else "#d50000"
status_text = "SYSTEM ACTIVE" if st.session_state.running else "SYSTEM OFFLINE"
st.markdown(f"<div style='text-align:center; margin-top:10px;'>"
            f"<span style='border:2px solid {status_color}; color:{status_color}; padding:5px; border-radius:5px;'>{status_text}</span>"
            f" <span style='border:2px solid #333; color:#333; padding:5px; border-radius:5px; margin-left:5px;'>SENT: {st.session_state.count}</span>"
            f"</div>", unsafe_allow_html=True)

# --- Footer ---
st.markdown("<div class='footer'>💀 SNAKE XD TOOL 💀<br>👑 OWNER: BERLIN ✌ <a href='https://www.facebook.com/rajput.bolti.public' style='color:#E9FF00;'>Contact</a></div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Auto-refresh logs ---
if st.session_state.running:
    update_logs()
    time.sleep(1)
    st.experimental_rerun()
