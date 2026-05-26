# Agents Layer
Contains specialized CrewAI Autonomous Agents defined as independent Python class files:
- planner.py: Lead Architectural Planner Agent (maps transcripts into structured execution roadmaps).
- developer.py: Manim Python Script Engineer Agent (translates roadmaps into clean Manim Python scripts).
- validator.py: Closed-Loop Semantic & Syntax QA Agent (catches compiler bugs and evaluates math correctness).
- editor.py: Audio-Visual Alignment Producer Agent (coordinates frame alignments and timing offsets).