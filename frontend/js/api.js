/**
 * KAVACH API CLIENT & AUDIO ENGINE
 */

const KavachAPI = {
  // Web Audio Synthesizer for High-Tech Sound FX
  audioCtx: null,
  soundEnabled: true,

  initAudio() {
    if (!this.audioCtx && (window.AudioContext || window.webkitAudioContext)) {
      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      this.audioCtx = new AudioCtxClass();
    }
    if (this.audioCtx && this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
  },

  setSoundEnabled(enabled) {
    this.soundEnabled = enabled;
  },

  playScanSound() {
    if (!this.soundEnabled) return;
    try {
      this.initAudio();
      if (!this.audioCtx) return;
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = 'sawtooth';
      
      const now = this.audioCtx.currentTime;
      osc.frequency.setValueAtTime(220, now);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.35);
      
      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start(now);
      osc.stop(now + 0.36);
    } catch (e) {
      console.warn('Audio not supported or blocked:', e);
    }
  },

  playResultSound(verdict) {
    if (!this.soundEnabled) return;
    try {
      this.initAudio();
      if (!this.audioCtx) return;
      const now = this.audioCtx.currentTime;

      if (verdict === 'scam') {
        // Dramatic Alert Klaxon
        [180, 140, 220].forEach((freq, i) => {
          const osc = this.audioCtx.createOscillator();
          const gain = this.audioCtx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(freq, now + i * 0.12);
          gain.gain.setValueAtTime(0.12, now + i * 0.12);
          gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.12 + 0.2);
          osc.connect(gain);
          gain.connect(this.audioCtx.destination);
          osc.start(now + i * 0.12);
          osc.stop(now + i * 0.12 + 0.22);
        });
      } else if (verdict === 'suspicious') {
        // Warning chime
        [350, 440].forEach((freq, i) => {
          const osc = this.audioCtx.createOscillator();
          const gain = this.audioCtx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now + i * 0.14);
          gain.gain.setValueAtTime(0.1, now + i * 0.14);
          gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.14 + 0.25);
          osc.connect(gain);
          gain.connect(this.audioCtx.destination);
          osc.start(now + i * 0.14);
          osc.stop(now + i * 0.14 + 0.26);
        });
      } else {
        // Safe pleasant arpeggio
        [440, 554.37, 659.25].forEach((freq, i) => {
          const osc = this.audioCtx.createOscillator();
          const gain = this.audioCtx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now + i * 0.1);
          gain.gain.setValueAtTime(0.08, now + i * 0.1);
          gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.1 + 0.3);
          osc.connect(gain);
          gain.connect(this.audioCtx.destination);
          osc.start(now + i * 0.1);
          osc.stop(now + i * 0.1 + 0.32);
        });
      }
    } catch (e) {
      console.warn('Audio play failed:', e);
    }
  },

  // API Calls
  async getHealth() {
    try {
      const res = await fetch('/api/health');
      if (!res.ok) throw new Error('Health check failed');
      return await res.json();
    } catch (e) {
      return { status: 'offline', ollama_running: false, model: 'gemma4:e4b' };
    }
  },

  async getSamples() {
    try {
      const res = await fetch('/api/samples');
      if (!res.ok) throw new Error('Failed to load samples');
      return await res.json();
    } catch (e) {
      console.error(e);
      return [];
    }
  },

  async checkThreat({ imageFile, text, language = 'en' }) {
    const formData = new FormData();
    if (imageFile) {
      formData.append('image', imageFile);
    }
    if (text) {
      formData.append('text', text);
    }
    formData.append('language', language);

    const res = await fetch('/api/check', {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errData.detail || 'Threat verification failed');
    }

    return await res.json();
  },

  async quickRuleCheck(text) {
    try {
      const res = await fetch('/api/quick-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) throw new Error('Quick check failed');
      return await res.json();
    } catch (e) {
      console.error(e);
      return null;
    }
  }
};

window.KavachAPI = KavachAPI;
