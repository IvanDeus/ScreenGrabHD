# ScreenGrabHD.py
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
import os

def get_ffmpeg_path():
    """Return ffmpeg path relative to current working directory"""
    cwd = os.getcwd()
    ffmpeg_path = os.path.join(cwd, "bin", "ffmpeg.exe")    
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    # Fallback: try common locations or PATH
    possible_paths = [
        "ffmpeg",   
        os.path.join(cwd, "ffmpeg.exe"),
        os.path.expanduser(r"~\Downloads\ffmpeg\bin\ffmpeg.exe"),
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run(
                [path, "-version"], 
                capture_output=True, 
                text=True, 
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode == 0:
                return path
        except:
            continue
    
    messagebox.showerror(
        "Error", 
        f"ffmpeg.exe not found!\n\n"
        f"Expected location:\n{ffmpeg_path}\n\n"
        "Please make sure 'bin' folder is in the current directory."
    )
    sys.exit(1)

def get_audio_devices(ffmpeg_path):
    """Parse ffmpeg dshow device list for audio capture devices."""
    try:
        result = subprocess.run(
            [ffmpeg_path, "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            capture_output=True, 
            encoding='utf-8', 
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        lines = result.stderr.splitlines()
        devices = []
        
        for line in lines:
            if '(audio)' in line and 'Alternative name' not in line:
                parts = line.split('"')
                if len(parts) >= 2:
                    devices.append(parts[1])
                    
        return devices
    except Exception as e:
        messagebox.showerror("Error", f"Failed to list audio devices: {e}")
        sys.exit(1)

def get_output_filename():
    """Generate a unique output filename by appending _01, _02, etc., if the file already exists."""
    base_name = "ScreenGrabHD_recording"
    ext = ".mp4"
    filename = f"{base_name}{ext}"
    counter = 1
    
    # Check if the file exists, if so, increment the counter
    while os.path.exists(filename):
        filename = f"{base_name}_{counter:02d}{ext}"
        counter += 1
        
    return filename

class FixedHDRegionSelector:
    def __init__(self, width=1280, height=720):
        # Set dimensions dynamically based on arguments
        self.CAPTURE_W = width
        self.CAPTURE_H = height

        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.35)
        self.root.configure(bg='black')
        self.root.title(f"Drag {self.CAPTURE_W}x{self.CAPTURE_H} frame | ENTER = Confirm | ESC = Cancel")
        self.root.overrideredirect(True)

        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0, cursor='fleur')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.current_x = (screen_w - self.CAPTURE_W) // 2
        self.current_y = (screen_h - self.CAPTURE_H) // 2

        self.rect_id = self.canvas.create_rectangle(
            self.current_x, self.current_y,
            self.current_x + self.CAPTURE_W, self.current_y + self.CAPTURE_H,
            outline='#00ff00', width=4, dash=(10, 4)
        )

        self.label_id = self.canvas.create_text(
            self.current_x + self.CAPTURE_W // 2,
            self.current_y + self.CAPTURE_H // 2,
            text=f"{self.CAPTURE_W}×{self.CAPTURE_H} (16:9)",
            fill='white', font=('Segoe UI', 18, 'bold')
        )

        self.drag_start_x = self.drag_start_y = 0

        self.canvas.bind('<ButtonPress-1>', self.on_drag_start)
        self.canvas.bind('<B1-Motion>', self.on_drag_motion)
        self.root.bind('<Return>', lambda e: self.confirm())
        self.root.bind('<Escape>', lambda e: self.root.destroy())

        self.root.focus_force()
        self.result = None
        self.root.mainloop()

    def on_drag_start(self, event):
        self.drag_start_x = event.x - self.current_x
        self.drag_start_y = event.y - self.current_y

    def on_drag_motion(self, event):
        new_x = event.x - self.drag_start_x
        new_y = event.y - self.drag_start_y

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        new_x = max(0, min(new_x, screen_w - self.CAPTURE_W))
        new_y = max(0, min(new_y, screen_h - self.CAPTURE_H))

        self.current_x, self.current_y = new_x, new_y
        self.canvas.coords(self.rect_id, new_x, new_y,
                           new_x + self.CAPTURE_W, new_y + self.CAPTURE_H)
        self.canvas.coords(self.label_id,
                           new_x + self.CAPTURE_W // 2,
                           new_y + self.CAPTURE_H // 2)

    def confirm(self):
        self.result = (self.current_x, self.current_y, self.CAPTURE_W, self.CAPTURE_H)
        self.root.destroy()


def main():
    ffmpeg_path = get_ffmpeg_path()
    print(f"Using FFmpeg: {ffmpeg_path}")

    # === Resolution Selection ===
    print("\n📺 Select Recording Resolution:")
    print(" [1] HD (1280x720) - Default")
    print(" [2] Full HD (1920x1080)")
    
    while True:
        res_choice = input("Select resolution [1/2] (default 1): ").strip()
        if res_choice == '2':
            capture_w, capture_h = 1920, 1080
            break
        elif res_choice in ['1', '']:
            capture_w, capture_h = 1280, 720
            break
        else:
            print("Invalid selection. Please enter 1 or 2.")

    # === Audio Device Selection ===
    devices = get_audio_devices(ffmpeg_path)
    if not devices:
        messagebox.showerror("Error", "No audio capture devices found")
        return

    print("\n🎤 Available Audio Devices:")
    for i, d in enumerate(devices):
        print(f" [{i}] {d}")

    while True:
        try:
            choice = input(f"\nSelect device [0-{len(devices)-1}]: ").strip()
            idx = int(choice)
            if 0 <= idx < len(devices):
                audio_device = devices[idx]
                break
            print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")

    # === Region Selection ===
    print(f"\n🖥️  Opening region selector for {capture_w}x{capture_h}... Drag the green frame.")
    selector = FixedHDRegionSelector(width=capture_w, height=capture_h)
    if not selector.result:
        print("Cancelled by user.")
        return

    ox, oy, vw, vh = selector.result
    print(f"✅ Selected: {vw}x{vh} at ({ox}, {oy}) | Audio: {audio_device}")

    # === Output Filename ===
    output_filename = get_output_filename()

    # === FFmpeg Recording ===
    cmd = [
        ffmpeg_path, "-y",
        "-f", "dshow", "-i", f"audio={audio_device}",
        "-f", "gdigrab", "-framerate", "30",
        "-offset_x", str(ox), "-offset_y", str(oy),
        "-video_size", f"{vw}x{vh}", "-i", "desktop",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output_filename
    ]

    print(f"\n🔴 Recording started... Saving to: {output_filename}")
    print("Press 'q' in this terminal to stop.\n")
    try:
        process = subprocess.run(cmd, check=False)
        if process.returncode == 0:
            print(f"\n✅ Recording saved as {output_filename}")
        else:
            print(f"\n❌ FFmpeg exited with code {process.returncode}")
    except KeyboardInterrupt:
        print("\nRecording stopped by user.")


if __name__ == "__main__":
    main()
