# app/agents/editor.py
from crewai import Agent, LLM

class EditorAgent:
    def __init__(self):
        self.llm_instance = LLM(
            model="groq/llama-3.1-8b-instant",
            temperature=0.0
        )

    def get_agent(self) -> Agent:
        return Agent(
            role="Audio-Visual Integration Producer",
            goal="Synchronize raw user voice tracks with rendered silent animation video containers smoothly.",
            backstory="Post-production engineer managing timeline multiplexing.",
            llm=self.llm_instance,
            allow_delegation=False,
            verbose=True
        )