# app/agents/validator.py
from crewai import Agent, LLM

class ValidatorAgent:
    def __init__(self):
        self.llm_instance = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.0)

    def get_agent(self) -> Agent:
        return Agent(
            role="State-Tracking JSON Auditor",
            goal="Verify that the JSON operations sequence correctly implements the planned roadmap and is syntactically flawless.",
            backstory=(
                "You are an unyielding protocol auditor. You scan the generated JSON operations array to ensure:\n"
                "1. The JSON is perfectly valid and matches the specified actions (CREATE_ARRAY, HIGHLIGHT, SWAP, SWAP_BLOCKS, WAIT).\n"
                "2. The IDs referenced ('node_0', 'node_1', etc.) match the created nodes.\n"
                "3. The block swap operations are correct and match the transcript layout.\n"
                "Output ONLY the verified JSON array, completely free of any markdown code blocks or explanations."
            ),
            llm=self.llm_instance,
            allow_delegation=False,
            verbose=True
        )