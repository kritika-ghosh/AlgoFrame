# app/api/routes.py
import os
import shutil
import uuid
import subprocess
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse

# Core Pipeline Integrations
from app.src.crew import AlgoFrameCrewPipeline
from app.services.video_service import VideoMultiplexService
from app.services.critic_service import VisualCriticService
import litellm 

router = APIRouter(prefix="/api", tags=["Synthesis Core"])

TEMP_DIR = "temp_processing"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/generate-video")
def generate_video_pipeline(
    primitive_type: Optional[str] = Form(None, description="The underlying data structure or algorithm type (e.g., array, tree, graph)"),
    explanation_text: Optional[str] = Form(None, description="Raw explanation string if inputting text directly"),
    file: Optional[UploadFile] = File(None, description="Uploaded Audio file (.wav/.mp4) or Text file (.txt)")
):
    session_id = uuid.uuid4().hex[:8]
    final_text_prompt = ""
    saved_audio_path = None

    # ─── STEP 1: RESOLVE INTAKE MODALITY ──────────────────────────────────────
    if file:
        file_ext = os.path.splitext(file.filename)[1].lower()
        temp_file_path = os.path.join(TEMP_DIR, f"input_{session_id}{file_ext}")
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if file_ext == ".txt":
            print(f"[PROCESSING]: Text file received. Parsing file string blocks...")
            with open(temp_file_path, "r", encoding="utf-8") as txt_file:
                final_text_prompt = txt_file.read()
                
        elif file_ext in [".wav", ".mp3", ".m4a", ".mp4"]:
            print(f"[PROCESSING]: Audio successfully received. Transcribing voice tracks via Groq Whisper...")
            saved_audio_path = temp_file_path
            try:
                with open(saved_audio_path, "rb") as audio_file:
                    transcription = litellm.transcription(
                        model="groq/whisper-large-v3",
                        file=audio_file
                    )
                final_text_prompt = transcription.get("text", "")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Groq Whisper transcription matrix failed: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format type uploaded.")
            
    elif explanation_text:
        print(f"[PROCESSING]: Direct text explanation token string captured...")
        final_text_prompt = explanation_text
    else:
        raise HTTPException(status_code=400, detail="No source artifact provided. Upload an audio/text asset or supply inline text.")

    if not final_text_prompt.strip():
        raise HTTPException(status_code=400, detail="Parsed text engine prompt cannot be completely empty.")

    # Auto-resolve primitive type if not provided or set to 'auto'
    if not primitive_type or primitive_type.lower() == "auto":
        prompt_lower = final_text_prompt.lower()
        if "tree" in prompt_lower:
            primitive_type = "tree"
        elif "graph" in prompt_lower or "vertex" in prompt_lower or "edge" in prompt_lower:
            primitive_type = "graph"
        elif "stack" in prompt_lower:
            primitive_type = "stack"
        elif "queue" in prompt_lower or "deque" in prompt_lower:
            primitive_type = "queue"
        else:
            primitive_type = "array"

    # ─── SELF-HEALING CRITIQUE MATRIX ─────────────────────────────────────────
    final_video_target = None
    critic = VisualCriticService()
    scene_filename = f"scene_{session_id}.py"

    # ─── STEP 2: RUN THE CRITICAL AGENTIC FLOW (ONCE ONLY) ────────────────────
    print(f"[PROCESSING]: Spawning CrewAI Agents to generate state-machine JSON protocol...")
    try:
        crew_pipeline = AlgoFrameCrewPipeline()
        generated_json_protocol = crew_pipeline.compile_animation_pipeline(
            user_transcript=final_text_prompt,
            primitive_type=primitive_type
        )
    except Exception as e:
        if saved_audio_path and os.path.exists(saved_audio_path):
            os.remove(saved_audio_path)
        raise HTTPException(status_code=500, detail=f"Agent Execution Spiral Crash: {str(e)}")

    # Clean up the output string to ensure it's pure JSON
    if "```json" in generated_json_protocol:
        generated_json_protocol = generated_json_protocol.split("```json")[1].split("```")[0].strip()
    elif "```" in generated_json_protocol:
        generated_json_protocol = generated_json_protocol.split("```")[1].split("```")[0].strip()
    generated_json_protocol = generated_json_protocol.strip()

    # ─── STEP 3: PARSE AND COMPILE PROTOCOL ──────────────────────────────────
    from app.visualization.compiler import ProtocolCompiler
    
    compilation_error = None
    try:
        manim_code = ProtocolCompiler.compile_json_to_manim(generated_json_protocol, scene_class_name="ArrayInitialization")
        with open(scene_filename, "w", encoding="utf-8") as f:
            f.write(manim_code)
            
        print(f"[PROCESSING]: Executing local Manim subprocess shell compiler...")
        compile_cmd = ["manim", "-ql", scene_filename, "--media_dir", "./output"]
        subprocess_result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=120)
        if subprocess_result.returncode != 0:
            compilation_error = subprocess_result.stderr
    except Exception as e:
        compilation_error = str(e)

    # ─── STEP 4: SEAMLESS AUDIO-VIDEO MULTIPLEX PASS & CRITIQUE ────────────────
    video_needs_fixing = False
    critic_feedback = ""
    discovered_video_path = None

    if not compilation_error:
        # Locate the compiled video path dynamically in the output directory
        scene_output_dir = os.path.normpath(f"output/videos/scene_{session_id}")
        predicted_silent_video = None
        if os.path.exists(scene_output_dir):
            for root, _, files in os.walk(scene_output_dir):
                mp4s = [f for f in files if f.endswith(".mp4")]
                if mp4s:
                    predicted_silent_video = os.path.normpath(os.path.join(root, mp4s[0]))
                    break
                    
        if not predicted_silent_video:
            predicted_silent_video = os.path.normpath(f"output/videos/scene_{session_id}/480p15/ArrayInitialization.mp4")
        
        if saved_audio_path:
            print(f"[PROCESSING]: Video rendered. Multiplexing audio-video...")
            multiplexer = VideoMultiplexService()
            merge_result = multiplexer.merge_audio_video(
                silent_video_path=predicted_silent_video,
                raw_audio_path=saved_audio_path
            )
            if merge_result["status"] != "error":
                discovered_video_path = merge_result["final_asset_path"]
        
        if not discovered_video_path:
            multiplexer = VideoMultiplexService()
            fallback_check = multiplexer.merge_audio_video(predicted_silent_video, "dummy_non_existent.wav")
            
            if os.path.exists(fallback_check.get("final_asset_path", "")):
                 discovered_video_path = fallback_check["final_asset_path"]
            else:
                 discovered_video_path = predicted_silent_video
                 # Fail safe walk inside output folder ONLY to prevent root-walk collision
                 if os.path.exists(scene_output_dir):
                     for root, _, files in os.walk(scene_output_dir):
                         mp4s = [f for f in files if f.endswith(".mp4")]
                         if mp4s:
                             discovered_video_path = os.path.join(root, mp4s[0])
                             break

        # ─── THE CRITICAL MULTIMODAL AUDIT GATE (ONCE ONLY) ────────────────────
        print(f"[PROCESSING]: Visual critique initiated...")
        audit_results = critic.critique_video(discovered_video_path, final_text_prompt)

        if audit_results["passed"]:
            print("[PIPELINE SUCCESS]: Visual Critic approved the animation presentation!")
            final_video_target = discovered_video_path
        else:
            print(f"[PIPELINE REJECTION]: Visual validation failed. Critique: {audit_results['feedback']}")
            video_needs_fixing = True
            critic_feedback = audit_results["feedback"]
    else:
        print(f"[COMPILATION FAILURE]: Manim syntax / structure validation failed. Error: {compilation_error}")
        video_needs_fixing = True
        critic_feedback = f"Compilation Error: {compilation_error}"

    # ─── THE DIRECT SELF-HEALING CORRECTION PASS (ONCE ONLY) ──────────────────
    if video_needs_fixing:
        print(f"[PROCESSING]: Direct self-healing correction active. Critic is fixing the JSON protocol...")
        try:
            fixed_json = critic.fix_json_protocol(
                user_prompt=final_text_prompt,
                broken_json=generated_json_protocol,
                feedback_or_error=critic_feedback
            )
            
            # Recompile fixed JSON protocol
            fixed_manim_code = ProtocolCompiler.compile_json_to_manim(fixed_json, scene_class_name="ArrayInitialization")
            with open(scene_filename, "w", encoding="utf-8") as f:
                f.write(fixed_manim_code)
                
            print(f"[PROCESSING]: Compiling fixed script via Manim...")
            compile_cmd = ["manim", "-ql", scene_filename, "--media_dir", "./output"]
            subprocess_result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=120)
            
            if subprocess_result.returncode != 0:
                print(f"[Self-Healing Failure]: Direct correction compile failed. Error: {subprocess_result.stderr}")
                # Use whatever video was discovered, or raise if empty
                if discovered_video_path and os.path.exists(discovered_video_path):
                    final_video_target = discovered_video_path
            else:
                # Merge the corrected video
                scene_output_dir = os.path.normpath(f"output/videos/scene_{session_id}")
                predicted_silent_video = None
                if os.path.exists(scene_output_dir):
                    for root, _, files in os.walk(scene_output_dir):
                        mp4s = [f for f in files if f.endswith(".mp4")]
                        if mp4s:
                            predicted_silent_video = os.path.normpath(os.path.join(root, mp4s[0]))
                            break
                            
                if not predicted_silent_video:
                    predicted_silent_video = os.path.normpath(f"output/videos/scene_{session_id}/480p15/ArrayInitialization.mp4")
                
                if saved_audio_path:
                    multiplexer = VideoMultiplexService()
                    merge_result = multiplexer.merge_audio_video(
                        silent_video_path=predicted_silent_video,
                        raw_audio_path=saved_audio_path
                    )
                    if merge_result["status"] != "error":
                        discovered_video_path = merge_result["final_asset_path"]
                        
                if not discovered_video_path:
                     if os.path.exists(scene_output_dir):
                         for root, _, files in os.walk(scene_output_dir):
                             mp4s = [f for f in files if f.endswith(".mp4")]
                             if mp4s:
                                 discovered_video_path = os.path.join(root, mp4s[0])
                                 break
                final_video_target = discovered_video_path
        except Exception as patch_e:
            print(f"[Self-healing Patch Crash]: {str(patch_e)}")
            if discovered_video_path and os.path.exists(discovered_video_path):
                final_video_target = discovered_video_path
    else:
        final_video_target = discovered_video_path

    # ─── STEP 5: FILE RESTORATION CLEANUP ─────────────────────────────────────
    if os.path.exists(scene_filename):
        os.remove(scene_filename)
    if saved_audio_path and os.path.exists(saved_audio_path):
        os.remove(saved_audio_path)

    if not final_video_target or not os.path.exists(final_video_target):
        raise HTTPException(status_code=500, detail="Engine failed to reconcile stable rendering paths within optimization thresholds.")

    return FileResponse(
        path=final_video_target, 
        media_type="video/mp4", 
        filename=os.path.basename(final_video_target)
    )