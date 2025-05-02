import csv
import subprocess
import os
import pydub
import tempfile
import argparse

def create_voice_prompt(text, focus_notes, output_file):
    """Create a voice prompt using macOS say command."""
    # Validate required fields
    if not text or text.strip() == "":
        raise ValueError("Effort_Description cannot be empty")
    # Focus notes are optional, so we'll just use the text if focus_notes is empty
    if not focus_notes or focus_notes.strip() == "":
        focus_notes = ""
    
    full_text = f"{text}. {focus_notes}"
    subprocess.run(['say', '-v', 'Samantha', '-o', output_file, full_text])

def create_beep_tone(phase, output_file):
    """Create beep tones based on the workout phase."""
    # Define frequencies and number of beeps for different phases
    frequencies = {
        'Warm-up': (440, 1),   # A4 (lower pitch), 1 beep
        'Interval': (880, 3),   # A5 (higher pitch), 3 beeps
        'Recovery': (587, 2),   # D5 (medium pitch), 2 beeps
        'Cool-down': (392, 1)   # G4 (lower pitch), 1 beep
    }
    
    frequency, num_beeps = frequencies.get(phase, (440, 1))
    
    # Create a single beep
    subprocess.run([
        'sox', '-n', output_file,
        'synth', '0.2', 'sine', str(frequency),  # Shorter beep duration
        'gain', '-3',  # Reduce volume slightly
        'repeat', str(num_beeps - 1),  # Repeat for multiple beeps
        'delay', '0.1'  # Add 0.1s delay between beeps
    ])

def main():
    parser = argparse.ArgumentParser(description='Create interval training audio with voice prompts and beeps.')
    parser.add_argument('--input', '-i', default='interval.csv', help='Input CSV file with interval data')
    parser.add_argument('--output', '-o', default='interval_music.mp3', help='Output audio file')
    parser.add_argument('--music', '-m', default='music.mp3', help='Background music file')
    parser.add_argument('--beep', '-b', default='beep.mp3', help='Beep sound file')
    parser.add_argument('--debug', action='store_true', help='Create debug audio without background music')
    args = parser.parse_args()

    # Read interval data from CSV
    intervals = []
    with open(args.input, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Ensure all required fields are present
            if not all(key in row for key in ['Effort_Description', 'Focus_Notes']):
                raise ValueError(f"Missing required fields in CSV row: {row}")
            # Validate that fields are not empty
            if not row['Effort_Description'] or not row['Focus_Notes']:
                raise ValueError(f"Empty required fields in CSV row: {row}")
            intervals.append(row)

    # Create temporary directory for voice prompts
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create voice prompts for each interval
        voice_files = []
        for i, interval in enumerate(intervals, 1):
            voice_file = os.path.join(temp_dir, f'voice_{i}.aiff')
            effort_desc = interval['Effort_Description']
            focus_notes = interval['Focus_Notes']
            create_voice_prompt(effort_desc, focus_notes, voice_file)
            voice_files.append(voice_file)

        # Create beep tones for each phase
        beep_files = []
        for i, interval in enumerate(intervals, 1):
            beep_file = os.path.join(temp_dir, f'beep_{i}.aiff')
            create_beep_tone(interval['Phase'], beep_file)
            beep_files.append(beep_file)

        # Create halfway point voice prompt
        halfway_file = os.path.join(temp_dir, 'halfway.aiff')
        create_voice_prompt("Halfway point, time to turn around", "", halfway_file)

        # Convert all AIFF files to MP3
        for file in voice_files + beep_files + [halfway_file]:
            mp3_file = file.replace('.aiff', '.mp3')
            subprocess.run(['ffmpeg', '-i', file, mp3_file])

        # Calculate total duration and halfway point
        total_duration = int(intervals[-1]['Cumulative_Time_Seconds'])
        halfway_point = total_duration // 2

        # Create base audio (music or silence)
        if args.debug:
            base_audio = pydub.AudioSegment.silent(duration=total_duration * 1000)
        else:
            base_audio = pydub.AudioSegment.from_mp3(args.music)
            # Loop music if shorter than total duration
            while len(base_audio) < total_duration * 1000:
                base_audio += base_audio
            # Reduce music volume to ?%
            base_audio = base_audio - 4.5  # Approximately ?% volume (-4.5 dB)

        # Overlay voice prompts and beeps
        current_position = 0
        for i, interval in enumerate(intervals):
            # Add beep
            beep = pydub.AudioSegment.from_mp3(beep_files[i].replace('.aiff', '.mp3'))
            base_audio = base_audio.overlay(beep, position=current_position)

            # Add voice prompt
            voice = pydub.AudioSegment.from_mp3(voice_files[i].replace('.aiff', '.mp3'))
            base_audio = base_audio.overlay(voice, position=current_position)

            # Add halfway point if this is the halfway interval
            if current_position == halfway_point * 1000:
                halfway_voice = pydub.AudioSegment.from_mp3(halfway_file.replace('.aiff', '.mp3'))
                base_audio = base_audio.overlay(halfway_voice, position=current_position)
                halfway_beep = pydub.AudioSegment.from_mp3(beep_files[i].replace('.aiff', '.mp3'))
                base_audio = base_audio.overlay(halfway_beep, position=current_position)

            # Update position for next interval
            current_position += int(interval['Duration_Seconds']) * 1000

        # Export final audio
        base_audio.export(args.output, format='mp3')
        print(f"Interval audio file created successfully: {args.output}")

if __name__ == '__main__':
    main() 