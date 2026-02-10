#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
import threading
import re
import os
import sys

def get_bundled_path(filename):
    """Get path to bundled resource, works for both dev and bundled app"""
    if getattr(sys, 'frozen', False):
        # Running as bundled app
        bundle_dir = sys._MEIPASS
    else:
        # Running in development
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(bundle_dir, filename)

def find_executable(name):
    """Find executable - first check bundled, then system"""
    # Check if bundled with app
    bundled_path = get_bundled_path(name)
    if os.path.isfile(bundled_path) and os.access(bundled_path, os.X_OK):
        return bundled_path
    
    # Common installation locations on macOS
    common_paths = [
        f'/opt/homebrew/bin/{name}',
        f'/usr/local/bin/{name}',
        f'/opt/local/bin/{name}',
        f'/usr/bin/{name}',
    ]
    
    for path in common_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    
    return None

class SubtitleBurnerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hardsubber")
        self.root.geometry("600x500")
        
        self.video_file = ""
        self.subtitle_file = ""
        self.process = None
        
        # Find ffmpeg and ffprobe executables
        self.ffmpeg_path = find_executable('ffmpeg')
        self.ffprobe_path = find_executable('ffprobe')
        
        # Video file selection
        tk.Label(root, text="Video File:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.video_label = tk.Label(root, text="No file selected", fg="gray")
        self.video_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        tk.Button(root, text="Browse", command=self.select_video).grid(row=0, column=2, padx=10, pady=10)
        
        # Subtitle file selection
        tk.Label(root, text="Subtitle File:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.subtitle_label = tk.Label(root, text="No file selected", fg="gray")
        self.subtitle_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        tk.Button(root, text="Browse", command=self.select_subtitle).grid(row=1, column=2, padx=10, pady=10)
        
        # Start and Stop buttons
        button_frame = tk.Frame(root)
        button_frame.grid(row=2, column=1, padx=10, pady=20)
        
        self.start_button = tk.Button(button_frame, text="Start", command=self.start_conversion, 
                                      state="disabled", width=10)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_conversion, 
                                     state="disabled", width=10, bg="#ff4444", fg="white")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(root, length=400, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(root, text="Ready", fg="blue")
        self.status_label.grid(row=4, column=0, columnspan=3, padx=10, pady=5)
        
        # Console output
        tk.Label(root, text="Console Output:").grid(row=5, column=0, columnspan=3, padx=10, pady=(10,0), sticky="w")
        
        # Create frame for console with scrollbar
        console_frame = tk.Frame(root)
        console_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")
        
        scrollbar = tk.Scrollbar(console_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.console = tk.Text(console_frame, height=12, width=70, yscrollcommand=scrollbar.set, 
                              bg="black", fg="#00ff00", font=("Courier", 9))
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.console.yview)
        
        # Make console read-only
        self.console.config(state=tk.DISABLED)
        
        # Configure grid weights for resizing
        root.grid_rowconfigure(6, weight=1)
        root.grid_columnconfigure(1, weight=1)
        
        # Check dependencies after UI is created
        self.check_dependencies()
    
    def check_dependencies(self):
        """Check if ffmpeg and ffprobe are available"""
        missing = []
        
        if not self.ffmpeg_path or not os.path.isfile(self.ffmpeg_path):
            missing.append('ffmpeg')
        if not self.ffprobe_path or not os.path.isfile(self.ffprobe_path):
            missing.append('ffprobe')
        
        if missing:
            error_msg = f"Missing required tools: {', '.join(missing)}\n\n"
            error_msg += "Please install ffmpeg:\n"
            error_msg += "  brew install ffmpeg\n\n"
            error_msg += "Then restart the application."
            
            self.log_to_console("=" * 60)
            self.log_to_console("ERROR: Missing Dependencies")
            self.log_to_console("=" * 60)
            self.log_to_console(error_msg)
            self.status_label.config(text="Missing ffmpeg - see console", fg="red")
            
            # Show error dialog
            from tkinter import messagebox
            messagebox.showerror("Missing Dependencies", error_msg)
        else:
            bundled = "bundled" if "MEIPASS" in self.ffmpeg_path else "system"
            self.log_to_console(f"Using {bundled} ffmpeg: {self.ffmpeg_path}")
            self.log_to_console(f"Using {bundled} ffprobe: {self.ffprobe_path}")
            self.log_to_console("Ready to process videos.")
        
    def select_video(self):
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov"), ("All files", "*.*")]
        )
        if filename:
            self.video_file = filename
            self.video_label.config(text=os.path.basename(filename), fg="black")
            self.check_ready()
    
    def select_subtitle(self):
        filename = filedialog.askopenfilename(
            title="Select Subtitle File",
            filetypes=[("Subtitle files", "*.srt *.ass"), ("All files", "*.*")]
        )
        if filename:
            self.subtitle_file = filename
            self.subtitle_label.config(text=os.path.basename(filename), fg="black")
            self.check_ready()
    
    def check_ready(self):
        if self.video_file and self.subtitle_file:
            self.start_button.config(state="normal")
    
    def start_conversion(self):
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress['value'] = 0
        
        # Convert SRT to ASS if needed
        if self.subtitle_file.endswith('.srt'):
            self.status_label.config(text="Converting subtitle to ASS...", fg="orange")
            self.root.update()
            subtitle_to_use = self.convert_to_ass()
        else:
            subtitle_to_use = self.subtitle_file
        
        # Start ffmpeg in a thread
        threading.Thread(target=self.run_ffmpeg, args=(subtitle_to_use,), daemon=True).start()
    
    def stop_conversion(self):
        """Stop the encoding process"""
        if self.process:
            self.log_to_console("\n" + "=" * 60)
            self.log_to_console("STOPPING: User requested stop...")
            self.log_to_console("=" * 60)
            self.status_label.config(text="Stopping...", fg="red")
            self.root.update()
            
            # Terminate the process
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            
            self.log_to_console("Process stopped.")
            self.status_label.config(text="Stopped by user", fg="red")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
    
    def convert_to_ass(self):
        # Convert SRT to ASS using inline code
        import re
        
        # Read SRT
        with open(self.subtitle_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        
        # Create ASS file with styling
        subtitle_dir = os.path.dirname(self.subtitle_file)
        ass_header = """[Script Info]
Title: Subtitles
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1920
PlayResY: 800

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,SF Arabic MPV,56,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,1,2,10,10,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        # Parse SRT and convert to ASS
        def srt_time_to_ass(srt_time):
            match = re.match(r'(\d+):(\d+):(\d+),(\d+)', srt_time)
            if match:
                h, m, s, ms = match.groups()
                centiseconds = int(ms) // 10
                return f'{h}:{m}:{s}.{centiseconds:02d}'
            return srt_time
        
        blocks = re.split(r'\n\n+', srt_content.strip())
        events = []
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                timing = lines[1]
                text = '\n'.join(lines[2:])
                # Remove HTML tags but keep content
                text = re.sub(r'<[^>]+>', '', text)
                # Convert newlines to ASS format line breaks
                text = text.replace('\n', '\\N')
                
                times = timing.split(' --> ')
                if len(times) == 2:
                    start = srt_time_to_ass(times[0].strip())
                    end = srt_time_to_ass(times[1].strip())
                    events.append(f'Dialogue: 0,{start},{end},Default,,0,0,0,,{text}')
        
        output_file = self.subtitle_file.rsplit('.', 1)[0] + '_converted.ass'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(ass_header)
            f.write('\n'.join(events))
        
        return output_file
    
    def log_to_console(self, message):
        """Add message to console output"""
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def run_ffmpeg(self, subtitle_file):
        output_file = self.video_file.rsplit('.', 1)[0] + '_subtitled.mp4'
        
        self.status_label.config(text="Processing video...", fg="orange")
        self.log_to_console("=" * 60)
        self.log_to_console("Starting subtitle burning process...")
        self.log_to_console(f"Video: {os.path.basename(self.video_file)}")
        self.log_to_console(f"Subtitle: {os.path.basename(subtitle_file)}")
        self.log_to_console(f"Output: {os.path.basename(output_file)}")
        self.log_to_console("=" * 60)
        
        # Get video duration first
        self.log_to_console("Analyzing video duration...")
        duration_cmd = [
            self.ffprobe_path, '-v', 'error', '-show_entries', 
            'format=duration', '-of', 
            'default=noprint_wrappers=1:nokey=1', self.video_file
        ]
        
        try:
            result = subprocess.run(duration_cmd, capture_output=True, text=True)
            total_duration = float(result.stdout.strip())
            hours = int(total_duration // 3600)
            minutes = int((total_duration % 3600) // 60)
            seconds = int(total_duration % 60)
            self.log_to_console(f"Video duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
        except Exception as e:
            total_duration = 0
            self.log_to_console(f"Warning: Could not determine duration - {e}")
        
        # Run ffmpeg
        self.log_to_console("\nStarting ffmpeg encoding...")
        cmd = [
            self.ffmpeg_path, '-y', '-i', self.video_file, '-vf',
            f'ass={subtitle_file}:fontsdir={os.path.dirname(subtitle_file)}',
            '-c:a', 'copy', output_file
        ]
        
        self.log_to_console(f"Command: {' '.join(cmd[:4])}...")
        
        self.process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Parse output for progress
        last_log_time = 0
        for line in self.process.stdout:
            # Log every 5 seconds or important lines
            time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
            if time_match:
                h, m, s = time_match.groups()
                current_time = int(h) * 3600 + int(m) * 60 + float(s)
                
                if total_duration > 0:
                    progress_pct = (current_time / total_duration) * 100
                    self.progress['value'] = min(progress_pct, 100)
                    
                    # Extract speed and fps if available
                    speed_match = re.search(r'speed=\s*([\d.]+)x', line)
                    fps_match = re.search(r'fps=\s*([\d.]+)', line)
                    
                    speed_str = f" @ {speed_match.group(1)}x" if speed_match else ""
                    fps_str = f" ({fps_match.group(1)} fps)" if fps_match else ""
                    
                    status_text = f"Processing: {progress_pct:.1f}% complete{speed_str}{fps_str}"
                    self.status_label.config(text=status_text, fg="orange")
                    
                    # Log every 5 seconds
                    if current_time - last_log_time >= 5:
                        self.log_to_console(f"Progress: {progress_pct:.1f}% - {int(h):02d}:{int(m):02d}:{int(float(s)):02d}{speed_str}")
                        last_log_time = current_time
                    
                    self.root.update_idletasks()
            elif 'error' in line.lower() or 'warning' in line.lower():
                self.log_to_console(line.strip())
        
        self.process.wait()
        
        if self.process.returncode == 0:
            self.progress['value'] = 100
            self.log_to_console("\n" + "=" * 60)
            self.log_to_console("SUCCESS! Encoding complete.")
            self.log_to_console(f"Output saved: {output_file}")
            self.log_to_console("=" * 60)
            self.status_label.config(text="Complete! Closing in 3 seconds...", fg="green")
            self.stop_button.config(state="disabled")
            self.root.update()
            self.root.after(3000, self.root.destroy)
        elif self.process.returncode == -15:  # SIGTERM
            # Process was stopped by user
            self.stop_button.config(state="disabled")
        else:
            self.log_to_console("\n" + "=" * 60)
            self.log_to_console(f"ERROR! Process failed with code {self.process.returncode}")
            self.log_to_console("=" * 60)
            self.status_label.config(text="Error occurred!", fg="red")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleBurnerGUI(root)
    root.mainloop()
