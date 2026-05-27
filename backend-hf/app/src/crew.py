# app/src/crew.py
from crewai import Crew, Task, Process
from app.agents.planner import PlannerAgent
from app.agents.developer import DeveloperAgent
from app.agents.validator import ValidatorAgent

class AlgoFrameCrewPipeline:
    def __init__(self):
        self.planner = PlannerAgent().get_agent()
        self.developer = DeveloperAgent().get_agent()
        self.validator = ValidatorAgent().get_agent()

    def compile_animation_pipeline(self, user_transcript: str, primitive_type: str) -> str:
        task_plan = Task(
            description=f"Analyze transcript: '{user_transcript}' for primitive: '{primitive_type}'. Output a step roadmap.",
            expected_output="Markdown roadmap tracking state modifications per frame step.",
            agent=self.planner,
            cache=False
        )

        task_develop = Task(
            description=(
                "Convert the roadmap into an executable Python Manim script. Write explicit scene movements. "
                "CRUCIAL COLOR RULES: Never use variable names for custom colors. If you want a custom color, "
                "use an explicit Hex string inline (e.g., color='#FFBF00' instead of color=AMBER). Otherwise use standard 'GOLD' or 'ORANGE'."
            ),
            expected_output="Pure Python code block inheriting from Manim Scene class.",
            agent=self.developer,
            cache=False
        )

        task_validate = Task(
            description=f"Verify code syntax and alignment with user input: '{user_transcript}'. Fix any errors found.",
            expected_output="Pure, executable Python code string block inheriting from a Manim Scene class completely free of markdown wrappers or inline explanations.",
            agent=self.validator,
            cache=False
        )

        # Build the crew tracking only structural logic layers
        crew = Crew(
            agents=[self.planner, self.developer, self.validator],
            tasks=[task_plan, task_develop, task_validate],
            process=Process.sequential,
            verbose=True,
            memory=False
        )

        # Execute the orchestration loop
        result = crew.kickoff(inputs={
            'prompt': user_transcript,
            'primitive_type': primitive_type
        })
        
        return str(result)