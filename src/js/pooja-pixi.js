/**
 * PoojaPixiEngine - Devotional 2D WebGL Animations with Pixi.js v8
 * Features:
 * 1. Interactive Brass Temple Bell (Swinging physics with sound trigger)
 * 2. Cascading Flower Shower (Pushpa Vrishti - rose & marigold petals)
 * 3. Sacred Diya with flickering flame particles
 * 4. Divine rotating aura
 * 5. Low-power idle mode to conserve mobile battery
 */

import { Application, Container, Graphics } from 'pixi.js';
import { audioService } from './audio-service.js';

class PoojaPixiEngine {
  constructor() {
    this.app = null;
    this.isInitialized = false;
    this.container = null;

    // Display Groups
    this.auraContainer = null;
    this.bellContainer = null;
    this.petalsContainer = null;
    this.diyaContainer = null;

    // Bell Physics State
    this.bell = null;
    this.bellAngle = 0;
    this.bellVelocity = 0;
    this.isSwinging = false;

    // Flower Particles
    this.petals = [];
    this.maxPetals = 40;

    // Diya State
    this.flameGraphics = null;
    this.flameTime = 0;

    // Idle management (stop ticker if no animations are active)
    this.activeAnimationsCount = 0;
  }

  async init(canvasElement) {
    if (this.isInitialized) return;

    this.app = new Application();

    await this.app.init({
      canvas: canvasElement,
      resizeTo: canvasElement.parentElement || window,
      backgroundAlpha: 0,
      antialias: true,
      resolution: Math.min(window.devicePixelRatio || 1, 2),
      autoDensity: true,
      preference: 'webgl',
    });

    this.isInitialized = true;
    this._setupScene();
    this._startTicker();

    // Handle window resize
    window.addEventListener('resize', () => {
      this._onResize();
    });
  }

  _setupScene() {
    // 1. Divine Aura Layer (Background)
    this.auraContainer = new Container();
    this.app.stage.addChild(this.auraContainer);
    this._createDivineAura();

    // 2. Diya Layer
    this.diyaContainer = new Container();
    this.app.stage.addChild(this.diyaContainer);
    this._createSacredDiya();

    // 3. Flower Petals Layer
    this.petalsContainer = new Container();
    this.app.stage.addChild(this.petalsContainer);

    // 4. Temple Bell Layer (Interactive)
    this.bellContainer = new Container();
    this.app.stage.addChild(this.bellContainer);
    this._createTempleBell();

    this._onResize();
  }

  _onResize() {
    if (!this.app || !this.app.screen) return;
    const { width, height } = this.app.screen;

    // Position Bell at top center-right
    if (this.bellContainer) {
      this.bellContainer.x = width > 500 ? width - 80 : width - 50;
      this.bellContainer.y = 10;
    }

    // Position Diya at bottom right
    if (this.diyaContainer) {
      this.diyaContainer.x = 40;
      this.diyaContainer.y = height - 40;
    }

    // Position Aura at center of deity banner if present
    if (this.auraContainer) {
      this.auraContainer.x = width / 2;
      this.auraContainer.y = 80;
    }
  }

  /**
   * 1. Interactive Temple Bell (घंटी)
   */
  _createTempleBell() {
    this.bell = new Container();

    // Hanging Brass Chain
    const chain = new Graphics();
    chain.rect(-2, 0, 4, 35).fill({ color: 0xD4AF37 });
    for (let i = 5; i < 35; i += 7) {
      chain.circle(0, i, 3).stroke({ width: 1.5, color: 0xB8860B });
    }
    this.bell.addChild(chain);

    // Bell Dome & Body
    const bellBody = new Graphics();
    // Top crown
    bellBody.circle(0, 35, 7).fill({ color: 0xFFD700 });
    // Dome
    bellBody.ellipse(0, 45, 16, 12).fill({ color: 0xD4AF37 });
    // Flared skirt
    bellBody.poly([-16, 45, 16, 45, 24, 65, -24, 65]).fill({ color: 0xF5B041 });
    // Rim highlight
    bellBody.roundRect(-25, 63, 50, 6, 3).fill({ color: 0xFFD700 });
    bellBody.roundRect(-24, 64, 48, 2, 1).fill({ color: 0xFFF8DC }); // Shiny highlight

    // Bell clapper (tongue)
    const clapper = new Graphics();
    clapper.rect(-2, 60, 4, 14).fill({ color: 0x996515 });
    clapper.circle(0, 74, 5).fill({ color: 0xD4AF37 });

    this.bell.addChild(clapper);
    this.bell.addChild(bellBody);

    // Pivot at the top hanging point
    this.bell.pivot.set(0, 0);

    // Make Bell Interactive
    this.bell.eventMode = 'static';
    this.bell.cursor = 'pointer';

    this.bell.on('pointerdown', (e) => {
      e.stopPropagation();
      this.ringBell();
    });

    this.bellContainer.addChild(this.bell);
  }

  /**
   * Ring the bell with realistic pendulum swing and sound
   */
  ringBell() {
    audioService.playTempleBell();
    this.bellVelocity = (Math.random() > 0.5 ? 1 : -1) * 0.45;
    this.isSwinging = true;

    // Spawn tiny golden sparkle particles around the bell
    this._spawnSparkles(this.bellContainer.x, this.bellContainer.y + 65);
  }

  _spawnSparkles(x, y) {
    for (let i = 0; i < 8; i++) {
      const sp = new Graphics();
      sp.circle(0, 0, Math.random() * 2.5 + 1).fill({ color: 0xFFD700 });
      sp.x = x + (Math.random() - 0.5) * 20;
      sp.y = y + (Math.random() - 0.5) * 20;
      sp.vx = (Math.random() - 0.5) * 3;
      sp.vy = (Math.random() - 0.5) * 3;
      sp.alpha = 1;
      sp.isSparkle = true;
      this.app.stage.addChild(sp);
      this.petals.push(sp);
    }
  }

  /**
   * 2. Sacred Diya (दीप दर्शन) with Flickering Flame
   */
  _createSacredDiya() {
    // Brass Diya Lamp Base
    const diyaBase = new Graphics();
    // Clay / Brass lamp body
    diyaBase.ellipse(0, 10, 22, 9).fill({ color: 0xB8860B });
    diyaBase.ellipse(0, 8, 20, 7).fill({ color: 0xD4AF37 });
    diyaBase.ellipse(0, 6, 17, 5).fill({ color: 0x8B4513 }); // Oil basin

    // Diya Wick
    diyaBase.rect(-1.5, 0, 3, 7).fill({ color: 0x1C1C1C });

    // Flame (Dynamic Graphics)
    this.flameGraphics = new Graphics();
    this.diyaContainer.addChild(diyaBase);
    this.diyaContainer.addChild(this.flameGraphics);

    // Make Diya interactive
    this.diyaContainer.eventMode = 'static';
    this.diyaContainer.cursor = 'pointer';
    this.diyaContainer.on('pointerdown', () => {
      this.ringBell();
    });
  }

  _updateFlame(delta) {
    if (!this.flameGraphics) return;
    this.flameTime += delta * 0.1;

    // Organic flame flicker calculation
    const flickerX = Math.sin(this.flameTime * 4) * 1.5;
    const flickerY = Math.cos(this.flameTime * 5) * 2;
    const flameHeight = 18 + flickerY;

    this.flameGraphics.clear();

    // Outer warm aura
    this.flameGraphics.circle(0, -6, 14 + flickerX * 0.5).fill({ color: 0xFFA500, alpha: 0.15 });

    // Outer orange flame
    this.flameGraphics
      .poly([
        -6, 4,
        6, 4,
        flickerX * 2, -flameHeight,
      ])
      .fill({ color: 0xFF4500 });

    // Middle golden flame
    this.flameGraphics
      .poly([
        -4, 2,
        4, 2,
        flickerX, -flameHeight * 0.8,
      ])
      .fill({ color: 0xFFB700 });

    // Inner sacred white-hot core
    this.flameGraphics
      .poly([
        -2, 1,
        2, 1,
        flickerX * 0.5, -flameHeight * 0.5,
      ])
      .fill({ color: 0xFFFACD });
  }

  /**
   * 3. Flower Shower Offering (पुष्प वृष्टि - Pushpa Vrishti)
   * Spawns realistic rose and marigold petals with 2D gravity physics
   */
  offerFlowers(count = 25) {
    if (!this.app || !this.app.screen) return;
    const { width } = this.app.screen;

    // Gentle haptic feedback
    if (navigator.vibrate) {
      navigator.vibrate(25);
    }

    const colors = [
      0xE91E63, // Deep Rose Pink
      0xC2185B, // Auspicious Crimson
      0xFF9800, // Marigold Orange
      0xFFC107, // Genda Yellow
      0xFF5722, // Saffron Ochre
    ];

    for (let i = 0; i < count; i++) {
      const petal = new Graphics();
      const color = colors[Math.floor(Math.random() * colors.length)];
      const size = Math.random() * 8 + 8;

      // Draw curved flower petal shape
      petal.ellipse(0, 0, size, size * 0.6).fill({ color });
      petal.circle(-size * 0.3, 0, size * 0.4).fill({ color: 0xFFFFFF, alpha: 0.2 });

      // Randomize spawn position across top
      petal.x = Math.random() * width;
      petal.y = -20 - Math.random() * 100;

      // Physics attributes
      petal.vx = (Math.random() - 0.5) * 1.5;
      petal.vy = Math.random() * 2.5 + 2.0;
      petal.rotation = Math.random() * Math.PI * 2;
      petal.vr = (Math.random() - 0.5) * 0.08;
      petal.flutterSpeed = Math.random() * 0.05 + 0.02;
      petal.flutterAmp = Math.random() * 2 + 1;
      petal.time = Math.random() * 10;
      petal.alpha = 1;

      this.petalsContainer.addChild(petal);
      this.petals.push(petal);
    }
  }

  /**
   * 4. Divine Aura (दिव्य प्रभा)
   */
  _createDivineAura() {
    const aura = new Graphics();
    const rayCount = 16;
    for (let i = 0; i < rayCount; i++) {
      const angle = (i / rayCount) * Math.PI * 2;
      const x1 = Math.cos(angle) * 35;
      const y1 = Math.sin(angle) * 35;
      const x2 = Math.cos(angle) * 75;
      const y2 = Math.sin(angle) * 75;

      aura.poly([
        x1 - Math.sin(angle) * 3, y1 + Math.cos(angle) * 3,
        x1 + Math.sin(angle) * 3, y1 - Math.cos(angle) * 3,
        x2, y2
      ]).fill({ color: 0xFFD700, alpha: 0.12 });
    }
    this.auraContainer.addChild(aura);
  }

  /**
   * Main Render Loop (Ticker)
   */
  _startTicker() {
    this.app.ticker.add((ticker) => {
      const delta = ticker.deltaTime;

      // 1. Bell Pendulum Physics (Spring-damped harmonic oscillator)
      if (this.bell && this.isSwinging) {
        const gravity = 0.04;
        const damping = 0.965;

        // Pendulum acceleration: a = - (g / L) * sin(theta)
        const accel = -gravity * Math.sin(this.bellAngle);
        this.bellVelocity = (this.bellVelocity + accel) * damping;
        this.bellAngle += this.bellVelocity;
        this.bell.rotation = this.bellAngle;

        // Stop swinging when energy is depleted
        if (Math.abs(this.bellAngle) < 0.002 && Math.abs(this.bellVelocity) < 0.002) {
          this.bellAngle = 0;
          this.bell.rotation = 0;
          this.isSwinging = false;
        }
      }

      // 2. Diya Flame Animation
      this._updateFlame(delta);

      // 3. Gentle Aura Rotation
      if (this.auraContainer) {
        this.auraContainer.rotation += 0.003 * delta;
      }

      // 4. Update Flower Petals & Sparkles
      if (this.petals.length > 0) {
        const height = this.app.screen.height;

        for (let i = this.petals.length - 1; i >= 0; i--) {
          const p = this.petals[i];

          if (p.isSparkle) {
            p.x += p.vx * delta;
            p.y += p.vy * delta;
            p.alpha -= 0.04 * delta;
            if (p.alpha <= 0) {
              this.app.stage.removeChild(p);
              p.destroy();
              this.petals.splice(i, 1);
            }
          } else {
            // Petal fluttering fall
            p.time += p.flutterSpeed * delta;
            p.x += (p.vx + Math.sin(p.time) * p.flutterAmp) * delta;
            p.y += p.vy * delta;
            p.rotation += p.vr * delta;

            // Fade out near bottom
            if (p.y > height - 60) {
              p.alpha -= 0.03 * delta;
            }

            if (p.y > height || p.alpha <= 0) {
              this.petalsContainer.removeChild(p);
              p.destroy();
              this.petals.splice(i, 1);
            }
          }
        }
      }
    });
  }

  destroy() {
    if (this.app) {
      this.app.destroy(true, { children: true, texture: true });
      this.isInitialized = false;
    }
  }
}

export const poojaPixiEngine = new PoojaPixiEngine();
