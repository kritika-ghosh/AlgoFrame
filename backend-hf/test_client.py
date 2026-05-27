# test_swap_client.py
import requests
import os

def test_text_synthesis():
    url = "http://127.0.0.1:7860/api/generate-video"
    
    # 1. Formulate the technical explanation paragraph for swapping
    explanation = (
    "We want to animate the Block Swap Algorithm to left-rotate an array by 2 positions. "
    "Initialize a contiguous 5-element array container displaying the integers 10, 20, 30, 40, and 50 positioned horizontally. "
    "Step 1: Divide the array into two primary visual chunks. Highlight the first two elements [10, 20] as 'Block A' "
    "using a distinct blue border outline, and the remaining three elements [30, 40, 50] as 'Block B' using a gold border outline. "
    "Step 2: Because Block B is longer than Block A, subdivide Block B. Keep the single element [30] stationary, "
    "and group the rightmost two elements [40, 50] into a sub-block called 'Block Br' that perfectly matches the size of Block A. "
    "Step 3: Animate a block-level swap. Arcing gracefully along parallel paths, shift the elements of Block A [10, 20] "
    "downward and over to the final two slots of the array, while simultaneously moving Block Br [40, 50] upward and "
    "into the first two slots of the array. The visual arrangement is now [40, 50, 30, 10, 20]. "
    "Step 4: Change the background fill of the slots containing [10, 20] to a solid deep green to indicate they have "
    "successfully reached their final, permanently shifted index locations. "
    "Step 5: Conclude by animating a final swap between the remaining active elements [40, 50] and the middle element [30] "
    "to achieve the completely rotated final state of [30, 40, 50, 10, 20], fading out all labels except the final array container."
)
    
    # 2. Package request parameters matching FastAPI's Form intake expectations
    payload = {
        "primitive_type": "variables",
        "explanation_text": explanation
    }
    
    print("🚀 Sending direct text explanation payload to AlgoFrame Core Engine...")
    print(f"📝 Prompt: \"{explanation[:60]}...\"")
    print("============================================================")
    
    try:
        # Fire the POST request without passing files to trigger text modality
        response = requests.post(url, data=payload, timeout=180)
        
        if response.status_code == 200:
            output_filename = "swap_animation_production.mp4"
            
            # Write the raw incoming byte stream into a physical video file container
            with open(output_filename, "wb") as f:
                f.write(response.content)
                
            print("\n============================================================")
            print(f"✅ SUCCESS! Final video compiled and saved to disk.")
            print(f"🎬 Asset Location: {os.path.abspath(output_filename)}")
        else:
            print(f"\n❌ FAILURE: Server returned status code {response.status_code}")
            try:
                print(f"Detailed Error: {response.json()}")
            except Exception:
                print(f"Raw Response Text: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Transport layer connection failure: {e}")

if __name__ == "__main__":
    test_text_synthesis()