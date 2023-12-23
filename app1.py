# from flask import Flask, request, jsonify
# import os
# import threading
# import dg
# import os.path
# import asyncio
# import boto3
# from botocore.exceptions import NoCredentialsError

# app = Flask(__name__)
# tasks = {}

# # AWS S3 setup
# AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
# AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
# S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

# # Set up AWS S3 client
# s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

# # def upload_to_s3(file_name, content):
# #     try:
# #         s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=file_name, Body=content)
# #         return True
# #     except NoCredentialsError:
# #         return False

# # def upload_to_s3(file_path, task_id):
# #     try:
# #         file_path = f"{task_id}.txt"
# #         # Open the file in binary read mode
# #         with open(file_path, 'rb') as file:
# #             s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=f"{task_id}.txt", Body=file)
# #         return True
# #     except NoCredentialsError:
# #         return False


# # def process_audio(file_path, task_id):
# #     try:
# #         diarization_result = asyncio.run(dg.main_transcription())
# #         result_file_name = f"{task_id}.txt"
# #         upload_to_s3(result_file_name, task_id)
# #     except Exception as e:
# #         error_file_name = f"{task_id}_error.txt"
# #         upload_to_s3(error_file_name, str(e))

# def upload_to_s3(file_path, task_id):
#     try:
#         # Upload the file at 'file_path' to S3
#         with open(file_path, 'rb') as file:
#             s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=f"{task_id}.txt", Body=file)
#         return True
#     except NoCredentialsError:
#         return False

# # def process_audio(file_path, task_id):
# #     try:
# #         diarization_result = asyncio.run(dg.main_transcription())
# #         result_file_name = f"{task_id}.txt"

# #         # Write the response to a text file
# #         with open(result_file_name, 'w') as file:
# #             file.write(diarization_result)

# #         # Call upload_to_s3 with the path of the newly created file
# #         upload_to_s3(result_file_name, task_id)
# #     except Exception as e:
# #         error_file_name = f"{task_id}_error.txt"
# #         with open(error_file_name, 'w') as file:
# #             file.write(str(e))
# #         upload_to_s3(error_file_name, task_id)

# import json

# def process_audio(file_path, task_id):
#     try:
#         diarization_result = asyncio.run(dg.main_transcription())
#         result_file_name = f"{task_id}.txt"

#         # Convert the dictionary to a JSON string if it's not a string
#         if not isinstance(diarization_result, str):
#             diarization_result = json.dumps(diarization_result, indent=4)

#         # Write the response to a text file
#         with open(result_file_name, 'w') as file:
#             file.write(diarization_result)

#         # Call upload_to_s3 with the path of the newly created file
#         upload_to_s3(result_file_name, task_id)
#     except Exception as e:
#         error_file_name = f"{task_id}_error.txt"
#         with open(error_file_name, 'w') as file:
#             file.write(str(e))
#         upload_to_s3(error_file_name, task_id)



# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files or 'id' not in request.form:
#         return jsonify({'error': 'Missing file or ID'}), 400

#     file = request.files['file']
#     task_id = request.form['id']

#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     if file:
#         _, file_extension = os.path.splitext(file.filename)
#         filename = os.path.join('recordings', f"{task_id}{file_extension}")
#         file.save(filename)

#         tasks[task_id] = {'result': None}

#         thread = threading.Thread(target=process_audio, args=(filename, task_id))
#         thread.start()

#         return jsonify({'task_id': task_id}), 202

# @app.route('/result/<task_id>', methods=['GET'])
# def get_result(task_id):
#     try:
#         result_file = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=f"{task_id}.txt")
#         diarization_result = result_file['Body'].read().decode('utf-8')
#         return jsonify({'result': diarization_result}), 200
#     except s3_client.exceptions.NoSuchKey:
#         return jsonify({'error': 'Result not found'}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify
import os
import threading
import dg
import os.path

app = Flask(__name__)
tasks = {}

def process_audio(file_path, task_id):
    try:
        transcripts = asyncio.run(dg.main_transcription(file_path))  # Assuming the transcription function needs the file path
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
    task_id = request.form.get('task_id')
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
