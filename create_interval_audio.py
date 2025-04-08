import csv
import subprocess
import os
import argparse
from pydub import AudioSegment
import tempfile

def create_voice_prompt(text, output_file):
    """Create a voice prompt using macOS's say command"""
    subprocess.run(['say', '-v', 'Samantha', '-o', output_file, text])

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create interval training audio with voice prompts')
    parser.add_argument('--input', '-i', default='interval.csv', help='Input CSV file with interval data')
    parser.add_argument('--output', '-o', default='interval_music.mp3', help='Output audio file')
    parser.add_argument('--music', '-m', default='music.mp3', help='Background music file')
    parser.add_argument('--beep', '-b', default='beep.mp3', help='Beep sound file')
    parser.add_argument('--debug', action='store_true', help='Create debug audio without background music')
    args = parser.parse_args()

    # Read the interval CSV file
    intervals = []
    with open(args.input, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            intervals.append(row)

    # Calculate total duration and halfway point
    total_duration = int(intervals[-1]['Cumulative_Time_Seconds'])
    halfway_point = total_duration // 2

    # Create temporary directory for voice prompts
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create voice prompts for each interval
        voice_files = []
        for i, interval in enumerate(intervals, 1):
            voice_file = os.path.join(temp_dir, f'voice_{i}.aiff')
            create_voice_prompt(interval['Effort_Description'], voice_file)
            voice_files.append(voice_file)

        # Create special halfway mark voice prompt
        halfway_voice_file = os.path.join(temp_dir, 'halfway.aiff')
        create_voice_prompt("Halfway point, time to turn around", halfway_voice_file)
        voice_files.append(halfway_voice_file)

        # Convert voice prompts to MP3
        voice_mp3s = []
        for voice_file in voice_files:
            mp3_file = voice_file.replace('.aiff', '.mp3')
            subprocess.run(['ffmpeg', '-i', voice_file, '-acodec', 'libmp3lame', mp3_file])
            voice_mp3s.append(mp3_file)

        # Load beep sound
        beep = AudioSegment.from_mp3(args.beep)

        # Create base audio
        if args.debug:
            # Create a silent audio track of appropriate length
            total_duration_ms = total_duration * 1000  # Convert to milliseconds
            base_audio = AudioSegment.silent(duration=total_duration_ms)
        else:
            # Load the music file
            base_audio = AudioSegment.from_mp3(args.music)
        
        # Overlay beeps and voice prompts
        current_position = 0  # Start at 0 seconds
        
        # Add halfway mark at calculated position
        halfway_position = halfway_point * 1000
        halfway_voice = AudioSegment.from_mp3(voice_mp3s[-1])  # Last file is the halfway prompt
        base_audio = base_audio.overlay(halfway_voice, position=halfway_position)
        base_audio = base_audio.overlay(beep, position=halfway_position)

        # Add all other intervals
        for i, (interval, voice_mp3) in enumerate(zip(intervals, voice_mp3s[:-1]), 1):
            voice = AudioSegment.from_mp3(voice_mp3)
            base_audio = base_audio.overlay(voice, position=current_position)
            base_audio = base_audio.overlay(beep, position=current_position)
            # Update position for next interval
            current_position += int(interval['Duration_Seconds']) * 1000

    # Export the final audio
    base_audio.export(args.output, format="mp3")
    print(f"Interval audio file created successfully: {args.output}")

if __name__ == "__main__":
    main() 