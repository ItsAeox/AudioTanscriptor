# VideoTranscriptor

A comprehensive Python-based application for transcribing speech from various sources - video files, audio files, and live microphone input - using multiple speech recognition engines.

## Features

- **Video Transcription**: Extract and transcribe audio from video files
- **Audio Transcription**: Transcribe existing audio files
- **Live Transcription**: Real-time transcription from microphone input
- **Multiple Recognition Engines**:
  - OpenAI Whisper (high accuracy)
  - CMU Sphinx (offline capability)
- **User-friendly GUI**: Simple interface for all transcription modes
- **Flexible Output Options**: Save transcriptions to text files

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/VideoTranscriptor.git
   cd VideoTranscriptor
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. For OpenAI Whisper, you may need additional system dependencies based on your OS:
   - On Windows: Make sure you have Visual C++ Build Tools installed
   - On Linux: `sudo apt-get install ffmpeg`
   - On macOS: `brew install ffmpeg`

## Usage

### Launch the application

Run the main launcher script:
```
python transcriptor_launcher.py
```

### Video Transcription

1. Select "Video Transcription" from the main menu
2. Click "Browse" to select a video file
3. Choose an output location for the transcription
4. Select a transcription engine (Whisper recommended for accuracy)
5. Click "Start Transcription" to begin the process

### Audio Transcription

1. Select "Audio Transcription" from the main menu
2. Click "Browse" to select an audio file
3. Choose an output location for the transcription
4. Select a transcription engine
5. Click "Start Transcription"

### Live Transcription

1. Select "Live Transcription" from the main menu
2. Make sure your microphone is connected and working
3. Click "Start Recording" to begin transcribing
4. Speak clearly into your microphone
5. Click "Stop Recording" when finished
6. Save the transcription using the "Save" button

## Recognition Engines

- **OpenAI Whisper**: State-of-the-art accuracy but requires more computational resources
- **CMU Sphinx**: Works offline, good for privacy-sensitive applications or environments without internet connectivity

## Requirements

- SpeechRecognition >= 3.8.1
- moviepy >= 1.0.3
- PyAudio >= 0.2.11
- pydub >= 0.25.1
- pocketsphinx >= 0.1.15
- openai-whisper
- torch

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) for state-of-the-art speech recognition
- [CMU Sphinx](https://cmusphinx.github.io/) for offline speech recognition capabilities
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) Python library