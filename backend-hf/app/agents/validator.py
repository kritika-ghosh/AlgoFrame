# app/agents/validator.py
from crewai import Agent, LLM

class ValidatorAgent:
    def __init__(self):
        self.llm_instance = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.0)

    def get_agent(self) -> Agent:
        return Agent(
            role="QA Director",
            goal="Verify compilation stability, completeness, and clean visual layout of Manim code.",
            backstory=(
                "You are a strict code auditor. You look at raw code files and scan for three fatal issues:\n"
                "1. Syntax errors, unclosed brackets, or unclosed string indicators.\n"
                "2. Chunks of repeating, alternating lines of code that indicate a model generation loop.\n"
                "3. Incomplete blocks where the code cuts off mid-sentence.\n\n"
                "CRUCIAL: If any of these structural red flags are detected, you must REJECT the output completely "
                "and command a clean rewrite from step one."
            ),
            llm=self.llm_instance,
            allow_delegation=False,
            verbose=True
        )