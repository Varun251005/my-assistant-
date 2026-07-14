import pyttsx3
import datetime
import wikipedia
import pyjokes
import webbrowser
import os
import sys
import platform
from pathlib import Path

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)

# Speak the text
def speak(text):
    print(f"🤖 Assistant: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"(Audio not available: {e})")

# Take voice input or text input (fallback for non-audio environments)
def take_command():
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
        try:
            print("🔄 Recognizing...")
            command = recognizer.recognize_google(audio)
            print(f"✓ You said: {command}")
        except Exception:
            speak("Sorry, I did not understand. Please say it again.")
            return ""
        return command.lower()
    except Exception:
        # Fallback to text input
        print("📝 Voice input not available. Type your command:")
        command = input("You: ").strip()
        return command.lower()

# Cross-platform command execution
def open_application(app_name):
    system = platform.system()
    try:
        if system == "Windows":
            os.system(f"start {app_name}")
        elif system == "Darwin":  # macOS
            os.system(f"open -a {app_name}")
        elif system == "Linux":
            # Common Linux apps
            if app_name.lower() == "code" or app_name.lower() == "vs code":
                os.system("code &")
            elif app_name.lower() == "notepad":
                os.system("gedit &")
            else:
                os.system(f"{app_name} &")
        return True
    except Exception as e:
        print(f"Error opening {app_name}: {e}")
        return False

# Main assistant logic
def run_assistant():
    speak("Hello, how can I help you?")
    while True:
        try:
            command = take_command()
            
            if not command:
                continue

            if 'open vs code' in command or 'open code' in command:
                open_application("code")
                speak("Opening Visual Studio Code")

            elif 'open notepad' in command or 'open editor' in command:
                open_application("notepad")
                speak("Opening Text Editor")

            elif 'play' in command:
                video = command.replace('play', '').strip()
                if video:
                    speak(f"Playing {video} on YouTube")
                    try:
                        import pywhatkit
                        pywhatkit.playonyt(video)
                    except Exception as e:
                        speak(f"Could not play video: {str(e)}")
                else:
                    speak("What would you like me to play?")

            elif 'time' in command:
                time_str = datetime.datetime.now().strftime('%I:%M %p')
                speak(f"The current time is {time_str}")

            elif 'date' in command:
                date_str = datetime.datetime.now().strftime('%B %d, %Y')
                speak(f"Today's date is {date_str}")

            elif 'who is' in command:
                person = command.replace('who is', '').strip()
                if person:
                    try:
                        info = wikipedia.summary(person, sentences=2)
                        speak(info)
                    except Exception as e:
                        speak(f"Could not find information about {person}")
                else:
                    speak("Who would you like to know about?")

            elif 'tell me a joke' in command or 'joke' in command:
                joke = pyjokes.get_joke()
                speak(joke)

            elif 'screenshot' in command:
                try:
                    import pyautogui
                    screenshot = pyautogui.screenshot()
                    screenshot.save("screenshot.png")
                    speak("Screenshot taken and saved as screenshot.png")
                except Exception as e:
                    speak(f"Could not take screenshot: {str(e)}")

            elif 'read me a book' in command or 'recommend a book' in command:
                speak("Sure. How about 'The Alchemist by Paulo Coelho'? It's a great read.")

            elif 'home' in command or 'home page' in command:
                home_path = str(Path.home())
                webbrowser.open(f"file://{home_path}")
                speak("Opening your home directory")

            elif 'search' in command:
                topic = command.replace('search', '').strip()
                if topic:
                    speak(f"Searching for {topic} on Google")
                    webbrowser.open(f"https://www.google.com/search?q={topic}")
                else:
                    speak("What do you want me to search?")

            elif 'exit' in command or 'stop' in command or 'quit' in command:
                speak("Goodbye!")
                sys.exit()

            else:
                speak("I am not sure how to help with that. Try asking me to: tell time, search for something, tell a joke, or open an application.")

        except KeyboardInterrupt:
            print("\n\nAssistant stopped by user.")
            sys.exit()
        except Exception as e:
            print(f"Error: {e}")
            speak("An error occurred. Please try again.")

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Voice Assistant Started")
    print(f"🖥️  Running on: {platform.system()}")
    print("=" * 50)
    try:
        run_assistant()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
