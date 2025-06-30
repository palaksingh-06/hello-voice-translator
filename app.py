from flask import Flask, render_template, request
import os
from gtts import gTTS
import speech_recognition as sr
from googletrans import Translator
import pyttsx3
import random
import time
import logging

app = Flask(__name__)

translator = Translator()
recognizer = sr.Recognizer()
engine = pyttsx3.init()
logging.basicConfig(level=logging.INFO)

# Supported languages for gTTS
gtts_lang_map = {
    "en": "en",
    "hi": "hi",
    "fr": "fr",
    "es": "es"
}

@app.route("/", methods=["GET", "POST"])
def index():
    translated_text = ""
    filename = None

    if request.method == "POST":
        src_lang = request.form["srcLang"]
        dest_lang = request.form["destLang"]

        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1.5)
                logging.info("Listening...")
                try:
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                except sr.WaitTimeoutError:
                    translated_text = "No speech detected. Please try again."
                    return render_template("index.html", translated=translated_text, audio_file=None, random=random.random)

            try:
                text = recognizer.recognize_google(audio, language=src_lang)
                print("🎤 Recognized input:", text)
            except sr.UnknownValueError:
                translated_text = "Could not understand the audio."
                return render_template("index.html", translated=translated_text, audio_file=None, random=random.random)
            except sr.RequestError:
                translated_text = "Speech recognition service is unavailable."
                return render_template("index.html", translated=translated_text, audio_file=None, random=random.random)

            translated = translator.translate(text, src=src_lang, dest=dest_lang)
            translated_text = translated.text

            logging.info(f"Original: {text}")
            logging.info(f"Translated: {translated_text}")

            tts_lang = gtts_lang_map.get(dest_lang, "en")
            tts = gTTS(text=translated_text, lang=tts_lang)

            # Ensure static directory exists
            os.makedirs("static", exist_ok=True)

            filename = f"output_{int(time.time())}.mp3"
            tts.save(os.path.join("static", filename))
            logging.info(f"Audio saved as {filename}")

            # ✅ Remove old audio files **after** saving new one
            for f in os.listdir("static"):
                if f.startswith("output_") and f.endswith(".mp3") and f != filename:
                    try:
                        os.remove(os.path.join("static", f))
                    except Exception as cleanup_error:
                        logging.warning(f"Failed to remove old file: {cleanup_error}")

        except Exception as e:
            translated_text = "Error: " + str(e)

    return render_template("index.html", translated=translated_text, audio_file=filename, random=random.random)

if __name__ == "__main__":
    app.run(debug=True)



        
