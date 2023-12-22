from flask import Flask, request, jsonify
import os
import threading
import dg
import os.path
import asyncio
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)
tasks = {}

# AWS S3 setup
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

# Set up AWS S3 client
s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

def upload_to_s3(file_name, content):
    try:
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=file_name, Body=content)
        return True
    except NoCredentialsError:
        return False

def process_audio(file_path, task_id):
    try:
        diarization_result = asyncio.run(dg.perform_diarization(file_path))
        result_file_name = f"{task_id}.txt"
        upload_to_s3(result_file_name, diarization_result)
    except Exception as e:
        error_file_name = f"{task_id}_error.txt"
        upload_to_s3(error_file_name, str(e))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'id' not in request.form:
        return jsonify({'error': 'Missing file or ID'}), 400

    file = request.files['file']
    task_id = request.form['id']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        _, file_extension = os.path.splitext(file.filename)
        filename = os.path.join('recordings', f"{task_id}{file_extension}")
        file.save(filename)

        tasks[task_id] = {'result': None}

        thread = threading.Thread(target=process_audio, args=(filename, task_id))
        thread.start()

        return jsonify({'task_id': task_id}), 202

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    try:
        result_file = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=f"{task_id}.txt")
        diarization_result = result_file['Body'].read().decode('utf-8')
        return jsonify({'result': diarization_result}), 200
    except s3_client.exceptions.NoSuchKey:
        return jsonify({'error': 'Result not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
