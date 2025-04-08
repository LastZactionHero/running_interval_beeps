# Running Interval Beeps

A tool to create interval training audio with voice prompts and beeps.

## Requirements

- Python 3.x
- FFmpeg
- pydub
- macOS (for voice synthesis)

## Installation

1. Install Python dependencies:
```bash
pip install pydub
```

2. Install FFmpeg:
```bash
brew install ffmpeg
```

## Usage

Basic usage:
```bash
python create_interval_audio.py
```

Advanced usage with options:
```bash
python create_interval_audio.py --input interval.csv --output output.mp3 --music background.mp3 --beep beep.mp3
```

### Command Line Options

- `--input`, `-i`: Input CSV file with interval data (default: interval.csv)
- `--output`, `-o`: Output audio file (default: interval_music.mp3)
- `--music`, `-m`: Background music file (default: music.mp3)
- `--beep`, `-b`: Beep sound file (default: beep.mp3)
- `--debug`: Create debug audio without background music (just beeps and voice)

### CSV Format

The input CSV file should have the following columns:
- `StepID`: Unique identifier for each step
- `Phase`: Phase of the workout (Warm-up, Interval, Recovery, Cool-down)
- `Duration_Seconds`: Duration of the step in seconds
- `Effort_Description`: Description of the effort level
- `Cumulative_Time_Seconds`: Cumulative time from start in seconds
- `Focus_Notes`: Additional notes about the step

Example:
```csv
StepID,Phase,Duration_Seconds,Effort_Description,Cumulative_Time_Seconds,Focus_Notes
1,Warm-up,180,Brisk Walk,180,"Relax shoulders, head level"
2,Interval,30,Faster Pace (7/10 Effort),210,"Stay tall, controlled effort"
```

## Debug Mode

To test the timing of intervals without background music, use the debug mode:
```bash
python create_interval_audio.py --debug --input debug.csv --output debug_audio.mp3
```

This will create an audio file with just the beeps and voice prompts, making it easier to verify the timing of intervals.

## Features

- Voice prompts and beeps synchronized with workout intervals
- Halfway point announcement for out-and-back workouts
- Debug mode for testing timing without background music
- Flexible input/output file configuration
- Dynamic timing based on interval durations

## File Requirements

- `music.mp3`: Background music file (optional if using debug mode)
- `beep.mp3`: Beep sound file
- Input CSV file with interval data

## Notes

- The script uses macOS's built-in text-to-speech (Samantha voice)
- Voice prompts and beeps are placed at the start of each interval
- Timing is calculated based on the sum of previous interval durations
- The halfway point is automatically calculated based on the total workout duration
- All timings are in milliseconds internally for precise audio placement 