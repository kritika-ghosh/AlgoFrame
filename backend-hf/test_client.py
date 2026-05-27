# test_client.py
import os
import wave
import struct
import httpx
import json

def create_dummy_wav(filename="dummy_test.wav", duration_seconds=1):
    """Generates a brief, valid blank audio file to satisfy multipart form requirements."""
    sample_rate = 44100
    num_samples = sample_rate * duration_seconds
    
    with wave.open(filename, "w") as wav_file:
        wav_file.setparams((1, 2, sample_rate, num_samples, "NONE", "not compressed"))
        for _ in range(num_samples):
            wav_file.writeframes(struct.pack('h', 0))
    print(f" -> Generated temporary audio boundary file: {filename}")

def run_local_pipeline_test():
    server_url = "http://127.0.0.1:7860/api/generate-video"
    dummy_audio = "dummy_test.wav"
    
    # 1. Initialize temporary boundary asset files
    create_dummy_wav(dummy_audio, duration_seconds=1)
    
    payload_data = {
        "primitive_type": "ARRAY" 
    }
    
    print(f" -> Injecting streaming request parameters to endpoint: {server_url}")
    print(" -> Awaiting Agentic Execution Stream updates...\n" + "="*60)
    
    try:
        # Open file handler inside an absolute contextual container pass
        with open(dummy_audio, "rb") as f:
            file_payload = {
                "audio_file": (dummy_audio, f, "audio/wav")
            }
            
            # Connect via an HTTP client supporting Live Event-Stream reading
            with httpx.Client(timeout=60.0) as client:
                with client.stream("POST", server_url, data=payload_data, files=file_payload) as response:
                    if response.status_code != 200:
                        print(f"Server returned an error status protocol: {response.status_code}")
                        return
                    
                    # Read incoming server lines sequentially as they stream in
                    for line in response.iter_lines():
                        if line.startswith("data: "):
                            clean_line = line.replace("data: ", "").strip()
                            event_data = json.loads(clean_line)
                            
                            status = event_data.get("status")
                            message = event_data.get("message", "")
                            
                            if status == "processing":
                                print(f" ⚙️ [PROCESSING]: {message}")
                            elif status == "completed":
                                print("\n" + "="*60)
                                print(f" 🎉 [SUCCESS]: {message}")
                                print(f" 📦 Final Asset Video URL: {event_data.get('video_url')}")
                            elif status == "failed":
                                print(f" ❌ [FAILURE]: {message}")
                                
    except Exception as e:
        print(f"Transport layer testing anomaly: {str(e)}")
    finally:
        # File streams are fully closed here, making deletion 100% safe on Windows
        if os.path.exists(dummy_audio):
            try:
                os.remove(dummy_audio)
                print("\n -> Cleaned up temporary audio files.")
            except Exception as e:
                print(f"\n -> Warning: Local disk asset cleanup trace discrepancy: {str(e)}")

if __name__ == "__main__":
    run_local_pipeline_test()