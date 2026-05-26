# Services Layer (Tool Drivers & Utilities)
Wrappers handling lower-level system actions and microservice integrations:
- audio_service.py: Interfaces with Groq Whisper for rapid voice transcription.
- manim_service.py: Command-line subprocess runner that executes and compiles raw Manim scripts.
- video_service.py: High-performance FFmpeg command multiplexer (stitches audio to video streams without re-encoding).
- storage_service.py: Coordinates temporary video storage arrays and asset persistence paths.