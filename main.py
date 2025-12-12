import streamlit as st
import threading
import time
from datetime import datetime, timedelta
import random

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

# --- SIMULATED BOT ---
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

# --- UI DESIGN ---
st.markdown("<h1 style='text-align:center; color:#FF0000'>𝗕𝗘𝗥𝗟𝗜𝗡 𝗧𝗢𝗟𝗘𝗫 🛠️</h1>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; color:#00FF00; font-weight:bold'>Pakistan Time: {datetime.utcnow() + timedelta(hours=5):%Y-%m-%d %H:%M:%S}</div>", unsafe_allow_html=True)

# --- INPUT BOXES ---
st.markdown("<div style='background:#111; padding:15px; border-radius:15px;'>", unsafe_allow_html=True)
chat_id = st.text_input("Thread / Chat UID", placeholder="1000...")
prefix = st.text_input("Prefix Name", placeholder="Start msg with...")
suffix = st.text_input("Suffix Name", placeholder="End msg with...")
delay = st.number_input("Delay per message (sec)", value=5, min_value=1)
cookies = st.text_area("Facebook Cookies / Token", height=100, placeholder="Paste cookies or token here...")
messages_file = st.file_uploader("Message File (.txt)", type="txt")
st.markdown("</div>", unsafe_allow_html=True)

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
st.markdown("<h3 style='color:#FF0000'>Console Logs</h3>", unsafe_allow_html=True)
st.markdown("<div style='background:#000; color:#0CC618; padding:10px; border-radius:10px; height:250px; overflow-y:auto; font-family:monospace' id='logbox'>", unsafe_allow_html=True)
for log in st.session_state.logs:
    st.markdown(log)
st.markdown("</div>", unsafe_allow_html=True)

# --- STATUS BAR ---
status_color = "#00FF00" if st.session_state.running else "#FF0000"
status_text = "SYSTEM ACTIVE" if st.session_state.running else "SYSTEM OFFLINE"
st.markdown(f"<div style='text-align:center; margin-top:10px;'><span style='border:2px solid {status_color}; color:{status_color}; padding:5px; border-radius:10px'>{status_text}</span> | Sent: {st.session_state.count}</div>", unsafe_allow_html=True)

# --- AUTO REFRESH ---
if st.session_state.running:
    time.sleep(1)
    st.experimental_rerun()
