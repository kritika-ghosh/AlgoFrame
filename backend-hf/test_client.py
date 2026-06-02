# test_swap_client.py
import requests
import os

def test_text_synthesis():
    url = "http://127.0.0.1:7860/api/generate-video"
    
    # 1. Your refined algorithmic roadmap
    algorithm_steps = """
To perform a basic swap of two numbers, $a$ and $b$, the algorithm utilizes a temporary storage variable to facilitate the exchange of their respective values without losing data.The process begins by assigning the value of $a$ to the temporary variable, effectively creating a safe copy of that data. With the original value of $a$ secured, the value of $b$ is then assigned to $a$. Finally, the value held in the temporary variable is assigned to $b$. This sequence of three assignments ensures that the initial values are inverted—meaning the original value of $a$ now resides in $b$, and the original value of $b$ now resides in $a$—completing the swap without the need for additional arithmetic operations.
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