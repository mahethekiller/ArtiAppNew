export class AdService {
  constructor() {
    this.initialized = false;
    this.isNative = !!window.Capacitor && window.Capacitor.isNativePlatform();
    this.bannerVisible = false;

    // Real Ad Units for Aarti Sangrah
    this.AD_UNITS = {
      banner: 'ca-app-pub-7746616500591109/3590577369',
      interstitial: 'ca-app-pub-7746616500591109/1187775300',
      appOpen: 'ca-app-pub-7746616500591109/4778526793'
    };
  }

  async init() {
    if (this.initialized) return;
    if (this.isNative) {
      try {
        const { AdMob } = await import('@capacitor-community/admob');
        await AdMob.initialize({
          requestTrackingAuthorization: true,
          testingDevices: ['C549CBE901E653FE7F7CB20EE5C505D9', 'EMULATOR'],
          initializeForTesting: true
        });
        this.initialized = true;
        console.log('[AdMob] Native SDK initialized successfully');
      } catch (err) {
        console.warn('[AdMob] Native initialization failed:', err);
      }
    } else {
      this.initialized = true;
      console.log('[AdMob] Running in Browser/Development mode');
    }
  }

  async initAppOpenAd() {
    await this.init();
    if (this.isNative) {
      try {
        const { AdMob, AppOpenAdPluginEvents } = await import('@capacitor-community/admob');
        
        await AdMob.loadAppOpen({
          adId: this.AD_UNITS.appOpen,
          isTesting: false
        });

        // The promise resolves when the ad is successfully loaded
        await AdMob.showAppOpen();
      } catch (e) {
        console.warn('[AdMob] App Open Ad init failed:', e);
      }
    }
  }

  async preloadInterstitial(space = 'ADMOB_Interstitial_General') {
    await this.init();
    if (this.isNative) {
      try {
        const { AdMob, InterstitialAdPluginEvents } = await import('@capacitor-community/admob');
        await AdMob.prepareInterstitial({
          adId: this.AD_UNITS.interstitial,
          isTesting: false
        });

        // Preload next one when current one is dismissed
        AdMob.addListener(InterstitialAdPluginEvents.Dismissed, () => {
           AdMob.prepareInterstitial({
             adId: this.AD_UNITS.interstitial,
             isTesting: false
           }).catch(console.warn);
        });
      } catch (e) {
        console.warn('[AdMob] Interstitial Preload failed:', e);
      }
    }
  }

  async showInterstitial(space = 'ADMOB_Interstitial_General') {
    await this.init();
    if (this.isNative) {
      try {
        const { AdMob } = await import('@capacitor-community/admob');
        // Show the preloaded interstitial
        await AdMob.showInterstitial();
        return true;
      } catch (e) {
        console.warn('[AdMob] Interstitial Show failed:', e);
        // It might not be loaded yet, try to load it for next time
        this.preloadInterstitial();
        return false;
      }
    } else {
      console.log('[AdMob Mock] Interstitial triggered');
      return true;
    }
  }

  async loadBanner(space = 'ADMOB_Banner_Home', position = 'bottom') {
    await this.init();
    if (this.bannerVisible) return;
    if (this.isNative) {
      try {
        const { AdMob, BannerAdPosition, BannerAdSize, BannerAdPluginEvents } = await import('@capacitor-community/admob');
        
        AdMob.addListener(BannerAdPluginEvents.SizeChanged, (size) => {
          if (size && size.height > 0) {
            document.documentElement.style.setProperty('--admob-current-height', `${size.height}px`);
          }
        });

        await AdMob.showBanner({
          adId: this.AD_UNITS.banner,
          adSize: BannerAdSize.ADAPTIVE_BANNER,
          position: position === 'top' ? BannerAdPosition.TOP_CENTER : BannerAdPosition.BOTTOM_CENTER,
          margin: 0,
          isTesting: false
        });
        this.bannerVisible = true;
      } catch (e) {
        console.warn('[AdMob] Show banner failed:', e);
      }
    }
  }

  async hideBanner() {
    if (!this.bannerVisible) return;
    if (this.isNative) {
      try {
        const { AdMob } = await import('@capacitor-community/admob');
        await AdMob.hideBanner();
        this.bannerVisible = false;
        document.documentElement.style.setProperty('--admob-current-height', '0px');
      } catch (e) {
        console.warn('[AdMob] Hide banner failed:', e);
      }
    }
  }
}

export const adService = new AdService();
