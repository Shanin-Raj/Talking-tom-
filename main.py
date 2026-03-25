import sounddevice as sd
import numpy as np
import time
import queue
import vosk
import pyttsx3
import json
import os
import sys
import soundfile as sf

# Constants
SAMPLE_RATE = 44100
CHANNELS = 1 # Mono
SILENCE_THRESHOLD = 0.01 # Increased slightly above your background noise (0.0060)
SILENCE_DURATION = 1.5 # Increased slightly to prevent cutting off between words
MIN_RECORD_DURATION = 0.5 # Minimum duration to actually trigger playback

# Static Offline Data
GREETINGS = {
    "hello": "Hello there! How are you doing today?",
    "hi": "Hi! Nice to meet you.",
    "good morning": "Good morning to you too!",
    "good night": "Sleep well! Good night.",
    "how are you": "I am just a simple Python bot, but I'm doing great!"
}

def get_rms(data):
    """Calculate the Root Mean Square (volume) of the audio data"""
    return np.sqrt(np.mean(data**2))

def record_until_silence():
    print("Listening... (Speak now!)")
    q = queue.Queue()

    def callback(indata, frames, time, status):
        """This is called for each audio block by sounddevice."""
        if status:
            print(status)
        q.put(indata.copy())
    
    # Start continuous background recording stream
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=callback):
        recording = []
        is_speech_started = False
        silence_start_time = None
        
        while True:
            data = q.get()
            volume = get_rms(data)
            
            # Print a volume meter so we can see what the mic is hearing
            meter_length = int(volume * 500)
            meter = "|" * min(meter_length, 30) # Cap meter length at 30
            
            # State 1: Waiting for speech to start
            if not is_speech_started:
                print(f"\r[Vol: {volume:.4f}] {meter}".ljust(50), end="", flush=True)
                if volume > SILENCE_THRESHOLD:
                    is_speech_started = True
                    print("\n🔈 Speech detected! Recording...")
                    recording.append(data)
            # State 2: Currently recording speech
            else:
                recording.append(data)
                
                if volume > SILENCE_THRESHOLD:
                    print(f"\rRecording [Vol: {volume:.4f}] {meter}".ljust(50), end="", flush=True)
                
                # Check for silence dropping below threshold
                if volume < SILENCE_THRESHOLD:
                    if silence_start_time is None:
                        silence_start_time = time.time()
                    elif time.time() - silence_start_time > SILENCE_DURATION:
                        print("\n🔇 Silence detected. Processing...")
                        break
                else:
                    # Reset silence timer if they speak again
                    silence_start_time = None
                    
    # Combine individual chunks into one continuous array
    if recording:
        audio_data = np.concatenate(recording, axis=0)
        return audio_data
    return None

def apply_robot_effect(audio_data, sample_rate):
    """
    Applies a simple 'dalek' robot effect by multiplying with a sine wave (ring modulation).
    For the classic 'Talking Tom' high-pitch effect, we can just play it back at a faster sample rate.
    """
    t = np.arange(len(audio_data)) / sample_rate
    mod_freq = 45.0  # Hz - determines how "metallic" the voice is
    carrier = np.sin(2 * np.pi * mod_freq * t)
    carrier = carrier.reshape(-1, 1) # Match audio shape (N, 1)
    
    # Modulate
    robot_audio = audio_data * carrier
    
    # Normalize volume to avoid clipping
    max_val = np.max(np.abs(robot_audio))
    if max_val > 0:
        robot_audio = robot_audio / max_val
        
    return robot_audio

def process_audio_intent(audio, model):
    """Converts the recorded float audio to PCM Int16, and feeds it to Vosk STT."""
    # Convert numpy float arrays [-1.0, 1.0] to int16 [-32768, 32767]
    audio_int16 = (audio * 32767).astype(np.int16)
    
    # Create recognizer for this run
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    
    # Accept waveform (requires raw bytes)
    recognizer.AcceptWaveform(audio_int16.tobytes())
    res = json.loads(recognizer.FinalResult())
    return res.get("text", "").strip()

def main():
    # 1. Initialize pyttsx3 offline text-to-speech engine
    engine = pyttsx3.init()
    engine.setProperty('rate', 160) # Default rate is often a bit fast
    
    # 2. Check and load the Vosk offline model
    print("\nLoading Offline Vosk STT Model (this takes a few seconds)...")
    if not os.path.exists("model"):
        print("❌ Model foldler 'model' not found! Please run 'python download_model.py' first.")
        sys.exit(1)
        
    # Set vosk log level to -1 to suppress spammy warnings
    vosk.SetLogLevel(-1)
    model = vosk.Model("model")
    
    print("\n=== PyTalkingTom Offline Action Bot ===")
    print("Press Ctrl+C to exit.\n")
    
    # Print out default devices
    print(f"Using default input  device: {sd.default.device[0]}")
    print(f"Using default output device: {sd.default.device[1]}\n")
    
    try:
        while True:
            # 1. Listen for audio
            audio = record_until_silence()
            
            if audio is None or len(audio) < int(SAMPLE_RATE * MIN_RECORD_DURATION):
                print("Audio too short, ignoring.")
                continue
                
            # 2. Process audio with Speech-to-Text
            print("🧠 Analyzing speech...")
            recognized_text = process_audio_intent(audio, model)
            print(f"   You said: '{recognized_text}'")
            
            # 3. Check against static dictionary
            response = None
            for key, reply in GREETINGS.items():
                if key in recognized_text.lower():
                    response = reply
                    break
            
            # 4. Action!
            if response:
                print(f"🤖 Known Greeting! Replying: '{response}'")
                
                # We save pyttsx3 speech to a file and play it via sounddevice
                # This ensures the audio goes to the exact same speaker as the parrot effect!
                tts_filename = "temp_greeting.wav"
                engine.save_to_file(response, tts_filename)
                engine.runAndWait()
                
                # Play it through sounddevice
                if os.path.exists(tts_filename):
                    data, fs = sf.read(tts_filename, dtype='float32')
                    sd.play(data, samplerate=fs)
                    sd.wait()
                    os.remove(tts_filename)
                    
            else:
                print("⚙️ Applying standard parrot robot effect...")
                processed_audio = apply_robot_effect(audio, SAMPLE_RATE)
                print("🔊 Playing back robot voice...")
                sd.play(processed_audio, samplerate=SAMPLE_RATE)
                sd.wait() # Wait until audio is done playing completely
            
            print("✅ Done. Ready for more.")
            print("-" * 30)
            time.sleep(0.2) # Small pause before listening again to avoid echo loops
            
    except KeyboardInterrupt:
        print("\nExiting PyTalkingTom...")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
