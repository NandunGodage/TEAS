from flask import Flask, render_template, request
import os
import speech_recognition as sr
from googletrans import Translator
from tensorflow.keras.models import load_model  # Keras for .h5 model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences  # Fix import
from werkzeug.utils import secure_filename
import ffmpeg  # Replacing moviepy with ffmpeg for audio extraction
import json

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"mp4", "mov", "avi"}

# Load your custom trained model for summarization (Keras .h5 format)
model_path = "model_folder/summarization_model.h5"  # Update with your actual model path
model = load_model(model_path)

# Load the tokenizer from the JSON file (if you have saved it separately)
tokenizer_path = "model_folder/tokenizer.json"  # Path to your tokenizer json file
with open(tokenizer_path, 'r') as f:
    tokenizer_json = json.load(f)
    tokenizer = tokenizer_from_json(tokenizer_json)

# Function to check allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

# Function to extract audio using ffmpeg
def extract_audio(video_path, audio_path):
    try:
        ffmpeg.input(video_path).output(audio_path, format="wav", acodec="pcm_s16le", ac=1, ar="16000").run(overwrite_output=True)
    except Exception as e:
        print("Error extracting audio:", e)
        return None
    return audio_path

# Function to convert speech to text
def speech_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data, language="ta")  # Tamil Language
    except sr.UnknownValueError:
        return "Speech could not be understood"
    except sr.RequestError:
        return "Error with Speech Recognition API"

# Function to translate text
def translate_text(text, target_lang="en"):
    translator = Translator()
    return translator.translate(text, dest=target_lang).text

# Function to summarize text using your custom model (Keras .h5 model)
def summarize_text(text):
    # Tokenizing the input text
    input_seq = tokenizer.texts_to_sequences([text])
    input_seq = pad_sequences(input_seq, maxlen=512, padding='post')

    # Predict the summary
    summary = model.predict(input_seq)

    # Decoding the summary into readable text
    decoded_summary = tokenizer.sequences_to_texts(summary)[0]
    return decoded_summary

@app.route("/tamil_summarization", methods=["GET", "POST"])
def tamil_summarization():
    summary_text = None
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("tamil_summarization.html", summary="No file uploaded.")

        file = request.files["file"]
        if file.filename == "" or not allowed_file(file.filename):
            return render_template("tamil_summarization.html", summary="Invalid file format.")

        # Save uploaded video
        filename = secure_filename(file.filename)
        video_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(video_path)

        # Convert video to audio
        audio_path = video_path.replace(".mp4", ".wav")
        extracted_audio = extract_audio(video_path, audio_path)

        if not extracted_audio:
            return render_template("tamil_summarization.html", summary="Error extracting audio from video.")

        # Convert speech to Tamil text
        tamil_text = speech_to_text(audio_path)

        # Translate Tamil text to English
        english_text = translate_text(tamil_text, "en")

        # Summarize English text using your custom model
        summarized_text = summarize_text(english_text)

        # Translate summarized English text back to Tamil
        final_summary = translate_text(summarized_text, "ta")

        return render_template("tamil_summarization.html", summary=final_summary)

    return render_template("tamil_summarization.html", summary=summary_text)

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
