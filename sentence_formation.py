from flask import Flask, render_template, request, jsonify
import pandas as pd
import random
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

app = Flask(__name__)

# Load trained model and tokenizer for sentence validation
model_path = "your_model_directory"  # Update with the actual path of your trained model
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

# Load dataset (CSV with normal and jumbled sentences)
csv_file = "sentences.csv"  # Make sure the CSV contains columns: "sentence", "jumbled"

# Function to fetch a random sentence from the CSV
def get_random_sentence():
    df = pd.read_csv(csv_file)
    row = df.sample(n=1).iloc[0]
    return row["sentence"], row["jumbled"]

# Function to validate student’s sentence arrangement
def check_sentence(user_sentence, correct_sentence):
    inputs = tokenizer(user_sentence, correct_sentence, return_tensors="pt", truncation=True)
    outputs = model(**inputs)
    prediction = torch.argmax(outputs.logits).item()
    return prediction == 1  # Return True if the model classifies it as correct

@app.route("/sentence_formation", methods=["GET", "POST"])
def sentence_formation():
    if request.method == "POST":
        action = request.json.get("action")

        if action == "generate":
            sentence, jumbled = get_random_sentence()
            return jsonify({"sentence": sentence, "jumbled": jumbled})

        elif action == "check":
            user_sentence = request.json.get("user_sentence")
            correct_sentence = request.json.get("correct_sentence")

            if check_sentence(user_sentence, correct_sentence):
                return jsonify({"success": True, "message": "Correct! Well done! 🎉"})
            else:
                return jsonify({"success": False, "message": "Try again! Keep going! 😊"})

    return render_template("sentence_formation.html")

if __name__ == "__main__":
    app.run(debug=True)
