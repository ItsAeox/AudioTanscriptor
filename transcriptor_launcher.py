import os
import tkinter as tk
from tkinter import ttk, font
import importlib.util
import sys

# Custom color scheme
COLORS = {
    "primary_red": "#C41E3A",      # Cardinal red - primary color
    "secondary_red": "#8B0000",    # Dark red for accents
    "light_red": "#FF6B6B",        # Light red for highlights
    "white": "#FFFFFF",            # White
    "light_gray": "#F5F5F5",       # Light gray for backgrounds
    "dark_gray": "#333333",        # Dark gray for text
    "border_gray": "#E0E0E0",      # Border color for separation
    "hover_red": "#D32C47"         # Slightly lighter red for hover effects
}

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

def launch_live_transcriptor():
    # Load the live_transcriptor.py module dynamically
    live_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 "live_transcriptor", "live_transcriptor.py")
    
    # Import the module dynamically
    spec = importlib.util.spec_from_file_location("live_transcriptor", live_file_path)
    live_module = importlib.util.module_from_spec(spec)
    sys.modules["live_transcriptor"] = live_module
    spec.loader.exec_module(live_module)
    
    # Create a new window and application
    root = tk.Tk()
    app = live_module.LiveTranscriptorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

class TranscriptorLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transcriptor Suite")
        self.root.geometry("650x950")
        self.root.resizable(True, True)
        self.root.configure(bg=COLORS["white"])
        
        # Set icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Configure styles
        self.configure_styles()
        
        # Create widgets
        self.create_widgets()
    
    def configure_styles(self):
        # Create custom styles for widgets
        self.style = ttk.Style()
        
        # Configure frame styles
        self.style.configure("Main.TFrame", background=COLORS["white"])
        self.style.configure("Card.TFrame", background=COLORS["light_gray"], 
                            relief="raised", borderwidth=1)
        
        # Configure label styles
        self.style.configure("Title.TLabel", 
                            background=COLORS["white"], 
                            foreground=COLORS["primary_red"], 
                            font=("Segoe UI", 24, "bold"))
        
        self.style.configure("Subtitle.TLabel", 
                            background=COLORS["white"], 
                            foreground=COLORS["secondary_red"], 
                            font=("Segoe UI", 14))
        
        self.style.configure("CardTitle.TLabel", 
                            background=COLORS["light_gray"], 
                            foreground=COLORS["primary_red"], 
                            font=("Segoe UI", 14, "bold"))
        
        self.style.configure("CardDesc.TLabel", 
                            background=COLORS["light_gray"], 
                            foreground=COLORS["dark_gray"], 
                            font=("Segoe UI", 10))
        
        self.style.configure("Footer.TLabel", 
                            background=COLORS["white"], 
                            foreground=COLORS["secondary_red"], 
                            font=("Segoe UI", 9))
        
        # Configure button styles
        self.style.configure("TButton", 
                            background=COLORS["primary_red"], 
                            foreground=COLORS["primary_red"],
                            font=("Segoe UI", 11))
        
        # Button hover effect
        self.style.map("TButton",
                       background=[("active", COLORS["hover_red"])],
                       foreground=[("active", COLORS["primary_red"])])
        
        # New feature button style
        self.style.configure("New.TButton", 
                            background=COLORS["secondary_red"], 
                            foreground=COLORS["primary_red"],
                            font=("Segoe UI", 11, "bold"))
        
        # New feature button hover effect
        self.style.map("New.TButton",
                      background=[("active", COLORS["primary_red"])],
                      foreground=[("active", COLORS["primary_red"])])
    
    def create_widgets(self):
        # Main container frame
        main_frame = ttk.Frame(self.root, style="Main.TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        header_frame = ttk.Frame(main_frame, style="Main.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="TRANSCRIPTOR SUITE", 
                              style="Title.TLabel")
        title_label.pack(pady=(10, 5))
        
        subtitle_label = ttk.Label(header_frame, text="Advanced Audio & Video Transcription", 
                                 style="Subtitle.TLabel")
        subtitle_label.pack(pady=(0, 10))
        
        # Description section
        desc_frame = ttk.Frame(main_frame, style="Main.TFrame")
        desc_frame.pack(fill=tk.X, pady=10)
        
        description_text = """
        Welcome to the Transcriptor Suite! This application provides powerful tools 
        for converting spoken language into text using state-of-the-art AI models.
        Choose one of the options below to begin:
        """
        
        desc_label = ttk.Label(desc_frame, text=description_text, 
                             background=COLORS["white"],
                             foreground=COLORS["dark_gray"],
                             font=("Segoe UI", 11),
                             wraplength=550,
                             justify="center")
        desc_label.pack(pady=10)
        
        # App cards section
        cards_frame = ttk.Frame(main_frame, style="Main.TFrame")
        cards_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Audio Transcriptor card
        self.create_app_card(
            cards_frame,
            "Audio Transcriptor",
            "Convert audio files to text with high accuracy.\nSupports various audio formats.",
            self.open_audio_transcriptor
        )
        
        # Video Transcriptor card
        self.create_app_card(
            cards_frame,
            "Video Transcriptor",
            "Extract and transcribe audio from video files.\nSupports popular video formats.",
            self.open_video_transcriptor
        )
        
        # Live Transcriptor card
        self.create_app_card(
            cards_frame,
            "Live Voice Transcriptor",
            "Transcribe your voice in real-time as you speak.\nCompare multiple transcription engines.",
            self.open_live_transcriptor,
            is_new=True
        )
        
        # Footer
        footer_frame = ttk.Frame(main_frame, style="Main.TFrame")
        footer_frame.pack(fill=tk.X, pady=10)
        
        footer_text = "Powered by OpenAI Whisper and CMU Sphinx • English language optimized"
        footer_label = ttk.Label(footer_frame, text=footer_text, style="Footer.TLabel", justify="center")
        footer_label.pack(side=tk.BOTTOM)
    
    def create_app_card(self, parent, title, description, command, is_new=False):
        # Card container
        card_frame = ttk.Frame(parent, style="Card.TFrame", padding=15)
        card_frame.pack(fill=tk.X, pady=10, ipady=10)
        
        # Content area
        content_frame = ttk.Frame(card_frame, style="Card.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title row
        title_frame = ttk.Frame(content_frame, style="Card.TFrame")
        title_frame.pack(fill=tk.X, anchor="w")
        
        title_label = ttk.Label(title_frame, text=title, style="CardTitle.TLabel")
        title_label.pack(side=tk.LEFT)
        
        if is_new:
            new_tag = tk.Label(
                title_frame, 
                text="NEW", 
                bg=COLORS["light_red"],
                fg=COLORS["white"],
                padx=5,
                pady=1,
                font=("Segoe UI", 8, "bold")
            )
            new_tag.pack(side=tk.LEFT, padx=(10, 0))
        
        # Description
        desc_label = ttk.Label(content_frame, text=description, style="CardDesc.TLabel", wraplength=500)
        desc_label.pack(pady=(5, 15), anchor="w")
        
        # Button
        button_style = "New.TButton" if is_new else "TButton"
        launch_button = ttk.Button(
            content_frame,
            text="Launch Application",
            command=command,
            style=button_style,
            width=25
        )
        launch_button.pack(pady=(0, 5))
    
    def open_audio_transcriptor(self):
        self.root.destroy()
        launch_audio_transcriptor()
    
    def open_video_transcriptor(self):
        self.root.destroy()
        launch_video_transcriptor()
    
    def open_live_transcriptor(self):
        self.root.destroy()
        launch_live_transcriptor()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriptorLauncherApp(root)
    root.mainloop()