from deepgram import Deepgram
import asyncio, os, sys, shutil
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
# Your Deepgram API Key
DEEPGRAM_API_KEY = os.environ.get('DEEPGRAM_API_KEY')

# Folders for storing recordings and transcripts
FOLDER_PATH = 'recordings'
TRANSCRIPTIONS_FOLDER = 'transcriptions'
COMPLETED_FOLDER = 'recordings_processed'

def seconds_to_timestamp(seconds):
    """Convert seconds to a timestamp format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f'{hours:02}:{minutes:02}:{seconds:05.2f}'

def format_transcript(words):
    """Format the words array into a dialogue transcript."""
    current_speaker = None
    transcript = []
    for word_info in words:
        speaker = word_info["speaker"]
        if current_speaker != speaker:
            if transcript: 
                transcript.append('\n')
            transcript.append(f'SPEAKER {speaker} {seconds_to_timestamp(word_info["start"])}\n')
            current_speaker = speaker
        transcript.append(word_info['word'] + ' ')
    return ''.join(transcript).strip()

def process_words(words):
    for word_info in words:
        word = word_info["word"]
        start = word_info["start"]
        end = word_info["end"]
        speaker = word_info["speaker"]
        print(f"Word: '{word}', Start: {start}, End: {end}, Speaker: {speaker}")

# Function to save transcript to text file in the transcriptions folder
def save_transcript(filename, transcript):
    if not os.path.exists(TRANSCRIPTIONS_FOLDER):
        os.makedirs(TRANSCRIPTIONS_FOLDER)
    with open(os.path.join(TRANSCRIPTIONS_FOLDER, f"{filename}.txt"), "w") as file:
        file.write(transcript)

# Function to move the processed audio file
def move_processed_file(filename):
    if not os.path.exists(COMPLETED_FOLDER):
        os.makedirs(COMPLETED_FOLDER)
    shutil.move(os.path.join(FOLDER_PATH, filename), os.path.join(COMPLETED_FOLDER, filename))

# Async main function with filename argument
async def main_transcription(target_filename):
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    transcripts = {}

    # Check if the target file exists and is either a WAV or MP3 file
    if target_filename in os.listdir(FOLDER_PATH) and (target_filename.endswith('.wav') or target_filename.endswith('.mp3')):
        file_path = os.path.join(FOLDER_PATH, target_filename)
        print(f"Transcribing {target_filename}...")

        with open(file_path, 'rb') as audio:
            source = {
                'buffer': audio,
                'mimetype': 'audio/wav' if target_filename.endswith('.wav') else 'audio/mpeg'
            }
            options = {
                'smart_format': True,
                'diarize': True  # Enable diarization
            }
            try:
                response = await asyncio.create_task(
                    deepgram.transcription.prerecorded(source, options)
                )

                # Handle the response with diarization data
                words_array = response["results"]["channels"][0]["alternatives"][0]["words"]

                # Process the words array
                transcript = format_transcript(words_array)
                transcripts[target_filename] = transcript
                print(transcript)
                print(f"Transcript for {target_filename} added.")

                # Move the processed file
                move_processed_file(target_filename)

                # Update MongoDB entry (if applicable)
                # update_mongodb_entry(target_filename, client)

            except Exception as e:
                print(f"Error transcribing {target_filename}: {e}")
    else:
        print(f"File {target_filename} not found or not a supported audio file format.")

    return transcripts

# # Async main function with filename argument
# async def main_transcription(target_filename):
#     deepgram = Deepgram(DEEPGRAM_API_KEY)
#     transcripts = {}

#     # Check if the target file exists in the folder
#     if target_filename in os.listdir(FOLDER_PATH) and target_filename.endswith('.wav'):
#         file_path = os.path.join(FOLDER_PATH, target_filename)
#         print(f"Transcribing {target_filename}...")

#         with open(file_path, 'rb') as audio:
#             source = {
#                 'buffer': audio,
#                 'mimetype': 'audio/wav'
#             }
#             options = {
#                 'smart_format': True,
#                 'diarize': True  # Enable diarization
#             }
#             try:
#                 response = await asyncio.create_task(
#                     deepgram.transcription.prerecorded(source, options)
#                 )

#                 # Handle the response with diarization data
#                 words_array = response["results"]["channels"][0]["alternatives"][0]["words"]

#                 # Process the words array
#                 transcript = format_transcript(words_array)
#                 transcripts[target_filename] = transcript
#                 print(transcript)
#                 print(f"Transcript for {target_filename} added.")

#                 # Move the processed file
#                 move_processed_file(target_filename)

#                 # Update MongoDB entry (if applicable)
#                 # update_mongodb_entry(target_filename, client)

#             except Exception as e:
#                 print(f"Error transcribing {target_filename}: {e}")
#     else:
#         print(f"File {target_filename} not found or not a WAV file.")

#     return transcripts

## Transcribing all the files in a folder
# # Async main function
# async def main_transcription():
#     deepgram = Deepgram(DEEPGRAM_API_KEY)
#     transcripts = {}

#     # Iterating over each file in the folder
#     for filename in os.listdir(FOLDER_PATH):
#         if filename.endswith('.wav'):  # Check if the file is a WAV file
#             file_path = os.path.join(FOLDER_PATH, filename)
#         # elif filename.endswith('.mp3'):  # Check if the file is a WAV file
#         #     file_path = os.path.join(FOLDER_PATH, filename)
#             print(f"Transcribing {filename}...")

#             with open(file_path, 'rb') as audio:
#                 source = {
#                     'buffer': audio,
#                     'mimetype': 'audio/wav'
#                 }
#                 options = {
#                     'smart_format': True,
#                     'diarize': True  # Enable diarization
#                 }
#                 try:
#                     response = await asyncio.create_task(
#                         deepgram.transcription.prerecorded(source, options)
#                     )

#                     # Handle the response with diarization data
#                     words_array = response["results"]["channels"][0]["alternatives"][0]["words"]

#                     # Process the words array
#                     transcript = format_transcript(words_array)
#                     transcripts[filename] = transcript
#                     print(transcript)
#                     print(f"Transcript for {filename} added.")

#                     # Move the processed file
#                     move_processed_file(filename)

#                     # Update MongoDB entry
#                     # update_mongodb_entry(filename, client)

#                 except Exception as e:
#                     print(f"Error transcribing {filename}: {e}")

#     return transcripts
