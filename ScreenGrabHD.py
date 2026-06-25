import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import os
import configparser

# Define the configuration file path in the same directory as the script
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ScreenGrabHD.cnf")

def get_ffmpeg_path():
    """Return ffmpeg path relative to current working directory"""
    cwd = os.getcwd()
    ffmpeg_path = os.path.join(cwd, "bin", "ffmpeg.exe")    
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    
    possible_paths = [
        "ffmpeg",   
        os.path.join(cwd, "ffmpeg.exe"),
        os.path.expanduser(r"~\Downloads\ffmpeg\bin\ffmpeg.exe"),
    ]
    
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    for path in possible_paths:
        try:
            result = subprocess.run(
                [path, "-version"], 
                capture_output=True, 
                text=True, 
                timeout=5,
                creationflags=creationflags
            )
            if result.returncode == 0:
                return path
        except:
            continue
    
    return None

def get_audio_devices(ffmpeg_path):
    """Parse ffmpeg dshow device list for audio capture devices."""
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        result = subprocess.run(
            [ffmpeg_path, "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            capture_output=True, 
            encoding='utf-8', 
            creationflags=creationflags
        )
        lines = result.stderr.splitlines()
        devices = []
        
        for line in lines:
            if '(audio)' in line and 'Alternative name' not in line:
                parts = line.split('"')
                if len(parts) >= 2:
                    devices.append(parts[1])
                    
        return devices
    except Exception:
        return []

def get_output_filename():
    """Generate a unique output filename by appending _01, _02, etc., if the file already exists."""
    base_name = "ScreenGrabHD_recording"
    ext = ".mp4"
    filename = f"{base_name}{ext}"
    counter = 1
    
    while os.path.exists(filename):
        filename = f"{base_name}_{counter:02d}{ext}"
        counter += 1
        
    return filename

class ScreenGrabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ScreenGrabHD Settings")
        self.root.geometry("450x400")
        self.root.resizable(False, False)
        
        # 1. Check FFmpeg
        self.ffmpeg_path = get_ffmpeg_path()
        if not self.ffmpeg_path:
            self.root.update()
            messagebox.showerror("Error", "ffmpeg.exe not found!\n\nPlease make sure 'bin' folder is in the current directory.")
            self.root.destroy()
            sys.exit(1)
            
        # 2. Get Audio Devices
        self.devices = get_audio_devices(self.ffmpeg_path)
        if not self.devices:
            self.root.update()
            messagebox.showerror("Error", "No audio capture devices found or failed to list devices.")
            self.root.destroy()
            sys.exit(1)
            
        # 3. Auto-detect System Audio
        self.sys_audio_idx = -1
        sys_keywords = ['stereo mix', 'stereomix', 'what u hear', 'loopback', 'cable output', 'virtual-audio-capturer', 'wave out mix']
        for i, d in enumerate(self.devices):
            if any(kw in d.lower() for kw in sys_keywords):
                self.sys_audio_idx = i
                break
                
        # 4. Build Initial UI
        self.build_settings_ui()
        
    def clear_window(self):
        """Clears all widgets and resets window attributes to normal."""
        self.root.unbind('<Return>')
        self.root.unbind('<Escape>')
        
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Reset window to standard windowed mode
        self.root.attributes('-topmost', False)
        self.root.overrideredirect(False)
        self.root.attributes('-alpha', 1.0)
        self.root.configure(bg='SystemButtonFace') # Default Windows background
        
        self.root.update_idletasks()

    def build_settings_ui(self):
        """Step 1: Settings Dialog"""
        self.clear_window()
        self.root.title("ScreenGrabHD Settings")
        self.root.geometry("450x400")
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"+{x}+{y}")

        # Resolution
        tk.Label(self.root, text="Recording Resolution:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        self.resolution = tk.StringVar(value="1280x720")
        tk.Radiobutton(self.root, text="HD (1280x720)", variable=self.resolution, value="1280x720").grid(row=1, column=0, sticky="w", padx=40)
        tk.Radiobutton(self.root, text="Full HD (1920x1080)", variable=self.resolution, value="1920x1080").grid(row=2, column=0, sticky="w", padx=40)
        
        # Microphone (Added "Disabled" option)
        tk.Label(self.root, text="Microphone Device:", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", padx=20, pady=(15, 5))
        mic_options = ["Disabled"] + self.devices
        self.mic_combo = ttk.Combobox(self.root, values=mic_options, state="readonly", width=45)
        self.mic_combo.grid(row=4, column=0, padx=20)
        if self.devices:
            self.mic_combo.set(self.devices[0])
        else:
            self.mic_combo.set("Disabled")
            
        # System Audio
        tk.Label(self.root, text="System Audio Device:", font=("Segoe UI", 10, "bold")).grid(row=5, column=0, sticky="w", padx=20, pady=(15, 5))
        sys_audio_options = ["Disabled"] + self.devices
        self.sys_combo = ttk.Combobox(self.root, values=sys_audio_options, state="readonly", width=45)
        self.sys_combo.grid(row=6, column=0, padx=20)
        
        if self.sys_audio_idx != -1:
            self.sys_combo.set(self.devices[self.sys_audio_idx])
        else:
            self.sys_combo.set("Disabled")
            
        # --- Load previously saved settings ---
        self.load_settings()
            
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.grid(row=7, column=0, pady=30)
        tk.Button(btn_frame, text="Select Region & Record", command=self.start_region_selector, bg="#4CAF50", fg="white", width=20, font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel", command=self.root.destroy, width=10, font=("Segoe UI", 10)).pack(side="left", padx=10)

    def load_settings(self):
        """Load settings from ScreenGrabHD.cnf if it exists."""
        if os.path.exists(CONFIG_FILE):
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE, encoding='utf-8')
            if 'Settings' in config:
                s = config['Settings']
                
                res = s.get('resolution', fallback=None)
                if res in ["1280x720", "1920x1080"]:
                    self.resolution.set(res)
                    
                mic = s.get('microphone', fallback=None)
                mic_options = ["Disabled"] + self.devices
                if mic and mic in mic_options:
                    self.mic_combo.set(mic)
                    
                sys_aud = s.get('system_audio', fallback=None)
                sys_options = ["Disabled"] + self.devices
                if sys_aud and sys_aud in sys_options:
                    self.sys_combo.set(sys_aud)

    def save_settings(self):
        """Save current settings to ScreenGrabHD.cnf."""
        config = configparser.ConfigParser()
        config['Settings'] = {
            'resolution': self.resolution.get(),
            'microphone': self.mic_combo.get(),
            'system_audio': self.sys_combo.get()
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                config.write(f)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def start_region_selector(self):
        """Step 2: Fullscreen Region Selector"""
        # --- Save settings before proceeding ---
        self.save_settings()
        
        res = self.resolution.get()
        w, h = map(int, res.split('x'))
        mic = self.mic_combo.get()
        sys_audio = self.sys_combo.get()
        
        # Process "Disabled" states
        mic_dev = None if mic == "Disabled" else mic
        sys_audio_dev = None if sys_audio == "Disabled" else sys_audio
        
        # Validation: Ensure at least one audio source is selected
        if not mic_dev and not sys_audio_dev:
            messagebox.showerror("Error", "Both Microphone and System Audio are disabled.\nPlease select at least one audio source.")
            return
            
        if mic_dev and sys_audio_dev and mic_dev == sys_audio_dev:
            messagebox.showerror("Error", "Microphone and System Audio cannot be the same device.")
            return
            
        self.settings = {
            "width": w,
            "height": h,
            "mic": mic_dev,
            "sys_audio": sys_audio_dev
        }
        
        self.clear_window()
        self.root.title("Select Recording Region")
        
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        # Manually set geometry to screen size to act as fullscreen
        self.root.geometry(f"{screen_w}x{screen_h}+0+0")
        self.root.overrideredirect(True)
        self.root.attributes('-alpha', 0.35)
        self.root.configure(bg='black')
        self.root.attributes('-topmost', True)
        
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0, cursor='fleur')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.pos = {"x": (screen_w - w) // 2, "y": (screen_h - h) // 2}
        self.width = w
        self.height = h
        
        self.rect_id = self.canvas.create_rectangle(
            self.pos["x"], self.pos["y"],
            self.pos["x"] + w, self.pos["y"] + h,
            outline='#00ff00', width=4, dash=(10, 4)
        )
        
        self.label_id = self.canvas.create_text(
            self.pos["x"] + w // 2,
            self.pos["y"] + h // 2,
            text=f"{w}×{h} (16:9)",
            fill='white', font=('Segoe UI', 18, 'bold')
        )
        
        self.drag_data = {"x": 0, "y": 0}
        
        self.canvas.bind('<ButtonPress-1>', self.on_drag_start)
        self.canvas.bind('<B1-Motion>', self.on_drag_motion)
        self.root.bind('<Return>', lambda e: self.confirm_region())
        self.root.bind('<Escape>', lambda e: self.cancel_region())
        
        self.root.focus_force()

    def on_drag_start(self, event):
        self.drag_data["x"] = event.x - self.pos["x"]
        self.drag_data["y"] = event.y - self.pos["y"]

    def on_drag_motion(self, event):
        new_x = event.x - self.drag_data["x"]
        new_y = event.y - self.drag_data["y"]
        
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        new_x = max(0, min(new_x, screen_w - self.width))
        new_y = max(0, min(new_y, screen_h - self.height))
        
        self.pos["x"], self.pos["y"] = new_x, new_y
        self.canvas.coords(self.rect_id, new_x, new_y, new_x + self.width, new_y + self.height)
        self.canvas.coords(self.label_id, new_x + self.width // 2, new_y + self.height // 2)

    def confirm_region(self):
        self.region = (self.pos["x"], self.pos["y"], self.width, self.height)
        self.start_recording()

    def cancel_region(self):
        self.root.destroy()

    def start_recording(self):
        """Step 3: Recording Status Window"""
        self.clear_window() # Restores window decorations
        self.root.title("Recording...")
        self.root.geometry("300x150")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.root.winfo_screenheight() // 2) - (150 // 2)
        self.root.geometry(f"+{x}+{y}")
        
        tk.Label(self.root, text="🔴 Recording in progress...", font=("Segoe UI", 12, "bold"), fg="red").pack(pady=20)
        
        self.output_filename = get_output_filename()
        tk.Label(self.root, text=f"Saving to:\n{self.output_filename}", font=("Segoe UI", 9), wraplength=280).pack(pady=5)
        
        # Build FFmpeg Command Dynamically
        ox, oy, vw, vh = self.region
        mic_device = self.settings["mic"]
        sys_device = self.settings["sys_audio"]
        ffmpeg_path = self.ffmpeg_path
        
        cmd = [ffmpeg_path, "-y"]
        
        has_mic = bool(mic_device)
        has_sys = bool(sys_device)
        
        # 1. Add Audio Inputs
        if has_mic:
            cmd.extend(["-f", "dshow", "-i", f"audio={mic_device}"])
        if has_sys:
            cmd.extend(["-f", "dshow", "-i", f"audio={sys_device}"])
            
        # 2. Add Video Input
        cmd.extend([
            "-f", "gdigrab", "-framerate", "24",
            "-offset_x", str(ox), "-offset_y", str(oy),
            "-video_size", f"{vw}x{vh}", "-i", "desktop"
        ])
        
        # 3. Determine Stream Indices for Mapping
        input_idx = 0
        mic_idx = -1
        sys_idx = -1
        
        if has_mic:
            mic_idx = input_idx
            input_idx += 1
        if has_sys:
            sys_idx = input_idx
            input_idx += 1
            
        vid_idx = input_idx
        
        # 4. Map Streams & Apply Filters based on enabled devices
        if has_mic and has_sys:
            cmd.extend([
                "-filter_complex", 
                f"[{mic_idx}:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a0];"
                f"[{sys_idx}:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a1];"
                f"[a0][a1]amerge=inputs=2[a]",
                "-map", f"{vid_idx}:v", "-map", "[a]",
                "-c:a", "aac", "-b:a", "192k"
            ])
        elif has_mic:
            cmd.extend([
                "-map", f"{vid_idx}:v", "-map", f"{mic_idx}:a",
                "-c:a", "aac", "-b:a", "128k"
            ])
        elif has_sys:
            cmd.extend([
                "-map", f"{vid_idx}:v", "-map", f"{sys_idx}:a",
                "-c:a", "aac", "-b:a", "128k"
            ])
            
        # 5. Video Encoding Settings
        cmd.extend([
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-ac", "2",
            "-movflags", "+faststart",
            self.output_filename
        ])
            
        # Start Process
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            
        self.process = subprocess.Popen(
            cmd, 
            stdin=subprocess.PIPE,   # <--- CRITICAL: Allows us to send 'q' to FFmpeg
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            creationflags=creationflags
        )
        
        # Stop Button
        tk.Button(self.root, text="Stop Recording", command=self.stop_recording, bg="#f44336", fg="white", font=("Segoe UI", 10, "bold"), width=15).pack(pady=10)
        
        self.root.protocol("WM_DELETE_WINDOW", self.stop_recording)
        self.check_process()
        
    def stop_recording(self):
        """Gracefully stops FFmpeg and updates UI."""
        if self.process.poll() is None:
            try:
                # Send 'q' to FFmpeg's stdin. This is the official, 100% reliable way 
                # to tell FFmpeg to stop recording and finalize the MP4 file.
                self.process.stdin.write(b'q')
                self.process.stdin.flush()
            except Exception:
                # Fallback to force kill if stdin is broken
                self.process.terminate()
                    
        # Update UI to show it's stopping
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.DISABLED, text="Stopping...")
            elif isinstance(widget, tk.Label) and "Recording in progress" in widget.cget("text"):
                widget.config(text="⏳ Finalizing video...", fg="orange")
            
    def check_process(self):
        """Checks if FFmpeg has finished."""
        if not self.root.winfo_exists():
            return
        if self.process.poll() is not None:
            if self.root.winfo_exists():
                retcode = self.process.returncode
                if retcode == 0:
                    messagebox.showinfo("Success", f"✅ Recording saved as:\n{self.output_filename}", parent=self.root)
                else:
                    messagebox.showerror("Error", f"❌ FFmpeg exited with code {retcode}", parent=self.root)
                self.root.destroy()
        else:
            self.root.after(500, self.check_process)

def main():
    root = tk.Tk()
    app = ScreenGrabApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
