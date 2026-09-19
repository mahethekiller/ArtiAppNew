/**
 * Main Application Router & Controller
 * Connects DataService (API + Local Sync), StorageService, AudioService, PoojaPixiEngine, and ReaderController
 */

import { dataService } from './data-service.js';
import { storageService } from './storage.js';
import { audioService } from './audio-service.js';
import { poojaPixiEngine } from './pooja-pixi.js';
import { readerController } from './reader.js';
import { adService } from './ad-service.js';

class App {
  constructor() {
    this.currentTab = 'home';
    this.selectedCategory = 'all';
    this._toastTimer = null;
  }

  async init() {
    // 1. Load Aarti & Category Datasets (Immediate local cache + background API sync)
    await dataService.loadData();

    // 2. Initialize PixiJS Devotional Canvas
    const canvasEl = document.getElementById('poojaCanvas');
    if (canvasEl) {
      await poojaPixiEngine.init(canvasEl);
    }

    // 3. Initialize Reader Controller with DOM elements
    readerController.init({
      artiTitle: document.getElementById('readerTitleDev'),
      artiSubTitle: document.getElementById('readerSubInfo'),
      artiMeaning: document.getElementById('readerMeaning'),
      readerImageWrap: document.getElementById('readerImageWrap'),
      readerImg: document.getElementById('readerImg'),
      lyricsContainer: document.getElementById('lyricsContainer'),
      readerScrollContainer: document.getElementById('readerScrollContainer'),
      btnFontDec: document.getElementById('btnFontDec'),
      btnFontInc: document.getElementById('btnFontInc'),
      fontSizeLabel: document.getElementById('fontSizeLabel'),
      btnOfferFlowers: document.getElementById('btnOfferFlowers'),
      btnRingBell: document.getElementById('btnRingBell'),
      btnSoundShankh: document.getElementById('btnSoundShankh'),
      btnShare: document.getElementById('btnShare'),
      btnFavorite: document.getElementById('btnFavorite'),
      btnToggleScript: document.getElementById('btnToggleScript'),
      themeButtons: document.querySelectorAll('.theme-dot'),
    });

    // 4. Render Initial Views
    this.applySettingsToApp();
    this.renderHome();
    this.renderCategories();
    this.bindAppEvents();

    // 5. Setup Live Sync Status Monitoring
    this.setupSyncMonitoring();

    // 6. Initialize Ads
    adService.initAppOpenAd();
    adService.preloadInterstitial();
    adService.loadBanner('ADMOB_Banner_Home', 'bottom');
  }

  setupSyncMonitoring() {
    const syncStatusPill = document.getElementById('syncStatusPill');
    const syncStatusText = document.getElementById('syncStatusText');
    const syncIcon = document.getElementById('syncIcon');

    dataService.onSyncStatusChange(({ status, details, meta }) => {
      if (!syncStatusPill || !syncStatusText) return;

      syncStatusPill.className = 'sync-status-pill';

      if (status === 'syncing') {
        syncStatusPill.classList.add('status-syncing');
        syncStatusText.textContent = 'सिंक हो रहा है...';
        if (syncIcon) syncIcon.classList.add('spinning');
      } else if (status === 'synced') {
        syncStatusPill.classList.add('status-synced');
        const count = details.aartiCount || dataService.getAllArties().length;
        syncStatusText.textContent = `लाइव API (${count})`;
        if (syncIcon) syncIcon.classList.remove('spinning');

        // Re-render views with freshest data
        this.renderHome();
        this.renderCategories();
        if (this.currentTab === 'favorites') {
          this.renderFavorites();
        } else if (this.currentTab === 'search') {
          this.handleSearch(document.getElementById('searchInput')?.value || '');
        }

        if (details.force) {
          this.showToast(`✅ ${count} आरतियां सिंक हुईं (API Live)`);
        }
      } else if (status === 'offline') {
        syncStatusPill.classList.add('status-offline');
        const count = dataService.getAllArties().length;
        syncStatusText.textContent = `ऑफ़लाइन (${count})`;
        if (syncIcon) syncIcon.classList.remove('spinning');
        if (details.force) {
          this.showToast(`📡 ऑफ़लाइन मोड • ${count} आरतियां सुरक्षित हैं`);
        }
      }
    });

    // Initialize initial indicator from meta
    const meta = dataService.getSyncMeta();
    if (meta && meta.lastSyncedAt) {
      syncStatusPill.classList.add('status-synced');
      syncStatusText.textContent = `API सिंक (${meta.aartiCount || dataService.getAllArties().length})`;
    } else {
      syncStatusPill.classList.add('status-synced');
      syncStatusText.textContent = `लाइव API (${dataService.getAllArties().length})`;
    }
  }

  async triggerManualSync() {
    const syncIcon = document.getElementById('syncIcon');
    if (syncIcon) syncIcon.classList.add('spinning');
    this.showToast('🔄 API से डेटा सिंक हो रहा है...');
    await dataService.syncFromApi(true);
  }

  showToast(message) {
    const toast = document.getElementById('syncToast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    toast.style.display = 'block';

    if (this._toastTimer) clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => { toast.style.display = 'none'; }, 300);
    }, 2800);
  }

  bindAppEvents() {
    // Header Sync Button
    const btnHeaderSync = document.getElementById('btnHeaderSync');
    if (btnHeaderSync) {
      btnHeaderSync.addEventListener('click', () => {
        this.triggerManualSync();
      });
    }

    // Header Sound / Bell
    const btnHeaderSound = document.getElementById('btnHeaderSound');
    if (btnHeaderSound) {
      btnHeaderSound.addEventListener('click', () => {
        poojaPixiEngine.ringBell();
      });
    }

    // Close Reader View
    const btnBack = document.getElementById('btnBackFromReader');
    if (btnBack) {
      btnBack.addEventListener('click', () => {
        this.closeReader();
      });
    }

    // Bottom Navigation Tabs
    const navButtons = document.querySelectorAll('.nav-item');
    navButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tab = e.currentTarget.dataset.tab;
        this.switchTab(tab);
      });
    });

    // Settings Sync Button
    const btnSettingsSync = document.getElementById('btnSettingsSync');
    if (btnSettingsSync) {
      btnSettingsSync.addEventListener('click', () => {
        this.triggerManualSync();
      });
    }

    // Global Theme Switcher
    const globalThemeDots = document.querySelectorAll('.global-theme-dot');
    globalThemeDots.forEach(dot => {
      dot.addEventListener('click', (e) => {
        const theme = e.currentTarget.dataset.theme;
        storageService.updateSettings({ theme: theme });
        this.applySettingsToApp();
      });
    });

    // Search Input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.handleSearch(e.target.value);
      });
    }

    // Quick Pooja Bar Actions on Home Screen
    const homeBtnFlowers = document.getElementById('homeBtnFlowers');
    if (homeBtnFlowers) {
      homeBtnFlowers.addEventListener('click', () => {
        poojaPixiEngine.offerFlowers(30);
      });
    }

    const homeBtnBell = document.getElementById('homeBtnBell');
    if (homeBtnBell) {
      homeBtnBell.addEventListener('click', () => {
        poojaPixiEngine.ringBell();
      });
    }

    const homeBtnShankh = document.getElementById('homeBtnShankh');
    if (homeBtnShankh) {
      homeBtnShankh.addEventListener('click', () => {
        audioService.playShankh();
      });
    }

    // Today's Deity Hero Banner Tap
    const heroBanner = document.getElementById('heroBanner');
    if (heroBanner) {
      heroBanner.addEventListener('click', () => {
        const todayDeity = dataService.getTodaysDeity();
        if (todayDeity) {
          const arties = dataService.getArtiesByCategory(todayDeity.id);
          if (arties && arties.length > 0) {
            this.openReader(arties[0]);
          }
        }
      });
    }
  }

  switchTab(tab) {
    this.currentTab = tab;

    // Update nav icons
    document.querySelectorAll('.nav-item').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tab);
    });

    // Show/Hide search bar
    const searchHeader = document.getElementById('searchHeader');
    if (searchHeader) {
      searchHeader.style.display = tab === 'search' ? 'flex' : 'none';
      if (tab === 'search') {
        document.getElementById('searchInput')?.focus();
      }
    }

    // Toggle Tab Sections
    const homeHero = document.getElementById('homeHeroSection');
    const categoriesSection = document.getElementById('categoriesSection');
    const artiListSectionTitle = document.getElementById('artiListSectionTitle');

    if (tab === 'home') {
      if (homeHero) homeHero.style.display = 'block';
      if (categoriesSection) categoriesSection.style.display = 'block';
      if (artiListSectionTitle) artiListSectionTitle.textContent = 'सभी आरतियां (All Aartis)';
      this.renderArtiList(dataService.getAllArties());
    } else if (tab === 'favorites') {
      if (homeHero) homeHero.style.display = 'none';
      if (categoriesSection) categoriesSection.style.display = 'none';
      if (artiListSectionTitle) artiListSectionTitle.textContent = 'मेरी पसंदीदा आरतियां (My Favorites)';
      this.renderFavorites();
    } else if (tab === 'categories') {
      if (homeHero) homeHero.style.display = 'none';
      if (categoriesSection) categoriesSection.style.display = 'block';
      if (artiListSectionTitle) artiListSectionTitle.textContent = 'देवता वर्ग (Deity Collections)';
      this.renderArtiList(dataService.getAllArties());
    } else if (tab === 'search') {
      if (homeHero) homeHero.style.display = 'none';
      if (categoriesSection) categoriesSection.style.display = 'none';
      if (artiListSectionTitle) artiListSectionTitle.textContent = 'खोज परिणाम (Search Results)';
      this.handleSearch(document.getElementById('searchInput')?.value || '');
    } else if (tab === 'settings') {
      if (homeHero) homeHero.style.display = 'none';
      if (categoriesSection) categoriesSection.style.display = 'none';
      if (artiListSectionTitle) artiListSectionTitle.parentElement.style.display = 'none';
      if (document.getElementById('artiList')) document.getElementById('artiList').style.display = 'none';
      const settingsSection = document.getElementById('settingsSection');
      if (settingsSection) settingsSection.style.display = 'block';
    }

    // Cleanup hiding for other tabs
    if (tab !== 'settings') {
      if (artiListSectionTitle) artiListSectionTitle.parentElement.style.display = 'block';
      if (document.getElementById('artiList')) document.getElementById('artiList').style.display = 'grid';
      const settingsSection = document.getElementById('settingsSection');
      if (settingsSection) settingsSection.style.display = 'none';
    }
  }

  applySettingsToApp() {
    const settings = storageService.getSettings();
    document.body.classList.remove('theme-ivory', 'theme-night', 'theme-parchment');
    if (settings.theme) {
      document.body.classList.add(settings.theme);
    }

    // Update active state on all theme dots across the app
    document.querySelectorAll('.theme-dot').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.theme === settings.theme);
    });
  }

  renderHome() {
    const today = dataService.getTodaysDeity();
    const heroTitle = document.getElementById('heroTitle');
    const heroSub = document.getElementById('heroSub');
    const heroTag = document.getElementById('heroTag');

    if (heroTitle && today) {
      heroTitle.textContent = `${today.name_devanagari || today.name} आरती`;
    }
    if (heroSub && today) {
      heroSub.textContent = `आज ${today.day_hindi || 'पावन दिन'} का पावन दिन • ${today.title_sub || 'नित्य पूजा'}`;
    }
    if (heroTag && today) {
      heroTag.textContent = `आज का विशेष (${today.day_hindi || 'दिन'})`;
    }

    if (this.currentTab === 'home') {
      if (this.selectedCategory === 'all') {
        this.renderArtiList(dataService.getAllArties());
      } else {
        this.renderArtiList(dataService.getArtiesByCategory(this.selectedCategory));
      }
    }
  }

  renderCategories() {
    const container = document.getElementById('categoryScroll');
    if (!container) return;

    container.innerHTML = '';

    // "All" item
    const allCard = document.createElement('div');
    allCard.className = `category-card ${this.selectedCategory === 'all' ? 'active' : ''}`;
    allCard.dataset.catId = 'all';
    allCard.innerHTML = `
      <div class="category-icon">🕉️</div>
      <div class="category-name">सभी आरतियां</div>
      <div class="category-count">${dataService.getAllArties().length} आरतियां</div>
    `;
    allCard.addEventListener('click', () => this.filterCategory('all'));
    container.appendChild(allCard);

    // Deities
    dataService.getCategories().forEach(cat => {
      const card = document.createElement('div');
      card.className = `category-card ${this.selectedCategory === cat.id ? 'active' : ''}`;
      card.dataset.catId = cat.id;
      card.innerHTML = `
        <div class="category-icon">${cat.icon || '🕉️'}</div>
        <div class="category-name">${cat.name_devanagari || cat.name}</div>
        <div class="category-count">${cat.arti_count || 0} आरतियां</div>
      `;
      card.addEventListener('click', () => this.filterCategory(cat.id));
      container.appendChild(card);
    });
  }

  filterCategory(catId) {
    this.selectedCategory = catId;

    document.querySelectorAll('.category-card').forEach(c => {
      c.classList.toggle('active', c.dataset.catId === catId);
    });

    if (catId === 'all') {
      this.renderArtiList(dataService.getAllArties());
    } else {
      const filtered = dataService.getArtiesByCategory(catId);
      this.renderArtiList(filtered);
    }
  }

  renderArtiList(arties) {
    const listContainer = document.getElementById('artiList');
    if (!listContainer) return;

    listContainer.innerHTML = '';

    if (!arties || arties.length === 0) {
      listContainer.innerHTML = `
        <div style="text-align:center; padding: 40px 20px; color: var(--text-muted);">
          <div style="font-size: 36px; margin-bottom: 8px;">🪔</div>
          <p>कोई आरती नहीं मिली (No Aarti Found).</p>
        </div>
      `;
      return;
    }

    arties.forEach(arti => {
      const card = document.createElement('div');
      card.className = 'arti-card';
      const isFav = storageService.isFavorite(arti.id);

      const hasImg = !!arti.image;
      card.innerHTML = `
        ${hasImg ? `<div class="arti-thumb-wrap"><img class="arti-thumb-img" src="${arti.image}" alt="${arti.title || 'Aarti'}" loading="lazy" onerror="this.parentElement.style.display='none'"></div>` : ''}
        <div class="arti-info">
          <div class="arti-title-dev">${arti.title_devanagari || arti.title}</div>
          <div class="arti-title-eng">${arti.title || ''}</div>
          <div class="arti-meta">
            <span class="arti-meta-tag">🕉️ ${arti.deity_devanagari || arti.deity}</span>
            <span class="arti-meta-tag">⏱️ ${arti.duration_minutes ? arti.duration_minutes + ' मिनट' : (arti.duration_approx || '3 min')}</span>
            ${isFav ? '<span class="arti-meta-tag" style="color:var(--color-gold-primary);">⭐ पसंदीदा</span>' : ''}
          </div>
        </div>
        <div class="arti-arrow">▶</div>
      `;

      card.addEventListener('click', () => {
        this.openReader(arti);
      });

      listContainer.appendChild(card);
    });
  }

  renderFavorites() {
    const favIds = storageService.getFavorites();
    const favArties = favIds
      .map(id => dataService.getArtiById(id))
      .filter(Boolean);

    this.renderArtiList(favArties);
  }

  handleSearch(query) {
    const results = dataService.search(query);
    this.renderArtiList(results);
  }

  async openReader(arti) {
    // Show interstitial occasionally before opening reader
    await adService.showInterstitial();

    readerController.loadArti(arti);
    const readerEl = document.getElementById('readerView');
    if (readerEl) {
      readerEl.classList.add('open');
    }
  }

  closeReader() {
    readerController.cleanup();
    const readerEl = document.getElementById('readerView');
    if (readerEl) {
      readerEl.classList.remove('open');
    }

    // Refresh list in case favorites changed
    if (this.currentTab === 'favorites') {
      this.renderFavorites();
    }
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});
