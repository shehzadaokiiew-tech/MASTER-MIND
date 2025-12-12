import streamlit as st
import requests
import time
from datetime import datetime

FLASK_URL = 'http://localhost:5000'  # Flask backend URL

st.set_page_config(page_title="VIP Task Manager", layout="wide", page_icon="🚀")

# Custom CSS for VIP-style UI
st.markdown("""
<style>
.main { background-color: #ffffff; }
.stButton>button { border-radius: 10px; background-color: #007bff; color: white; }
.card { background-color: #f8f9fa; border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["Main Task Panel", "Task History & Logs"])

if page == "Main Task Panel":
    st.title("🚀 VIP Automated Task Manager")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Cookie Input")
    tab1, tab2 = st.tabs(["Manual Paste", "Upload File"])
    with tab1:
        manual_cookies = st.text_area("Paste cookies (one per line)")
        if st.button("Submit Manual Cookies"):
            response = requests.post(f"{FLASK_URL}/upload_cookies", data={'manual': manual_cookies})
            st.success(response.json().get('message', 'Error'))
    with tab2:
        uploaded_file = st.file_uploader("Upload cookies file")
        if st.button("Upload File"):
            if uploaded_file:
                files = {'file': uploaded_file}
                response = requests.post(f"{FLASK_URL}/upload_cookies", files=files)
                st.success(response.json().get('message', 'Error'))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Task Configuration")
    group_uid = st.text_input("Group UID")
    prefix = st.text_input("Prefix Name")
    target = st.text_input("Target Name")
    message_file = st.file_uploader("Upload Message Text File")
    delay = st.slider("Delay (seconds per message)", 0.1, 10.0, 1.0)
    if st.button("Create Task"):
        if message_file:
            messages = [line.decode('utf-8').strip() for line in message_file if line.decode('utf-8').strip()]
            data = {
                'group_uid': group_uid,
                'prefix': prefix,
                'target': target,
                'messages': messages,
                'delay': delay
            }
            response = requests.post(f"{FLASK_URL}/create_task", json=data)
            st.success(f"Task created with ID: {response.json().get('task_id')}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Task Control")
    task_id = st.number_input("Task ID to Control", min_value=0, step=1)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Task"):
            response = requests.post(f"{FLASK_URL}/start_task/{task_id}")
            st.success(response.json().get('message', 'Error'))
    with col2:
        if st.button("Stop Task"):
            response = requests.post(f"{FLASK_URL}/stop_task/{task_id}")
            st.success(response.json().get('message', 'Error'))
    st.markdown('</div>', unsafe_allow_html=True)

    # Live Console/Log (polls every 2 seconds)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Live Console/Log")
    log_placeholder = st.empty()
    while True:
        response = requests.get(f"{FLASK_URL}/get_tasks")
        tasks = response.json()
        for task in tasks:
            if task['id'] == task_id:
                logs = "\n".join(task['logs'])
                log_placeholder.text_area("Logs", logs, height=200)
                break
        time.sleep(2)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Task History & Logs":
    st.title("📊 Task History & Logs")
    response = requests.get(f"{FLASK_URL}/get_tasks")
    tasks = response.json()
    for task in tasks:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"Task {task['id']} - {task['status']}")
        st.write(f"Start Time: {task['start_time']}")
        st.write(f"Stop Time: {task['stop_time']}")
        st.write(f"Uptime: {task['uptime']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"Restart {task['id']}", key=f"restart_{task['id']}"):
                requests.post(f"{FLASK_URL}/restart_task/{task['id']}")
                st.success("Restarted")
        with col2:
            if st.button(f"Delete {task['id']}", key=f"delete_{task['id']}"):
                requests.delete(f"{FLASK_URL}/delete_task/{task['id']}")
                st.success("Deleted")
        with col3:
            if st.button(f"View Details {task['id']}", key=f"details_{task['id']}"):
                st.write("Config:", task['config'])
                st.write("Logs:", "\n".join(task['logs']))
        st.markdown('</div>', unsafe_allow_html=True)