from flask import Flask, request, jsonify
import os
import threading
import dg
import os.path
import asyncio

app = Flask(__name__)
tasks = {}

def process_audio(file_path, task_id):
    try:
        transcripts = asyncio.run(dg.main_transcription()) 
        tasks[task_id] = {'result': transcripts}
    except Exception as e:
        tasks[task_id] = {'result': str(e)}

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Retrieve the task ID from the request
    task_id = request.form.get('id')
    if not task_id:
        return jsonify({'error': 'Task ID is required'}), 400

    if file:
        # Extract extension from the original file name
        _, file_extension = os.path.splitext(file.filename)

        # Use task_id as the name but keep the original extension
        filename = os.path.join('recordings', f"{task_id}{file_extension}")
        file.save(filename)

        tasks[task_id] = {'result': None}

        thread = threading.Thread(target=process_audio, args=(filename, task_id))
        thread.start()

        return jsonify({'task_id': task_id}), 202

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    if task_id not in tasks:
        return jsonify({'error': 'Invalid task ID'}), 404

    result = tasks[task_id]

    if 'result' not in result or result['result'] is None:
        return jsonify({'status': 'Processing'}), 202
    else:
        return jsonify({'result': result['result']}), 200

if __name__ == '__main__':
    app.run(debug=True)
