import streamlit as st import time import threading import uuid from selenium import webdriver from selenium.webdriver.common.by import By from selenium.webdriver.common.keys import Keys from selenium.webdriver.chrome.options import Options from selenium.webdriver.chrome.service import Service from selenium.webdriver.common.action_chains import ActionChains from datetime import datetime from webdriver_manager.chrome import ChromeDriverManager from webdriver_manager.core.os_manager import ChromeType from streamlit.runtime.scriptrunner import add_script_run_ctx

-------------------------

New Streamlit App: Snake XD (Styled + Task Manager)

Save this file and run: streamlit run snake_xd_streamlit_new.py

Requirements: streamlit, selenium, webdriver-manager

-------------------------

st.set_page_config(page_title="SNAKE XD TOOL - NEW", layout="wide")

--- Load custom CSS to mimic screenshot's neon / dark style ---

CUSTOM_CSS = """

<style>
:root{--bg:#0c0b0b;--panel:#100b0b;--accent:#ffb300;--accent-2:#ff3b3b;--muted:#bdbdbd}
body {background: radial-gradient(#070707, #000000);}
.main-container{max-width:780px;margin:18px auto;padding:18px;background:linear-gradient(180deg,#0f0a0a, #130d0d);border-radius:22px;box-shadow:0 0 40px rgba(255,255,255,0.03) inset, 0 10px 40px rgba(0,0,0,0.7)}
.title-box{background:transparent;text-align:center;padding:14px 4px 8px}
.vip-title{font-family:Impact, sans-serif;color:#fff;font-size:36px;margin:0;text-shadow:0 0 20px rgba(255,179,0,0.15)}
.vip-subtitle{color:var(--muted);font-weight:600;letter-spacing:2px}
.label{color:#fff;font-weight:700;margin-bottom:6px}
.input-box{background:transparent;border-radius:10px;padding:8px;border:2px solid rgba(255,60,60,0.06)}
.stTextInput>div>div>input, textarea, .stTextArea>div>div>textarea{background:transparent;color:#fff;border:2px solid rgba(255,60,60,0.25);padding:12px;border-radius:8px}
.stNumberInput>div>div>input{background:transparent;color:#fff;border:2px solid rgba(255,60,60,0.25);padding:12px;border-radius:8px}
.stFileUploader>div{border:2px dashed rgba(255,60,60,0.25);padding:8px;border-radius:8px}
.button-neon{background:linear-gradient(90deg,#000,#0b0b0b);color:#fff;font-weight:800;padding:12px;border-radius:12px;border:3px solid rgba(255,60,60,0.6);width:100%}
.status-badge{display:inline-block;padding:8px 14px;border-radius:22px;font-weight:700}
.terminal-window{background:#060505;padding:12px;border-radius:10px;max-height:240px;overflow:auto;border:1px solid rgba(255,255,255,0.03)}
.log-line{color:#dcdcdc;font-family:monospace;padding:4px 0;border-bottom:1px dotted rgba(255,255,255,0.02)}
.task-row{display:flex;gap:8px;align-items:center}
.token-select{width:100%;padding:10px;border-radius:8px;border:2px solid rgba(255,179,0,0.35);background:transparent;color:#fff}
</style>""" st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

-------------------------

Session state initialization

-------------------------

if 'tasks' not in st.session_state: st.session_state.tasks = {}  # task_id -> {thread, stop_event, meta}

Helper: add log to a per-task log list stored in session_state

def add_task_log(task_id, msg): try: ts = datetime.now().strftime("%H:%M:%S") logs = st.session_state.tasks[task_id].setdefault('logs', []) logs.append(f"[{ts}] {msg}") if len(logs) > 200: logs.pop(0) except Exception: pass

--- BROWSER SETUP (same as original but exposed for reuse) ---

def setup_browser(headless=True): options = Options() if headless: options.add_argument('--headless=new') options.add_argument('--no-sandbox') options.add_argument('--disable-dev-shm-usage') options.add_argument('--disable-notifications') options.add_argument('--disable-popup-blocking') options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36') try: service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()) return webdriver.Chrome(service=service, options=options) except Exception: return webdriver.Chrome(options=options)

--- Core messaging process (per-task) ---

def start_process(task_id, chat_id, prefix, suffix, delay, cookies, messages, headless=True, max_loops=None): driver = None stop_event = st.session_state.tasks[task_id]['stop_event'] add_task_log(task_id, "🚀 Task initialized") try: driver = setup_browser(headless=headless) add_task_log(task_id, "🌐 Browser opened")

# inject cookies if provided
    try:
        driver.get('https://www.facebook.com')
        time.sleep(2)
        if cookies:
            for cookie in cookies.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    try:
                        driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com'})
                    except Exception as e:
                        # ignore bad cookie
                        pass
    except Exception as e:
        add_task_log(task_id, f"⚠️ Cookie inject failed: {str(e)[:40]}")

    url = f"https://www.facebook.com/messages/t/{chat_id}"
    add_task_log(task_id, f"🔗 Opening chat {chat_id}")
    driver.get(url)
    time.sleep(6)

    idx = 0
    loops = 0
    while not stop_event.is_set():
        try:
            box = None
            selectors = [
                'div[aria-label="Message"][contenteditable="true"]',
                'div[role="textbox"][contenteditable="true"]',
                'div[contenteditable="true"]',
                'textarea'
            ]
            for s in selectors:
                try:
                    found = driver.find_elements(By.CSS_SELECTOR, s)
                    if found and found[0].is_displayed():
                        box = found[0]
                        break
                except Exception:
                    continue

            if box:
                base_msg = messages[idx % len(messages)]
                part1 = f"{prefix} " if prefix else ""
                part3 = f" {suffix}" if suffix else ""
                final_msg = f"{part1}{base_msg}{part3}"

                try:
                    actions = ActionChains(driver)
                    actions.move_to_element(box).click().send_keys(final_msg).perform()
                    time.sleep(0.4)
                    actions.send_keys(Keys.ENTER).perform()
                except Exception:
                    try:
                        driver.execute_script("arguments[0].focus();", box)
                        driver.execute_script(f"arguments[0].innerText = `{final_msg}`;", box)
                        box.send_keys(Keys.ENTER)
                    except Exception as e:
                        add_task_log(task_id, f"❌ Send failed: {str(e)[:60]}")

                st.session_state.tasks[task_id]['sent'] = st.session_state.tasks[task_id].get('sent', 0) + 1
                add_task_log(task_id, f"✅ Sent: {final_msg}")
                idx += 1
                loops += 1
                if max_loops and loops >= max_loops:
                    add_task_log(task_id, "⏹️ Reached max loops")
                    break
                # sleep with periodic stop check
                slept = 0
                while slept < delay:
                    if stop_event.is_set():
                        break
                    time.sleep(1)
                    slept += 1
            else:
                add_task_log(task_id, "⚠️ Message box not found, retrying...")
                for _ in range(5):
                    if stop_event.is_set():
                        break
                    time.sleep(1)

        except Exception as e:
            add_task_log(task_id, f"❌ Loop error: {str(e)[:60]}")
            time.sleep(3)

except Exception as e:
    add_task_log(task_id, f"🛑 Crash: {str(e)[:80]}")
finally:
    try:
        if driver:
            driver.quit()
            add_task_log(task_id, "🔚 Browser closed")
    except Exception:
        pass
    st.session_state.tasks[task_id]['running'] = False
    add_task_log(task_id, "🔴 Task stopped")

--- Task control functions ---

def create_and_start_task(chat_id, prefix, suffix, delay, cookies, messages, headless=True, max_loops=None): task_id = str(uuid.uuid4())[:8] stop_event = threading.Event() st.session_state.tasks[task_id] = { 'meta': { 'chat_id': chat_id, 'prefix': prefix, 'suffix': suffix, 'delay': delay, }, 'stop_event': stop_event, 'running': True, 'logs': [], 'sent': 0 } thread = threading.Thread(target=start_process, args=(task_id, chat_id, prefix, suffix, delay, cookies, messages, headless, max_loops), daemon=True) add_script_run_ctx(thread) st.session_state.tasks[task_id]['thread'] = thread thread.start() return task_id

def stop_task(task_id): if task_id in st.session_state.tasks: st.session_state.tasks[task_id]['stop_event'].set() st.session_state.tasks[task_id]['running'] = False add_task_log(task_id, '🛑 Stop requested by user')

-------------------------

UI - Left panel: controls

-------------------------

st.markdown('<div class="main-container">', unsafe_allow_html=True) st.markdown('<div class="title-box"><h1 class="vip-title">NADU X SALLU — SNAKE XD</h1><div class="vip-subtitle">CONVO WEB TOOL</div></div>', unsafe_allow_html=True)

with st.form('task_form'): token_type = st.selectbox('SELECT TOKEN TYPE', options=['SINGLE TOKEN', 'MULTI TOKEN']) single_token = st.text_input('SINGLE TOKEN DALO' if token_type=='SINGLE TOKEN' else 'TOKENS (comma separated)')

chat_id = st.text_input('Enter Inbox/convo uid')
heater_name = st.text_input('Enter Your heater name')
delay = st.number_input('ENTER TIME (seconds)', min_value=1, value=60)

cookies = st.text_area('ENTER FACEBOOK COOKIES (VIP)')
abuse_file = st.file_uploader('ENTER ABUSE FILE (.txt)', type=['txt'])

submitted = st.form_submit_button('CREATE & START TASK ✅')

if submitted:
    if not chat_id or not cookies:
        st.error('CHAT ID aur COOKIES dono zaroori hain!')
    else:
        # build message list
        msgs = []
        if abuse_file:
            try:
                msgs = [l.strip() for l in abuse_file.getvalue().decode().splitlines() if l.strip()]
            except Exception:
                msgs = [abuse_file.name]
        else:
            if token_type == 'SINGLE TOKEN' and single_token:
                msgs = [single_token]
            else:
                # fallback
                msgs = [f"Hello from {heater_name or 'Heater'}"]

        task_id = create_and_start_task(chat_id, heater_name, single_token if token_type=='SINGLE TOKEN' else '', int(delay), cookies, msgs)
        st.success(f'Task created: {task_id} — It will run until you stop it')

st.markdown('<hr/>', unsafe_allow_html=True)

-------------------------

UI - Right panel: tasks list and controls

-------------------------

st.subheader('ACTIVE TASKS') if not st.session_state.tasks: st.info('Koi task active nahin hai. Upar form bhar ke task start karo.') else: for tid, data in list(st.session_state.tasks.items()): meta = data.get('meta', {}) col1, col2 = st.columns([3,1]) with col1: st.markdown(f"ID: {tid} — Chat: {meta.get('chat_id','-')} — Prefix: {meta.get('prefix','-')} — Sent: {data.get('sent',0)}") last_logs = '\n'.join(data.get('logs',[])[-6:]) st.text_area(f'Logs {tid}', value=last_logs, height=120, key=f'logs_{tid}') with col2: if data.get('running'): if st.button(f'STOP {tid}', key=f'stop_{tid}'): stop_task(tid) st.experimental_rerun() else: st.markdown('Stopped')

st.markdown('</div>', unsafe_allow_html=True)

Auto-refresh small UI while there are running tasks

if any(d.get('running') for d in st.session_state.tasks.values()): time.sleep(1) st.experimental_rerun()
