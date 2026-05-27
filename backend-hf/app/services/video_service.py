# app/services/video_service.py
import os
import subprocess
import uuid

class VideoMultiplexService:
    def __init__(self, final_dir: str = "output"):
        self.final_dir = final_dir
        os.makedirs(self.final_dir, exist_ok=True)

    def merge_audio_video(self, silent_video_path: str, raw_audio_path: str) -> dict:
        """
        Uses an FFmpeg stream copy subprocess configuration to multiplex audio and video tracks.
        Avoids re-encoding individual pixels to complete the task in fractions of a second.
        """
        # 1. Normalize paths to protect against cross-platform slash variation
        normalized_video = os.path.normpath(silent_video_path)
        raw_audio_path = os.path.normpath(raw_audio_path)

        parts = normalized_video.split(os.sep)
        resolved_video_path = None

        # 2. Extract the specific scene script hash token (e.g., "scene_deda2765")
        scene_dir_name = None
        for part in parts:
            if "scene_" in part:
                scene_dir_name = part
                break

        # 3. FAST ISOLATED SEARCH
        # Target only the exact scene directory folder path, eliminating slow .venv traversal loops
        if scene_dir_name and "output" in parts:
            out_idx = parts.index("output")
            sub_parts = parts[out_idx:]
            
            for root_prefix in [".", "app"]:
                for i, p in enumerate(sub_parts):
                    if "scene_" in p:
                        # Reconstruct explicit path directly to target folder (e.g., "./output/videos/scene_deda2765")
                        scene_folder = os.path.join(root_prefix, *sub_parts[:i+1])
                        
                        if os.path.exists(scene_folder):
                            # Scan exclusively inside this directory for the target file
                            for sub_root, _, sub_files in os.walk(scene_folder):
                                mp4s = [f for f in sub_files if f.endswith(".mp4")]
                                if mp4s:
                                    resolved_video_path = os.path.join(sub_root, mp4s[0])
                                    break
                        break
                if resolved_video_path:
                    break

        # 4. Apply the discovered path override or fallback to original
        if resolved_video_path:
            print(f"🎯 [Path Sniffer Success] Located actual video asset container at: {resolved_video_path}")
            silent_video_path = resolved_video_path
        else:
            silent_video_path = normalized_video

        # Final asset visibility checks before handing off to FFmpeg pipelines
        if not os.path.exists(silent_video_path):
            return {"status": "error", "message": f"Source asset not found: {silent_video_path}"}
        if not os.path.exists(raw_audio_path):
            return {"status": "error", "message": f"Audio track layer not found: {raw_audio_path}"}

        output_filename = f"final_production_{uuid.uuid4().hex[:8]}.mp4"
        destination_path = os.path.join(self.final_dir, output_filename)

        try:
            command = [
                "ffmpeg", "-y",
                "-i", silent_video_path,
                "-i", raw_audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                destination_path
            ]

            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=15
            )

            if process.returncode == 0 and os.path.exists(destination_path):
                return {
                    "status": "success",
                    "final_asset_path": destination_path,
                    "filename": output_filename
                }
            else:
                return {
                    "status": "error",
                    "message": f"FFmpeg operational crash: {process.stderr or process.stdout}"
                }

        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "FFmpeg execution exceeded structural timeout bounds."}
        except Exception as e:
            return {"status": "error", "message": f"Media stream multiplexer internal runtime fault: {str(e)}"}