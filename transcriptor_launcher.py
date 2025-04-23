import os
import tkinter as tk
from tkinter import ttk
import importlib.util
import sys

def launch_audio_transcriptor():
    # Load the audio_transcriptor.py module dynamically
    audio_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 "audio_transcriptor", "audio_transcriptor.py")
    
    # Import the module dynamically
    spec = importlib.util.spec_from_file_location("audio_transcriptor", audio_file_path)
    audio_module = importlib.util.module_from_spec(spec)
    sys.modules["audio_transcriptor"] = audio_module
    spec.loader.exec_module(audio_module)
    
    # Create a new window and application
    root = tk.Tk()
    app = audio_module.AudioTranscriptorApp(root)
    root.mainloop()

def launch_video_transcriptor():
    # Load the video_transcriptor.py module dynamically
    video_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 "video_transcriptor", "video_transcriptor.py")
    
    # Import the module dynamically
    spec = importlib.util.spec_from_file_location("video_transcriptor", video_file_path)
    video_module = importlib.util.module_from_spec(spec)
    sys.modules["video_transcriptor"] = video_module
    spec.loader.exec_module(video_module)
    
    # Create a new window and application
    root = tk.Tk()
    app = video_module.VideoTranscriptorApp(root)
    root.mainloop()

class TranscriptorLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcriptor Launcher")
        self.root.geometry("400x300")
        self.root.resizable(True, True)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Transcriptor App", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Description
        description = ttk.Label(main_frame, text="Choose which transcriptor you want to use:")
        description.pack(pady=20)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        # Audio Transcriptor Button - this now launches a standalone window
        audio_button = ttk.Button(
            buttons_frame, 
            text="Audio Transcriptor", 
            command=self.open_audio_transcriptor,
            width=20
        )
        audio_button.pack(pady=10)
        
        # Video Transcriptor Button - this now launches a standalone window
        video_button = ttk.Button(
            buttons_frame, 
            text="Video Transcriptor", 
            command=self.open_video_transcriptor,
            width=20
        )
        video_button.pack(pady=10)
        
        # Footer
        footer_text = "Audio transcriptor works with .wav, .mp3, .flac files\nVideo transcriptor extracts audio from video files"
        footer = ttk.Label(main_frame, text=footer_text, justify=tk.CENTER)
        footer.pack(side=tk.BOTTOM, pady=10)
    
    def open_audio_transcriptor(self):
        # Close the launcher window
        self.root.destroy()
        # Open the audio transcriptor
        launch_audio_transcriptor()
    
    def open_video_transcriptor(self):
        # Close the launcher window
        self.root.destroy()
        # Open the video transcriptor
        launch_video_transcriptor()

def main():
    root = tk.Tk()
    app = TranscriptorLauncherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()