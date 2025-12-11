# main.py
import streamlit as st
import threading, time, uuid, os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

# ---------- Flask API (task manager) ----------
app = Flask("berlin_tolex_api")
CORS(app)

UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory tasks store
tasks = {}
tasks_lock = threading.Lock()
last_task_id = None

def safe_log(task_id, text):
    with tasks_lock:
        if task_id in tasks:
            tasks[task_id]['logs'].append(text)

def worker(task_id, first_name, second_name, interval_sec, msgs, token):
    safe_log(task_id, f"Task started — {first_name} | {second_name} | messages={len(msgs)} | token_preview={(token[:18]+'...') if token else '<no-token>'}")
    with tasks_lock:
        tasks[task_id]['status'] = 'running'
        tasks[task_id]['start_ts'] = time.time()
    try:
        # simulate login
        safe_log(task_id, f"Login successful for {first_name} as {second_name}")
        for i, msg in enumerate(msgs, start=1):
            if tasks[task_id]['stop_event'].is_set():
                safe_log(task_id, "Received stop signal — exiting.")
                with tasks_lock:
                    tasks[task_id]['status'] = 'stopped'
                return
            # simulate sending
            safe_log(task_id, f"Sending message #{i}: {msg[:140]}")
            # artificial delay to mimic real work
            time.sleep(max(1.0, float(interval_sec)))
        safe_log(task_id, "All messages sent — finishing.")
        with tasks_lock:
            tasks[task_id]['status'] = 'finished'
    except Exception as e:
        safe_log(task_id, f"Worker exception: {e}")
        with tasks_lock:
            tasks[task_id]['status'] = 'error'

@app.route('/start', methods=['POST'])
def api_start():
    global last_task_id
    first_name = request.form.get('first_name','').strip()
    second_name = request.form.get('second_name','').strip()
    interval = request.form.get('time','1').strip()
    token_text = request.form.get('cookie_text','')

    # message file required
    msgs = []
    if 'msg_file' in request.files and request.files['msg_file'].filename:
        f = request.files['msg_file']
        try:
            txt = f.read().decode(errors='ignore')
            msgs = [ln.strip() for ln in txt.splitlines() if ln.strip()]
        except Exception as e:
            return jsonify({'error': 'failed reading message file: '+str(e)}), 400
    else:
        return jsonify({'error':'msg_file required'}), 400

    if not first_name or not second_name:
        return jsonify({'error':'first_name and second_name required'}), 400

    # create task
    task_id = str(uuid.uuid4())[:12]
    stop_evt = threading.Event()
    with tasks_lock:
        tasks[task_id] = {
            'thread': None,
            'stop_event': stop_evt,
            'logs': [],
            'status': 'queued',
            'start_ts': None,
            'meta': {'first_name': first_name, 'second_name': second_name, 'interval': interval}
        }
        last_task_id = task_id

    t = threading.Thread(target=worker, args=(task_id, first_name, second_name, interval, msgs, token_text), daemon=True)
    tasks[task_id]['thread'] = t
    t.start()

    resp = make_response(jsonify({'task_id': task_id}))
    if token_text:
        # set cookie on response for convenience
        resp.set_cookie('vip_token', token_text, max_age=60*60*24)
    return resp

@app.route('/status/<task_id>', methods=['GET'])
def api_status(task_id):
    with tasks_lock:
        if task_id not in tasks:
            return jsonify({'error':'unknown task','logs':[]}), 404
        d = tasks[task_id]
        return jsonify({'status': d['status'], 'logs': d['logs'][-200:], 'start_ts': int(d['start_ts']) if d['start_ts'] else None})

@app.route('/stop', methods=['POST'])
def api_stop():
    data = request.get_json() or {}
    task_id = data.get('task_id')
    if not task_id:
        return jsonify({'error':'task_id required'}), 400
    with tasks_lock:
        if task_id not in tasks:
            return jsonify({'error':'unknown task'}), 404
        tasks[task_id]['stop_event'].set()
    return jsonify({'ok': True, 'task_id': task_id})

@app.route('/last_task', methods=['GET'])
def api_last_task():
    with tasks_lock:
        if not tasks:
            return jsonify({'task_id': ''})
        # last inserted
        last = list(tasks.keys())[-1]
        return jsonify({'task_id': last, 'status': tasks[last]['status'], 'start_ts': int(tasks[last]['start_ts']) if tasks[last]['start_ts'] else None})

def run_flask():
    # run on 127.0.0.1:8765
    app.run(host='127.0.0.1', port=8765, debug=False, threaded=True)

# ---------------- Streamlit UI embedding ----------------
st.set_page_config(page_title="Berlin Tolex Controller", layout="wide")
if 'flask_started' not in st.session_state:
    # launch flask in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    st.session_state['flask_started'] = True
    time.sleep(0.2)

st.title("Berlin Tolex — Controller (Streamlit)")
st.caption("If the embedded UI cannot connect to backend, ensure you allow localhost connections.")

# embed the index.html
HERE = os.path.dirname(__file__)
html_path = os.path.join(HERE, "index.html")
if not os.path.exists(html_path):
    st.error("index.html missing. Save the provided index.html in same folder as main.py")
else:
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=760, scrolling=True)

st.markdown("---")
st.write("Flask API running at `http://127.0.0.1:8765` inside the Streamlit process.")
