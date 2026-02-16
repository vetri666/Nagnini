import pvporcupine
import pyaudio
import struct
import pyautogui
import os
import json
from vosk import Model, KaldiRecognizer

# ===== CONFIGURATION =====
ACCESS_KEY = pjVTyg8UIx00s1wL6n0jORQ1d+azt1fIkS/93HP0j6kybYdjWxrGEg==  # Replace with your key
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

# ===== COMMAND FUNCTIONS =====
def execute_command(command):
    command = command.lower()
    print(f"Executing: {command}")
    
    if "open chrome" in command or "open browser" in command:
        os.system("start chrome")
    elif "open notepad" in command:
        os.system("notepad")
    elif "close window" in command or "close this" in command:
        pyautogui.hotkey('alt', 'f4')
    elif "minimize" in command:
        pyautogui.hotkey('win', 'd')
    elif "switch tab" in command or "next tab" in command:
        pyautogui.hotkey('ctrl', 'tab')
    elif "previous tab" in command:
        pyautogui.hotkey('ctrl', 'shift', 'tab')
    elif "type" in command:
        text = command.replace("type", "").strip()
        pyautogui.write(text)
    elif "click" in command:
        pyautogui.click()
    else:
        print("Command not recognized")

# ===== MAIN LOOP =====
print("Nagini Assistant Ready! Say 'Jarvis' to activate...")

try:
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        
        keyword_index = porcupine.process(pcm)
        
        if keyword_index >= 0:
            print("Wake word detected! Listening for command...")
            
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