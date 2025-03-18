from flask import Flask, render_template, request, redirect, url_for
import os
import speech_recognition as sr
from werkzeug.utils import secure_filename
import random
import torch
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"wav", "mp3"}

# Load your pre-trained model here
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-xlsr-53")
model = Wav2Vec2ForSequenceClassification.from_pretrained("path_to_your_model")

# Function to check allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

# Function to record and recognize speech
def recognize_speech(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        # Convert speech to text
        text = recognizer.recognize_google(audio_data, language="ta")  # Tamil Language
        return text
    except sr.UnknownValueError:
        return "Speech could not be understood"
    except sr.RequestError:
        return "Error with Speech Recognition API"

# Function to evaluate the speech using the trained model
def evaluate_pronunciation(input_audio):
    # Process the audio and get predictions
    inputs = processor(input_audio, return_tensors="pt", sampling_rate=16000)
    with torch.no_grad():
        logits = model(**inputs).logits
    # Make prediction
    predicted_class = logits.argmax().item()
    return predicted_class

@app.route("/speech_therapy", methods=["GET", "POST"])
def speech_therapy():
    # List of words/images for each difficulty
    words = {
        "easy": ["அம்மா", "அப்பா", "படி", "நன்றி"],
        "medium": ["கம்ப்யூட்டர்", "பரிசு", "சிரிப்பு", "படம்"],
        "hard": ["செயல்முறை", "தொழில்நுட்பம்", "பரிமாணம்", "அமைப்பியல்"]
    }
    
    current_word = None
    message = None
    reward_message = None
    difficulty = None
    audio_path = None

    if request.method == "POST":
        # Handle word selection
        difficulty = request.form.get("difficulty")
        current_word = random.choice(words[difficulty])
        # Handle audio file upload
        if "file" in request.files:
            file = request.files["file"]
            if file.filename == "" or not allowed_file(file.filename):
                return redirect(request.url)
            filename = secure_filename(file.filename)
            audio_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(audio_path)

            # Evaluate pronunciation
            predicted_word = recognize_speech(audio_path)
            correct = current_word in predicted_word

            if correct:
                message = "Great job! Your pronunciation is correct!"
                reward_message = "🎉 You earned a star! 🎉"
            else:
                message = f"Oops! Try again. You said: {predicted_word}"

    return render_template(
        "speech_therapy.html",
        current_word=current_word,
        message=message,
        reward_message=reward_message,
        difficulty=difficulty,
        audio_path=audio_path
    )

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
