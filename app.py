from apiconfig import ModelStory, ModelJumble, ModelGenerateWords
# from botocore.exceptions import NoCredentialsError
from prompts import (
    story_generation_tamil_prompt,
    tamil_language_evaluation_prompt,
    generate_story_ver_02_prompt,
    generate_tamil_words_prompt,
    match_tamil_words_prompt,
    generate_tamil_english_summary_prompt,
    generate_jumble_reasoning_prompt,
    generate_jumble_matching_reasoning_prompt
)

from functions_gpt import (
    convert_json_to_string,
    convert_string_to_json,
    convert_audio_to_transcript,
    clear_folder,
    convert_json_to_string_non_ascii,
    extract_audio_from_video,
    generate_reasoning_text,
    generate_text
)

from cloud import upload_file_to_s3
from fastapi import FastAPI, File, UploadFile, Form
import uvicorn
from openai import OpenAI
import boto3
import os
import yaml
import json


with open('./config/config.yml', 'r') as file:
    config_keys = yaml.safe_load(file)


gpt_fine_tune_key = config_keys['OPEN_AI_KEY']
fine_tune_job_id = config_keys['FINE_TUNE_JOB_ID']
reasoning_model_id = config_keys['REASONING_MODEL_ID']
fine_tune_job_id_ver_2 = config_keys['FINE_TUNE_JOB_ID_2']
latest_gpt_version = config_keys['LATEST_MODEL_VERSION']
reasoning_mini_model_id = config_keys['REASONING_MINI_MODEL_ID']

TEMP_FILE_NAME = config_keys['TEMP_FILE_NAME']
AUDIO_FOLDER_NAME = config_keys['AUDIO_FOLDER_NAME']
VIDEO_FOLDER_NAME = config_keys['VIDEO_FOLDER_NAME']

client = OpenAI(api_key = gpt_fine_tune_key)
os.makedirs(VIDEO_FOLDER_NAME, exist_ok=True)


def generate_story_ver_02_prompt_func(model_id, test_input):
    """Prompt Engineering for Tamil Language Evaluation"""
    try:
        completion = client.chat.completions.create(
          model=model_id,
          messages=generate_story_ver_02_prompt(test_input),
          response_format={
            "type": "text"
          },
          temperature=2,
          top_p=0.5,
          frequency_penalty=0,
          presence_penalty=0
        )
        return completion.choices[0].message.content
    except Exception as e:
        return ''



def generate_tamil_story(model_id, test_input):
    return generate_text(model_id, test_input, story_generation_tamil_prompt)

# def generate_jumble_words(model_id, test_input):
#     return generate_text(model_id, test_input, generate_jumble_prompt)

def generate_tamil_words(model_id, test_input):
    return generate_text(model_id, test_input, generate_tamil_words_prompt)

def match_tamil_words(model_id, test_input):
    return generate_text(model_id, test_input, match_tamil_words_prompt)

def generate_tamil_english_summary(model_id, test_input):
    return generate_text(model_id, test_input, generate_tamil_english_summary_prompt)

def generate_jumble_words_format(json_str):
    return generate_reasoning_text(
            model_id=reasoning_mini_model_id,
            test_input=json_str,
            prompt_func=generate_jumble_reasoning_prompt,
            response_format={"type": "json_object"},
            reasoning_effort='low'
    )


def evaluate_tamil_sentence_format(public_url):
    return generate_reasoning_text(
            model_id=reasoning_model_id,
            test_input=public_url,
            prompt_func=tamil_language_evaluation_prompt,
            response_format={"type": "json_object"},
            reasoning_effort='low'
    )

def check_jumble_sentence_correctness_format(json_str):
    return generate_reasoning_text(
        model_id=reasoning_mini_model_id,
        test_input=json_str,
        prompt_func=generate_jumble_matching_reasoning_prompt,
        response_format={"type": "json_object"},
        reasoning_effort='low'
    )



def generate_tamil_story_func(user_id, test_input): 
    try:
        print(test_input) 
        if test_input.split(',')[1] == "0":
            print("if",test_input)
            response = generate_tamil_story(fine_tune_job_id, test_input.split(',')[0])
        else:
            
            formatted_json = {
                    'கதையின் பெயர்': test_input.split(',')[0],
                    'சொற்கள்': test_input.split(',')[1]
                    }
            
            json_str = convert_json_to_string_non_ascii(formatted_json)
            print("else",json_str)
            response = generate_story_ver_02_prompt_func(fine_tune_job_id_ver_2, json_str)

        response_json = {
            'user_id': user_id,
            'heading': test_input.split(',')[0],
            'story': response
        }
        return response_json, '', 200
    except Exception as e:
        return '', str(e), 400
    

def generate_tamil_words_func(user_id, test_input): 
    try: 
        formatted_json = {
                'difficulty': test_input['difficulty'],
                }
            
        json_str = convert_json_to_string_non_ascii(formatted_json)
        response = generate_tamil_words(fine_tune_job_id_ver_2, json_str)
        response = convert_string_to_json(response)
        response_json = {
            'user_id': user_id,
            'heading': test_input,
            'words': response
        }
        return response_json, '', 200
    except Exception as e:
        return '', str(e), 400
    

def generate_tamil_jumble_func(user_id, test_input):
    try:
        print(test_input)
        # formatted_json = {
        #         'difficulty': test_input,
        #         }
        
        json_str = convert_json_to_string_non_ascii(test_input)
        json_response_string = generate_jumble_words_format(json_str)
        json_response_dict = json.loads(json_response_string)

        return json_response_dict, '', 200
    except Exception as e:
        return {}, str(e), 400
    
def match_tamil_words_func(user_id, test_input):
    try:
        formatted_json = {
                'original': test_input["original"],
                'transcript': test_input["transcript"]
                }
        
        json_str = convert_json_to_string_non_ascii(formatted_json)
        json_response_string = match_tamil_words(latest_gpt_version, json_str)
        json_response_dict = convert_string_to_json(json_response_string)

        return json_response_dict, '', 200
    except Exception as e:
        return {}, str(e), 400


def evaluate_tamil_sentence_func(user_id, test_input):
    try:
        json_response_string = evaluate_tamil_sentence_format(test_input)
        json_response_dict = convert_string_to_json(json_response_string)
        return json_response_dict, '', 200
    except Exception as e:
        return {}, str(e), 400
    
def evaluate_jumble_tamil_sentence_matching_func(user_id, test_input):
    try:
        print(test_input)
        json_str = convert_json_to_string_non_ascii(test_input)
        json_response_string = check_jumble_sentence_correctness_format(json_str)
        json_response_dict = convert_string_to_json(json_response_string)
        return json_response_dict, '', 200
    except Exception as e:
        return {}, str(e), 400

def process_video_for_audio_extraction(file_path):
    try:
        extract_audio_from_video(file_path)
        with open(AUDIO_FOLDER_NAME + '/' + TEMP_FILE_NAME, "rb") as audio_f:
            transcription = convert_audio_to_transcript(audio_f)
        return transcription, '', 200
    except Exception as e:
        return {}, str(e), 400
    

def generate_tamil_english_summary_func(user_id, test_input):
    try:
        print(test_input)
        formatted_json = {"transcript": test_input["transcript"]}


        json_str = convert_json_to_string(formatted_json)
        json_response_string = generate_tamil_english_summary(latest_gpt_version, json_str)
        print("summ", json_response_string)
        json_response_dict = json.loads(json_response_string)
        print("summdic", json_response_dict)
        return json_response_dict, '', 200
    except Exception as e:
        return {}, str(e), 400

app = FastAPI(docs_url=None, redoc_url=None)

@app.get('/info')
def index():
    return {'result': {'message': 'Tamil Story Generation Service'}, 'code': 200, 'error': ''}

@app.get('/health')
def health_check():
    return {'result': {'message': 'Tamil Story Generation Service'}, 'code': 200, 'error': ''}

@app.post('/generate/story/tamil')
def generate_tamil_story_api(data: ModelStory):
    if not data.user or not data.text:
        return {'result': '', 'code': 400, 'error': {'message': 'story generation failed! Please send proper request.'}}
    
    result, error, status = generate_tamil_story_func(data.user, data.text)
    return {'result': result, 'code': status, 'error': error}

@app.post('/generate/words/tamil')
def generate_tamil_words_api(data: ModelJumble):
    if not data.user or not data.text:
        return {'result': '', 'code': 400, 'error': {'message': 'words generation failed! Please send proper request.'}}
    
    result, error, status = generate_tamil_words_func(data.user, data.text)
    return {'result': result, 'code': status, 'error': error}

@app.post('/generate/questions/jumble')
def get_jumble_words_api(data: ModelJumble):
    if not data.user or not data.text:
        return {'result': '', 'code': 400, 'error': {'message': 'jumble generation failed! Please send proper request.'}}
    
    result, error, status = generate_tamil_jumble_func(data.user, data.text)
    return {'result': result, 'code': status, 'error': error}

@app.post('/check/questions/jumble')
def get_check_jumble_words_api(data: ModelJumble):
    if not data.user or not data.text:
        return {'result': '', 'code': 400, 'error': {'message': 'jumble generation failed! Please send proper request.'}}
    
    result, error, status = evaluate_jumble_tamil_sentence_matching_func(data.user, data.text)
    return {'result': result, 'code': status, 'error': error}

@app.post('/generate/image/evaluation')
def get_evaluate_tamil_api(data: ModelStory):
    if not data.user or not data.text:
        return {'result': '', 'code': 400, 'error': {'message': 'jumble generation failed! Please send proper request.'}}
    
    result, error, status = evaluate_tamil_sentence_func(data.user, data.text)
    return {'result': result, 'code': status, 'error': error}

@app.post('/generate/questions/match')
def get_pronounce_match_words_api(data: ModelJumble):
    if not data.user or not data.text:
        return {'result': '', 'code': 400, 'error': {'message': 'match words failed! Please send proper request.'}}
    
    result, error, status = match_tamil_words_func(data.user, data.text)
    return {'result': result, 'code': status, 'error': error}

@app.post('/generate/transcriptions/summary')
def get_video_extractor_api(data: ModelJumble):
    if not data.user or not data.text:
        return {'result': '', 'code': 400, 'error': {'message': 'match words failed! Please send proper request.'}}
    
    result, error, status = generate_tamil_english_summary_func(data.user, data.text)
    return {'result': result, 'code': status, 'error': error}



# @app.post('/detect/transcription/video')
# def get_transcript_video_api(user: str = Form(...), file: UploadFile = File(...)):
#     if not user or not file:
#         return {'result': '', 'code': 400, 'error': {'message': 'Extraction failed! Please send proper request.'}}
#     file_path = os.path.join(VIDEO_FOLDER_NAME, file.filename)
#     with open(file_path, "wb") as video_file:
#         video_file.write(file.file.read())
#         result, error, status = process_video_for_audio_extraction(file_path)
#     return {'result': result, 'code': status, 'error': error}


@app.post("/detect/transcription/video")
def get_transcript_video_api(
    user: str = Form(...),
    file: UploadFile = File(...)
):
    if not user or not file:
        return {
            "result": "",
            "code": 400,
            "error": {"message": "Extraction failed! Please send proper request."}
        }

    # ensure our temp folders exist
    os.makedirs(VIDEO_FOLDER_NAME, exist_ok=True)
    os.makedirs(AUDIO_FOLDER_NAME, exist_ok=True)

    video_path = os.path.join(VIDEO_FOLDER_NAME, file.filename)

    try:
        # 1) save the uploaded video
        with open(video_path, "wb") as vf:
            vf.write(file.file.read())

        # 2) extract audio into AUDIO_FOLDER_NAME / TEMP_FILE_NAME
        extract_audio_from_video(video_path)

        # 3) open the extracted audio and transcribe it
        audio_path = os.path.join(AUDIO_FOLDER_NAME, TEMP_FILE_NAME)
        with open(audio_path, "rb") as af:
            transcript = convert_audio_to_transcript(af)

        # successful response
        return {
            "result": transcript,
            "code": 200,
            "error": ""
        }

    except Exception as e:
        # on any error return a 500
        return {
            "result": "",
            "code": 500,
            "error": {"message": f"Transcription failed: {e}"}
        }

    finally:
        # always clean up both folders
        clear_folder(VIDEO_FOLDER_NAME)
        clear_folder(AUDIO_FOLDER_NAME)


@app.post("/detect/transcription/audio")
async def get_transcript_audio_api(
    user: str = Form(...),
    file: UploadFile = File(...)
):
    # 1) Basic request validation
    if not user or not file:
        return {
            "result": "",
            "code": 400,
            "error": {"message": "Extraction failed! Please send proper request."}
        }

    # 2) Ensure our tmp folder exists
    os.makedirs(AUDIO_FOLDER_NAME, exist_ok=True)
    file_path = os.path.join(AUDIO_FOLDER_NAME, file.filename)

    # 3) Write out the incoming file
    with open(file_path, "wb") as out_f:
        out_f.write(await file.read())

    # 4) Transcribe inside try/except/finally so that clear_folder ALWAYS runs
    try:
        with open(file_path, "rb") as audio_f:
            transcript = convert_audio_to_transcript(audio_f)
        return {
            "result": transcript,
            "code": 200,
            "error": ""
        }
    except Exception as e:
        return {
            "result": "",
            "code": 500,
            "error": {"message": f"Transcription failed: {e}"}
        }
    finally:
        clear_folder(AUDIO_FOLDER_NAME)

@app.post("/detect/transcription/audio")
def get_transcript_audio_api(user: str = Form(...), file: UploadFile = File(...)):
    if not user or not file:
        return {
            "result": "",
            "code": 400,
            "error": {"message": "Extraction failed! Please send proper request."},
        }

    os.makedirs(AUDIO_FOLDER_NAME, exist_ok=True)
    file_path = os.path.join(AUDIO_FOLDER_NAME, file.filename)
    with open(file_path, "wb") as out_f:
        out_f.write(file.file.read())

    with open(file_path, "rb") as audio_f:
        try:
            transcript = convert_audio_to_transcript(audio_f)
            clear_folder(AUDIO_FOLDER_NAME)
        except Exception as e:
            clear_folder(AUDIO_FOLDER_NAME)
            return {
                "result": "",
                "code": 500,
                "error": {"message": f"Transcription failed: {e}"},
            }

    return {
        "result": transcript,
        "code": 200,
        "error": "",
    }

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)