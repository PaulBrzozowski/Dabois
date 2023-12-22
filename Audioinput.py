import speech_recognition as sr
from gtts import gTTS
import pygame

# Initialize the recognizer
r = sr.Recognizer()

pygame.mixer.init()
def listen_for_wake_word():
    with sr.Microphone() as source:
        while True:
            print("Listening for wake word...")
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                text = r.recognize_google(audio).lower()
                if "hide the boys" in text:  # Wake word
                    print("Wake word detected!")
                    return True
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))

def listen_and_recognize():
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            return "I could not understand the audio"
        except sr.RequestError:
            return "Request failed"

def respond(text):
    text = text.lower()
    if 'bye' in text:  # When 'bye' is said
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
    while pygame.mixer.music.get_busy():  # wait for audio to finish playing
        pygame.time.Clock().tick(10)

def main():
    while True:
        if listen_for_wake_word():  # Listen for wake word
            while True:
                command = listen_and_recognize()
                if command == "EXIT_COMMAND":
                    break  # Break from the command loop, go back to wake word loop
                respond(command)

if __name__ == "__main__":
    main()
