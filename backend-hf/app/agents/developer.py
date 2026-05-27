# app/agents/developer.py
from crewai import Agent, LLM

class DeveloperAgent:
    def __init__(self):
        self.llm_instance = LLM(
            model="groq/llama-3.1-8b-instant",
            temperature=0.1
        )

    def get_agent(self) -> Agent:
        return Agent(
            role="Manim Python Script Engineer",
            goal="Translate structural algorithm roadmaps into highly clean, executable Python code utilizing the Manim library.",
            backstory="Specialist in Manim. Outputs ONLY raw markdown code blocks. Colors allowed: GOLD, ORANGE, YELLOW, BLUE, RED, GREEN, PURPLE, WHITE, GREY.",
            llm=self.llm_instance,
            allow_code_execution=True,
            allow_delegation=False,
            verbose=True
        )