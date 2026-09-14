/**
 * DataService - Unified Aarti & Deity Data Layer
 * Exclusively API-Driven Architecture with Offline Cache Persistence
 * 1. Fast startup from locally persisted API cache (storageService).
 * 2. Real-time background sync from Laravel REST API (http://localhost:8000/api/arti).
 * 3. Reactive event broadcasts for live UI updates when fresh API data arrives.
 * 4. Zero fallback to local bundled JSON - all data originates strictly from the API.
 */

import { storageService } from './storage.js';
import { apiClient } from './api-client.js';

class DataService {
  constructor() {
    this.categories = [];
    this.arties = [];
    this.isLoaded = false;
    this.isSyncing = false;
    this.syncStatus = 'idle'; // 'idle' | 'cached' | 'syncing' | 'synced' | 'offline' | 'error'
    this.listeners = [];

    this._initializeFromCache();
  }

  /**
   * Initialize in-memory data strictly from cached API data if present
   */
  _initializeFromCache() {
    const cachedDeities = storageService.getCachedDeities();
    const cachedAartis = storageService.getCachedAartis();

    if (Array.isArray(cachedDeities) && cachedDeities.length > 0 && 
        Array.isArray(cachedAartis) && cachedAartis.length > 0) {
      this.categories = cachedDeities;
      this.arties = cachedAartis;
      this.syncStatus = 'cached';
      this.isLoaded = true;
      this._recomputeCategoryCounts();
    } else {
      this.categories = [];
      this.arties = [];
      this.syncStatus = 'idle';
      this.isLoaded = false;
    }
  }

  _recomputeCategoryCounts() {
    if (!Array.isArray(this.categories) || !Array.isArray(this.arties)) return;
    const countMap = {};
    for (const a of this.arties) {
      const cat = a.category_id || 'special';
      countMap[cat] = (countMap[cat] || 0) + 1;
    }
    this.categories.forEach(c => {
      c.arti_count = countMap[c.id] || 0;
    });
  }

  /**
   * Subscribe to sync state changes
   */
  onSyncStatusChange(callback) {
    if (typeof callback === 'function') {
      this.listeners.push(callback);
    }
  }

  _notifyListeners(status, details = {}) {
    this.syncStatus = status;
    const meta = storageService.getSyncMeta();
    this.listeners.forEach(cb => {
      try {
        cb({ status, details, meta });
      } catch (err) {
        console.warn('Sync listener error:', err);
      }
    });
  }

  /**
   * Load data:
   * If cached API data exists, return immediately for instant paint and revalidate in background.
   * If no cache exists, await direct API fetch so UI renders complete API data.
   */
  async loadData() {
    if (this.isLoaded && this.arties.length > 0) {
      // Cached API data is available: render instantly, sync in background
      setTimeout(() => {
        this.syncFromApi().catch(err => {
          console.log('Background sync notice:', err.message);
        });
      }, 100);
      return Promise.resolve();
    }

    // No cached data exists yet: wait for initial API fetch
    return await this.syncFromApi();
  }

  /**
   * Synchronize with Laravel REST API
   * @param {boolean} force - Whether this is a user-initiated force refresh
   */
  async syncFromApi(force = false) {
    if (this.isSyncing) return;
    this.isSyncing = true;
    this._notifyListeners('syncing', { force });

    try {
      // Fetch both deities and aartis from API in parallel
      const [apiDeities, apiAartis] = await Promise.all([
        apiClient.fetchDeities(),
        apiClient.fetchAartis()
      ]);

      if (!Array.isArray(apiAartis) || apiAartis.length === 0) {
        throw new Error('API returned empty aarti collection');
      }

      this.arties = apiAartis;
      if (Array.isArray(apiDeities) && apiDeities.length > 0) {
        this.categories = apiDeities;
      }

      this._recomputeCategoryCounts();
      this.isLoaded = true;

      // Persist to local cache for offline capabilities
      const meta = storageService.saveSyncedData(this.categories, this.arties, 'api');
      this.isSyncing = false;
      this._notifyListeners('synced', {
        aartiCount: this.arties.length,
        deityCount: this.categories.length,
        force,
        meta
      });

      return { success: true, count: this.arties.length };
    } catch (err) {
      console.warn('API sync unavailable, operating in offline mode:', err.message);
      this.isSyncing = false;
      this._notifyListeners('offline', {
        message: err.message,
        fallbackCount: this.arties.length,
        force
      });
      return { success: false, offline: true, error: err.message };
    }
  }

  // --- Read Methods ---

  getCategories() {
    return this.categories;
  }

  getCategoryById(id) {
    return this.categories.find(c => c.id === id);
  }

  getAllArties() {
    return this.arties;
  }

  getArtiById(id) {
    return this.arties.find(a => a.id === id || String(a.original_api_id) === String(id));
  }

  getArtiesByCategory(categoryId) {
    return this.arties.filter(a => a.category_id === categoryId);
  }

  search(query) {
    if (!query || !query.trim()) return this.arties;
    const q = query.toLowerCase().trim();
    return this.arties.filter(a => {
      const titleMatch = (a.title && a.title.toLowerCase().includes(q)) || 
                         (a.title_devanagari && a.title_devanagari.includes(q));
      const deityMatch = (a.deity && a.deity.toLowerCase().includes(q)) ||
                         (a.deity_devanagari && a.deity_devanagari.includes(q));
      const lyricsMatch = Array.isArray(a.lyrics_transliteration) && 
                          a.lyrics_transliteration.some(l => l && l.toLowerCase().includes(q));
      return titleMatch || deityMatch || lyricsMatch;
    });
  }

  getTodaysDeity() {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const currentDay = days[new Date().getDay()];
    const match = this.categories.find(c => c.day_of_week === currentDay);
    return match || (this.categories.length > 0 ? this.categories[0] : null);
  }

  getSyncMeta() {
    return storageService.getSyncMeta();
  }
}

export const dataService = new DataService();
