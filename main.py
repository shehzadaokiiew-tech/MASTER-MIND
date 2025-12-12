import streamlit as st
import threading
import time
from datetime import datetime, timedelta
import random

# --- PAGE CONFIG ---
st.set_page_config(page_title="𝗕𝗘𝗥𝗟𝗜𝗡 𝗧𝗢𝗟𝗘𝗫", layout="wide")

# --- SESSION STATE ---
if 'running' not in st.session_state: st.session_state.running = False
if 'logs' not in st.session_state: st.session_state.logs = []
if 'count' not in st.session_state: st.session_state.count = 0
if 'task_id' not in st.session_state: st.session_state.task_id = None

# --- LOG FUNCTION ---
def add_log(msg):
    ts = (datetime.utcnow() + timedelta(hours=5)).strftime("%H:%M:%S")  # Pakistan time
    st.session_state.logs.append(f"[{ts}] {msg}")
    if len(st.session_state.logs) > 200:
        st.session_state.logs.pop(0)

# --- BOT SIMULATION ---
def start_bot(chat_id, prefix, suffix, delay, messages):
    st.session_state.task_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    idx = 0
    add_log(f"🚀 Task #{st.session_state.task_id} started for chat {chat_id}")
    while st.session_state.running:
        msg = messages[idx % len(messages)]
        final_msg = f"{prefix} {msg} {suffix}".strip()
        st.session_state.count += 1
        add_log(f"✅ [Task {st.session_state.task_id}] Sent: {final_msg}")
        idx += 1
        time.sleep(delay)
    add_log(f"🛑 Task #{st.session_state.task_id} stopped")

# --- OLD TOOL STYLE HTML ---
st.markdown("""
<style>
body {background-color:#080808; color:white; font-family:Arial;}
.container {max-width:380px; margin:auto; padding:20px; border-radius:20px; background:#111; box-shadow:0 0 15px #FF0000;}
input, textarea, select {background:#000; color:#0CC618; border:1px double #1459BE; border-radius:10px; width:100%; padding:7px; margin-bottom:15px;}
button {width:100%; height:40px; border-radius:10px; margin-top:10px; font-weight:bold;}
.btn-start {background:#0CC618; color:#000; border:none;}
.btn-stop {background:#FF0000; color:#fff; border:none;}
.footer {text-align:center; color:#CAFF0D; margin-top:20px;}
.log-box {background:#000; padding:10px; border-radius:10px; height:250px; overflow-y:auto; font-family:monospace; color:#0CC618;}
h1, h2, h3 {text-align:center;}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="container">', unsafe_allow_html=True)
st.markdown('<h1>𝗕𝗘𝗥𝗟𝗜𝗡 𝗧𝗢𝗟𝗘𝗫 😎👿</h1>', unsafe_allow_html=True)
st.markdown(f'<h3>Pakistan Time: {(datetime.utcnow() + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")}</h3>', unsafe_allow_html=True)

# --- INPUT BOXES ---
chat_id = st.text_input("Thread / Chat UID", placeholder="1000...")
prefix = st.text_input("Prefix Name", placeholder="Start msg with...")
suffix = st.text_input("Suffix Name", placeholder="End msg with...")
delay = st.number_input("Delay per message (sec)", value=5, min_value=1)
cookies = st.text_area("Facebook Cookies / Token", height=100, placeholder="Paste cookies or token here...")
messages_file = st.file_uploader("Message File (.txt)", type="txt")

# --- BUTTONS ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 START"):
        if not st.session_state.running:
            if messages_file and chat_id:
                messages = [l.strip() for l in messages_file.getvalue().decode().splitlines() if l.strip()]
                st.session_state.running = True
                st.session_state.count = 0
                st.session_state.logs = []
                t = threading.Thread(target=start_bot, args=(chat_id, prefix, suffix, delay, messages))
                t.start()
            else:
                st.error("Please provide Chat ID and Message File!")

with col2:
    if st.button("🛑 STOP"):
        st.session_state.running = False

# --- CONSOLE LOG BOX ---
st.markdown("<h3>Console Logs</h3>", unsafe_allow_html=True)
st.markdown('<div class="log-box">', unsafe_allow_html=True)
for log in st.session_state.logs:
    st.markdown(log)
st.markdown('</div>', unsafe_allow_html=True)

# --- STATUS BAR ---
status_color = "#00FF00" if st.session_state.running else "#FF0000"
status_text = "SYSTEM ACTIVE" if st.session_state.running else "SYSTEM OFFLINE"
st.markdown(f'<div style="text-align:center; margin-top:10px;"><span style="border:2px solid {status_color}; color:{status_color}; padding:5px; border-radius:10px">{status_text}</span> | Sent: {st.session_state.count}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- AUTO REFRESH ---
if st.session_state.running:
    time.sleep(1)
    st.experimental_rerun()
