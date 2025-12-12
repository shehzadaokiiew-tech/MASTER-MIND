import time
import random
import threading
from datetime import datetime

class Task:
    def __init__(self, task_id, config, cookies):
        self.task_id = task_id
        self.config = config  # Dict with group_uid, prefix, target, messages, delay
        self.cookies = cookies  # List of cookie dicts
        self.status = "Stopped"
        self.start_time = None
        self.stop_time = None
        self.uptime = 0
        self.logs = []
        self.thread = None
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self.status = "Running"
            self.start_time = datetime.now()
            self.thread = threading.Thread(target=self.run_task)
            self.thread.start()

    def stop(self):
        self.running = False
        self.status = "Stopped"
        self.stop_time = datetime.now()
        if self.thread:
            self.thread.join()

    def restart(self):
        self.stop()
        self.start()

    def run_task(self):
        messages = self.config['messages']
        delay = self.config['delay']
        index = 0
        while self.running and index < len(messages):
            # Simulate sending a message (replace with real logic, e.g., Selenium)
            success = random.choice([True, False])  # Mock success/failure
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] Message {index+1}: {'Sent' if success else 'Failed'} - {self.config['prefix']} {self.config['target']} {messages[index]}"
            self.logs.append(log_entry)
            index += 1
            time.sleep(delay)
        self.status = "Completed"
        self.running = False

# Global task storage (in-memory, for demo; use a DB for persistence)
tasks = {}
task_counter = 0