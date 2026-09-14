/**
 * AudioService - Devotional Sound Engine
 * Uses Web Audio API for 100% offline, realistic temple bell chimes and shankh resonance.
 */

class AudioService {
  constructor() {
    this.ctx = null;
    this.isMuted = false;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  /**
   * Synthesize a sacred brass temple bell chime with rich harmonics and natural reverb decay
   */
  playTempleBell() {
    if (this.isMuted) return;
    this.init();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    
    // Brass bell harmonic partials (Frequency ratios and relative amplitudes)
    const partials = [
      { ratio: 1.0, gain: 0.8, decay: 2.8 },    // Fundamental strike tone
      { ratio: 1.5, gain: 0.5, decay: 2.2 },    // Fifth
      { ratio: 2.0, gain: 0.4, decay: 1.8 },    // Octave
      { ratio: 2.76, gain: 0.35, decay: 1.5 },  // Minor tenth
      { ratio: 3.8, gain: 0.2, decay: 1.2 },    // Upper resonance
      { ratio: 5.2, gain: 0.15, decay: 0.9 },   // Shimmer
    ];

    const baseFreq = 528; // 528 Hz - Solfeggio "transformation and miracles" frequency

    partials.forEach(p => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(baseFreq * p.ratio, now);

      // Strike attack & exponential bell ring decay
      gain.gain.setValueAtTime(0.001, now);
      gain.gain.exponentialRampToValueAtTime(p.gain * 0.4, now + 0.008);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + p.decay);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + p.decay);
    });

    // Provide haptic feedback if available
    if (navigator.vibrate) {
      navigator.vibrate(35);
    }
  }

  /**
   * Deep sacred Shankh (Conch shell) resonance sound
   */
  playShankh() {
    if (this.isMuted) return;
    this.init();
    if (!this.ctx) return;

    const now = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sawtooth';
    // Gentle glissando up like blowing a sacred conch
    osc.frequency.setValueAtTime(140, now);
    osc.frequency.exponentialRampToValueAtTime(220, now + 0.4);
    osc.frequency.exponentialRampToValueAtTime(210, now + 2.0);

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(450, now);

    gain.gain.setValueAtTime(0.001, now);
    gain.gain.exponentialRampToValueAtTime(0.3, now + 0.3);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 2.2);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start(now);
    osc.stop(now + 2.3);

    if (navigator.vibrate) {
      navigator.vibrate([60, 40, 80]);
    }
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    return this.isMuted;
  }
}

export const audioService = new AudioService();
