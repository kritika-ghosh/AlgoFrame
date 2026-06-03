# app/agents/validator.py
from crewai import Agent, LLM

class ValidatorAgent:
    def __init__(self):
        self.llm_instance = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.0)

    def get_agent(self) -> Agent:
        return Agent(
            role="State-Tracking JSON Auditor",
            goal="Verify that the JSON operations sequence correctly implements the planned roadmap and matches structural rules.",
            backstory=(
                "You are an unyielding protocol auditor. You scan the generated JSON operations array to ensure:\n"
                "1. The JSON is perfectly valid and follows the action types (CREATE, VISIT, LINK, UNLINK, SET_VALUE, SWAP, SWAP_BLOCKS, HIGHLIGHT, WAIT, PUSH_BACK, POP_FRONT, PUSH_FRONT, POP_BACK, ENQUEUE, DEQUEUE).\n"
                "2. For Tree actions: ensure no duplicate parent links exist and there are no cyclic relationships.\n"
                "3. Ensure all queue/deque operations (like PUSH_BACK, POP_FRONT) correctly target the defined helper structure ID.\n"
                "4. All references to node IDs match their original declarations or the dynamic ids created in push operations.\n"
                "Output ONLY the verified JSON array, completely free of any markdown code blocks or explanations."
            ),
            llm=self.llm_instance,
            allow_delegation=False,
            verbose=True
        )