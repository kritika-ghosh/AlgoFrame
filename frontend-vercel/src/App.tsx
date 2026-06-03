import { useState, useEffect } from 'react';
import { LandingPage } from './components/LandingPage';
import { Workspace } from './components/Workspace';

const BACKEND_URL = 'https://huggingface.co/spaces/kritika53245/AlgoFrame';

function App() {
  const [page, setPage] = useState<'landing' | 'workspace'>('landing');
  const [systemStatus, setSystemStatus] = useState<'online' | 'waking_up' | 'offline'>('waking_up');

  // Verify backend system health status on mount
  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/health`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json'
          }
        });
        
        if (response.ok) {
          setSystemStatus('online');
        } else {
          setSystemStatus('waking_up');
        }
      } catch (err) {
        console.warn('Backend is offline or waking up:', err);
        setSystemStatus('offline');
      }
    };

    checkSystemHealth();
    // Poll status check every 30 seconds
    const interval = setInterval(checkSystemHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      {/* CRT scanline simulation */}
      <div className="crt-effect"></div>

      {/* Top Status Header */}
      <header className="status-header">
        <div className="logo-block">
          <div className="logo-text">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--color-cyan)' }}>
              <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
              <polyline points="2 17 12 22 22 17"></polyline>
              <polyline points="2 12 12 17 22 12"></polyline>
            </svg>
            ALGOFRAME AI
          </div>
        </div>

        <div className="system-status">
          <div className="status-indicator">
            <span>CORE NODE:</span>
            {systemStatus === 'online' && (
              <>
                <span className="node-pulse" style={{ backgroundColor: 'var(--color-green)', boxShadow: 'var(--shadow-green)' }}></span>
                <span style={{ color: 'var(--color-green)' }}>OPERATIONAL</span>
              </>
            )}
            {systemStatus === 'waking_up' && (
              <>
                <span className="node-pulse" style={{ backgroundColor: 'var(--color-amber)', boxShadow: '0 0 10px var(--color-amber)', animationDuration: '1s' }}></span>
                <span style={{ color: 'var(--color-amber)' }}>WAKING UP / INITIALIZING</span>
              </>
            )}
            {systemStatus === 'offline' && (
              <>
                <span className="node-pulse" style={{ backgroundColor: 'var(--color-red)', boxShadow: '0 0 10px var(--color-red)' }}></span>
                <span style={{ color: 'var(--color-red)' }}>NODE FAULT / DISCONNECTED</span>
              </>
            )}
          </div>
          <div>
            <span>NODE_ID: hf-space-core-2026</span>
          </div>
        </div>
      </header>

      {/* Main Pages */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {page === 'landing' ? (
          <LandingPage onStart={() => setPage('workspace')} />
        ) : (
          <Workspace onBack={() => setPage('landing')} />
        )}
      </main>
    </div>
  );
}

export default App;
