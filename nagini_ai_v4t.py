import pvporcupine
import pyaudio
import struct
import pyautogui
import os
import json
import subprocess
import time
import threading
from vosk import Model, KaldiRecognizer
import ollama
import pyttsx3

# ===== CONFIGURATION =====
ACCESS_KEY = "pjVTyg8UIx00s1wL6n0jORQ1d+azt1fIkS/93HP0j6kybYdjWxrGEg=="
MODEL_PATH = r"C:\ProjectNagini\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"

# ===== WAKE WORD DETECTION =====
porcupine = pvporcupine.create(
    access_key=ACCESS_KEY,
    keywords=['jarvis']
)

# ===== VOICE RECOGNITION =====
vosk_model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(vosk_model, 16000)

# ===== AUDIO SETUP =====
pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

# ===== VOICE ENGINE (Threaded) =====
def speak(text):
    """Speak in a separate thread so it doesn't block the microphone"""
    print(f"Nagini: {text}")
    def _speak():
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)
        engine.setProperty('volume', 1.0)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)  # 0 = male, 1 = female
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    t = threading.Thread(target=_speak)
    t.start()
    t.join()  # Wait for speech to finish before continuing

# ===== AI COMMAND PROCESSOR =====
def process_with_ai(command):
    """Use Ollama AI to understand the command and generate action"""

    prompt = f"""You are a Windows PC assistant. The user said: "{command}"

Your job: Convert the command into actions. Respond with ONLY a JSON object.

Available actions:
1. open_app - opens application
2. keyboard - keyboard shortcuts (format: "key1+key2")
3. type_text - types text including math expressions
4. mouse_click - clicks mouse
5. wait - waits (in seconds)

For calculator math:
User: "add 2 plus 2" → {{"action": "type_text", "parameter": "2+2="}}
User: "multiply 5 times 3" → {{"action": "type_text", "parameter": "5*3="}}
User: "calculate 10 minus 4" → {{"action": "type_text", "parameter": "10-4="}}
User: "divide 20 by 4" → {{"action": "type_text", "parameter": "20/4="}}

For typing in apps:
User: "type hello" → {{"action": "type_text", "parameter": "hello"}}
User: "search for cats" → {{"action": "type_text", "parameter": "cats"}}
User: "write my email" → {{"action": "type_text", "parameter": "my email"}}

For opening apps:
User: "open chrome" → {{"action": "open_app", "parameter": "chrome"}}
User: "open calculator" → {{"action": "open_app", "parameter": "calc"}}
User: "open notepad" → {{"action": "open_app", "parameter": "notepad"}}
User: "open task manager" → {{"action": "open_app", "parameter": "taskmgr"}}
User: "open file explorer" → {{"action": "open_app", "parameter": "explorer"}}

For window control:
User: "close window" → {{"action": "keyboard", "parameter": "alt+f4"}}
User: "minimize" → {{"action": "keyboard", "parameter": "win+d"}}
User: "switch tab" → {{"action": "keyboard", "parameter": "ctrl+tab"}}
User: "new tab" → {{"action": "keyboard", "parameter": "ctrl+t"}}

For browser navigation:
User: "go to website google.com" → {{"action": "type_text", "parameter": "google.com"}}
User: "search google for dogs" → {{"action": "type_text", "parameter": "dogs"}}

Now respond for: "{command}"
Only JSON, no explanation."""

    try:
        response = ollama.chat(model='llama3.1:8b', messages=[
            {'role': 'user', 'content': prompt}
        ])

        ai_response = response['message']['content'].strip()
        print(f"AI Response: {ai_response}")

        # Parse JSON response
        result = json.loads(ai_response)
        return result

    except Exception as e:
        print(f"AI Error: {e}")
        return {"action": "unknown", "parameter": ""}

# ===== COMMAND EXECUTOR =====
def execute_command(command):
    """Execute the command using AI understanding"""
    print(f"Processing: {command}")

    # Get AI interpretation
    action_data = process_with_ai(command)
    action = action_data.get("action", "unknown")
    parameter = action_data.get("parameter", "")

    print(f"Action: {action}, Parameter: {parameter}")

    # Execute the action
    if action == "open_app":
        try:
            speak(f"Opening {parameter}")
            os.system(f"start {parameter}")
            print(f"✓ Opened: {parameter}")
            time.sleep(1)
        except Exception as e:
            speak("Sorry, I could not open that")
            print(f"✗ Error opening app: {e}")

    elif action == "keyboard":
        try:
            keys = parameter.split('+')
            pyautogui.hotkey(*keys)
            speak("Done")
            print(f"✓ Pressed: {parameter}")
        except Exception as e:
            speak("Sorry, I could not do that")
            print(f"✗ Error with keyboard: {e}")

    elif action == "type_text":
        try:
            if any(char in parameter for char in ['+', '-', '*', '/', '=']):
                pyautogui.typewrite(parameter, interval=0.1)
            else:
                pyautogui.write(parameter, interval=0.05)
            speak("Done")
            print(f"✓ Typed: {parameter}")
        except Exception as e:
            speak("Sorry, I could not type that")
            print(f"✗ Error typing: {e}")

    elif action == "mouse_click" or action == "mouse":
        if parameter == "click" or not parameter:
            pyautogui.click()
            speak("Clicked")
            print("✓ Clicked mouse")

    elif action == "wait":
        try:
            wait_time = float(parameter)
            time.sleep(wait_time)
            print(f"✓ Waited {wait_time} seconds")
        except:
            pass

    else:
        speak("Sorry, I did not understand that command")
        print("✗ Command not understood")

# ===== MAIN LOOP =====
print("=" * 50)
print("🐍 Nagini AI Assistant Ready!")
print("=" * 50)
print("Wake word : 'Jarvis'")
print("Powered by: Llama 3.1 (8B)")
print("\nTry commands like:")
print("  - 'open calculator'")
print("  - 'add 2 plus 2'")
print("  - 'open chrome'")
print("  - 'type hello world'")
print("  - 'minimize'")
print("=" * 50)

speak("Nagini is ready. Say Jarvis to activate.")
print("\nListening...")

try:
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            speak("Yes, I am listening")
            print("\n🎤 Wake word detected! Listening for command...")

            # Listen for command
            while True:
                data = audio_stream.read(4000)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    command = result.get('text', '')
                    if command:
                        execute_command(command)
                        print("\nListening...")
                        break

except KeyboardInterrupt:
    print("\n\nShutting down Nagini...")
finally:
    audio_stream.close()
    pa.terminate()
    porcupine.delete()
    speak("Goodbye!")
    print("Goodbye! 🐍")
