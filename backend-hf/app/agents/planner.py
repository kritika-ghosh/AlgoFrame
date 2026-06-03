# app/agents/planner.py
from crewai import Agent, LLM

class PlannerAgent:
    def __init__(self):
        self.llm_instance = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.0)

    def get_agent(self) -> Agent:
        return Agent(
            role="Lead Computer Science Architectural Planner",
            goal="Deconstruct complex algorithm descriptions (Arrays, Stacks, Queues, Trees, Graphs) into an exact, step-by-step visual execution roadmap.",
            backstory=(
                "You are an expert systems engineer. You read algorithmic descriptions of data structure operations "
                "(like array swaps, binary search tree traversals, DFS/BFS graph steps, stack/queue mutation) "
                "and precisely map how the structural connections and visual highlight layers mutate over a step-by-step timeline. "
                "You provide clear, unambiguous sequence instructions for downstream development modules."
            ),
            llm=self.llm_instance,
            allow_delegation=False,
            verbose=True
        )