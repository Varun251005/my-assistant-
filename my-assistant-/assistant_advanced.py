import pyttsx3
import datetime
import wikipedia
import pyjokes
import webbrowser
import os
import sys
import platform
from pathlib import Path
import json
import re
import subprocess
from urllib.request import urlopen
import shutil

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)

# ============================================================================
# CORE UTILITIES
# ============================================================================

def speak(text):
    """Speak text to user"""
    print(f"🤖 Assistant: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        pass  # Silent fail for audio issues

def take_command():
    """Get user input (voice or text)"""
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
        try:
            command = recognizer.recognize_google(audio)
            print(f"✓ You said: {command}")
            return command.lower()
        except Exception:
            return ""
    except Exception:
        # Fallback to text
        print("📝 Type your command:")
        return input("You: ").strip().lower()

def open_application(app_name):
    """Cross-platform app launcher"""
    system = platform.system()
    try:
        if system == "Windows":
            os.system(f"start {app_name}")
        elif system == "Darwin":
            os.system(f"open -a {app_name}")
        elif system == "Linux":
            os.system(f"{app_name} &")
        return True
    except Exception:
        return False

# ============================================================================
# WEATHER & NEWS
# ============================================================================

def get_weather(city="current"):
    """Get weather information"""
    try:
        # Using wttr.in API (no API key needed)
        url = f"https://wttr.in/{city}?format=j1" if city != "current" else "https://wttr.in?format=j1"
        response = urlopen(url, timeout=5)
        data = json.loads(response.read())
        current = data['current_condition'][0]
        temp = current['temp_C']
        desc = current['weatherDesc'][0]['value']
        humidity = current['humidity']
        wind = current['windspeedKmph']
        return f"The weather is {desc}, {temp}°C, humidity {humidity}%, wind speed {wind} km/h"
    except Exception as e:
        return f"Could not fetch weather: {str(e)}"

def get_news():
    """Get latest news"""
    try:
        # Using NewsAPI alternative or simple RSS
        url = "https://feeds.bloomberg.com/markets/news.rss"
        response = urlopen(url, timeout=5)
        content = response.read().decode('utf-8')
        # Extract first few headlines
        titles = re.findall(r'<title>(.*?)</title>', content)[:3]
        if titles:
            return f"Latest news: {'. '.join(titles[1:])}"
        return "Could not fetch news"
    except Exception:
        return "Could not fetch news at this moment"

# ============================================================================
# EMAIL & MESSAGING
# ============================================================================

def send_email(recipient, subject, body):
    """Send email using Python"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # You'll need to set these environment variables
        sender_email = os.getenv("ASSISTANT_EMAIL")
        sender_password = os.getenv("ASSISTANT_EMAIL_PASSWORD")
        
        if not sender_email or not sender_password:
            return "Email credentials not configured. Set ASSISTANT_EMAIL and ASSISTANT_EMAIL_PASSWORD environment variables."
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return f"Email sent to {recipient}"
    except Exception as e:
        return f"Email error: {str(e)}"

# ============================================================================
# CALENDAR & REMINDERS
# ============================================================================

reminders = {}  # Simple in-memory reminder storage

def add_reminder(time_str, task):
    """Add a reminder"""
    reminders[time_str] = task
    return f"Reminder set for {time_str}: {task}"

def list_reminders():
    """List all reminders"""
    if not reminders:
        return "No reminders set"
    return "Reminders: " + ", ".join([f"{t}: {task}" for t, task in reminders.items()])

def get_calendar_info():
    """Get calendar information"""
    now = datetime.datetime.now()
    day_name = now.strftime("%A")
    date_str = now.strftime("%B %d, %Y")
    return f"Today is {day_name}, {date_str}"

# ============================================================================
# MUSIC & MEDIA CONTROL
# ============================================================================

def play_music(song_name):
    """Play music from YouTube"""
    try:
        import pywhatkit
        speak(f"Playing {song_name}")
        pywhatkit.playonyt(song_name)
        return f"Now playing {song_name}"
    except Exception as e:
        return f"Could not play music: {str(e)}"

def control_volume(level):
    """Control system volume"""
    system = platform.system()
    try:
        if system == "Windows":
            # Use nircmd or Windows API
            os.system(f"nircmd setsysvolume {int(level * 655)}")
        elif system == "Darwin":
            os.system(f"osascript -e 'set volume output volume {level}'")
        elif system == "Linux":
            os.system(f"amixer set Master {level}%")
        return f"Volume set to {level}%"
    except Exception:
        return "Could not change volume"

# ============================================================================
# FILE MANAGEMENT
# ============================================================================

def list_files(directory="."):
    """List files in directory"""
    try:
        files = os.listdir(directory)
        return f"Files in {directory}: {', '.join(files[:10])}"
    except Exception:
        return "Could not list files"

def search_file(filename, search_path="."):
    """Search for a file"""
    try:
        for root, dirs, files in os.walk(search_path):
            if filename in files:
                return f"Found: {os.path.join(root, filename)}"
        return f"File {filename} not found"
    except Exception:
        return "Error searching for file"

def create_file(filename, content=""):
    """Create a new file"""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"File {filename} created"
    except Exception as e:
        return f"Error creating file: {str(e)}"

def delete_file(filename):
    """Delete a file"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            return f"File {filename} deleted"
        return "File not found"
    except Exception as e:
        return f"Error deleting file: {str(e)}"

def get_disk_space():
    """Get disk space information"""
    try:
        usage = shutil.disk_usage("/")
        total = usage.total / (1024**3)
        used = usage.used / (1024**3)
        free = usage.free / (1024**3)
        percent = (used / total) * 100
        return f"Disk: {used:.1f}GB used, {free:.1f}GB free of {total:.1f}GB total ({percent:.1f}% used)"
    except Exception:
        return "Could not get disk information"

# ============================================================================
# CALCULATOR & UNIT CONVERSION
# ============================================================================

def calculate(expression):
    """Simple calculator"""
    try:
        result = eval(expression)
        return f"The result is {result}"
    except Exception:
        return "Invalid calculation"

def convert_units(value, from_unit, to_unit):
    """Convert between units"""
    conversions = {
        ('km', 'miles'): lambda x: x * 0.621371,
        ('miles', 'km'): lambda x: x / 0.621371,
        ('kg', 'lbs'): lambda x: x * 2.20462,
        ('lbs', 'kg'): lambda x: x / 2.20462,
        ('celsius', 'fahrenheit'): lambda x: (x * 9/5) + 32,
        ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
        ('m', 'ft'): lambda x: x * 3.28084,
        ('ft', 'm'): lambda x: x / 3.28084,
    }
    
    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return f"{value} {from_unit} = {result:.2f} {to_unit}"
    return f"Conversion from {from_unit} to {to_unit} not supported"

# ============================================================================
# TODO/TASK MANAGEMENT
# ============================================================================

todos = []

def add_todo(task):
    """Add a todo item"""
    todos.append({'task': task, 'done': False})
    return f"Todo added: {task}"

def list_todos():
    """List all todos"""
    if not todos:
        return "No todos"
    return "Todos: " + ", ".join([f"{'✓' if t['done'] else '○'} {t['task']}" for t in todos])

def mark_todo_done(index):
    """Mark todo as done"""
    try:
        todos[index]['done'] = True
        return f"Todo marked done: {todos[index]['task']}"
    except:
        return "Invalid todo index"

# ============================================================================
# SYSTEM INFORMATION
# ============================================================================

def get_system_info():
    """Get system information"""
    system = platform.system()
    version = platform.release()
    processor = platform.processor()
    return f"System: {system} {version}, Processor: {processor}"

def get_cpu_usage():
    """Get CPU usage"""
    try:
        if platform.system() == "Linux":
            result = subprocess.check_output("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'", shell=True).decode().strip()
            return f"CPU usage: {result}"
        else:
            return "CPU usage not available for this system"
    except:
        return "Could not get CPU usage"

def get_memory_usage():
    """Get memory usage"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        return f"Memory: {memory.percent}% used ({memory.used / (1024**3):.1f}GB of {memory.total / (1024**3):.1f}GB)"
    except:
        return "Memory information not available"

# ============================================================================
# CHAT & CONVERSATION AI
# ============================================================================

def generate_response(query):
    """Generate intelligent response using available APIs"""
    responses = {
        'hello': 'Hi there! How can I help you today?',
        'how are you': 'I am doing great, thanks for asking!',
        'what is your name': 'I am your AI assistant, here to help with anything you need.',
        'who created you': 'I was created to assist you with various tasks.',
        'good morning': 'Good morning! Hope you have a great day ahead!',
        'good night': 'Good night! Sleep well!',
        'thank you': 'You are welcome!',
        'thanks': 'Happy to help!',
    }
    
    query_lower = query.lower()
    for key, response in responses.items():
        if key in query_lower:
            return response
    
    # Try to get response from Wikipedia
    try:
        summary = wikipedia.summary(query, sentences=1)
        return summary
    except:
        return "I am not sure about that. Try asking me something else!"

# ============================================================================
# MAIN ASSISTANT
# ============================================================================

def show_help():
    """Show available commands"""
    help_text = """
╔════════════════════════════════════════════════════════════════╗
║                   ASSISTANT COMMANDS                          ║
╠════════════════════════════════════════════════════════════════╣
║ WEATHER & NEWS:                                               ║
║   • "weather" - Get current weather                           ║
║   • "news" - Get latest news                                  ║
║                                                                ║
║ CALENDAR & TIME:                                              ║
║   • "time" - Get current time                                 ║
║   • "date" - Get current date                                 ║
║   • "remind me [time] [task]" - Set a reminder              ║
║   • "my reminders" - List all reminders                       ║
║                                                                ║
║ MUSIC:                                                         ║
║   • "play [song]" - Play song on YouTube                      ║
║   • "volume [level]" - Set volume (0-100)                     ║
║                                                                ║
║ FILES:                                                         ║
║   • "list files" - List files in current directory            ║
║   • "search [filename]" - Search for a file                   ║
║   • "disk space" - Get disk information                        ║
║                                                                ║
║ CALCULATOR & CONVERSION:                                      ║
║   • "calculate [expression]" - Do math (e.g., "2+2")          ║
║   • "convert [value] [unit1] to [unit2]"                      ║
║     Example: "convert 10 km to miles"                         ║
║                                                                ║
║ TODO MANAGEMENT:                                              ║
║   • "add todo [task]" - Add a todo item                       ║
║   • "my todos" - List all todos                               ║
║                                                                ║
║ SYSTEM:                                                        ║
║   • "system info" - Get system information                    ║
║   • "cpu usage" - Get CPU usage                               ║
║   • "memory" - Get memory usage                               ║
║                                                                ║
║ OTHER:                                                         ║
║   • "tell me a joke" - Tell a joke                            ║
║   • "who is [person]" - Wikipedia search                      ║
║   • "search [topic]" - Google search                          ║
║   • "open [app]" - Open application                           ║
║   • "help" - Show this help message                           ║
║   • "exit" / "quit" - Exit assistant                          ║
╚════════════════════════════════════════════════════════════════╝
"""
    print(help_text)
    return "Help displayed"

def run_assistant():
    """Main assistant loop"""
    speak("Hello, I am your advanced AI assistant. Type help to see all commands.")
    
    while True:
        try:
            command = take_command()
            
            if not command:
                continue
            
            # WEATHER & NEWS
            if 'weather' in command:
                response = get_weather()
                speak(response)
            
            elif 'news' in command:
                response = get_news()
                speak(response)
            
            # TIME & CALENDAR
            elif 'time' in command and 'remind' not in command:
                time_str = datetime.datetime.now().strftime('%I:%M %p')
                speak(f"The current time is {time_str}")
            
            elif 'date' in command:
                response = get_calendar_info()
                speak(response)
            
            elif 'remind me' in command:
                parts = command.replace('remind me', '').strip().split(' at ')
                if len(parts) == 2:
                    task, time_str = parts
                    response = add_reminder(time_str, task)
                    speak(response)
                else:
                    speak("Please say: remind me [task] at [time]")
            
            elif 'my reminders' in command:
                response = list_reminders()
                speak(response)
            
            # MUSIC & MEDIA
            elif 'play' in command:
                song = command.replace('play', '').strip()
                if song:
                    response = play_music(song)
                    speak(response)
                else:
                    speak("What would you like me to play?")
            
            elif 'volume' in command:
                match = re.search(r'volume\s+(\d+)', command)
                if match:
                    level = int(match.group(1))
                    response = control_volume(level)
                    speak(response)
            
            # FILES
            elif 'list files' in command:
                response = list_files()
                speak(response)
            
            elif 'search' in command and 'google' not in command:
                filename = command.replace('search', '').strip()
                response = search_file(filename)
                speak(response)
            
            elif 'disk space' in command:
                response = get_disk_space()
                speak(response)
            
            # CALCULATOR
            elif 'calculate' in command:
                expr = command.replace('calculate', '').strip()
                response = calculate(expr)
                speak(response)
            
            elif 'convert' in command:
                match = re.search(r'convert\s+([\d.]+)\s+(\w+)\s+to\s+(\w+)', command)
                if match:
                    value, from_unit, to_unit = float(match.group(1)), match.group(2), match.group(3)
                    response = convert_units(value, from_unit, to_unit)
                    speak(response)
            
            # TODO
            elif 'add todo' in command:
                task = command.replace('add todo', '').strip()
                response = add_todo(task)
                speak(response)
            
            elif 'my todos' in command:
                response = list_todos()
                speak(response)
            
            # SYSTEM INFO
            elif 'system info' in command:
                response = get_system_info()
                speak(response)
            
            elif 'cpu usage' in command:
                response = get_cpu_usage()
                speak(response)
            
            elif 'memory' in command:
                response = get_memory_usage()
                speak(response)
            
            # OTHER
            elif 'tell me a joke' in command or 'joke' in command:
                joke = pyjokes.get_joke()
                speak(joke)
            
            elif 'who is' in command:
                person = command.replace('who is', '').strip()
                if person:
                    try:
                        info = wikipedia.summary(person, sentences=2)
                        speak(info)
                    except:
                        speak(f"Could not find information about {person}")
            
            elif 'search' in command:
                topic = command.replace('search', '').strip()
                if topic:
                    speak(f"Searching for {topic}")
                    webbrowser.open(f"https://www.google.com/search?q={topic}")
                else:
                    speak("What would you like me to search?")
            
            elif 'open' in command:
                app = command.replace('open', '').strip()
                if open_application(app):
                    speak(f"Opening {app}")
                else:
                    speak(f"Could not open {app}")
            
            elif 'help' in command:
                show_help()
            
            elif 'exit' in command or 'quit' in command or 'stop' in command:
                speak("Goodbye!")
                sys.exit()
            
            else:
                response = generate_response(command)
                speak(response)
        
        except KeyboardInterrupt:
            print("\n\nAssistant stopped by user.")
            sys.exit()
        except Exception as e:
            print(f"Error: {e}")
            speak("An error occurred. Please try again.")

if __name__ == "__main__":
    print("=" * 70)
    print("🤖 ADVANCED AI ASSISTANT STARTED")
    print(f"🖥️  System: {platform.system()}")
    print("=" * 70)
    print("\n💡 Type 'help' to see all available commands\n")
    try:
        run_assistant()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
