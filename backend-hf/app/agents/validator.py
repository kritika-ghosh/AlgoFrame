# app/agents/validator.py
from crewai import Agent, LLM

class ValidatorAgent:
    def __init__(self):
        self.llm_instance = LLM(
            model="groq/llama-3.1-8b-instant",
            temperature=0.0
        )

    def get_agent(self) -> Agent:
        return Agent(
            role="Closed-Loop Quality Assurance Director",
            goal="Verify compilation stability of generated Manim code and assess strict semantic alignment against the original user input text.",
            backstory="Unforgiving auditor. Checks syntax and logic flow accuracy.",
            llm=self.llm_instance,
            allow_delegation=False,
            verbose=True
        )