import numpy as np
from scipy.io import wavfile
import subprocess
import os

# Generate a 1-second beep sound
sample_rate = 44100
duration = 1.0
frequency = 1000

t = np.linspace(0, duration, int(sample_rate * duration), False)
beep = np.sin(2 * np.pi * frequency * t) * 0.5

# Convert to 16-bit PCM
beep = (beep * 32767).astype(np.int16)

# Save as WAV
wavfile.write('beep.wav', sample_rate, beep)

# Convert to MP3
subprocess.run(['ffmpeg', '-i', 'beep.wav', 'beep.mp3'])

# Clean up
os.remove('beep.wav') 