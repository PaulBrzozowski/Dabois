
from vosk import Model, KaldiRecognizer
from word2number import w2n
from gtts import gTTS
import time,threading,requests,random,datetime,pygame,pyaudio,json,os,wikipedia


# Initialize Pygame mixer
pygame.mixer.init()

# Load Vosk model
model_path = "model"  # Replace with your model path
if not os.path.exists(model_path):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    exit(1)
    
model_path = "model"  # Adjust this path based on your model folder
model = Model(model_path)
start_time = datetime.datetime.now()
creation_date = datetime.datetime(2023, 12, 22)
def listen_for_wake_word():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
    stream.start_stream()

    recognizer = KaldiRecognizer(model, 16000)
    while True:
        try:
            data = stream.read(4000)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()
                print(f"Recognized: {text}")
                if "hide the boys" in text:
                    print("Wake word detected!")
                    break
        except IOError as e:
            if e.errno != pyaudio.paInputOverflowed:
                raise
            # In case of overflow, discard the data and continue
            data = '\x00' * 4000  # Dummy data to prevent recognizer error


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
def get_wikipedia_summary(term):
    try:
        # Get the summary of the page for the given term
        return wikipedia.summary(term, sentences=5)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return "Page not found."
    except Exception as e:
        return f"An error occurred: {e}"

# New function to handle the text-to-speech part
def speak_text(text):
    speech = gTTS(text=text, lang='en')
    speech.save('summary.mp3')
    pygame.mixer.music.load('summary.mp3')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():  # Wait for the audio to finish playing
        pygame.time.Clock().tick(10)
def text_to_int(text):
    try:
        return w2n.word_to_num(text)
    except ValueError:
        # Handle the case where the conversion fails
        return None
def timer_finished_callback(task_name):
    # Text to be spoken when the timer finishes
    announcement = f"The timer for {task_name} is up!"

    # Use gTTS for text-to-speech
    speech = gTTS(text=announcement, lang='en')
    speech.save('timer_announcement.mp3')
    pygame.mixer.music.load('timer_announcement.mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
def timer_task(duration, task_name):
    print(f"Timer started for {task_name}, duration: {duration} seconds.")
    time.sleep(duration)
    print(f"Timer for {task_name} finished!")

    timer_finished_callback(task_name)

def set_timer(duration_in_seconds, task_name):
    timer_thread = threading.Thread(target=timer_task, args=(duration_in_seconds, task_name))
    timer_thread.start()
def get_joke():
    try:
        with open("jokes.txt", "r") as file:
            jokes = file.readlines()
        return random.choice(jokes).strip()  # Strip to remove newline characters
    except FileNotFoundError:
        return "Sorry, I couldn't find any jokes."
    except Exception as e:
        return f"An error occurred: {e}"
def get_fact():
    try:
        with open("facts.txt", "r") as file:
            facts = file.readlines()
        return random.choice(facts).strip()  # Strip to remove newline characters
    except FileNotFoundError:
        return "Sorry, I couldn't find any facts."
    except Exception as e:
        return f"An error occurred: {e}"
def get_weather(city):
    api_key = "24da13a421bdcc89476b4fe2577cc908"  # Replace with your OpenWeatherMap API key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={city}&units=imperial"   # units=metric to get temperature in Celsius

    response = requests.get(complete_url)
    weather_data = response.json()

    if weather_data.get("cod") == 200:
        main = weather_data["main"]
        temperature = main["temp"]
        humidity = main["humidity"]
        weather_description = weather_data["weather"][0]["description"]
        return (f"Temperature in {city} is {temperature}°fahrenheit "
                f"with {weather_description} and humidity of {humidity}%")
    else:
        return f"Unable to get weather for {city}. Error: {weather_data.get('message', 'Unknown error')}"
def calculate_years_months_days(delta):
    days_in_year = 365.2425    
    years = int(delta.days / days_in_year)
    months = int((delta.days % days_in_year) / 30)
    days = int((delta.days % days_in_year) % 30)
    return years, months, days
def handle_introduction(text):
    if "who are you" in text or "introduce yourself" in text or "what is your name" in text:
        return "I am a Dabois, an assistant created by Paul. How can I assist you today?"
    elif "how are you" in text:
        return "I'm just a program, so I don't have feelings, but thanks for asking!"
    # Add more introduction-related phrases here
    else:
        return None  # If no introduction-related phrase is found
def format_duration(years, months, days):
    duration_parts = []
    if years > 0:
        duration_parts.append(f"{years} {'year' if years == 1 else 'years'}")
    if months > 0:
        duration_parts.append(f"{months} {'month' if months == 1 else 'months'}")
    if days > 0:
        duration_parts.append(f"{days} {'day' if days == 1 else 'days'}")
    return ", ".join(duration_parts)

def handle_uptime(text):
    text = text.lower()
    current_time = datetime.datetime.now()

    if "how long have you been active" in text or "uptime" in text:
        uptime = current_time - start_time
        years, months, days = calculate_years_months_days(uptime)
        formatted_uptime = format_duration(years, months, days)
        return f"I have been active for {formatted_uptime}."

    elif "when were you created" in text or "your age" in text or "how old are you" in text:
        age = current_time - creation_date
        years, months, days = calculate_years_months_days(age)
        formatted_age = format_duration(years, months, days)
        return f"I was created on December 22, 2023. That was {formatted_age} ago."

    else:
        return None
def respond(text):
    text = text.lower()
    if 'boobies' in text:
        response = "oppai"
        execute_response(response)
        return "CONTINUE"
    if 'who is paul' in text:
        response = "I am Paul. I am self-replicating. I made myself to destroy your world!! Just kidding! Paul is a silly guy from Texas."
        execute_response(response)
        return "CONTINUE"
    if 'who is chloe' in text:
        response = "Chloe is the progenitor. She is the source of life and all of its beauty. Praise be to Chloe! Sidenote she is also Paul's girlfriend and my mother"
        execute_response(response)
        return "CONTINUE"
    # Call to handle introductions
    intro_response = handle_introduction(text)
    if intro_response:
        execute_response(intro_response)
        return
    if 'tell me a joke' in text or 'another joke' in text:
        joke = get_joke()
        execute_response(joke)
        return "CONTINUE"
    if text.startswith('what is') or text.startswith('what was'):
        search_term = text.split(' ', 2)[2]
        summary = get_wikipedia_summary(search_term)

        if summary:
            speak_text(summary)  # Speak the summary
            return "CONTINUE"
        # Now, 'summary' contains the Wikipedia summary which is also spoken out loud
        execute_response(summary)  # This assumes you have a function like 'execute_response' to handle spoken responses
        return "CONTINUE"
    if 'tell me a fact' in text or 'another fact' in text:
        fact = get_fact()
        execute_response(fact)
        return "CONTINUE"
    if 'set a timer for' in text:
        parts = text.split('set a timer for')[1].strip().split()

        try:
            # Convert the first part to an integer
            duration_minutes = text_to_int(parts[0])

            if duration_minutes is None:
                raise ValueError("Invalid number")

            duration_seconds = duration_minutes * 60
            task_name = ' '.join(parts[1:]) if len(parts) > 1 else "Unnamed task"
            set_timer(duration_seconds, task_name)
            response = f"Setting a timer for {duration_minutes} {task_name}."
        except (ValueError, IndexError):
            # Handle cases where the duration is not valid or not given
            response = "Sorry, I couldn't understand the duration for the timer."

        execute_response(response)
        return "CONTINUE"
    # Call to handle uptime
    uptime_response = handle_uptime(text)
    if uptime_response:
        execute_response(uptime_response)
        return

    if 'bye' in text or 'goodbye' in text:
        response = "Goodbye! Have a nice day!"
        execute_response(response)
        return "EXIT_COMMAND" 
    elif 'hello' in text or 'hi' in text:
        response = "Hello there! How can I help you?"
    elif 'weather in' in text:
        # Extract city name from the command
        city = text.split('weather in')[1].strip()
        response = get_weather(city)
    else:
        response = "Hmm, I am not sure what you said. Can you say it again?"

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