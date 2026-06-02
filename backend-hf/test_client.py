# test_swap_client.py
import requests
import os

def test_text_synthesis():
    url = "http://127.0.0.1:7860/api/generate-video"
    
    # 1. Your refined algorithmic roadmap
    algorithm_steps = """
To merge two sorted sub-arrays (Block A and Block B) into a single sorted range without allocating a new array, you must treat the array like a series of blocks that need to be "rotated" past each other.

The algorithm relies on the Array Rotation principle, which is an application of the reversal algorithm we discussed earlier. The process generally follows these logic points:

Find the Pivot: You search for the first element in Block B that is smaller than the last element of Block A. This identifies the "misplaced" elements that prevent the array from being sorted.

Divide and Conquer: You identify sub-blocks within the ranges. You aren't just swapping individual elements; you are identifying a "partition" point and swapping entire contiguous chunks (blocks) of data.

Block Rotation (The Swap): To move a block of elements across another without extra space, you use a three-step reversal sequence:

Reverse the first block.

Reverse the second block.

Reverse the combined range.
This effectively swaps the positions of the two blocks in-place without needing a temporary buffer equal to the size of the array.

Recursion: After the swap, the problem is divided into two smaller sub-problems, which are solved recursively until the entire array is sorted.
"""

    # 2. Package into the payload
    # Note: Ensure the key 'explanation_text' matches what your API expects in the Form
    payload = {
        "primitive_type": "variables",
        "explanation_text": algorithm_steps,
        "system_prompt": (
            "You are a state-aware Manim compiler. "
            "You strictly follow the provided steps to mutate the array state registry. "
            "Never create duplicates; always swap pointers."
        )
    }
    
    print("🚀 Sending algorithmic logic roadmap to AlgoFrame Core Engine...")
    print("============================================================")
    
    try:
        response = requests.post(url, data=payload, timeout=300)
        
        if response.status_code == 200:
            output_filename = "swap_animation_production.mp4"
            with open(output_filename, "wb") as f:
                f.write(response.content)
            print(f"✅ SUCCESS! Saved to: {os.path.abspath(output_filename)}")
        else:
            print(f"❌ FAILURE: Status {response.status_code}")
            print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"⚠️ Transport failure: {e}")

if __name__ == "__main__":
    test_text_synthesis()