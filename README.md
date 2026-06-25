# ScreenGrabHD
A lightweight, portable Windows screen recorder built with Python and FFmpeg.

ScreenGrabHD lets you position a fixed 16:9 recording frame anywhere on your screen, capture microphone and/or system audio, and save directly to a high-quality MP4 file with minimal setup.

Perfect for creating tutorials, software demonstrations, online lessons, and quick screen recordings without the complexity of full-featured video editing suites.

## Features

* 🎥 Fixed 16:9 recording region
* 📺 HD (1280×720) and Full HD (1920×1080) recording modes
* 🎙 Record microphone audio
* 🔊 Record system audio (Stereo Mix or compatible loopback device)
* 🎚 Simultaneous microphone + system audio recording
* 📦 Portable setup (no installation required)
* ⚡ Powered by FFmpeg for reliable MP4 output
* 💾 Automatic filename numbering to prevent overwriting recordings
* ⚙ Remembers your previously selected settings

## Example Output Size

Typical recording size:

| Resolution | Approximate Size   |
| ---------- | ------------------ |
| 1280×720   | ~1 GB per hour     |
| 1920×1080  | ~1.5–2 GB per hour |

Actual file size depends on screen activity and content complexity.

---

## Requirements

### Windows

* Windows 10 or Windows 11
* Python 3.14 or newer
* FFmpeg

### Download Python

Download the latest version of Python:

[https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

### Download FFmpeg

#### For Windows x64 (AMD64)

Download:

[https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

Recommended package:

`ffmpeg-git-essentials`

#### For Windows ARM64

Download:

[https://github.com/tordona/ffmpeg-win-arm64/releases](https://github.com/tordona/ffmpeg-win-arm64/releases)

---

## Installation

1. Download and extract FFmpeg.
2. Place `ScreenGrabHD.py` inside the FFmpeg directory.

Your folder structure should look like:

```text
ffmpeg/
├── bin/
│   └── ffmpeg.exe
├── ScreenGrabHD.py
└── ...
```

Alternatively, you may place `ffmpeg.exe` in your system PATH.

---

## Enabling System Audio Recording

To record Windows system audio together with your microphone:

1. Open **Settings**
2. Navigate to:

```text
System → Sound → All Sound Devices
```

3. Enable **Stereo Mix** (if available)

Depending on your sound card manufacturer, the device may also appear as:

* Stereo Mix
* What U Hear
* Wave Out Mix
* Loopback Device

If your hardware does not provide a Stereo Mix device, you can use a virtual audio cable solution.

---

## Usage

Run the application:

```bash
python ScreenGrabHD.py
```

### Recording Workflow

1. Select recording resolution
2. Select microphone device (optional)
3. Select system audio device (optional)
4. Click **Select Region & Record**
5. Drag the recording frame to the desired location
6. Press **Enter** to begin recording
7. Click **Stop Recording** when finished

Recorded videos are saved as:

```text
ScreenGrabHD_recording.mp4
ScreenGrabHD_recording_01.mp4
ScreenGrabHD_recording_02.mp4
...
```

---

## Audio Recording Notes

* At least one audio source must be selected.
* Microphone and system audio cannot use the same device.
* When both microphone and system audio are enabled, ScreenGrabHD automatically merges them into a single audio track.

---

## Configuration

ScreenGrabHD automatically saves your settings in:

```text
ScreenGrabHD.cnf
```

The following preferences are remembered between sessions:

* Recording resolution
* Microphone device
* System audio device

---

## Troubleshooting

### FFmpeg Not Found

Ensure one of the following exists:

```text
bin/ffmpeg.exe
```

or

```text
ffmpeg.exe
```

or FFmpeg is available in your system PATH.

### No Audio Devices Detected

Verify that:

* Your microphone is connected and enabled.
* FFmpeg can access DirectShow devices.
* Stereo Mix or a loopback device is enabled if recording system audio.

### MP4 File Is Corrupted After Forced Exit

Always stop recording using the **Stop Recording** button. ScreenGrabHD gracefully tells FFmpeg to finalize the MP4 file before closing.

---

## Built With

* Python
* Tkinter
* FFmpeg

---


2026 [ ivan deus ]
