# app/services/manim_service.py
import os
import subprocess
import uuid
from app.core.config import settings

class ManimCompilerService:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def compile_scene_string(self, code_string: str, scene_class_name: str) -> dict:
        """
        Writes a raw string payload into a local file and executes Manim via a CLI subprocess.
        Returns a dictionary containing execution status and relevant media paths or errors.
        """
        session_id = str(uuid.uuid4())[:8]
        script_filename = f"scene_{session_id}.py"
        
        # Clean up code blocks if the agent wrapped the string inside markdown ticks
        if "```python" in code_string:
            code_string = code_string.split("```python")[1].split("```")[0].strip()
        elif "```" in code_string:
            code_string = code_string.split("```")[1].split("```")[0].strip()

        # Step 1: Securely write the code string onto the disk storage layer
        with open(script_filename, "w") as f:
            f.write(code_string)

        try:
            # Step 2: Build compilation command strings using configured quality profiles
            # e.g., 'manim -ql -v WARNING scene_123.py MySceneClassName --media_dir ./output'
            command = [
                "manim",
                settings.MANIM_QUALITY_FLAG,
                "-v", "WARNING",
                script_filename,
                scene_class_name,
                "--media_dir", f"./{self.output_dir}"
            ]

            # Execute code compilation loop inside a isolated terminal subprocess shell
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=180 # Set strict execution timeout limits to protect server resources
            )

            # Step 3: Parse execution statuses
            if process.returncode == 0:
                # Trace where Manim writes compiled mp4 assets based on standard file tree structures:
                # output/videos/scene_uuid/480p30/MySceneClassName.mp4
                expected_output_path = os.path.join(
                    self.output_dir, "videos", f"scene_{session_id}", "480p30", f"{scene_class_name}.mp4"
                )
                
                return {
                    "status": "success",
                    "video_path": expected_output_path,
                    "clean_up_target": script_filename,
                    "log": process.stdout
                }
            else:
                return {
                    "status": "failed",
                    "error_trace": process.stderr or process.stdout,
                    "clean_up_target": script_filename
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "error_trace": "Process runtime exception: Code execution loop exceeded 30s timeout threshold.",
                "clean_up_target": script_filename
            }
        except Exception as e:
            return {
                "status": "failed",
                "error_trace": f"System runtime exception: {str(e)}",
                "clean_up_target": script_filename
            }