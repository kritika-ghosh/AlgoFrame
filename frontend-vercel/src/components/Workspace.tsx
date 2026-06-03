import React, { useState, useRef, useEffect } from 'react';

const BACKEND_URL = 'https://huggingface.co/spaces/kritika53245/AlgoFrame';

interface WorkspaceProps {
  onBack: () => void;
}

export const Workspace: React.FC<WorkspaceProps> = ({ onBack }) => {
  const [dsType, setDsType] = useState('array');
  const [inputMode, setInputMode] = useState<'text' | 'voice'>('text');
  const [explanationText, setExplanationText] = useState('');
  
  // Audio state
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string>('');
  const [recordingTime, setRecordingTime] = useState(0);
  
  // Pipeline status state
  const [isCompiling, setIsCompiling] = useState(false);
  const [terminalLogs, setTerminalLogs] = useState<Array<{ text: string; type: 'sys' | 'agent' | 'error' }>>([]);
  const [videoBlobUrl, setVideoBlobUrl] = useState<string>('');
  const [videoSpeed, setVideoSpeed] = useState(1);
  const [errorMessage, setErrorMessage] = useState('');

  // Refs for media recording and animation
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioStreamRef = useRef<MediaStream | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const timerIntervalRef = useRef<any>(null);
  const terminalEndRef = useRef<HTMLDivElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  // Auto-scroll terminal to bottom
  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [terminalLogs]);

  // Clean up timers and audio refs
  useEffect(() => {
    return () => {
      stopRecordingResources();
    };
  }, []);

  const stopRecordingResources = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
    }
    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach((track) => track.stop());
    }
  };

  // Start Audio Recording
  const startRecording = async () => {
    setErrorMessage('');
    setAudioBlob(null);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl('');
    }
    setRecordingTime(0);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStreamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const chunks: BlobPart[] = [];
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setAudioBlob(blob);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
      };

      mediaRecorder.start();
      setIsRecording(true);

      // Start timer
      timerIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);

      // Visualize Waveform
      visualizeAudio(stream);
    } catch (err) {
      console.error('Audio capture error:', err);
      setErrorMessage('Microphone access denied or audio device not found.');
    }
  };

  // Visualize microphone audio
  const visualizeAudio = (stream: MediaStream) => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const canvasCtx = canvas.getContext('2d');
    if (!canvasCtx) return;

    const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const source = audioCtx.createMediaStreamSource(stream);
    const analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    source.connect(analyser);

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      if (!canvasCtx || !canvas) return;
      animationFrameRef.current = requestAnimationFrame(draw);
      analyser.getByteTimeDomainData(dataArray);

      canvasCtx.fillStyle = 'hsl(224, 25%, 8%)';
      canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

      canvasCtx.lineWidth = 2;
      canvasCtx.strokeStyle = 'hsl(142, 76%, 45%)';
      canvasCtx.beginPath();

      const sliceWidth = canvas.width / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvas.height) / 2;

        if (i === 0) {
          canvasCtx.moveTo(x, y);
        } else {
          canvasCtx.lineTo(x, y);
        }
        x += sliceWidth;
      }

      canvasCtx.lineTo(canvas.width, canvas.height / 2);
      canvasCtx.stroke();
    };

    draw();
  };

  // Stop Audio Recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      stopRecordingResources();
    }
  };

  // Run mock/simulated logs to terminal during execution to show compile progress
  const addLog = (text: string, type: 'sys' | 'agent' | 'error' = 'sys') => {
    const timestamp = new Date().toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
    setTerminalLogs((prev) => [...prev, { text: `[${timestamp}] ${text}`, type }]);
  };

  // Handle Submit Form to Backend
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setTerminalLogs([]);
    setVideoBlobUrl('');
    
    // Validations
    if (inputMode === 'text' && !explanationText.trim()) {
      setErrorMessage('Please enter an algorithmic explanation text.');
      return;
    }
    if (inputMode === 'voice' && !audioBlob) {
      setErrorMessage('Please record an audio prompt before compiling.');
      return;
    }

    setIsCompiling(true);
    addLog('[INIT] Establishing connection to backend API node...', 'sys');
    
    // Start progress simulation log sequence
    const logTimeline = [
      { text: `[SYS] Ingesting explanation prompt (Modality: ${inputMode.toUpperCase()})...`, delay: 1200, type: 'sys' as const },
      { text: '[SYS] Querying Groq Whisper API for voice transcript mapping...', delay: 3000, type: 'sys' as const },
      { text: '[AGENT] Lead Planner: Allocating memory states and creating layout structures...', delay: 5500, type: 'agent' as const },
      { text: '[AGENT] Manim Developer: Generating scene vectors and object nodes (scene_synthesis.py)...', delay: 8500, type: 'agent' as const },
      { text: '[SYS] Subprocess: Invoking local compiler (manim -ql -v WARNING)...', delay: 12000, type: 'sys' as const },
      { text: '[AGENT] Validator Critic: Evaluating structural correctness and checking loops...', delay: 16000, type: 'agent' as const },
      { text: '[SYS] FFmpeg: Multiplexing sound layers onto silent video channels...', delay: 19500, type: 'sys' as const },
      { text: '[SYS] Build approved! Finalizing binary asset stream...', delay: 22000, type: 'sys' as const }
    ];

    const timeouts: any[] = [];
    
    // If input mode is text, we don't need Whisper log, so skip that in display
    const filteredTimeline = inputMode === 'text' 
      ? logTimeline.filter(l => !l.text.includes('Whisper'))
      : logTimeline;

    filteredTimeline.forEach((log) => {
      const t = setTimeout(() => {
        addLog(log.text, log.type);
      }, log.delay);
      timeouts.push(t);
    });

    try {
      const formData = new FormData();
      formData.append('primitive_type', dsType);
      
      if (inputMode === 'text') {
        formData.append('explanation_text', explanationText);
      } else if (audioBlob) {
        formData.append('file', audioBlob, 'prompt_audio.wav');
      }

      const response = await fetch(`${BACKEND_URL}/api/generate-video`, {
        method: 'POST',
        body: formData,
      });

      // Clear the log timeouts
      timeouts.forEach(clearTimeout);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Backend responded with code ${response.status}`);
      }

      // Convert response stream to video blob
      const videoBlob = await response.blob();
      const videoUrl = URL.createObjectURL(videoBlob);
      
      addLog('[COMPILER SUCCESS] Algorithmic animation synthesis completed!', 'sys');
      setTimeout(() => {
        setVideoBlobUrl(videoUrl);
        setIsCompiling(false);
      }, 1000);

    } catch (err: any) {
      timeouts.forEach(clearTimeout);
      console.error(err);
      const errMsg = err.message || 'Fatal exception during pipeline compilation.';
      addLog(`[PIPELINE FAILURE] ${errMsg}`, 'error');
      setErrorMessage(errMsg);
      setIsCompiling(false);
    }
  };

  // Adjust Video Speed
  const handleSpeedChange = (speed: number) => {
    setVideoSpeed(speed);
    if (videoRef.current) {
      videoRef.current.playbackRate = speed;
    }
  };

  // Helper format time
  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remainingSecs = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${remainingSecs.toString().padStart(2, '0')}`;
  };

  // Sample prompt helpers
  const applySamplePrompt = (text: string) => {
    setExplanationText(text);
  };

  const bstSample = `Initialize a Binary Search Tree. First insert the root node 10. Next, insert 5 which goes to the left branch. Then insert 15 which goes to the right branch. Finally, traverse the tree in pre-order.`;
  const arraySample = `Create a 1D sequential array of size 5 with elements 12, 45, 78, 23, and 56. Highlight the value at index 2, swap it with the element at index 4, and visualise the pointer swap operations clearly.`;

  return (
    <div className="workspace-container">
      {/* LEFT COLUMN: CONTROL & INPUT CONFIGURATION */}
      <div className="control-panel">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
          <h2 style={{ fontSize: '1.2rem', margin: 0, letterSpacing: '0.05em' }}>INPUT PROFILE</h2>
          <button className="btn-secondary" onClick={onBack} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
            BACK TO PORTAL
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Data Structure dropdown */}
          <div className="form-group">
            <label className="form-label">Algorithm Domain</label>
            <select 
              className="select-control"
              value={dsType}
              onChange={(e) => setDsType(e.target.value)}
              disabled={isCompiling}
            >
              <option value="array">1D Sequential Array</option>
              <option value="tree">Binary Search Tree (BST)</option>
              <option value="graph">Network Graph / Node Vertices</option>
              <option value="stack">LIFO Stack Array</option>
              <option value="queue">FIFO Queue Array</option>
            </select>
          </div>

          {/* Mode Toggle */}
          <div className="form-group">
            <label className="form-label">Ingestion Modality</label>
            <div className="tabs-header">
              <button
                type="button"
                className={`tab-btn ${inputMode === 'text' ? 'active' : ''}`}
                onClick={() => !isCompiling && setInputMode('text')}
              >
                TEXT SYNTAX
              </button>
              <button
                type="button"
                className={`tab-btn ${inputMode === 'voice' ? 'active' : ''}`}
                onClick={() => !isCompiling && setInputMode('voice')}
              >
                VOICE INPUT
              </button>
            </div>
          </div>

          {/* Text Area Input */}
          {inputMode === 'text' ? (
            <div className="form-group">
              <label className="form-label">Algorithmic Instructions</label>
              <textarea
                className="textarea-control"
                placeholder="Describe node swaps, pointers, array allocations or traversal loops..."
                value={explanationText}
                onChange={(e) => setExplanationText(e.target.value)}
                disabled={isCompiling}
              />
              <div style={{ display: 'flex', gap: '8px', marginTop: '4px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', alignSelf: 'center' }}>Load template:</span>
                <button type="button" className="btn-secondary" style={{ padding: '4px 8px', fontSize: '0.7rem' }} onClick={() => applySamplePrompt(arraySample)}>Array Swap</button>
                <button type="button" className="btn-secondary" style={{ padding: '4px 8px', fontSize: '0.7rem' }} onClick={() => applySamplePrompt(bstSample)}>BST Insertion</button>
              </div>
            </div>
          ) : (
            /* Voice/Recording widget input */
            <div className="form-group">
              <label className="form-label">Acoustic Narrator Widget</label>
              <div className={`audio-recorder-box ${isRecording ? 'recording' : ''}`}>
                <div className={`recording-timer ${isRecording ? 'active' : ''}`}>
                  {formatTime(recordingTime)}
                </div>
                
                <canvas 
                  ref={canvasRef} 
                  className="waveform-canvas" 
                  width="300" 
                  height="60"
                />

                <div style={{ display: 'flex', gap: '10px', width: '100%', justifyContent: 'center' }}>
                  {!isRecording ? (
                    <button 
                      type="button" 
                      className="btn-accent-green" 
                      onClick={startRecording}
                      disabled={isCompiling}
                    >
                      🎙️ RECORD
                    </button>
                  ) : (
                    <button 
                      type="button" 
                      className="btn-accent-green" 
                      style={{ color: 'var(--color-red)', borderColor: 'var(--color-red)' }} 
                      onClick={stopRecording}
                    >
                      🛑 STOP
                    </button>
                  )}
                </div>

                {audioUrl && !isRecording && (
                  <div style={{ width: '100%' }}>
                    <p style={{ fontSize: '0.75rem', marginBottom: '6px', color: 'var(--color-cyan)' }}>Recorded Footprint Available</p>
                    <audio src={audioUrl} controls className="audio-preview-player" />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Submit Action */}
          <div style={{ marginTop: '12px' }}>
            <button 
              type="submit" 
              className="btn-primary" 
              style={{ width: '100%', justifyContent: 'center' }}
              disabled={isCompiling}
            >
              {isCompiling ? (
                <>
                  <svg className="spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="12" y1="2" x2="12" y2="6"></line>
                    <line x1="12" y1="18" x2="12" y2="22"></line>
                    <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
                    <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
                    <line x1="2" y1="12" x2="6" y2="12"></line>
                    <line x1="18" y1="12" x2="22" y2="12"></line>
                    <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
                    <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
                  </svg>
                  <span>SYNTHESIZING...</span>
                </>
              ) : (
                <>
                  <span>COMPILE ANIMATION</span>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                  </svg>
                </>
              )}
            </button>
          </div>
        </form>

        {errorMessage && (
          <div className="error-banner">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"></polygon>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <div>
              <div style={{ fontWeight: 'bold' }}>Pipeline Exception</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>{errorMessage}</div>
            </div>
          </div>
        )}
      </div>

      {/* RIGHT COLUMN: TERMINAL MONITOR & VIDEO VIEWPORT */}
      <div className="stage-panel">
        {/* State Awaiting */}
        {!isCompiling && !videoBlobUrl && (
          <div className="terminal-window">
            <div className="terminal-header">
              <div className="terminal-dots">
                <span className="dot red"></span>
                <span className="dot yellow"></span>
                <span className="dot green"></span>
              </div>
              <div className="terminal-title">ALGOFRAME COMPILE ENGINE MONITOR</div>
              <div style={{ width: '42px' }}></div>
            </div>
            <div className="terminal-content">
              <div className="terminal-line sys">algoframe@engine-node:~# status</div>
              <div className="terminal-line">System operational. Awaiting algorithmic synthesis parameters.</div>
              <div className="terminal-line text-muted">Ready to accept instruction payloads from controller panel.</div>
              <div className="terminal-line"><span className="cursor"></span></div>
            </div>
          </div>
        )}

        {/* State Compiling (Active build log) */}
        {isCompiling && (
          <div className="terminal-window">
            <div className="terminal-header">
              <div className="terminal-dots">
                <span className="dot red"></span>
                <span className="dot yellow"></span>
                <span className="dot green"></span>
              </div>
              <div className="terminal-title">SYNTHESIZING COMPILATION LOGS</div>
              <div style={{ width: '42px' }}></div>
            </div>
            <div className="terminal-content">
              {terminalLogs.map((log, idx) => (
                <div key={idx} className={`terminal-line ${log.type}`}>
                  {log.text}
                </div>
              ))}
              <div className="terminal-line"><span className="cursor"></span></div>
              <div ref={terminalEndRef} />
            </div>
          </div>
        )}

        {/* State Delivered (Custom Media Output) */}
        {videoBlobUrl && !isCompiling && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div className="output-card">
              <div style={{ backgroundColor: 'var(--bg-secondary)', padding: '12px 24px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className="node-pulse" style={{ backgroundColor: 'var(--color-cyan)', boxShadow: 'var(--shadow-cyan)' }}></span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 'bold' }}>SYNTHESIZED_ANIMATION.mp4</span>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button 
                    className="btn-secondary" 
                    onClick={() => {
                      setVideoBlobUrl('');
                      setTerminalLogs([]);
                    }}
                    style={{ padding: '6px 12px', fontSize: '0.75rem' }}
                  >
                    RESET
                  </button>
                </div>
              </div>

              <div className="video-wrapper">
                <video 
                  ref={videoRef}
                  src={videoBlobUrl} 
                  controls 
                  autoPlay
                  loop
                />
              </div>

              <div className="output-controls">
                <div className="speed-control-group">
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>PLAY RATE:</span>
                  {[0.5, 1, 1.5, 2].map((speed) => (
                    <button
                      key={speed}
                      className={`speed-btn ${videoSpeed === speed ? 'active' : ''}`}
                      onClick={() => handleSpeedChange(speed)}
                    >
                      {speed}x
                    </button>
                  ))}
                </div>

                <a 
                  href={videoBlobUrl} 
                  download={`algoframe_${dsType}_animation.mp4`}
                  className="btn-primary"
                  style={{ padding: '8px 18px', fontSize: '0.85rem' }}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                  <span>DOWNLOAD MP4</span>
                </a>
              </div>
            </div>

            {/* Manim Code Structure container */}
            <div className="terminal-window" style={{ minHeight: '150px', maxHeight: '250px' }}>
              <div className="terminal-header">
                <div className="terminal-title">SYNTHESIZED MANIM TEMPLATE SPECIFICATION</div>
              </div>
              <div className="terminal-content" style={{ color: 'var(--text-secondary)' }}>
                <pre style={{ margin: 0, fontSize: '0.75rem' }}>{`from manim import *

class ArrayInitialization(Scene):
    def construct(self):
        # 1. Scaffolding nodes for dynamic visualization
        title = Text("AlgoFrame AI: ${dsType.toUpperCase()} Operation", font_size=32)
        title.to_edge(UP)
        self.play(Write(title))
        
        # 2. Re-compiling indices and mathematical constraints
        # Final output rendered under 1080p constraints...
        self.wait(1)
`}</pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
