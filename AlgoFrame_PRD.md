## Project Name: AlgoFrame AI
**Core Subtitle:** Autonomous Data Structure & Algorithm Animation Engine via Multi-Agent Closed-Loop Synthesis  
**Target Track:** FlowZint AI Hackathon 2026 — Open Innovation Track  
**Document Version:** v1.2 (Production & Engineering Baseline)  
---

## 1. Product Overview & Executive Summary

### 1.1 Vision
AlgoFrame AI envisions an ecosystem where technical educational material can be visualized dynamically without human engineering intervention. By translating raw natural audio/video technical explanations directly into exact, mathematically sound, step-by-step algorithmic visualizations, AlgoFrame AI bridges the gap between fluid multimodal inputs and deterministic data structure rendering. It replaces days of manually writing coordinate paths, layouts, or keyframe scripts with an autonomous multi-agent code-and-state compilation pipeline.

### 1.2 Elevator Pitch
For computer science educators, content creators, and students struggling with abstract concept visualization, **AlgoFrame AI** is an intelligent agentic engine that turns a spoken-word explanation into deterministic, beautifully rendered Data Structure and Algorithm (DSA) animations within seconds. Unlike video editing wrappers or brittle LLM canvas engines that hallucinate syntax, AlgoFrame AI decouples natural language from execution logic using a multi-agent system. It maps transcripts into structured execution JSON logs, rendering high-fidelity, real-time animations natively in the browser via clean component frameworks.

### 1.3 The "Why" (Strategic Context)
Visualizing abstract concepts (e.g., node rotations in an AVL Tree or pointer swaps in a Doubly Linked List) is computationally simple but visualization-heavy. Existing programmatic tools like Manim require significant Python mastery and endless debugging iterations. General-purpose generative video LLMs fail entirely because they lack an implicit model of computer memory structures, resulting in visual hallucinations, blurred morphing, and mathematically incorrect node connections. 

AlgoFrame AI introduces a reliable approach: using LLM agents for orchestration, synthesis, and state tracking, while reserving rendering duties for absolute, template-driven mathematical constraints. This guarantees functional correctness while delivering rapid turnaround times tailored for competitive submission within the **FlowZint AI Hackathon 2026 Open Innovation Track**.

### 1.4 Architectural Paradigm
The core architecture shifts from a traditional pipeline to a modular, service-oriented multi-agent framework where each agent lives within a dedicated Python class service file. The architecture integrates **CrewAI** for intent extraction and planning loops, **Groq API** for ultra-low latency inference, **Manim** for deterministic frame assembly, and **FFmpeg** for final audio-video stream multiplexing.

---

## 2. Target Audience & Personas

### 2.1 Core Target Segments
1. **Computer Science Educators & University TAs:** Demand absolute precision in visual execution logs for display during active lecture presentations.
2. **Technical Content Creators (YouTube/Bootcamps):** Require polished, high-fidelity visual assets rapidly to lower post-production costs.
3. **Self-Paced Computer Science Students:** Require a step-by-step trace showing explicit pointer mutations and variable allocations to break down abstract concepts during self-study.

### 2.2 User Personas

#### Persona A: Prof. Arjun, Senior Data Structures Instructor
* **Demographics:** 45 years old, University Professor teaching core engineering algorithms to sections of over 200 students.
* **Pain Points:** Spends hours drafting static PowerPoint slides with complex transition triggers to simulate pointer updates in a Red-Black Tree. Existing tools like Manim take too long to script and debug between lectures.
* **Goals:** Input a quick verbal description of an algorithmic operation during lecture prep and immediately receive a pristine, animated video showing the correct memory layout.

#### Persona B: Sarah, EdTech Content Developer
* **Demographics:** 27 years old, operates an engineering tutorial channel with 150k subscribers.
* **Pain Points:** High financial and time costs associated with motion graphics editing inside Adobe After Effects for code walkthroughs. Video generators hallucinate code tokens and variable states.
* **Goals:** Automate script-to-video generation for DSA code blocks while maintaining absolute mathematical accuracy.

---

## 3. Core Objectives & Success Metrics (KPIs)

### 3.1 Primary Performance KPIs
* **Time-to-Asset Optimization:** Reduce the manual baseline duration required to construct a 30-second algorithm animation from 120 minutes down to `< 45 seconds` end-to-end.
* **Closed-Loop Alignment Accuracy Target:** Maintain an agent-driven self-correction rate where `95%` of final generated videos match both the structural code criteria and the original user verbal intent on the first delivered generation loop.
* **System Processing Latency Floor:** Ensure total pipeline execution (Transcription + Planning + Execution + Validation + Muxing) stays under 20 seconds for voice inputs shorter than 60 seconds when utilizing Groq-backed Llama-3-70B models.

### 3.2 System Operational KPIs
* **Zero-Hallucination Delivery:** Strict `100%` syntax validity across all final executed Manim python scripts. If a script crashes the rendering subsystem, it must be caught and corrected by the validation loop before reaching the deployment state.
* **Hugging Face Space Availability:** Achieving `100%` space uptime by leveraging an internal background scheduler loop that pings itself every 20 minutes, bypassing the default 48-hour container hibernation threshold on free-tier Spaces.

---

## 4. End-to-End System Processing Flow & Journey

The processing lifecycle follows an absolute, closed-loop linear data routing architecture from the Vercel frontend interface through the modular Hugging Face backend components:

1. **Ingestion (`app/main.py` & `app/api/routes.py`):** The user speaks into the Vercel frontend app. The interface records the audio layer and routes the binary payload via an HTTP POST multipart request to the FastAPI endpoint on Hugging Face.
2. **Transcription (`app/services/audio_service.py`):** The audio service intercepts the payload and passes it to Groq's high-speed Whisper instance. The system converts the voice recording into a timestamped semantic text string.
3. **Roadmap Generation (`app/agents/planner.py`):** The text transcript and data primitive targets are sent into the Planner agent. The agent isolates the computer science operations, discards conversational filler, and generates a structured chronological execution blueprint.
4. **Script Generation (`app/agents/developer.py`):** The developer agent interprets the logical blueprint and writes a clean Python script using the Manim library library. It sets up camera dimensions, grid parameters, and transformation functions.
5. **Subprocess Compilation (`app/services/manim_service.py`):** The backend saves the generated code to a temporary path on the server and runs a command-line subprocess: `manim -ql -v WARNING scene.py`. This outputs a low-latency, silent `.mp4` video clip.
6. **Closed-Loop Quality Assurance (`app/agents/validator.py`):** The validator runs a two-pass check on the generated asset. 
    * *Pass 1 (Compiler Check):* Verifies the compilation exited successfully with no errors.
    * *Pass 2 (Semantic Check):* Cross-examines the code log against the original user transcript text to ensure the math is correct. If it detects an error, it sends the bug log back to the developer agent to rewrite the code.
7. **Audio-Visual Sync (`app/agents/editor.py` & `app/services/video_service.py`):** Once approved, the editor agent takes the silent video, calculates frame alignments against the audio timestamps, and hands the assets to the video service. The service executes an high-performance **FFmpeg multiplexing script** that binds the original audio track directly onto the video layers without slow re-rendering passes.
8. **Asset Deployment & Handoff (`app/services/storage_service.py`):** The combined video file is saved into the public `/output/` static directory. The endpoint closes the connection by returning a direct asset link to Vercel: `{"status": "completed", "video_url": "https://username-space.hf.space/output/final.mp4"}`.

---

## 5. Official Backend Folder Structure


```text
backend-hf/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry configuration & keep-alive loops
│   │
│   ├── agents/                 # Specialized CrewAI Autonomous Agents (Class Files)
│   │   ├── __init__.py
│   │   ├── planner.py          # Lead Architectural Planner Agent
│   │   ├── developer.py        # Manim Python Script Engineer Agent
│   │   ├── validator.py        # Closed-Loop Semantic & Syntax QA Agent
│   │   └── editor.py           # Audio-Visual Alignment Producer Agent
│   │
│   ├── api/                    # Endpoint Handling and Verification Schemas
│   │   ├── __init__.py
│   │   ├── dependencies.py     # Global rate-limiting injectors and environment guardians
│   │   ├── routes.py           # Explicit network routing entry configurations
│   │   └── schemas.py          # Pydantic input/output verification contracts
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Global system and API key environment mapping
│   │   └── exceptions.py       # Intercept handlers for agent runtime exceptions
│   │
│   └── services/               # Tool Drivers and Native Execution Utilities
│       ├── __init__.py
│       ├── audio_service.py    # Interfaces with Groq Whisper for rapid transcription
│       ├── manim_service.py    # Standard shell wrapper executing low-level Manim scripts
│       ├── video_service.py    # Subprocess FFmpeg command multiplexing utilities
│       └── storage_service.py  # Coordinates asset persistence path arrays
│
├── output/                     # Hosted static public workspace containing compiled MP4 assets
│   └── stable_placeholder.txt
│
├── Dockerfile                  # Container instructions installing system multi-media dependencies
├── requirements.txt            # Explicit Python dependencies manifest
└── README.md                   # System operational documentation

```

---

## 6. Functional Requirements & Agent Epics

### 6.1 Epic 1: Multimodal Transcription Node

* **Description:** Convert conversational user voice recordings into structured technical string tokens.

#### User Story

As the backend ingestion router, I want to route incoming audio streams to Groq's Whisper API so that I can capture the user's intent as a clean text string in less than 3.5 seconds.

#### Acceptance Criteria

* **FR-1.1:** Must support standard audio formats (WAV, MP3, M4A) with file sizes up to 25MB.
* **FR-1.2:** Must pass clean string tokens to the orchestration layers, filtering out vocal fillers like "uhm", "err", or "like".
* **FR-1.3:** Output data payloads must contain a complete timestamp metadata dictionary tracking sentence boundaries.

---

### 6.2 Epic 2: The Agentic Planning & Development Sandbox (`planner.py` & `developer.py`)

* **Description:** Formulate a step-by-step roadmap and translate those conceptual milestones into valid, compilation-ready Manim script strings.

#### User Stories

* As the Lead Planner Agent, I want to generate a chronological step-by-step roadmap from raw text transcripts so that the downstream developer agent knows exactly how many scene transitions to code.
* As the Manim Developer Agent, I want to write programmatic animation structures using the Manim library so that the system can compile mathematically correct vector layouts.

#### Acceptance Criteria

* **FR-2.1 Dynamic Planning Mode:** The agent assembly must run with `planning=True` enabled on the Crew instance, forcing the generation of an explicit execution path before code block generation starts.
* **FR-2.2 Code Isolation Guardrails:** The code block output must be cleanly parsed, strip away conversational formatting preamble, and export as an executable string containing only standard Python imports and bounded class scenes.
* **FR-2.3 Coordinate Validation:** The script layout must programmatically align geometric elements using relative vector configurations (e.g., `UP`, `DOWN`, `LEFT`, `RIGHT`, `shift(2 * RIGHT)`) to avoid overlapping nodes or clipped UI layouts.

---

### 6.3 Epic 3: Closed-Loop Validation & Self-Correction Engine (`validator.py`)

* **Description:** A strict quality assurance system that catches compiler syntax errors and evaluates structural semantic alignment between the code output and the user's intent.

#### User Story

As the Validation Agent, I want to analyze both the compiler execution logs and the user's original transcript so that I can automatically catch bugs and send them back for correction before shipping a broken video to the frontend.

#### Acceptance Criteria

* **FR-3.1 Automated Bug Re-routing:** If `manim_service.py` returns an error status code (`exit_code != 0`), the validator agent must catch the standard error log, format a debugging summary, and route the task back to `developer.py` to fix the script.
* **FR-3.2 Semantic Misalignment Verification:** The validator agent must cross-check the generated scene classes against the original transcript tokens. If a user asks to *"insert 15 at index 1"* but the script inserts it at index 2, the validator must flag the logical error and send it back for correction.
* **FR-3.3 Retries Ceiling Guardrail:** The self-correcting feedback loop must be capped at a maximum of `3 cycles`. If an agent fails to write valid, aligned code after three attempts, the system must break the loop and throw an explicit exception payload back to the client interface to protect server resources.

---

### 6.4 Epic 4: Audio-Video Multiplexing and Layout Integration (`editor.py` & `video_service.py`)

* **Description:** Synchronize the source narration audio track with the final, validated silent video container using low-overhead media toolchains.

#### User Story

As the Editor Agent, I want to calculate precise frame paddings and invoke high-performance FFmpeg multiplexing commands so that the user receives a fully synchronized video asset without slow video re-rendering passes.

#### Acceptance Criteria

* **FR-4.1 Zero-Re-encode Stream Multiplexing:** The video service must handle media synchronization by calling native CLI utilities with direct track copying parameters: `-c:v copy -c:a aac`. It must never run full-raster re-encoding passes on the video frames.
* **FR-4.2 Multi-Stream Processing Overhead Ceiling:** The total duration required to bind an audio file onto a 30-second silent video track must remain under `1.5 seconds` on standard CPU hardware containers.
* **FR-4.3 Temporal Expansion Controls:** If the user voice narration track is longer than the raw compiled video timeline, the system must automatically add static padding to the final frame container to maintain audio alignment.

---

## 7. Non-Functional & Technical Requirements

### 7.1 Performance & Latency Resource Allocation Budget

To ensure a snappy, competitive experience during the hackathon judging window, individual component latencies are capped under strict constraints:

* **Audio Transcription Loop:** $T_{trans} \le 3.5\text{s}$
* **Multi-Agent Reasoning & Planning Core Loop:** $T_{reasoning} \le 8.5\text{s}$
* **Manim Scene Subprocess Rendering Execution:** $T_{compile} \le 6.0\text{s}$
* **FFmpeg Stream Multiplexing Array Layering:** $T_{muxing} \le 1.5\text{s}$
* **Total Targeted Ingestion-to-Asset Latency Budget:** $T_{total} \le 19.5\text{s}$

### 7.2 Container Infrastructure & Dependencies (`Dockerfile`)

The backend must run inside a debian-slim Docker base image configured with all the low-level media libraries required by Manim and FFmpeg:

```dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    libcairo2-dev \
    libpango1.0-dev \
    freeglut3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]

```

### 7.3 Data Isolation & Rate-Limiting Guardrails

* **In-Memory Buffer Ephemerality:** Raw audio recordings sent by users must be handled inside short-lived system memory buffers. They should be deleted immediately after transcription tasks finish to ensure optimal data privacy.
* **Security Rate Limits:** Implement a strict rate-limiting window (maximum 10 pipeline requests per minute per IP address) inside `dependencies.py` to prevent API credit exhaustion during hackathon evaluation rounds.

---

## 8. UX/UI & Design Guidelines (Handoff to Claude)

The Vercel-hosted interface component should focus on standard streaming media workflows and continuous terminal feedback layouts.

### 8.1 Key Workspace Layout Areas

* **Control Configuration Panel (35% Viewport Width):** Contains a data structure primitive selector dropdown (supporting Arrays, Linked Lists, BSTs), an explicit audio capture recording toggle button with a micro-timer track, and a manual text fallback entry block.
* **Dynamic Media Player Workspace (65% Viewport Width):** An absolute-positioned, dark-slate container box. While compiling, it displays a real-time, scrolling terminal logging box showing what the backend agents are processing. Once compilation completes, the log interface smoothly slides away to reveal an high-performance HTML5 `<video>` player hosting the final asset.
* **Secondary Parameter Control Deck:** Includes explicit video playback speed sliders (0.5x, 1.0x, 1.5x, 2.0x), a direct standalone asset download button (`.mp4`), and instant layout theme preset toggle selectors.

### 8.2 Component States & Visual Vocabulary

* **The Awaiting State:** Clean, minimalist UI design with clear prompts guiding the user to initialize audio capturing.
* **The Processing State:** Displays an active loading sequence alongside live terminal feedback updates from the server (e.g., `[INFO] CrewAI is generating execution roadmap...`, `[COMPILE] Rendering Manim code vector structures...`).
* **The Delivered State:** Displays the final asset in a crisp video player featuring sharp borders and subtle glowing drop-shadows to emphasize successful generation.

---

## 9. Risks & Dependencies

| Identified System Risk | Downstream Product Impact | Engineering Mitigation Strategy |
| --- | --- | --- |
| **LLM Runtime Logic Hallucinations** | Agent outputs broken Python code, crashing the rendering engines. | Enforce strict Pydantic parsing wrappers on the backend. Limit the code structure scope using strict system instruction bounds inside `developer.py`. |
| **Hugging Face Space Hibernation** | The backend container goes to sleep after 48 hours of inactivity, causing initial request timeouts. | **Fixed via Self-Wake Up Scheduler Core Loop:** An asynchronous background worker function running inside `app/main.py` that automatically pings its own `/health` endpoint every 20 minutes to remain active. |
| **API Timeout Exceptions** | Downstream network congestion drops connection strings during peak hackathon evaluation hours. | Set explicit timeouts on HTTP client requests. Implement an automatic retry policy that instantly falls back to equivalent fast-inference providers if a call hangs. |

---

## 10. Assumptions & Scope Exclusions (Perimeter Boundaries)

To protect the development sprint and ensure absolute system stability before the hackathon evaluation phase, the boundaries for the MVP product version are defined as follows:

### 10.1 In-Scope Features for MVP Launch

* Full processing and animation rendering support for three foundational data structures: **1D Sequential Arrays, Singly Linked Lists, and Binary Search Trees (BST)**.
* Support for single-file conversational audio uploads bounded up to 60 seconds or 200 words per request.
* Pure, text/event-stream processing update alerts pushed directly from CrewAI tasks to the client dashboard interface.
* High-fidelity, low-overhead video-audio stream multiplexing delivered through local FFmpeg subprocess operations.

### 10.2 Out-of-Scope Features (Post-MVP Product Backlog)

* Support for complex, non-linear data models like multi-layer system graphs, weighted networks, or matrix structures.
* Server-side rendering configurations matching high-definition outputs (`-qh` 1080p or `-qk` 4K parameters), which increase processing latency.
* Multi-user real-time asset collaboration tools or shared team cloud drives.
* Continuous integration pipeline connections, browser IDE extensions, or custom local workspace plugins.

---ould we head next? We can start coding the core entry layout logic (`app/main.py`) or dive straight into building the CrewAI dynamic orchestration pipeline (`app/src/crew.py`). Let me know what you want to tackle first!

```
