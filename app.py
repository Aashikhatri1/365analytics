
from flask import Flask, request, jsonify
import os
import threading
import dg
import gpt
import uuid
import os.path
import asyncio
from pymongo import MongoClient

app = Flask(__name__)
tasks = {}

# MongoDB setup
MONGO_DB_URI = os.environ.get("MONGO_DB_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME")
MONGO_DB_COLLECTION = os.environ.get("MONGO_DB_COLLECTION")

# Set up MongoDB connection
client = MongoClient(MONGO_DB_URI)
db = client[MONGO_DB_NAME]
collection = db[MONGO_DB_COLLECTION]

def generate_unique_task_id():
    return str(uuid.uuid4())

def process_audio(file_path, task_id):
    try:
        transcripts = asyncio.run(dg.main_transcription(file_path))
        response = gpt.gpt_response(transcripts)

        # Store response in MongoDB
        collection.insert_one({'session_id': task_id, 'result': response})
    except Exception as e:
        collection.insert_one({'session_id': task_id, 'result': str(e)})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        task_id = generate_unique_task_id()

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
    result = collection.find_one({'session_id': task_id})

    if result is None:
        return jsonify({'error': 'Invalid task ID'}), 404

    if 'result' not in result or result['result'] is None:
        return jsonify({'status': 'Processing'}), 202
    else:
        return jsonify({'result': result['result']}), 200

if __name__ == '__main__':
    app.run(debug=True)
