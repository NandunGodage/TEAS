from pathlib import Path
from openai import OpenAI
import yaml
import streamlit as st
import json
from moviepy import VideoFileClip
from pydub import AudioSegment

import os
import shutil

with open('./config/config.yml', 'r') as file:
    config_keys = yaml.safe_load(file)

gpt_fine_tune_key = config_keys['OPEN_AI_KEY']


TEMP_FILE_NAME = config_keys['TEMP_FILE_NAME']
AUDIO_FOLDER_NAME = config_keys['AUDIO_FOLDER_NAME']
VIDEO_FOLDER_NAME = config_keys['VIDEO_FOLDER_NAME']


client = OpenAI(api_key = gpt_fine_tune_key)

def text_to_audio(model, voice, input_text, speech_file_path):
    with client.audio.speech.with_streaming_response.create(
        model=model,
        voice=voice,
        input=input_text) as response:
        response.stream_to_file(speech_file_path)


# Function to read and play audio
def play_audio_file(audio_file_path):
    audio = AudioSegment.from_file(audio_file_path)
    audio.export('temp.wav', format="wav")
    audio_file = open('temp.wav', "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/wav")


def convert_audio_to_transcript(audio_file):
    transcription = client.audio.transcriptions.create(
        model="gpt-4o-transcribe", 
        file=audio_file,
        language="ta", 
        response_format="text",
        prompt="")
    return transcription


def extract_audio_from_video(mp4_file):
    video_clip = VideoFileClip(mp4_file)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(AUDIO_FOLDER_NAME + '/' + TEMP_FILE_NAME)
    audio_clip.close()
    video_clip.close()

def convert_json_to_string(formatted_json):
    json_str = json.dumps(formatted_json)
    return json_str

def convert_json_to_string_non_ascii(formatted_json):
    # ensure_ascii=False will let non‐ASCII characters pass through
    # indent=4 will pretty-print it if you like
    return json.dumps(formatted_json, ensure_ascii=False, indent=4)

def convert_string_to_json(formatted_string):
    str_json = json.loads(formatted_string)
    return str_json

def clear_folder(folder_path):
    """
    Deletes all files and directories inside `folder_path`, but leaves
    the folder itself intact.

    :param folder_path: path to the folder you want to clear
    """
    if not os.path.isdir(folder_path):
        return

    for entry in os.listdir(folder_path):
        entry_path = os.path.join(folder_path, entry)
        try:
            if os.path.isfile(entry_path) or os.path.islink(entry_path):
                os.unlink(entry_path)             
            elif os.path.isdir(entry_path):
                shutil.rmtree(entry_path)
        except Exception as e:
            print(f"Failed to delete {entry_path}. Reason: {e}")


def generate_reasoning_text(
    model_id, 
    test_input, 
    prompt_func,         # Generalized prompt engineering function
    response_format,     # For example: {"type": "json_object"}
    reasoning_effort     # For example: "low"
):
    """
    Generalized language evaluation using prompt engineering, customizable for any language/task.
    """
    try:
        completion = client.responses.create(
            model=model_id,
            input=prompt_func(test_input),
            text={
                "format": response_format    # Expecting a dict like {"type": "json_object"}
            },
            reasoning={
                "effort": reasoning_effort   # e.g., "low", "medium", "high"
            },
            tools=[],
            store=False
        )
        return completion.output[1].content[0].text

    except Exception as e:
        return e
    

def generate_text(model_id, test_input, prompt_function):
    """Generate text using the specified model and prompt function."""
    try:
        completion = client.chat.completions.create(
            model=model_id,
            messages=prompt_function(test_input)
        )
        return completion.choices[0].message.content
    except Exception as e:
        return ''