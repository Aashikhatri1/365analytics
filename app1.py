# from flask import Flask, request, jsonify
# import os
# import threading
# import dg
# import os.path
# import asyncio

# app = Flask(__name__)
# tasks = {}

# def process_audio(file_path, task_id):
#     try:
#         transcripts = asyncio.run(dg.main_transcription()) 
#         tasks[task_id] = {'result': transcripts}
#     except Exception as e:
#         tasks[task_id] = {'result': str(e)}

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     # Retrieve the task ID from the request
#     task_id = request.form.get('id')
#     if not task_id:
#         return jsonify({'error': 'Task ID is required'}), 400

#     if file:
#         # Extract extension from the original file name
#         _, file_extension = os.path.splitext(file.filename)

#         # Use task_id as the name but keep the original extension
#         filename = os.path.join('recordings', f"{task_id}{file_extension}")
#         file.save(filename)

#         tasks[task_id] = {'result': None}

#         thread = threading.Thread(target=process_audio, args=(filename, task_id))
#         thread.start()

#         return jsonify({'task_id': task_id}), 202

# @app.route('/result/<task_id>', methods=['GET'])
# def get_result(task_id):
#     if task_id not in tasks:
#         return jsonify({'error': 'Invalid task ID'}), 404

#     result = tasks[task_id]

#     if 'result' not in result or result['result'] is None:
#         return jsonify({'status': 'Processing'}), 202
#     else:
#         return jsonify({'result': result['result']}), 200

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify
import os
import threading
import dg
import requests
from urllib.parse import urlparse
import boto3
import asyncio
from flask import Flask, request, jsonify
import os.path

app = Flask(__name__)
tasks = {}

# MongoDB setup
MONGO_DB_URI = os.environ.get("MONGO_DB_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME")
MONGO_DB_COLLECTION = os.environ.get("MONGO_DB_COLLECTION_REC")

# Set up MongoDB connection
client = MongoClient(MONGO_DB_URI)
db = client[MONGO_DB_NAME]
collection = db[MONGO_DB_COLLECTION]

def download_file(url, local_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(response.content)

def process_audio(filename, task_id):
    try:
        transcripts = asyncio.run(dg.main_transcription(filename)) 
        tasks[task_id] = {'result': transcripts}
    except Exception as e:
        tasks[task_id] = {'result': str(e)}

@app.route('/upload_url', methods=['POST'])
def upload_recording_url():
    data = request.json
    if not data or 'file' not in data:
        return jsonify({'error': 'No file URL provided'}), 400

    file_url = data['file']
    task_id = data.get('id')
    file_type = data.get('type')  

    if not task_id:
        return jsonify({'error': 'ID is required'}), 400
        
    # Insert into MongoDB
    collection.insert_one({"file": file_url, "id": task_id, "type": file_type})
    
    parsed_url = urlparse(file_url)
    file_name = os.path.basename(parsed_url.path)
    _, file_extension = os.path.splitext(file_name)

    filepath = os.path.join('recordings', f"{task_id}{file_extension}")
    download_file(file_url, filepath)
    filename = f"{task_id}{file_extension}"
    tasks[task_id] = {'result': None}

    thread = threading.Thread(target=process_audio, args=(filename, task_id))
    thread.start()

    return jsonify({'task_id': task_id}), 202
    
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
        return jsonify({'error': 'ID is required'}), 400

    if file:
        # Extract extension from the original file name
        _, file_extension = os.path.splitext(file.filename)

        # Use task_id as the name but keep the original extension
        filepath = os.path.join('recordings', f"{task_id}{file_extension}")
        file.save(filepath)
        filename = f"{task_id}{file_extension}"
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


# # adding 'type' parameter
# @app.route('/result/<task_id>/<task_type>', methods=['GET'])
# def get_result(task_id, task_type):
#     if task_id not in tasks:
#         return jsonify({'error': 'Invalid task ID'}), 404

#     # Check if the task_type is valid
#     if task_type not in ['callRecording', 'meeting']:
#         return jsonify({'error': 'Invalid task type'}), 400

#     result = tasks[task_id]

#     # Check if the task type matches
#     if result.get('type') != task_type:
#         return jsonify({'error': 'Task type does not match'}), 400

#     if 'result' not in result or result['result'] is None:
#         return jsonify({'status': 'Processing', 'type': task_type}), 202
#     else:
#         return jsonify({'result': result['result'], 'type': task_type}), 200

# if __name__ == '__main__':
#     app.run(debug=True)
