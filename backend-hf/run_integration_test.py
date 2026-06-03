# run_integration_test.py
import subprocess
import time
import requests
import os

print("Starting local FastAPI server in background...")
server_process = subprocess.Popen(
    [".venv/Scripts/python", "-m", "uvicorn", "app.main:app", "--port", "7862", "--host", "127.0.0.1"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait for server to boot
time.sleep(8)

url = "http://127.0.0.1:7862/api/generate-video"
algorithm_steps = """
Binary Tree BFS/Level-Order Traversal:
Step 1: Initialize a binary tree structure. The root node is 10. Node 10 has left child 5 and right child 15. Node 5 has left child 2 and right child 7. Node 15 has left child 12 and right child 20.
Step 2: Start BFS level-order traversal by visiting node 10.
Step 3: Continue level 1 by visiting left child 5.
Step 4: Visit right child 15.
Step 5: Move to level 2 by visiting child 2.
Step 6: Visit child 7.
Step 7: Visit child 12.
Step 8: Visit child 20.
"""

payload = {
    "primitive_type": "tree",
    "explanation_text": algorithm_steps
}

print("Sending algorithmic request to local server...")
try:
    response = requests.post(url, data=payload, timeout=240)
    print("Response Status Code:", response.status_code)
    if response.status_code == 200:
        filename = "integration_test_output.mp4"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"SUCCESS! Saved video to: {os.path.abspath(filename)}")
        print("Video file size in bytes:", os.path.getsize(filename))
    else:
        print("FAILURE:", response.text)
except Exception as e:
    print("Request error:", e)
finally:
    print("Stopping local FastAPI server...")
    server_process.terminate()
    server_process.wait()
    print("Server stopped.")
