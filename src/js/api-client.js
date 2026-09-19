/**
 * ApiClient - REST API Communication Engine
 * Connects to the Laravel backend for live Aarti and Deity synchronization.
 * Supports configurable base URL, timeout abort controller, and schema normalization.
 */

const DEFAULT_API_BASE = 'https://www.onlinetxttools.com/api/arti';

export class ApiClient {
  constructor(baseUrl = null) {
    const rawBase = baseUrl || 
      (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) ||
      (typeof window !== 'undefined' && window.APP_CONFIG?.API_BASE_URL) || 
      DEFAULT_API_BASE;
    this.baseUrl = this._formatApiBase(rawBase);
    this.timeoutMs = 8000;
  }

  _formatApiBase(url) {
    if (!url) return DEFAULT_API_BASE;
    let clean = url.trim().replace(/\/+$/, '');
    if (!clean.includes('/api/arti')) {
      clean = `${clean}/api/arti`;
    }
    return clean;
  }

  setBaseUrl(url) {
    if (url) {
      this.baseUrl = this._formatApiBase(url);
    }
  }

  async _fetchWithTimeout(endpoint, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const url = `${this.baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          ...(options.headers || {})
        }
      });
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`API Error ${response.status}: ${response.statusText}`);
      }

      const json = await response.json();
      return json.data !== undefined ? json.data : json;
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        throw new Error(`API Request Timeout (${this.timeoutMs}ms) to ${endpoint}`);
      }
      throw err;
    }
  }

  /**
   * Fetch all deities/categories from API
   */
  async fetchDeities() {
    const rawDeities = await this._fetchWithTimeout('/deities');
    return this.normalizeDeities(rawDeities);
  }

  /**
   * Fetch all aartis from API
   */
  async fetchAartis() {
    const rawAartis = await this._fetchWithTimeout('/aartis');
    return this.normalizeAartis(rawAartis);
  }

  /**
   * Fetch single Aarti by ID or slug
   */
  async fetchAartiById(id) {
    const rawAarti = await this._fetchWithTimeout(`/aartis/${id}`);
    return this.normalizeSingleAarti(rawAarti);
  }

  /**
   * Normalize deities to match local frontend schema
   */
  normalizeDeities(rawList) {
    if (!Array.isArray(rawList)) return [];
    return rawList.map(item => {
      let resolvedImage = item.image_url;
      if (resolvedImage) {
        const filename = resolvedImage.split('/').pop();
        if (filename && (resolvedImage.includes('/images/arties/') || resolvedImage.includes('localhost:8000/images/'))) {
          resolvedImage = `/assets/images/arties/${filename}`;
        }
      }
      return {
        id: item.slug || String(item.id),
        name: item.name,
        name_devanagari: item.name_devanagari || item.name,
        title_sub: item.title_sub || item.description || '',
        day_of_week: item.day_of_week || 'Daily',
        day_hindi: item.day_hindi || 'प्रतिदिन',
        theme_color: item.theme_color || '#E65100',
        accent_color: item.accent_color || '#FFA726',
        icon: item.icon || '🕉️',
        arti_count: item.arti_count || (item.aartis ? item.aartis.length : 0),
        image_url: resolvedImage || null
      };
    });
  }

  /**
   * Normalize an array of Aarti records
   */
  normalizeAartis(rawList) {
    if (!Array.isArray(rawList)) return [];
    return rawList.map(item => this.normalizeSingleAarti(item));
  }

  /**
   * Normalize single Aarti to frontend schema
   */
  normalizeSingleAarti(item) {
    if (!item) return null;
    const slugId = item.slug || `arti-${item.id}`;
    const catId = item.category || (item.deity && (item.deity.slug || item.deity.category)) || 'special';

    // Resolve local / remote image fallback
    let resolvedImage = item.image_url;
    if (resolvedImage) {
      const filename = resolvedImage.split('/').pop();
      if (filename && (resolvedImage.includes('/images/arties/') || resolvedImage.includes('localhost:8000/images/'))) {
        resolvedImage = `/assets/images/arties/${filename}`;
      }
    } else {
      resolvedImage = `/assets/images/arties/${slugId}.jpg`;
    }

    let lyricsDev = item.lyrics_json || [];
    if (typeof lyricsDev === 'string') {
      try { lyricsDev = JSON.parse(lyricsDev); } catch (e) { lyricsDev = []; }
    }
    // Fallback: If lyrics_json is empty, but raw lyrics text is present, parse into structured sections
    if ((!lyricsDev || lyricsDev.length === 0) && typeof item.lyrics === 'string' && item.lyrics.trim()) {
      const paragraphs = item.lyrics.split(/\r?\n\s*\r?\n/).map(p => p.trim()).filter(Boolean);
      lyricsDev = paragraphs.map((para, idx) => ({
        type: idx === 0 && para.includes('॥') ? 'chorus' : 'verse',
        lines: para.split(/\r?\n/).map(l => l.trim()).filter(Boolean)
      }));
    }

    let lyricsTrans = item.lyrics_transliteration || [];
    if (typeof lyricsTrans === 'string') {
      try { lyricsTrans = JSON.parse(lyricsTrans); } catch (e) { lyricsTrans = []; }
    }

    return {
      id: slugId,
      original_api_id: item.id,
      category_id: catId,
      deity: item.deity_name || (item.deity && item.deity.name) || 'Devata',
      deity_devanagari: item.deity_devanagari || (item.deity && item.deity.name_devanagari) || item.deity_name || '',
      title: item.title || '',
      title_devanagari: item.title_devanagari || item.title || '',
      image: resolvedImage,
      duration_approx: item.duration || `${item.duration_minutes || 3} min`,
      duration_minutes: item.duration_minutes || 3,
      timing: item.timing || 'Daily Pooja / Aarti',
      timing_devanagari: item.timing_devanagari || 'नित्य पूजन एवं आरती',
      significance: item.significance || item.significance_devanagari || '',
      significance_devanagari: item.significance_devanagari || item.significance || '',
      meaning_short: item.meaning_short || item.significance || '',
      lyrics_devanagari: lyricsDev,
      lyrics_transliteration: lyricsTrans,
      popular: !!item.is_popular,
      language: 'हिंदी (Hindi)',
      author: 'पारंपरिक (Traditional)'
    };
  }
}

export const apiClient = new ApiClient();
