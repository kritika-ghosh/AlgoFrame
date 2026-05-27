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
import litellm 

router = APIRouter(prefix="/api", tags=["Synthesis Core"])

TEMP_DIR = "temp_processing"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/generate-video")
def generate_video_pipeline(
    primitive_type: str = Form(..., description="The underlying data structure or algorithm type (e.g., array, tree, graph)"),
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
            print(f"⚙️ [PROCESSING]: Text file received. Parsing file string blocks...")
            with open(temp_file_path, "r", encoding="utf-8") as txt_file:
                final_text_prompt = txt_file.read()
                
        elif file_ext in [".wav", ".mp3", ".m4a", ".mp4"]:
            print(f"⚙️ [PROCESSING]: Audio successfully received. Transcribing voice tracks via Groq Whisper...")
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
        print(f"⚙️ [PROCESSING]: Direct text explanation token string captured...")
        final_text_prompt = explanation_text
    else:
        raise HTTPException(status_code=400, detail="No source artifact provided. Upload an audio/text asset or supply inline text.")

    if not final_text_prompt.strip():
        raise HTTPException(status_code=400, detail="Parsed text engine prompt cannot be completely empty.")

    # ─── STEP 2: RUN THE CRITICAL AGENTIC FLOW ────────────────────────────────
    print(f"⚙️ [PROCESSING]: Spawning CrewAI Agents with dynamic planning optimization enabled...")
    try:
        crew_pipeline = AlgoFrameCrewPipeline()
        generated_manim_code = crew_pipeline.compile_animation_pipeline(
            user_transcript=final_text_prompt,
            primitive_type=primitive_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Execution Spiral Crash: {str(e)}")

    # ─── STEP 3: RUN COMPILER SUBPROCESS SHELL ────────────────────────────────
    print(f"⚙️ [PROCESSING]: Validator approved logic. Executing local Manim subprocess shell compiler...")
    
    # BULLETPROOF MARKDOWN STRIPPER
    # Safely slices out the code content and discards the markdown fence headers/footers
    if "```python" in generated_manim_code:
        generated_manim_code = generated_manim_code.split("```python")[1].split("```")[0]
    elif "```" in generated_manim_code:
        generated_manim_code = generated_manim_code.split("```")[1].split("```")[0]
    
    generated_manim_code = generated_manim_code.strip()
    # ─── BYPASS LATEX ENVIRONMENT DEPENDENCIES ─────────────────────────────
    # Forces Manim to use the local Pango system font engine instead of LaTeX
    generated_manim_code = generated_manim_code.replace("Tex(", "Text(")
    generated_manim_code = generated_manim_code.replace("MathTex(", "Text(")
    # ───────────────────────────────────────────────────────────────────────
    scene_filename = f"scene_{session_id}.py"
    with open(scene_filename, "w", encoding="utf-8") as f:
        f.write(generated_manim_code)

    try:
        compile_cmd = ["manim", "-ql", scene_filename]
        subprocess_result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=120)
        
        if subprocess_result.returncode != 0:
            print(f"Manim Compiler Trace: {subprocess_result.stderr}")
            raise HTTPException(status_code=500, detail="Manim internal scene execution validation fault.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manim Subprocess Engine Failure: {str(e)}")

    # ─── STEP 4: SEAMLESS AUDIO-VIDEO MULTIPLEX PASS ─────────────────────────
    predicted_silent_video = os.path.normpath(f"output/videos/scene_{session_id}/480p30/ArrayInitialization.mp4")

    if saved_audio_path:
        print(f"⚙️ [PROCESSING]: Video rendered. Initializing FFmpeg zero-re-encode audio-video multiplexing...")
        multiplexer = VideoMultiplexService()
        merge_result = multiplexer.merge_audio_video(
            silent_video_path=predicted_silent_video,
            raw_audio_path=saved_audio_path
        )
        
        if merge_result["status"] == "error":
            raise HTTPException(status_code=500, detail=f"Multiplexer Failure: {merge_result['message']}")
        
        final_video_target = merge_result["final_asset_path"]
    else:
        print(f"⚙️ [PROCESSING]: Video rendered. Text intake modality confirmed — skipping media multiplexer track...")
        multiplexer = VideoMultiplexService()
        fallback_check = multiplexer.merge_audio_video(predicted_silent_video, "dummy_non_existent.wav")
        
        if os.path.exists(fallback_check.get("final_asset_path", "")):
             final_video_target = fallback_check["final_asset_path"]
        else:
             final_video_target = predicted_silent_video
             for root, _, files in os.walk("."):
                 if f"scene_{session_id}" in root:
                     mp4s = [f for f in files if f.endswith(".mp4")]
                     if mp4s:
                         final_video_target = os.path.join(root, mp4s[0])
                         break

    # ─── STEP 5: FILE RESTORATION CLEANUP ─────────────────────────────────────
    if os.path.exists(scene_filename):
        os.remove(scene_filename)
    if saved_audio_path and os.path.exists(saved_audio_path):
        os.remove(saved_audio_path)

    if not os.path.exists(final_video_target):
        raise HTTPException(status_code=404, detail="Final compiled video production target missing from drive container.")

    return FileResponse(
        path=final_video_target, 
        media_type="video/mp4", 
        filename=os.path.basename(final_video_target)
    )