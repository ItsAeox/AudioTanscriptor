import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import speech_recognition as sr
import threading
import wave
import contextlib
from pydub import AudioSegment
import whisper
import tempfile

class AudioTranscriptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Transcriptor")
        self.root.geometry("600x600")
        self.root.resizable(True, True)
        
        self.audio_path = ""
        self.output_path = ""
        self.is_processing = False
        
        # Recognition engine selection
        self.engine_var = tk.StringVar(value="whisper")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Audio Transcriptor", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Audio File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        # Audio file selection
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(file_frame, text="Browse", command=self.browse_audio)
        browse_button.pack(side=tk.RIGHT)
        
        # Output file frame
        output_frame = ttk.LabelFrame(main_frame, text="Output File", padding="10")
        output_frame.pack(fill=tk.X, pady=10)
        
        # Output path selection
        self.output_path_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=50)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        output_button = ttk.Button(output_frame, text="Browse", command=self.browse_output)
        output_button.pack(side=tk.RIGHT)
        
        # Engine selection frame
        engine_frame = ttk.LabelFrame(main_frame, text="Recognition Engine", padding="10")
        engine_frame.pack(fill=tk.X, pady=10)
        
        # Radio buttons for engine selection
        whisper_radio = ttk.Radiobutton(engine_frame, text="OpenAI Whisper (High Accuracy)", 
                                      variable=self.engine_var, value="whisper")
        whisper_radio.pack(anchor=tk.W, pady=2)
        
        # Whisper model selection frame
        self.model_var = tk.StringVar(value="base")
        model_frame = ttk.Frame(engine_frame)
        model_frame.pack(fill=tk.X, padx=20, pady=5)
        
        model_label = ttk.Label(model_frame, text="Whisper Model:")
        model_label.pack(side=tk.LEFT, padx=(0, 10))
        
        tiny_radio = ttk.Radiobutton(model_frame, text="Tiny (Fast)", 
                                    variable=self.model_var, value="tiny")
        tiny_radio.pack(side=tk.LEFT, padx=5)
        
        base_radio = ttk.Radiobutton(model_frame, text="Base (Balanced)", 
                                    variable=self.model_var, value="base")
        base_radio.pack(side=tk.LEFT, padx=5)
        
        small_radio = ttk.Radiobutton(model_frame, text="Small (Better)", 
                                     variable=self.model_var, value="small")
        small_radio.pack(side=tk.LEFT, padx=5)
        
        # Google radio
        google_radio = ttk.Radiobutton(engine_frame, text="Google Speech Recognition (Online)", 
                                      variable=self.engine_var, value="google")
        google_radio.pack(anchor=tk.W, pady=2)
        
        # Sphinx radio
        sphinx_radio = ttk.Radiobutton(engine_frame, text="CMU Sphinx (Offline)", 
                                      variable=self.engine_var, value="sphinx")
        sphinx_radio.pack(anchor=tk.W, pady=2)
        
        # Process frame
        process_frame = ttk.Frame(main_frame)
        process_frame.pack(fill=tk.X, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(process_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to transcribe")
        status_label = ttk.Label(process_frame, textvariable=self.status_var)
        status_label.pack(anchor=tk.W, pady=5)
        
        # Audio info label
        self.audio_info_var = tk.StringVar(value="")
        audio_info_label = ttk.Label(process_frame, textvariable=self.audio_info_var)
        audio_info_label.pack(anchor=tk.W, pady=5)
        
        # Transcribe button - made larger and more prominent
        transcribe_frame = ttk.Frame(main_frame)
        transcribe_frame.pack(fill=tk.X, pady=10)
        
        self.transcribe_button = ttk.Button(
            transcribe_frame, 
            text="START TRANSCRIPTION", 
            command=self.start_transcription,
            style="Accent.TButton"
        )
        self.transcribe_button.pack(fill=tk.X, ipady=10, pady=10)
        
        # Create a custom style for the button to make it more visible
        button_style = ttk.Style()
        button_style.configure("Accent.TButton", font=("Arial", 12, "bold"))
    
    def browse_audio(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.flac *.aiff *.aac *.m4a *.ogg"),
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("WAV files", "*.wav"),
                ("MP3 files", "*.mp3"),
                ("FLAC files", "*.flac"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.audio_path = file_path
            self.file_path_var.set(file_path)
            
            # Auto-suggest output path
            suggested_output = os.path.splitext(file_path)[0] + "_transcript.txt"
            self.output_path = suggested_output
            self.output_path_var.set(suggested_output)
            
            # Display audio information if it's a WAV file
            if file_path.lower().endswith('.wav'):
                try:
                    with contextlib.closing(wave.open(file_path, 'r')) as f:
                        frames = f.getnframes()
                        rate = f.getframerate()
                        duration = frames / float(rate)
                        channels = f.getnchannels()
                        self.audio_info_var.set(f"Audio: {round(duration, 2)}s, {rate}Hz, {channels} channel(s)")
                except:
                    self.audio_info_var.set("Could not read audio information")
            else:
                self.audio_info_var.set("Audio information available only for WAV files")
    
    def browse_output(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Transcript As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.output_path = file_path
            self.output_path_var.set(file_path)
    
    def start_transcription(self):
        if not self.audio_path:
            messagebox.showerror("Error", "Please select an audio file to transcribe.")
            return
        
        if not self.output_path:
            messagebox.showerror("Error", "Please select an output path for the transcript.")
            return
        
        if self.is_processing:
            return
        
        self.is_processing = True
        self.transcribe_button.config(state=tk.DISABLED)
        self.status_var.set("Starting transcription process...")
        self.progress_var.set(0)
        
        # Start transcription in a separate thread
        transcription_thread = threading.Thread(target=self.transcribe_audio)
        transcription_thread.daemon = True
        transcription_thread.start()
    
    def transcribe_audio(self):
        temp_files = []
        try:
            self.status_var.set("Preparing audio...")
            self.root.update_idletasks()
            
            self.progress_var.set(10)
            
            # Determine which engine to use
            engine = self.engine_var.get()
            
            if engine == "whisper":
                # Use Whisper for transcription
                self.status_var.set(f"Loading Whisper {self.model_var.get()} model...")
                self.root.update_idletasks()
                
                # Load the selected model
                model = whisper.load_model(self.model_var.get())
                
                self.progress_var.set(30)
                self.status_var.set("Transcribing with Whisper (this may take a few minutes)...")
                self.root.update_idletasks()
                
                # Transcribe directly with Whisper
                result = model.transcribe(self.audio_path)
                
                self.progress_var.set(80)
                self.status_var.set("Whisper transcription completed!")
                
                text = result["text"]
                
            else:
                # Initialize speech recognition with improved settings
                recognizer = sr.Recognizer()
                # Adjust recognition parameters for better accuracy
                recognizer.energy_threshold = 300  # Increase energy threshold
                recognizer.pause_threshold = 0.8   # Adjust pause threshold
                recognizer.dynamic_energy_threshold = True
                
                file_extension = os.path.splitext(self.audio_path)[1].lower()
                
                # For non-WAV files, convert to WAV first using pydub
                temp_wav_path = None
                
                if file_extension != '.wav':
                    self.status_var.set(f"Converting {file_extension} file to WAV format...")
                    self.root.update_idletasks()
                    
                    try:
                        audio = AudioSegment.from_file(self.audio_path)
                        temp_wav_path = os.path.splitext(self.audio_path)[0] + "_temp.wav"
                        temp_files.append(temp_wav_path)
                        # Enhanced audio processing for better speech recognition
                        audio = audio.set_channels(1).set_frame_rate(16000)
                        # Normalize audio to improve speech detection
                        audio = audio.normalize()
                        audio.export(temp_wav_path, format="wav")
                        
                        # Use the temporary WAV file for transcription
                        audio_file_path = temp_wav_path
                    except Exception as e:
                        raise Exception(f"Error converting audio file: {str(e)}")
                else:
                    # Process WAV files too for better quality
                    try:
                        audio = AudioSegment.from_file(self.audio_path)
                        temp_wav_path = os.path.splitext(self.audio_path)[0] + "_processed.wav"
                        temp_files.append(temp_wav_path)
                        audio = audio.set_channels(1).set_frame_rate(16000)
                        audio = audio.normalize()
                        audio.export(temp_wav_path, format="wav")
                        audio_file_path = temp_wav_path
                    except:
                        # Fall back to original file if processing fails
                        audio_file_path = self.audio_path
                    
                # Load audio file
                try:
                    with sr.AudioFile(audio_file_path) as source:
                        self.status_var.set("Adjusting for ambient noise...")
                        self.root.update_idletasks()
                        # Longer ambient noise adjustment for better baseline
                        recognizer.adjust_for_ambient_noise(source, duration=1.0)
                        
                        self.status_var.set("Reading audio file...")
                        self.root.update_idletasks()
                        audio_data = recognizer.record(source)
                except Exception as e:
                    raise Exception(f"Error reading audio file: {str(e)}")
                
                self.progress_var.set(50)
                self.status_var.set("Converting speech to text...")
                self.root.update_idletasks()
                
                # Convert speech to text with improved settings
                text = ""
                error_messages = []
                
                if engine == "google":
                    try:
                        # Use language parameter for better accuracy
                        text = recognizer.recognize_google(
                            audio_data, 
                            language="en-US",  # Specify language
                            show_all=False     # Get best result only
                        )
                        self.status_var.set("Google Speech Recognition completed")
                    except sr.UnknownValueError:
                        error_messages.append("Google Speech Recognition could not understand the audio")
                    except sr.RequestError as e:
                        error_messages.append(f"Could not request results from Google Speech Recognition service; {e}")
                
                elif engine == "sphinx":
                    try:
                        # Configure Sphinx for better accuracy
                        text = recognizer.recognize_sphinx(
                            audio_data,
                            keyword_entries=[],  # Add domain-specific keywords if needed
                            grammar=None
                        )
                        self.status_var.set("CMU Sphinx completed")
                    except sr.UnknownValueError:
                        error_messages.append("Sphinx could not understand the audio")
                    except sr.RequestError as e:
                        error_messages.append(f"Sphinx error; {e}")
                
                # If we didn't get any transcription, raise an error
                if not text:
                    raise Exception("\n".join(error_messages))
            
            self.progress_var.set(90)
            self.status_var.set("Saving transcript...")
            self.root.update_idletasks()
            
            # Save transcript to file
            with open(self.output_path, 'w', encoding='utf-8') as file:
                file.write(text)
            
            self.progress_var.set(100)
            self.status_var.set("Transcription completed successfully!")
            messagebox.showinfo("Success", f"Transcription completed and saved to:\n{self.output_path}")
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            print(f"Transcription error: {error_message}")
            self.status_var.set(error_message)
            messagebox.showerror("Error", f"An error occurred during transcription:\n{str(e)}")
        
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        print(f"Warning: Could not delete temporary file: {temp_file}")
                    
            self.is_processing = False
            self.transcribe_button.config(state=tk.NORMAL)
            self.root.update_idletasks()

def main():
    root = tk.Tk()
    app = AudioTranscriptorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()