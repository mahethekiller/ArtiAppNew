# Mobile Safe Area Insets

When building mobile web apps, PWAs, or Capacitor/Cordova applications, always ensure that the app UI does not clash with the system status bar (notch) at the top or the home indicator at the bottom.

1. **Meta Viewport Tag**: Always include `viewport-fit=cover` in the `meta name="viewport"` tag in your `index.html`.
2. **CSS Insets**: Apply safe area padding and adjust heights accordingly for sticky/fixed headers and footers using CSS `env()` variables:
   - **Header**: 
     ```css
     height: calc([BASE_HEIGHT]px + env(safe-area-inset-top));
     padding-top: env(safe-area-inset-top);
     ```
   - **Footer (Bottom Nav)**: 
     ```css
     height: calc([BASE_HEIGHT]px + env(safe-area-inset-bottom));
     padding-bottom: env(safe-area-inset-bottom);
     ```
   - *Note*: You can use the shorthand `padding: env(safe-area-inset-top) [RIGHT] [BOTTOM] [LEFT];` as needed.
