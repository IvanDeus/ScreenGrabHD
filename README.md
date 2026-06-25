# ScreenGrabHD
ScreenGrabHD is a lightweight Windows screen recorder that lets you drag a fixed HD frame (16:9) anywhere on your screen, select an audio input device, and record directly to a high-quality MP4 file using FFmpeg. Simple, fast, and focused on clean HD recordings with minimal setup.

## Prereq
- Get [Python 3.14](https://www.python.org/downloads/windows/) for Windows 
- Get [FFMPEG ffmpeg-git-essentials](https://www.gyan.dev/ffmpeg/builds/) fow Windows AMD64
- Get [FFMPEG ffmpeg-win-arm64](https://github.com/tordona/ffmpeg-win-arm64/releases) for Windows ARM64

## Set-up

Download and unpack FFMPEG, and put ScreenGrabHD.py script inside FFMPEG directory.

To capture both Windows System audio and Microphone, go to control panel: System - Sound - All sound devices and enable **Stereo Mix**.


## Run

Simply click on a ScreenGrabHD.py script or run in terminal:

```
python ScreenGrabHD.py
```

2026 [ ivan deus ]
