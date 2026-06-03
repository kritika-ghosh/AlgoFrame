import React from 'react';

interface LandingPageProps {
  onStart: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onStart }) => {
  return (
    <div className="landing-hero">
      <div className="badge badge-green">
        <span className="node-pulse"></span>
        FLOWZINT HACKATHON 2026 — OPEN INNOVATION TRACK
      </div>
      
      <h1 className="hero-title">
        Autonomous Data Structure <br />
        <span className="gradient-text">&amp; Algorithm Animation</span>
      </h1>
      
      <p className="hero-desc">
        AlgoFrame AI converts voice transcripts or raw code explanations into mathematically sound, 
        step-by-step vector animations in the browser. Powered by multi-agent reasoning and deterministic rendering.
      </p>
      
      <div style={{ marginBottom: '60px' }}>
        <button className="btn-primary" onClick={onStart}>
          <span>START COMPILING / TRY IT OUT</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </button>
      </div>

      <h2 className="section-title">THE CLOSED-LOOP AGENTIC COMPILER</h2>
      
      <div className="pipeline-grid">
        <div className="pipeline-card">
          <div className="step-num">01</div>
          <h3>Speech Intake</h3>
          <p>Acoustic inputs are processed via Groq Whisper-v3 into semantic instruction models.</p>
        </div>
        
        <div className="pipeline-card">
          <div className="step-num">02</div>
          <h3>State Planner</h3>
          <p>Lead Planner agent maps the natural language explanation into logical sequence states.</p>
        </div>
        
        <div className="pipeline-card">
          <div className="step-num">03</div>
          <h3>Manim Dev</h3>
          <p>Developer agent translates states into precise Manim vector graphics coordinate declarations.</p>
        </div>
        
        <div className="pipeline-card">
          <div className="step-num">04</div>
          <h3>Local Subprocess</h3>
          <p>Subprocess script compilation spawns local rendering pipelines producing silent frames.</p>
        </div>

        <div className="pipeline-card">
          <div className="step-num">05</div>
          <h3>Semantic QA</h3>
          <p>Validation Critic runs closed-loop visual audits, correcting code mismatches automatically.</p>
        </div>

        <div className="pipeline-card">
          <div className="step-num">06</div>
          <h3>AV Multiplexer</h3>
          <p>FFmpeg merges the source vocal tracks onto compiled animations in real-time.</p>
        </div>
      </div>
    </div>
  );
};
