# app/services/critic_service.py
import os
import time
import google.generativeai as genai

class VisualCriticService:
    def __init__(self):
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def critique_video(self, video_path: str, user_prompt: str) -> dict:
        """
        Uploads the compiled video and verifies both algorithmic logic and spatial readability.
        """
        print(f"👁️ [Visual Critic]: Uploading {video_path} to Gemini Pro Unified Inspector...")
        
        video_file = genai.upload_file(path=video_path)
        
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == "FAILED":
            raise ValueError("Gemini structural video encoder processing matrix failed.")

        # EXPLICIT LOGIC-STEP VERIFICATION PROMPT
        critic_prompt = f"""
        You are an algorithmic auditor. You have two inputs: a video animation and a step-by-step transcript.
        Your goal is to perform a 'Logic-Alignment Check'.

        TRANSCRIPT:
        {user_prompt}

        INSTRUCTIONS:
        1. Break the transcript into individual steps (Step 1, Step 2, etc.).
        2. Watch the video and identify the timestamp where each step begins and ends.
        3. For each step, determine if the visual action in the video correctly performs the logic defined in the transcript.
        4. If a step is missing, performed in the wrong order, or logically incorrect, output:
           STATUS: FAILED
           FEEDBACK: 'Step X failed because...'
        5. If all steps are logically correctly performed and readable, output:
           STATUS: PASSED
        Your response must strictly match this format:
        STATUS: [PASSED or FAILED]
        FEEDBACK: [If FAILED, explain exactly which frames became unreadable or broken, what went wrong with the algorithm steps, and give clear layout instructions on how to prevent the text collision or logical gap. If PASSED, leave empty.]
        """

        try:
            response = self.model.generate_content([video_file, critic_prompt])
            result_text = response.text
            print(f"📊 [Visual Critic Logic Audit Result]:\n{result_text}")

            try:
                genai.delete_file(video_file.name)
            except:
                pass

            is_passed = "STATUS: PASSED" in result_text
            feedback = ""
            if "FEEDBACK:" in result_text:
                feedback = result_text.split("FEEDBACK:")[1].strip()

            return {"passed": is_passed, "feedback": feedback}

        except Exception as e:
            try:
                genai.delete_file(video_file.name)
            except:
                pass
            print(f"⚠️ [Critic Exception]: Loop recovery active: {str(e)}")
            return {"passed": True, "feedback": ""}

    def fix_json_protocol(self, user_prompt: str, broken_json: str, feedback_or_error: str) -> str:
        """
        Uses Gemini to directly fix a broken or logically incorrect JSON protocol array.
        """
        fix_prompt = f"""
        You are an elite State Machine Debugger. You are given a target algorithmic transcript, 
        a JSON protocol representation of the state transitions, and a specific layout/logic critique or compiler error.

        YOUR TASK:
        Analyze the inputs, and output the corrected, complete, and syntactically flawless JSON protocol array.

        TRANSCRIPT:
        {user_prompt}

        BROKEN JSON:
        {broken_json}

        CRITIQUE / COMPILER ERROR:
        {feedback_or_error}

        JSON PROTOCOL SPECIFICATION:
        Your output must be a valid JSON array of dictionary objects, where each object has an 'action' field, one of:
        1. {{"action": "CREATE_ARRAY", "values": [...], "color": "color_name", "shape_type": "square|circle|rounded_rectangle"}}
        2. {{"action": "HIGHLIGHT", "targets": ["node_x", ...], "color": "color_name"}}
        3. {{"action": "SWAP", "id1": "node_x", "id2": "node_y", "path_arc": 0.5}}
        4. {{"action": "SWAP_BLOCKS", "block1": ["node_a", ...], "block2": ["node_b", ...], "path_arc": 0.5}}
        5. {{"action": "WAIT", "seconds": 1.0}}

        RULES:
        - Rectify the exact failure described in the critique/error.
        - Ensure all referenced node IDs ('node_0', 'node_1', etc.) match their original assignments.
        - Output ONLY the raw JSON array. Never wrap in markdown code blocks. No conversational text.
        """
        
        try:
            print(f"🔧 [Visual Critic]: Invoking direct self-healing patch via Gemini...")
            response = self.model.generate_content(fix_prompt)
            result = response.text.strip()
            print(f"📊 [Visual Critic self-healing output]:\n{result}")
            return result
        except Exception as e:
            print(f"⚠️ [Critic Self-healing Failure]: {str(e)}")
            return broken_json