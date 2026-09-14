/**
 * StorageService - Local Persistence Engine
 * Saves user favorites, recent reading history, reader settings,
 * and offline-first cached API datasets (Deities & Aartis).
 */

const STORAGE_KEYS = {
  FAVORITES: 'arti_favorites',
  RECENTS: 'arti_recents',
  SETTINGS: 'arti_settings',
  CACHED_AARTIS: 'arti_cached_aartis',
  CACHED_DEITIES: 'arti_cached_deities',
  SYNC_META: 'arti_sync_meta',
};

const DEFAULT_SETTINGS = {
  fontSize: 20,          // In pixels (16 - 32)
  theme: 'theme-ivory',  // 'theme-ivory' | 'theme-night' | 'theme-parchment'
  autoScrollSpeed: 2,    // 1 to 5
  showTransliteration: false,
};

class StorageService {
  constructor() {
    this.favorites = this._get(STORAGE_KEYS.FAVORITES, [
      'arti-jaidev-jaidev-jai-mangal-murti-lyrics',
      'arti-hanuman-ji-ki-aarti',
      'arti-aarti-om-jai-jagdish-hare'
    ]);
    // Clean any legacy dummy favorites
    this.favorites = this.favorites.filter(id => typeof id === 'string' && id.startsWith('arti-'));
    if (this.favorites.length === 0) {
      this.favorites = [
        'arti-jaidev-jaidev-jai-mangal-murti-lyrics',
        'arti-hanuman-ji-ki-aarti',
        'arti-aarti-om-jai-jagdish-hare'
      ];
    }
    this.recents = this._get(STORAGE_KEYS.RECENTS, []).filter(id => typeof id === 'string' && id.startsWith('arti-'));
    this.settings = this._get(STORAGE_KEYS.SETTINGS, DEFAULT_SETTINGS);
  }

  _get(key, fallback) {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : fallback;
    } catch (e) {
      console.warn('Storage read failed, using fallback', e);
      return fallback;
    }
  }

  _set(key, val) {
    try {
      localStorage.setItem(key, JSON.stringify(val));
    } catch (e) {
      console.warn('Storage write failed', e);
    }
  }

  // --- Favorites & Recents ---
  isFavorite(artiId) {
    return this.favorites.includes(artiId);
  }

  toggleFavorite(artiId) {
    if (this.isFavorite(artiId)) {
      this.favorites = this.favorites.filter(id => id !== artiId);
    } else {
      this.favorites.unshift(artiId);
    }
    this._set(STORAGE_KEYS.FAVORITES, this.favorites);
    return this.isFavorite(artiId);
  }

  getFavorites() {
    return [...this.favorites];
  }

  addRecent(artiId) {
    this.recents = [artiId, ...this.recents.filter(id => id !== artiId)].slice(0, 10);
    this._set(STORAGE_KEYS.RECENTS, this.recents);
  }

  getRecents() {
    return [...this.recents];
  }

  // --- Reader Settings ---
  getSettings() {
    return { ...DEFAULT_SETTINGS, ...this.settings };
  }

  updateSettings(updates) {
    this.settings = { ...this.settings, ...updates };
    this._set(STORAGE_KEYS.SETTINGS, this.settings);
    return this.settings;
  }

  // --- Offline API Cache Persistence ---
  saveSyncedData(deities, aartis, source = 'api') {
    if (Array.isArray(deities) && deities.length > 0) {
      this._set(STORAGE_KEYS.CACHED_DEITIES, deities);
    }
    if (Array.isArray(aartis) && aartis.length > 0) {
      this._set(STORAGE_KEYS.CACHED_AARTIS, aartis);
    }
    const meta = {
      lastSyncedAt: new Date().toISOString(),
      source,
      aartiCount: aartis ? aartis.length : 0,
      deityCount: deities ? deities.length : 0,
    };
    this._set(STORAGE_KEYS.SYNC_META, meta);
    return meta;
  }

  getCachedDeities() {
    return this._get(STORAGE_KEYS.CACHED_DEITIES, null);
  }

  getCachedAartis() {
    const cached = this._get(STORAGE_KEYS.CACHED_AARTIS, null);
    if (!Array.isArray(cached)) return null;
    // If any legacy dummy aarti exists in cache, invalidate and force fresh API fetch
    const hasDummies = cached.some(a => !a.id || !a.id.startsWith('arti-'));
    if (hasDummies) {
      this.clearCache();
      return null;
    }
    return cached;
  }

  getSyncMeta() {
    return this._get(STORAGE_KEYS.SYNC_META, null);
  }

  clearCache() {
    try {
      localStorage.removeItem(STORAGE_KEYS.CACHED_DEITIES);
      localStorage.removeItem(STORAGE_KEYS.CACHED_AARTIS);
      localStorage.removeItem(STORAGE_KEYS.SYNC_META);
    } catch (e) {
      console.warn('Cache clear failed', e);
    }
  }
}

export const storageService = new StorageService();
