import pvporcupine
import pyaudio
import struct
import pyautogui
import os
import json
import subprocess
from vosk import Model, KaldiRecognizer
import ollama

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

# ===== AI COMMAND PROCESSOR =====
def process_with_ai(command):
    """Use Ollama AI to understand the command and generate action"""
    
    prompt = f"""You are a Windows PC assistant. The user said: "{command}"
    
Your job: Determine what action to take. Respond with ONLY a JSON object, nothing else.

Available actions:
1. open_app - opens an application (use Windows command like "chrome", "notepad", "taskmgr", "explorer", "calc", "whatsapp:", etc.)
2. keyboard - performs keyboard shortcuts (format: "key1+key2" like "alt+f4", "win+d", "ctrl+tab")
3. mouse - clicks the mouse
4. type_text - types text on keyboard
5. unknown - command not understood

Examples:
User: "open chrome" → {{"action": "open_app", "parameter": "chrome"}}
User: "open calculator" → {{"action": "open_app", "parameter": "calc"}}
User: "close window" → {{"action": "keyboard", "parameter": "alt+f4"}}
User: "minimize everything" → {{"action": "keyboard", "parameter": "win+d"}}
User: "type hello world" → {{"action": "type_text", "parameter": "hello world"}}
User: "click" → {{"action": "mouse", "parameter": "click"}}

Now respond for: "{command}"
Only JSON, no explanation."""

    try:
        response = ollama.chat(model='llama3.2:3b', messages=[
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
            os.system(f"start {parameter}")
            print(f"Opened: {parameter}")
        except Exception as e:
            print(f"Error opening app: {e}")
            
    elif action == "keyboard":
        try:
            keys = parameter.split('+')
            pyautogui.hotkey(*keys)
            print(f"Pressed: {parameter}")
        except Exception as e:
            print(f"Error with keyboard: {e}")
            
    elif action == "type_text":
        pyautogui.write(parameter)
        print(f"Typed: {parameter}")
        
    elif action == "mouse":
        if parameter == "click":
            pyautogui.click()
            print("Clicked mouse")
            
    else:
        print("Command not understood")

# ===== MAIN LOOP =====
print("Nagini AI Assistant Ready! Say 'Jarvis' to activate...")
print("(Powered by Llama 3.2 AI)")

try:
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        
        keyword_index = porcupine.process(pcm)
        
        if keyword_index >= 0:
            print("\n🎤 Wake word detected! Listening for command...")
            
            # Listen for command
            while True:
                data = audio_stream.read(4000)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    command = result.get('text', '')
                    if command:
                        execute_command(command)
                        break

except KeyboardInterrupt:
    print("\nShutting down Nagini...")
finally:
    audio_stream.close()
    pa.terminate()
    porcupine.delete()
