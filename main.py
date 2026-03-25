import sounddevice as sd
import numpy as np
import time
import queue

# Constants
SAMPLE_RATE = 44100
CHANNELS = 1 # Mono
SILENCE_THRESHOLD = 0.01 # Increased slightly above your background noise (0.0060)
SILENCE_DURATION = 1.5 # Increased slightly to prevent cutting off between words
MIN_RECORD_DURATION = 0.5 # Minimum duration to actually trigger playback

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

def main():
    print("=== PyTalkingTom Bot ===")
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
                
            # 2. Process audio
            print("⚙️ Applying effect...")
            processed_audio = apply_robot_effect(audio, SAMPLE_RATE)
            playback_rate = SAMPLE_RATE 
            
            # (Uncomment below to use classic "Talking Tom" chipmunk voice instead of Robot)
            # processed_audio = audio
            # playback_rate = int(SAMPLE_RATE * 1.5) # Play 50% faster
                
            print("🔊 Playing back robot voice...")
            
            # 3. Play audio out through the laptop speaker
            sd.play(processed_audio, samplerate=playback_rate)
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
