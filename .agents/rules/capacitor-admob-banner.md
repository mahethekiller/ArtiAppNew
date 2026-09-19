---
name: Capacitor AdMob Banner CSS Integration
description: Rule for preventing Capacitor AdMob banners from obscuring fixed bottom web UI elements.
---

# Capacitor AdMob Banner CSS Integration

When integrating `@capacitor-community/admob` banners in a web app, the banner renders natively **over** the webview by default (if margin is 0) or forces the webview to resize. 

To ensure the banner never overlaps fixed bottom navigation bars or floating toolbars:

1. **JS Event Listener**: Always capture the `BannerAdPluginEvents.SizeChanged` event when the banner loads, and write its height to a CSS variable on the `:root` element.

```javascript
import { AdMob, BannerAdPluginEvents } from '@capacitor-community/admob';

AdMob.addListener(BannerAdPluginEvents.SizeChanged, (size) => {
  if (size && size.height > 0) {
    document.documentElement.style.setProperty('--admob-current-height', `${size.height}px`);
  }
});
```

2. **CSS Integration**: Always use the `--admob-current-height` CSS variable to dynamically adjust the `bottom` or `padding-bottom` properties of fixed UI elements.

```css
/* Fixed bottom navigation */
.bottom-nav {
  position: absolute;
  /* Push up by the height of the banner */
  bottom: var(--admob-current-height, 0px); 
}

/* Scrollable content areas */
.scroll-container {
  /* Add padding to the bottom to allow scrolling past the banner */
  padding-bottom: calc(80px + var(--admob-current-height, 0px));
}
```

Never hardcode the `bottom: 0` for fixed elements if an AdMob banner is expected on the same screen.
