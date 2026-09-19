/**
 * ReaderController - Sacred Aarti Reading Canvas Controller
 * Features:
 * - Hands-free variable Auto-Scroll Engine (+ / - / Pause)
 * - Dynamic Font Scaling (A- / A+)
 * - Screen WakeLock (prevents screen dimming during Pooja)
 * - Devanagari & Transliteration Switcher
 * - Theme Switcher (Ivory / Night / Parchment)
 * - Native Web Share
 * - Virtual Pooja offerings (Flowers & Bell)
 */

import { storageService } from './storage.js';
import { audioService } from './audio-service.js';
import { poojaPixiEngine } from './pooja-pixi.js';

class ReaderController {
  constructor() {
    this.currentArti = null;
    this.wakeLock = null;

    this.wakeLock = null;

    // DOM Elements cache
    this.dom = {};
  }

  init(domElements) {
    this.dom = domElements;
    this._bindEvents();
    this.applySettings();
  }

  _bindEvents() {
    // Font Resizing
    if (this.dom.btnFontDec) {
      this.dom.btnFontDec.addEventListener('click', () => this.adjustFontSize(-2));
    }
    if (this.dom.btnFontInc) {
      this.dom.btnFontInc.addEventListener('click', () => this.adjustFontSize(2));
    }

    // Devotional Offerings
    if (this.dom.btnOfferFlowers) {
      this.dom.btnOfferFlowers.addEventListener('click', () => {
        poojaPixiEngine.offerFlowers(30);
      });
    }
    if (this.dom.btnRingBell) {
      this.dom.btnRingBell.addEventListener('click', () => {
        poojaPixiEngine.ringBell();
      });
    }
    if (this.dom.btnSoundShankh) {
      this.dom.btnSoundShankh.addEventListener('click', () => {
        audioService.playShankh();
      });
    }

    // Share Aarti
    if (this.dom.btnShare) {
      this.dom.btnShare.addEventListener('click', () => this.shareLyrics());
    }

    // Favorite Toggle
    if (this.dom.btnFavorite) {
      this.dom.btnFavorite.addEventListener('click', () => this.toggleFavorite());
    }

    // Transliteration Toggle
    if (this.dom.btnToggleScript) {
      this.dom.btnToggleScript.addEventListener('click', () => this.toggleScript());
    }

    // Reading Themes
    if (this.dom.themeButtons) {
      this.dom.themeButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
          const theme = e.currentTarget.dataset.theme;
          this.setTheme(theme);
        });
      });
    }
  }

  loadArti(arti) {
    this.currentArti = arti;
    storageService.addRecent(arti.id);

    // Request Screen WakeLock
    this.requestWakeLock();

    // Populate UI
    if (this.dom.artiTitle) {
      this.dom.artiTitle.textContent = arti.title_devanagari;
    }
    if (this.dom.artiSubTitle) {
      this.dom.artiSubTitle.textContent = `${arti.deity} • ${arti.author || 'पारंपरिक'} • ${arti.language}`;
    }
    if (this.dom.artiMeaning) {
      this.dom.artiMeaning.textContent = arti.meaning_short || '';
    }
    if (this.dom.readerImageWrap && this.dom.readerImg) {
      if (arti.image) {
        this.dom.readerImg.src = arti.image;
        this.dom.readerImageWrap.style.display = 'block';
      } else {
        this.dom.readerImageWrap.style.display = 'none';
      }
    }

    this._updateFavoriteButton();
    this.renderLyrics();

    // Scroll to top
    if (this.dom.readerScrollContainer) {
      this.dom.readerScrollContainer.scrollTop = 0;
    }
  }

  renderLyrics() {
    if (!this.currentArti || !this.dom.lyricsContainer) return;
    const settings = storageService.getSettings();

    this.dom.lyricsContainer.innerHTML = '';

    const transliterationData = this.currentArti.lyrics_hinglish || this.currentArti.lyrics_transliteration;
    const transLines = typeof transliterationData === 'string' ? transliterationData.split('\n') : transliterationData;

    if (settings.showTransliteration && transLines && transLines.length > 0) {
      // English Transliteration view
      const transBlock = document.createElement('div');
      transBlock.className = 'lyrics-transliteration';
      transBlock.innerHTML = transLines
        .map(line => (line && line.trim()) ? `<p class="lyrics-line">${line.trim()}</p>` : '<div class="lyrics-spacer"></div>')
        .join('');
      this.dom.lyricsContainer.appendChild(transBlock);
    } else {
      // Authentic Devanagari view
      if (this.currentArti.lyrics_devanagari && this.currentArti.lyrics_devanagari.length > 0) {
        this.currentArti.lyrics_devanagari.forEach((section, index) => {
          const secEl = document.createElement('div');
          secEl.className = `lyrics-section lyrics-${section.type}`;

          if (section.type === 'chorus') {
            const chorusBadge = document.createElement('div');
            chorusBadge.className = 'section-badge';
            chorusBadge.textContent = '॥ मुख्य चौपाई / Chorus ॥';
            secEl.appendChild(chorusBadge);
          }

          section.lines.forEach(line => {
            const p = document.createElement('p');
            p.className = 'lyrics-line';
            p.textContent = line;
            secEl.appendChild(p);
          });

          this.dom.lyricsContainer.appendChild(secEl);
        });
      } else if (this.currentArti.lyrics_hindi_plain) {
        // Fallback for plain text Hindi
        const plainBlock = document.createElement('div');
        plainBlock.className = 'lyrics-section';
        const lines = this.currentArti.lyrics_hindi_plain.split('\n');
        lines.forEach(line => {
          if (line.trim()) {
            const p = document.createElement('p');
            p.className = 'lyrics-line';
            p.textContent = line.trim();
            plainBlock.appendChild(p);
          } else {
            const spacer = document.createElement('div');
            spacer.className = 'lyrics-spacer';
            plainBlock.appendChild(spacer);
          }
        });
        this.dom.lyricsContainer.appendChild(plainBlock);
      }
    }

    // Closing Mangalacharan / Shloka marker
    const footerMark = document.createElement('div');
    footerMark.className = 'lyrics-footer-mark';
    footerMark.innerHTML = '<span>॥ इति सम्पूर्णम् ॥</span><br><small>हरि ॐ तत्सत्</small>';
    this.dom.lyricsContainer.appendChild(footerMark);
  }

  /* --- WakeLock (Keep Screen Awake during Puja) --- */
  async requestWakeLock() {
    if ('wakeLock' in navigator) {
      try {
        this.wakeLock = await navigator.wakeLock.request('screen');
        this.wakeLock.addEventListener('release', () => {
          this.wakeLock = null;
        });
      } catch (err) {
        console.warn('Screen WakeLock error:', err);
      }
    }
  }

  releaseWakeLock() {
    if (this.wakeLock) {
      this.wakeLock.release();
      this.wakeLock = null;
    }
  }


  /* --- Font Resizing --- */
  adjustFontSize(delta) {
    const settings = storageService.getSettings();
    const newSize = Math.max(16, Math.min(34, settings.fontSize + delta));
    storageService.updateSettings({ fontSize: newSize });
    this.applySettings();
  }

  /* --- Themes & Settings --- */
  setTheme(themeName) {
    storageService.updateSettings({ theme: themeName });
    this.applySettings();
  }

  toggleScript() {
    const settings = storageService.getSettings();
    storageService.updateSettings({ showTransliteration: !settings.showTransliteration });
    this.renderLyrics();
    if (this.dom.btnToggleScript) {
      this.dom.btnToggleScript.textContent = !settings.showTransliteration ? 'देवनागरी' : 'English';
    }
  }

  applySettings() {
    const settings = storageService.getSettings();

    // Font size
    document.documentElement.style.setProperty('--lyrics-font-size', `${settings.fontSize}px`);
    if (this.dom.fontSizeLabel) {
      this.dom.fontSizeLabel.textContent = `${settings.fontSize}px`;
    }

    // Theme class on document body
    document.body.classList.remove('theme-ivory', 'theme-night', 'theme-parchment');
    document.body.classList.add(settings.theme);

    if (this.dom.themeButtons) {
      this.dom.themeButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === settings.theme);
      });
    }
  }

  /* --- Favorites Toggle --- */
  toggleFavorite() {
    if (!this.currentArti) return;
    const isFav = storageService.toggleFavorite(this.currentArti.id);
    this._updateFavoriteButton();

    if (navigator.vibrate) {
      navigator.vibrate(40);
    }
  }

  _updateFavoriteButton() {
    if (!this.dom.btnFavorite || !this.currentArti) return;
    const isFav = storageService.isFavorite(this.currentArti.id);
    this.dom.btnFavorite.classList.toggle('is-favorited', isFav);
    this.dom.btnFavorite.innerHTML = isFav
      ? '<span class="icon">⭐</span>'
      : '<span class="icon">☆</span>';
  }

  /* --- Social Share --- */
  async shareLyrics() {
    if (!this.currentArti) return;

    const lyricsText = this.currentArti.lyrics_devanagari
      .map(sec => sec.lines.join('\n'))
      .join('\n\n');

    const shareData = {
      title: `${this.currentArti.title_devanagari} (${this.currentArti.title})`,
      text: `॥ ${this.currentArti.title_devanagari} ॥\n\n${lyricsText}\n\n— आरती संग्रह (Aarti Sangrah App)`,
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
      } catch (err) {
        // User cancelled or share error
      }
    } else if (navigator.clipboard) {
      await navigator.clipboard.writeText(shareData.text);
      alert('आरती कॉपी हो गई है! आप इसे WhatsApp पर शेयर कर सकते हैं। (Aarti copied to clipboard!)');
    }
  }

  cleanup() {
    this.releaseWakeLock();
  }
}

export const readerController = new ReaderController();
