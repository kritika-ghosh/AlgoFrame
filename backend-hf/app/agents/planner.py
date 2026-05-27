# app/agents/planner.py
from crewai import Agent, LLM

class PlannerAgent:
    def __init__(self):
        self.llm_instance = LLM(
            model="groq/llama-3.1-8b-instant",
            temperature=0.0
            # Removed custom key property to prevent payload schema leakage
        )

    def get_agent(self) -> Agent:
        return Agent(
            role="Lead Computer Science Architectural Planner",
            goal="Analyze raw user voice transcripts and extract precise chronological data structure operation roadmaps.",
            backstory="Expert at converting conversational human explanations into concise technical execution steps.",
            llm=self.llm_instance,
            allow_delegation=False,
            verbose=True
        )