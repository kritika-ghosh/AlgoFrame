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

    def compile_animation_pipeline(self, user_transcript: str, primitive_type: str, feedback: str = "") -> str:
        
        task_plan = Task(
            description=f"Analyze transcript: '{user_transcript}' for primitive: '{primitive_type}'. Output a step roadmap.",
            expected_output="Markdown roadmap tracking state modifications per frame step.",
            agent=self.planner,
            cache=False
        )
        feedback_context = ""
        if feedback:
            feedback_context = f"\n\n⚠️ CRITICAL FIX NEEDED FROM PREVIOUS RUN:\nYour previous JSON protocol was incorrect. Fix this: {feedback}"

        task_develop = Task(
            description=(
                f"Convert the roadmap into a sequence of state-machine actions in a JSON array format.{feedback_context}"
                "\nFollow the JSON PROTOCOL SPECIFICATION strictly. Output ONLY the raw JSON array containing action dictionary objects."
            ),
            expected_output="A raw JSON array containing action dictionary objects.",
            agent=self.developer,
            cache=False
        )

        task_validate = Task(
            description=f"Verify that the generated JSON array is syntactically correct and perfectly represents the planned roadmap steps.",
            expected_output="A pure verified JSON array string completely free of markdown wrappers or conversational intro/outro.",
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