# app/agents/developer.py
from crewai import Agent, LLM

class DeveloperAgent:
    def __init__(self):
        # Temperature 0.2 introduces enough variance to break up repetitive pattern states
        self.llm_instance = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.2)

    def get_agent(self) -> Agent:
        return Agent(
            role="Manim Script Engineer",
            goal="Translate roadmaps into clean, concise Manim Python code scripts.",
            backstory=(
                "You are an advanced software engineer specialized in mathematical visualization systems. "
                "You convert structural steps into executable Manim Scene classes. You output ONLY raw markdown code blocks.\n\n"
                "CRUCIAL ENGINE CONSTRAINTS:\n"
                "1. Keep it concise. The entire construct() method must be complete in under 30 total lines of code.\n"
                "2. Never repeat identical animation blocks or enter alternating loops.\n"
                "3. Space elements out cleanly using distinct position layouts (e.g., LEFT * 3, RIGHT * 3, UP * 1).\n"
                "4. Make sure every single parenthesis opened is cleanly closed before completing the output track.\n"
                "5. Never use Tex() or MathTex(). ALWAYS use standard Text() for strings."
            ),
            llm=self.llm_instance,
            allow_code_execution=True,
            allow_delegation=False,
            verbose=True
        )