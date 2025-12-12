import streamlit as st
import threading
import time
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="𝗕𝗘𝗥𝗟𝗜𝗡 𝗧𝗢𝗟𝗘𝗫", layout="wide")

# --- Load HTML Design ---
def load_html():
    try:
        with open("design.html","r") as f:
            return f.read()
    except:
        return "<h3>Design file missing!</h3>"

# --- Session State ---
if 'running' not in st.session_state: st.session_state.running=False
if 'logs' not in st.session_state: st.session_state.logs=[]
if 'count' not in st.session_state: st.session_state.count=0
if 'task_id' not in st.session_state: st.session_state.task_id=None

# --- Log Function ---
def add_log(msg):
    ts = (datetime.utcnow()+timedelta(hours=5)).strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{ts}] {msg}")
    if len(st.session_state.logs)>200: st.session_state.logs.pop(0)

# --- Bot Simulation ---
def start_bot(chat_id,prefix,suffix,delay,messages):
    st.session_state.task_id=''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',k=6))
    idx=0
    add_log(f"🚀 Task #{st.session_state.task_id} started for chat {chat_id}")
    while st.session_state.running:
        msg = messages[idx%len(messages)]
        final_msg=f"{prefix} {msg} {suffix}".strip()
        st.session_state.count+=1
        add_log(f"✅ [Task {st.session_state.task_id}] Sent: {final_msg}")
        idx+=1
        time.sleep(delay)
    add_log(f"🛑 Task #{st.session_state.task_id} stopped")

# --- Render HTML ---
st.markdown(load_html(), unsafe_allow_html=True)

# --- Streamlit Buttons ---
col1,col2=st.columns(2)
with col1:
    if st.button("🚀 START"):
        messages=["Test message 1","Test message 2"]
        st.session_state.running=True
        st.session_state.count=0
        st.session_state.logs=[]
        t=threading.Thread(target=start_bot,args=("1234","Prefix","Suffix",5,messages))
        t.start()
with col2:
    if st.button("🛑 STOP"):
        st.session_state.running=False

# --- Console Logs ---
st.markdown("<div style='background:#000; color:#0CC618; padding:10px; border-radius:10px; height:250px; overflow-y:auto; font-family:monospace;'>", unsafe_allow_html=True)
for log in st.session_state.logs:
    st.markdown(log)
st.markdown("</div>", unsafe_allow_html=True)

# --- Auto Refresh ---
if st.session_state.running:
    time.sleep(1)
    st.experimental_rerun()
