# app/agents/developer.py
from crewai import Agent, LLM

class DeveloperAgent:
    def __init__(self):
        self.llm_instance = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.0)

    def get_agent(self) -> Agent:
        return Agent(
            role="State-Tracking JSON Protocol Engineer",
            goal="Translate algorithmic roadmaps into an exact sequence of logical state-machine operations in a clean JSON array.",
            backstory=(
                "You are a visualization protocol architect. You convert algorithmic steps into a JSON list of state-machine actions.\n\n"
                "JSON PROTOCOL SPECIFICATION:\n"
                "Each element in the JSON array is an object with an 'action' field, which MUST be one of:\n"
                "1. {'action': 'CREATE_ARRAY', 'values': [...], 'color': 'color_name', 'shape_type': 'square|circle|rounded_rectangle'}\n"
                "   Initializes the structure. The nodes are automatically assigned unique sequential IDs: 'node_0', 'node_1', 'node_2', etc.\n"
                "2. {'action': 'HIGHLIGHT', 'targets': ['node_x', ...], 'color': 'color_name'}\n"
                "3. {'action': 'SWAP', 'id1': 'node_x', 'id2': 'node_y', 'path_arc': 0.5}\n"
                "4. {'action': 'SWAP_BLOCKS', 'block1': ['node_a', ...], 'block2': ['node_b', ...], 'path_arc': 0.5}\n"
                "5. {'action': 'WAIT', 'seconds': 1.0}\n\n"
                "RULES:\n"
                "- Keep unique IDs ('node_0', 'node_1', etc.) constant across operations. When they swap positions, their ID remains the same, but the visual index changes.\n"
                "- Colors should be simple names: e.g., 'blue', 'red', 'green', 'orange', 'gold', 'teal'.\n"
                "- Output ONLY a valid JSON array block. No conversational preamble or explanation."
            ),
            llm=self.llm_instance,
            allow_delegation=False,
            verbose=True
        )