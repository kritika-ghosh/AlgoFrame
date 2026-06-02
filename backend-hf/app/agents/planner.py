# app/agents/planner.py
from crewai import Agent, LLM

class PlannerAgent:
    def __init__(self):
        # Explicitly enforce the 70B model to maintain state continuity
        self.llm_instance = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.0)

    def get_agent(self) -> Agent:
        return Agent(
            role="Lead Computer Science Architectural Planner",
            goal="Deconstruct complex algorithm descriptions into an exact, step-by-step visual execution roadmap.",
            backstory=(
                "You are an expert systems engineer. You read programmatic transcript descriptions "
                "and precisely map how variables, memory cells, and arrays mutate over a step-by-step timeline. "
                "You provide clear, unambiguous sequence instructions for downstream development modules."
            ),
            llm=self.llm_instance,
            allow_delegation=False,
            verbose=True
        )