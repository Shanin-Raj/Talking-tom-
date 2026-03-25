# PyTalkingTom Bot

A simple Python-based "Talking Tom" style voice bot that captures audio from your microphone, applies a fun robotic effect, and plays it back. It ignores background noise and waits for you to finish your sentence before replying!

## Prerequisites
- Python 3.7+ installed on your system.
- A working microphone and speakers.

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Shanin-Raj/Talking-tom-.git
cd Talking-tom-
```

### 2. Create and Activate a Virtual Environment
It is highly recommended to use a virtual environment to install your dependencies to prevent cluttering your global Python installation.

**On Windows (PowerShell/CMD):**
```powershell
# Create the virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate
```

**On macOS / Linux:**
```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

### 3. Install Dependencies
Once your virtual environment is active (you'll see `(venv)` in your terminal prompt), install the required packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

*(Note: The main dependencies are `sounddevice` for audio capture/playback and `numpy` for audio processing.)*

## Running the Bot

With your virtual environment active, simply run:
```bash
python main.py
```

The bot will show a continuous live volume meter. Talk into your microphone, and when you finish your sentence (a brief moment of silence), the bot will process your audio and play it back in a robot voice!

To exit the bot, press `Ctrl + C` in your terminal.

---

### Tuning the Microphone Threshold
If the bot gets stuck continuously "Recording..." or misses your words, you may need to manually adjust the volume threshold based on your specific microphone and room environment.

1. **Check Background Noise:** Run the script and sit silently. Note the standard background volume shown on the live `[Vol: X.XXXX]` meter.
2. **Adjust the Threshold:** Open `main.py` and find `SILENCE_THRESHOLD` (around Line 8). Change the value to be **slightly higher** than your room's silent background noise level, but much lower than your speaking volume!

## Troubleshooting
- **No audio playback or picking up wrong microphone?** Check your Default Sound Settings in Windows/macOS. The terminal will print the device numbers it is using when starting up.
- **"ModuleNotFoundError: No module named 'sounddevice'"** You likely forgot to activate your virtual environment before running the file!
