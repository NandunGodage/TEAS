from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/tamil_summarization")
def tamil_summarization():
    return render_template("tamil_summarization.html")

@app.route("/sentence_formation")
def sentence_formation():
    return render_template("sentence_formation.html")

@app.route("/speech_therapy")
def speech_therapy():
    return render_template("speech_therapy.html")

if __name__ == "__main__":
    app.run(debug=True)
