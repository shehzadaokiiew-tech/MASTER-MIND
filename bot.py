from flask import Flask, request, jsonify, session
from werkzeug.utils import secure_filename
import os
from utils import Task, tasks, task_counter

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management
app.config['UPLOAD_FOLDER'] = '/tmp'  # Temp folder for uploads

@app.route('/upload_cookies', methods=['POST'])
def upload_cookies():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        with open(filepath, 'r') as f:
            cookies = [line.strip() for line in f if line.strip()]  # Simple parsing; assume one cookie per line
        session['cookies'] = cookies
        os.remove(filepath)  # Clean up
    elif 'manual' in request.form:
        cookies = request.form['manual'].split('\n')
        session['cookies'] = cookies
    return jsonify({'message': 'Cookies uploaded'})

@app.route('/create_task', methods=['POST'])
def create_task():
    global task_counter
    data = request.json
    config = {
        'group_uid': data['group_uid'],
        'prefix': data['prefix'],
        'target': data['target'],
        'messages': data['messages'],  # List from uploaded file
        'delay': data['delay']
    }
    cookies = session.get('cookies', [])
    task_id = task_counter
    tasks[task_id] = Task(task_id, config, cookies)
    task_counter += 1
    return jsonify({'task_id': task_id})

@app.route('/start_task/<int:task_id>', methods=['POST'])
def start_task(task_id):
    if task_id in tasks:
        tasks[task_id].start()
        return jsonify({'message': 'Task started'})
    return jsonify({'error': 'Task not found'}), 404

@app.route('/stop_task/<int:task_id>', methods=['POST'])
def stop_task(task_id):
    if task_id in tasks:
        tasks[task_id].stop()
        return jsonify({'message': 'Task stopped'})
    return jsonify({'error': 'Task not found'}), 404

@app.route('/restart_task/<int:task_id>', methods=['POST'])
def restart_task(task_id):
    if task_id in tasks:
        tasks[task_id].restart()
        return jsonify({'message': 'Task restarted'})
    return jsonify({'error': 'Task not found'}), 404

@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if task_id in tasks:
        tasks[task_id].stop()
        del tasks[task_id]
        return jsonify({'message': 'Task deleted'})
    return jsonify({'error': 'Task not found'}), 404

@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    task_list = []
    for task in tasks.values():
        task_list.append({
            'id': task.task_id,
            'status': task.status,
            'start_time': str(task.start_time) if task.start_time else None,
            'stop_time': str(task.stop_time) if task.stop_time else None,
            'uptime': str(datetime.now() - task.start_time) if task.start_time and task.running else '0',
            'config': task.config,
            'logs': task.logs[-10:]  # Last 10 logs for brevity
        })
    return jsonify(task_list)

if __name__ == '__main__':
    app.run(debug=True, port=21101)