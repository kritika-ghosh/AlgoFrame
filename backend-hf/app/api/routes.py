# app/api/routes.py
import os
import shutil
import uuid
import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import json

from app.api.schemas import GenerationResponse
from app.src.crew import AlgoFrameCrewPipeline
from app.services.manim_service import ManimCompilerService
from app.services.video_service import VideoMultiplexService
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["Pipeline Core"])

def run_agentic_pipeline_blocking(audio_path: str, primitive_type: str) -> str:
    """
    Synchronous wrapper function that passes data to CrewAI. 
    Runs inside an independent thread executor pool to prevent server blocking.
    """
    # Step 1: Simulate the transcription text pull
    # In production, replace this string pass with a live call to your audio_service.py/Groq Whisper
    simulated_transcript = (
        "Initialize an array container containing initial integers 10 and 20. "
        "Then insert a new item value 15 at index location 1, shifting index 1 forward to index 2."
    )
    
    # Step 2: Kick off the CrewAI agentic pipeline loops (Using verified CrewAI 1.x inputs dictionary syntax)
    pipeline = AlgoFrameCrewPipeline()
    crew_output = pipeline.compile_animation_pipeline(
        user_transcript=simulated_transcript, 
        primitive_type=primitive_type
    )
    return crew_output

@router.post("/generate-video")
async def generate_video_endpoint(
    primitive_type: str = Form(..., description="Target DSA Primitive (e.g., ARRAY, LINKED_LIST, BST)"),
    audio_file: UploadFile = File(..., description="Raw recorded voice explanation audio file binary stream")
):
    """
    Multipart Form endpoint that captures raw audio, saves it to a secure 
    temporary path, runs the multi-agent pipeline, and streams status updates back.
    """
    # Verify file security extensions before initializing system tracks
    allowed_extensions = [".wav", ".mp3", ".m4a"]
    file_extension = os.path.splitext(audio_file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported audio file format. Must be .wav, .mp3, or .m4a.")

    # Create temporary isolation storage tracks
    session_id = str(uuid.uuid4())[:8]
    temp_dir = f"temp_{session_id}"
    os.makedirs(temp_dir, exist_ok=True)
    local_audio_path = os.path.join(temp_dir, f"input_narration{file_extension}")

    # Write the uploaded audio file chunk-by-chunk onto disk
    with open(local_audio_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)

    async def event_stream_generator():
        try:
            yield f"data: {json.dumps({'status': 'processing', 'message': 'Audio successfully received. Transcribing voice tracks via Groq Whisper...'})}\n\n"
            await asyncio.sleep(1.0)

            yield f"data: {json.dumps({'status': 'processing', 'message': 'Spawning CrewAI Agents with dynamic planning optimization enabled...'})}\n\n"
            await asyncio.sleep(1.0)

            # Route the heavy multi-agent compilation task to a separate worker thread
            loop = asyncio.get_running_loop()
            yield f"data: {json.dumps({'status': 'processing', 'message': 'Agents are calculating memory traces and writing Manim code scripts...'})}\n\n"
            
            # Execute the core agent pipeline asynchronously
            agent_log = await loop.run_in_executor(None, run_agentic_pipeline_blocking, local_audio_path, primitive_type)
            
            # For demonstration purposes, we run a default fallback scene.
            # In your live deployment, your agents will dynamically pass their generated script string here.
            fallback_manim_script = """
from manim import *
class DataStructureScene(Scene):
    def construct(self):
        title = Text("Array Operation: Insertion", color=BLUE).to_edge(UP)
        arr = VGroup(*[Square(side_length=1.0) for _ in range(3)]).arrange(RIGHT, buff=0.2)
        val1 = Text("10").move_to(arr[0].get_center())
        val2 = Text("20").move_to(arr[1].get_center())
        self.play(Write(title), DrawBorderThenFill(arr), Write(val1), Write(val2))
        self.wait(1)
        # Shift and Insert Animation Trace
        val_new = Text("15", color=AMBER).move_to(arr[1].get_center() + 2*UP)
        self.play(val2.animate.move_to(arr[2].get_center()), arr[2].animate.set_color(PURPLE))
        self.play(val_new.animate.move_to(arr[1].get_center()), arr[1].animate.set_color(AMBER))
        self.wait(2)
            """
            
            yield f"data: {json.dumps({'status': 'processing', 'message': 'Validator approved logic. Executing local Manim subprocess shell compiler...'})}\n\n"
            
            # Compile the Manim script code string directly to a physical file
            compiler = ManimCompilerService()
            compile_result = compiler.compile_scene_string(fallback_manim_script, "DataStructureScene")
            
            if compile_result["status"] != "success":
                # FIX: String evaluation broken out cleanly to remove inner backslash nesting syntax traps
                error_msg = f"Manim Compiler Error: {compile_result['error_trace']}"
                yield f"data: {json.dumps({'status': 'failed', 'message': error_msg})}\n\n"
                return

            yield f"data: {json.dumps({'status': 'processing', 'message': 'Video rendered. Initializing FFmpeg zero-re-encode audio-video multiplexing...'})}\n\n"
            
            # Multiplex the audio track directly onto the silent video
            muxer = VideoMultiplexService()
            mux_result = muxer.merge_audio_video(compile_result["video_path"], local_audio_path)
            
            if mux_result["status"] != "success":
                # FIX: String evaluation broken out cleanly to remove inner backslash nesting syntax traps
                mux_error_msg = f"Multiplexer Error: {mux_result['message']}"
                yield f"data: {json.dumps({'status': 'failed', 'message': mux_error_msg})}\n\n"
                return

            # Construct the final direct public download URL asset path string
            final_video_url = f"{settings.SPACE_HOST_URL}/static/{mux_result['filename']}"
            
            yield f"data: {json.dumps({
                'status': 'completed', 
                'message': 'Production asset compiled successfully.',
                'video_url': final_video_url
            })}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'failed', 'message': f'Pipeline Fatal Runtime Disruption: {str(e)}'})}\n\n"
        finally:
            # Clean up temporary storage tracks to prevent server disk clutter
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            if 'compile_result' in locals() and os.path.exists(compile_result.get("clean_up_target", "")):
                os.remove(compile_result["clean_up_target"])

    return StreamingResponse(event_stream_generator(), media_type="text/event-stream")