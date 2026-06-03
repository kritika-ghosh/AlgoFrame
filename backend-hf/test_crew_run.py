# test_crew_run.py
import os
from dotenv import load_dotenv

load_dotenv()

# Set up API keys
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "")

import app.main  # Import app.main to register litellm patch!
from app.src.crew import AlgoFrameCrewPipeline

user_prompt = """
Binary Tree BFS/Level-Order Traversal:
Step 1: Initialize a binary tree structure. The root node is 10. Node 10 has left child 5 and right child 15. Node 5 has left child 2 and right child 7. Node 15 has left child 12 and right child 20.
Step 2: Initialize a queue and enqueue the root node (10).
Step 3: Dequeue node 10 and record it as visited. Enqueue its children (5 and 15).
Step 4: Dequeue node 5 and record it as visited. Enqueue its children (2 and 7).
Step 5: Dequeue node 15 and record it as visited. Enqueue its children (12 and 20).
Step 6: Dequeue node 2 and record it as visited. No children to enqueue.
Step 7: Dequeue node 7 and record it as visited. No children to enqueue.
Step 8: Dequeue node 12 and record it as visited. No children to enqueue.
Step 9: Dequeue node 20 and record it as visited. No children to enqueue.
"""

print("Running pipeline...")
pipeline = AlgoFrameCrewPipeline()
res = pipeline.compile_animation_pipeline(
    user_transcript=user_prompt,
    primitive_type="tree"
)
print("=== PIPELINE OUTPUT ===")
print(res)
