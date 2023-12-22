import json
import os
import pyaudio
from vosk import Model, KaldiRecognizer
from gtts import gTTS
import pygame

# Initialize Pygame mixer
pygame.mixer.init()

# Load Vosk model
model_path = "model"  # Replace with your model path
if not os.path.exists(model_path):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    exit(1)
    
model_path = "model"  # Adjust this path based on your model folder
model = Model(model_path)

def listen_for_wake_word():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    recognizer = KaldiRecognizer(model, 16000)
    while True:
        data = stream.read(4000)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").lower()
            print(f"Recognized: {text}")
            if "hide the boys" in text:
                print("Wake word detected!")
                break

    stream.stop_stream()
    stream.close()
    p.terminate()
    return True

def listen_and_recognize():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    recognizer = KaldiRecognizer(model, 16000)
    while True:
        data = stream.read(4000)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:  # Check if text is not empty
                print(f"Recognized: {text}")
                break

    stream.stop_stream()
    stream.close()
    p.terminate()
    return text
def respond(text):
    text = text.lower()
    if 'bye' in text or 'goodbye' in text:
        response = "Goodbye! Have a nice day!"
        execute_response(response)
        return "EXIT_COMMAND"
    elif 'hello' in text or 'hi' in text:
        response = "Hello there! How can I help you?"
    elif 'weather' in text:
        response = "The weather is looking great today!"
    else:
        response = "I'm not sure how to respond to that."
    execute_response(response)

def execute_response(response):
    speech = gTTS(text=response, lang='en')
    speech.save('response.mp3')
    pygame.mixer.music.load('response.mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
def main():
    while True:
        if listen_for_wake_word():  # Listens for the wake word
            print("Wake word detected. Ready for command.")
            while True:
                command = listen_and_recognize()
                response = respond(command)
                if response == "EXIT_COMMAND":
                    print("Switching to wake word listening mode.")
                    break  # Exit the inner loop and listen for wake word again

if __name__ == "__main__":
    main()
print("Current Working Directory:", os.getcwd())