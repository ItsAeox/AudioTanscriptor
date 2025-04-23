import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import tempfile
import time
import speech_recognition as sr
from pydub import AudioSegment
import whisper
import numpy as np
import pyaudio
import wave
import contextlib

class LiveTranscriptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Voice Transcriptor")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Recording state
        self.is_recording = False
        self.is_transcribing = False
        self.audio_queue = queue.Queue()
        self.transcription_queue = queue.Queue()
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.SILENCE_THRESHOLD = 1000  # Adjust based on your microphone
        self.SILENCE_DURATION = 1.5  # Seconds of silence to trigger processing
        
        # For continuous recording
        self.frames = []
        self.silence_frames = 0
        self.max_silence_frames = int(self.RATE / self.CHUNK * self.SILENCE_DURATION)
        
        # PyAudio instance
        self.pyaudio = pyaudio.PyAudio()
        
        # Recognition settings
        self.whisper_model = None
        self.whisper_model_name = "tiny"  # Default to tiny for faster processing
        self.language = "en"  # Set English as the default language
        
        # Create UI
        self.create_widgets()
        
        # Pre-load whisper model
        self.load_whisper_model_thread = threading.Thread(target=self.load_whisper_model)
        self.load_whisper_model_thread.daemon = True
        self.load_whisper_model_thread.start()
    
    def load_whisper_model(self):
        try:
            self.status_var.set("Loading Whisper model (this may take a moment)...")
            self.root.update_idletasks()
            self.whisper_model = whisper.load_model(self.whisper_model_name)
            self.status_var.set("Whisper model loaded. Ready to transcribe in English.")
        except Exception as e:
            self.status_var.set(f"Error loading Whisper model: {str(e)}")
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Live Voice Transcriptor", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Whisper model selection
        model_frame = ttk.Frame(settings_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        model_label = ttk.Label(model_frame, text="Whisper Model:")
        model_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.model_var = tk.StringVar(value="tiny")
        
        tiny_radio = ttk.Radiobutton(model_frame, text="Tiny (Fast)", 
                                    variable=self.model_var, value="tiny",
                                    command=self.change_whisper_model)
        tiny_radio.pack(side=tk.LEFT, padx=5)
        
        base_radio = ttk.Radiobutton(model_frame, text="Base (Balanced)", 
                                    variable=self.model_var, value="base",
                                    command=self.change_whisper_model)
        base_radio.pack(side=tk.LEFT, padx=5)
        
        small_radio = ttk.Radiobutton(model_frame, text="Small (Better)", 
                                    variable=self.model_var, value="small",
                                    command=self.change_whisper_model)
        small_radio.pack(side=tk.LEFT, padx=5)
        
        # Dual engine option
        self.dual_engine_var = tk.BooleanVar(value=False)
        dual_engine_check = ttk.Checkbutton(
            settings_frame, 
            text="Use both Whisper and Sphinx (compare results)",
            variable=self.dual_engine_var
        )
        dual_engine_check.pack(anchor=tk.W, pady=5)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Loading Whisper model...")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(anchor=tk.W, pady=5)
        
        # Transcription display
        transcription_frame = ttk.LabelFrame(main_frame, text="Transcription", padding="10")
        transcription_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Whisper transcription
        whisper_frame = ttk.LabelFrame(transcription_frame, text="Whisper Transcription", padding="10")
        whisper_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 5))
        
        self.whisper_text = tk.Text(whisper_frame, wrap=tk.WORD, width=40, height=10)
        self.whisper_text.pack(fill=tk.BOTH, expand=True)
        whisper_scrollbar = ttk.Scrollbar(self.whisper_text, command=self.whisper_text.yview)
        self.whisper_text.configure(yscrollcommand=whisper_scrollbar.set)
        whisper_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sphinx transcription
        sphinx_frame = ttk.LabelFrame(transcription_frame, text="Sphinx Transcription", padding="10")
        sphinx_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=(5, 0))
        
        self.sphinx_text = tk.Text(sphinx_frame, wrap=tk.WORD, width=40, height=10)
        self.sphinx_text.pack(fill=tk.BOTH, expand=True)
        sphinx_scrollbar = ttk.Scrollbar(self.sphinx_text, command=self.sphinx_text.yview)
        self.sphinx_text.configure(yscrollcommand=sphinx_scrollbar.set)
        sphinx_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Start/Stop button
        self.record_button = ttk.Button(
            control_frame,
            text="START RECORDING",
            command=self.toggle_recording,
            style="Record.TButton"
        )
        self.record_button.pack(fill=tk.X, ipady=10)
        
        # Clear button
        self.clear_button = ttk.Button(
            control_frame,
            text="Clear Transcription",
            command=self.clear_transcription
        )
        self.clear_button.pack(pady=10)
        
        # Create custom button style
        button_style = ttk.Style()
        button_style.configure("Record.TButton", font=("Arial", 12, "bold"))
    
    def change_whisper_model(self):
        if self.whisper_model_name != self.model_var.get():
            self.whisper_model_name = self.model_var.get()
            self.whisper_model = None  # Reset model
            
            # Load new model in background
            self.status_var.set(f"Loading {self.whisper_model_name} model...")
            load_thread = threading.Thread(target=self.load_whisper_model)
            load_thread.daemon = True
            load_thread.start()
    
    def toggle_recording(self):
        if self.whisper_model is None:
            messagebox.showerror("Error", "Whisper model is still loading. Please wait.")
            return
            
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.is_recording = True
        self.record_button.config(text="STOP RECORDING")
        self.status_var.set("Recording... Speak into your microphone")
        
        # Clear previous transcription if needed
        if not self.dual_engine_var.get():
            self.clear_transcription()
        
        # Reset frames
        self.frames = []
        self.silence_frames = 0
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        # Start transcription processing in a separate thread
        self.transcription_thread = threading.Thread(target=self.process_audio)
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
        
        # Start UI update thread
        self.update_thread = threading.Thread(target=self.update_transcription)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="START RECORDING")
        self.status_var.set("Recording stopped")
    
    def record_audio(self):
        stream = self.pyaudio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        self.frames = []
        
        try:
            while self.is_recording:
                data = stream.read(self.CHUNK)
                self.frames.append(data)
                
                # Check for silence to segment speech
                audio_data = np.frombuffer(data, dtype=np.int16)
                if np.abs(audio_data).mean() < self.SILENCE_THRESHOLD:
                    self.silence_frames += 1
                else:
                    self.silence_frames = 0
                
                # If we detect enough silence and have some data, process it
                if self.silence_frames > self.max_silence_frames and len(self.frames) > 10:
                    # Make a copy of the current frames and put them in the queue
                    frames_copy = self.frames.copy()
                    self.audio_queue.put(frames_copy)
                    
                    # Reset frames for next segment
                    self.frames = []
                    self.silence_frames = 0
        finally:
            stream.stop_stream()
            stream.close()
            
            # Process any remaining audio
            if self.frames:
                self.audio_queue.put(self.frames)
    
    def process_audio(self):
        self.is_transcribing = True
        
        try:
            while self.is_recording or not self.audio_queue.empty():
                try:
                    frames = self.audio_queue.get(timeout=1)  # Wait for up to 1 second
                    
                    # Convert frames to temporary WAV file
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                        temp_wav_path = temp_file.name
                        
                    wf = wave.open(temp_wav_path, 'wb')
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.pyaudio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()
                    
                    # Transcribe with Whisper
                    whisper_text = self.transcribe_with_whisper(temp_wav_path)
                    
                    # Transcribe with Sphinx if dual engine is enabled
                    if self.dual_engine_var.get():
                        sphinx_text = self.transcribe_with_sphinx(temp_wav_path)
                    else:
                        sphinx_text = ""
                    
                    # Add to transcription queue
                    self.transcription_queue.put((whisper_text, sphinx_text))
                    
                    # Remove temporary file
                    try:
                        os.unlink(temp_wav_path)
                    except:
                        pass
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Processing error: {e}")
                    continue
                    
        finally:
            self.is_transcribing = False
    
    def transcribe_with_whisper(self, audio_path):
        try:
            # Set language to English specifically for better accuracy
            result = self.whisper_model.transcribe(
                audio_path, 
                language=self.language,  # Specify English language
                task="transcribe"
            )
            return result["text"].strip()
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            return ""
    
    def transcribe_with_sphinx(self, audio_path):
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                
            # Specifically set to use English for Sphinx
            text = recognizer.recognize_sphinx(
                audio_data,
                language="en-US"  # Specify American English
            )
            return text.strip()
        except Exception as e:
            print(f"Sphinx transcription error: {e}")
            return ""
    
    def update_transcription(self):
        while self.is_recording or self.is_transcribing or not self.transcription_queue.empty():
            try:
                whisper_text, sphinx_text = self.transcription_queue.get(timeout=0.5)
                
                if whisper_text:
                    # Append to the text widget with a newline if there's already content
                    current_text = self.whisper_text.get("1.0", tk.END).strip()
                    if current_text:
                        self.whisper_text.insert(tk.END, f"\n{whisper_text}")
                    else:
                        self.whisper_text.insert(tk.END, whisper_text)
                    self.whisper_text.see(tk.END)  # Scroll to the end
                
                if sphinx_text:
                    current_text = self.sphinx_text.get("1.0", tk.END).strip()
                    if current_text:
                        self.sphinx_text.insert(tk.END, f"\n{sphinx_text}")
                    else:
                        self.sphinx_text.insert(tk.END, sphinx_text)
                    self.sphinx_text.see(tk.END)  # Scroll to the end
                
            except queue.Empty:
                time.sleep(0.1)
                continue
            except Exception as e:
                print(f"UI update error: {e}")
    
    def clear_transcription(self):
        self.whisper_text.delete("1.0", tk.END)
        self.sphinx_text.delete("1.0", tk.END)
    
    def on_closing(self):
        if self.is_recording:
            self.stop_recording()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = LiveTranscriptorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()