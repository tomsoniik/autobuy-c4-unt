import React from 'react';
import { Download, Crosshair, Shield, Zap, Terminal, Activity, CheckCircle2 } from 'lucide-react';
import './index.css';

function App() {
  return (
    <>
      <header className="header">
        <div className="logo">
          <Terminal size={28} color="#8b5cf6" />
          777<span>client</span>
        </div>
        <nav>
          <a href="#features" className="btn-secondary" style={{ padding: '8px 16px', fontSize: '0.9rem' }}>
            Features
          </a>
        </nav>
      </header>

      <main>
        <section className="hero">
          <div className="hero-badge">
            <Activity size={16} />
            <span>v2.4.0 is now live</span>
          </div>
          <h1>
            <span className="text-gradient">Automate. Dominate.</span>
            <br />
            <span className="text-gradient-primary">Win.</span>
          </h1>
          <p>
            The ultimate utility toolkit for Unturned. Featuring advanced No-Shake Recoil Control and a fully automated C4 Auto-Crafter. Experience pixel-perfect precision.
          </p>
          <div className="hero-actions">
            <button className="btn-primary">
              <Download size={20} />
              Download Now
            </button>
            <button className="btn-secondary">
              View Documentation
            </button>
          </div>
        </section>

        <section id="features" className="features">
          <h2 className="section-title">Why choose <span className="text-gradient-primary">777client</span>?</h2>
          <div className="features-grid">
            <div className="glass-panel feature-card">
              <div className="feature-icon icon-purple">
                <Crosshair size={28} />
              </div>
              <h3>Pixel-Perfect Recoil</h3>
              <p>Hardware-level input simulation with sub-pixel movement accumulation for zero-shake, laser-accurate spray control across all weapons.</p>
            </div>

            <div className="glass-panel feature-card">
              <div className="feature-icon icon-green">
                <Zap size={28} />
              </div>
              <h3>C4 Auto-Crafter</h3>
              <p>Fully automated macro that buys resources, clears UI elements, and crafts C4 charges while you're AFK. Includes smart OCR for error detection.</p>
            </div>

            <div className="glass-panel feature-card">
              <div className="feature-icon icon-orange">
                <Shield size={28} />
              </div>
              <h3>Auto-Detection</h3>
              <p>Smart screen scanning automatically detects your equipped weapon (Maplestrike, Zubeknakov, etc.) and adjusts the recoil pull profile seamlessly.</p>
            </div>
          </div>
        </section>

        <section className="preview-section">
          <h2 className="section-title">Designed for <span className="text-gradient">Simplicity</span></h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem', maxWidth: '600px' }}>
            A beautiful, intuitive GUI built with CustomTkinter. No more messy config files. Just plug, play, and dominate.
          </p>
          
          <div className="mockup-container">
            <div className="mockup-header">
              <div className="dot red"></div>
              <div className="dot yellow"></div>
              <div className="dot green"></div>
            </div>
            <div className="mockup-body">
              <div className="mockup-panel">
                <div className="mockup-title">
                  <Activity size={24} color="#8b5cf6" />
                  Auto-Crafter C4
                </div>
                <div className="toggle-row">
                  <span className="toggle-label">Makeshift Grenade (/b 1242 10)</span>
                  <div className="toggle-switch"></div>
                </div>
                <div className="toggle-row">
                  <span className="toggle-label">Wire (/b 65 10)</span>
                  <div className="toggle-switch"></div>
                </div>
                <div className="toggle-row">
                  <span className="toggle-label">Glue (/b glue 10)</span>
                  <div className="toggle-switch"></div>
                </div>
                <div className="toggle-row" style={{ marginTop: '20px' }}>
                  <span className="toggle-label" style={{ color: '#f59e0b' }}>AFK Mode (Infinite Loop)</span>
                  <div className="toggle-switch"></div>
                </div>
              </div>

              <div className="mockup-panel">
                <div className="mockup-title">
                  <Crosshair size={24} color="#ef4444" />
                  Recoil Control
                </div>
                <div className="toggle-row">
                  <span className="toggle-label" style={{ color: '#10b981' }}>Weapon Auto-Detection</span>
                  <div className="toggle-switch"></div>
                </div>
                <div className="toggle-row">
                  <span className="toggle-label">Aim Down Sights Only (RMB)</span>
                  <div className="toggle-switch"></div>
                </div>
                <div style={{ marginTop: '20px', padding: '15px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.85rem', color: 'gray', marginBottom: '8px' }}>Detected Weapon:</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#3b82f6', fontWeight: 'bold' }}>
                    <CheckCircle2 size={16} />
                    MAPLESTRIKE (Hip: 15.00)
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}

export default App;
