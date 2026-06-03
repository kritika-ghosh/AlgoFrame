# test_swap_client.py
import requests
import os

def test_text_synthesis():
    url = "http://127.0.0.1:7860/api/generate-video"
    
    # 1. Your refined algorithmic roadmap
    algorithm_steps = """
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

    # 2. Package into the payload
    # Note: Ensure the key 'explanation_text' matches what your API expects in the Form
    payload = {
        "primitive_type": "tree",
        "explanation_text": algorithm_steps
    }
    
    print("Sending algorithmic logic roadmap to AlgoFrame Core Engine...")
    print("============================================================")
    
    try:
        response = requests.post(url, data=payload, timeout=300)
        
        if response.status_code == 200:
            output_filename = "swap_animation_production.mp4"
            with open(output_filename, "wb") as f:
                f.write(response.content)
            print(f"SUCCESS! Saved to: {os.path.abspath(output_filename)}")
        else:
            print(f"FAILURE: Status {response.status_code}")
            print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"Transport failure: {e}")

if __name__ == "__main__":
    test_text_synthesis()