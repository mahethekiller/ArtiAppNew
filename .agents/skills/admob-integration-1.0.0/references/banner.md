# Banner Ads Integration

Banner ads are rectangular ads that appear at the top or bottom of the screen.

## Package Imports

```kotlin
import com.admob.adspace.banner.SpaceBanner
import com.admob.adspace.banner.BannerCallback
import com.admob.adspace.banner.BannerError
import com.admob.adspace.banner.AdRevenue
import com.google.android.libraries.ads.mobile.sdk.banner.AdView
import com.google.android.libraries.ads.mobile.sdk.banner.AdSize
```

## View API (XML/Kotlin)

### Layout XML

```xml
<FrameLayout
    android:id="@+id/bannerContainer"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="#E0E0E0"/>
```

### Basic Implementation

```kotlin
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import com.admob.adspace.banner.SpaceBanner
import com.admob.adspace.banner.BannerCallback
import com.admob.adspace.banner.BannerError
import com.admob.adspace.banner.AdRevenue
import com.google.android.libraries.ads.mobile.sdk.banner.AdView

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Show inline adaptive banner
        SpaceBanner.showInlineAdaptive(
            space = "ADMOB_Banner_Home",
            viewGroup = binding.bannerContainer,
            forceRefresh = false,
            center = true,
            callback = object : BannerCallback {
                override fun onLoaded(adView: AdView, space: String) {
                    // Banner loaded successfully
                }

                override fun onFailed(space: String, error: BannerError) {
                    // Hide container on failure
                    binding.bannerContainer.visibility = View.GONE
                }

                override fun onImpression(space: String) {
                    // Banner impression recorded
                }

                override fun onClicked(space: String) {
                    // Banner clicked
                }

                override fun onPaid(space: String, revenue: AdRevenue) {
                    // Revenue received: revenue.value, revenue.currencyCode
                }

                override fun onCollapsed(space: String, position: CollapsiblePosition) {
                    // Banner collapsed (for collapsible banners only)
                }
            }
        )
    }

    override fun onDestroy() {
        super.onDestroy()
        SpaceBanner.clearCache("ADMOB_Banner_Home")
    }
}
```

## Banner Types

### 1. Inline Adaptive Banner

Best for scrollable content (lists, feeds):

```kotlin
SpaceBanner.showInlineAdaptive(
    space = "ADMOB_Banner_Home",
    viewGroup = binding.bannerContainer,
    forceRefresh = false,
    center = true,
    callback = callback
)
```

### 2. Anchored Adaptive Banner

Best for fixed position (top/bottom of screen):

```kotlin
SpaceBanner.showAnchoredAdaptive(
    space = "ADMOB_Banner_Home",
    viewGroup = binding.bannerContainer,
    forceRefresh = false,
    center = true,
    callback = callback
)
```

### 3. Collapsible Banner

Banner with close button:

```kotlin
import com.admob.adspace.banner.CollapsiblePosition

SpaceBanner.showCollapsible(
    space = "ADMOB_Banner_Home",
    viewGroup = binding.bannerContainer,
    position = CollapsiblePosition.BOTTOM, // or TOP
    forceRefresh = false,
    center = true,
    callback = callback
)
```

### 4. Fixed Size Banner

Legacy fixed-size banner:

```kotlin
import com.google.android.libraries.ads.mobile.sdk.banner.AdSize

SpaceBanner.show(
    space = "ADMOB_Banner_Home",
    viewGroup = binding.bannerContainer,
    adSize = AdSize.BANNER, // 320x50
    forceRefresh = false,
    center = true,
    callback = callback
)
```

**Common AdSize values**:
- `AdSize.BANNER` - 320x50
- `AdSize.LARGE_BANNER` - 320x100
- `AdSize.MEDIUM_RECTANGLE` - 300x250
- `AdSize.FULL_BANNER` - 468x60
- `AdSize.LEADERBOARD` - 728x90

## Jetpack Compose Integration

Banner ads work seamlessly with Jetpack Compose using AndroidView wrapper. Below are comprehensive patterns for different use cases.

### Basic Banner Composable

```kotlin
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.viewinterop.AndroidView
import com.admob.adspace.banner.SpaceBanner
import com.admob.adspace.banner.BannerCallback
import com.admob.adspace.banner.BannerError
import com.admob.adspace.banner.AdRevenue
import com.google.android.libraries.ads.mobile.sdk.banner.AdView
import timber.log.Timber

@Composable
fun BannerAdView(
    spaceName: String = "ADMOB_Banner_Home",
    modifier: Modifier = Modifier,
    onLoad: (() -> Unit)? = null,
    onFail: ((String) -> Unit)? = null
) {
    val context = LocalContext.current
    var adViewInstance by remember { mutableStateOf<AdView?>(null) }
    var adLoaded by remember { mutableStateOf(false) }

    // Load ad on first composition
    LaunchedEffect(spaceName) {
        Timber.d("Loading banner ad: $spaceName")

        SpaceBanner.load(
            space = spaceName,
            callback = object : BannerCallback {
                override fun onLoaded(adView: AdView, space: String) {
                    Timber.d("Banner ad loaded successfully: $space")
                    adViewInstance = adView
                    adLoaded = true
                    onLoad?.invoke()
                }

                override fun onFailed(space: String, error: BannerError) {
                    Timber.e("Banner ad failed: $space - ${error.message}")
                    adLoaded = false
                    onFail?.invoke(error.message)
                }

                override fun onImpression(space: String) {
                    Timber.d("Banner impression recorded: $space")
                }

                override fun onClicked(space: String) {
                    Timber.d("Banner clicked: $space")
                }

                override fun onPaid(space: String, revenue: AdRevenue) {
                    Timber.d("Banner revenue: $space - ${revenue.value} ${revenue.currencyCode}")
                }

                override fun onCollapsed(space: String, position: CollapsiblePosition) {
                    Timber.d("Banner collapsed: $space at $position")
                }
            }
        )
    }

    // Cleanup on dispose
    DisposableEffect(Unit) {
        onDispose {
            Timber.d("Clearing banner cache: $spaceName")
            SpaceBanner.clearCache(spaceName)
            adViewInstance = null
        }
    }

    // Show ad when loaded
    if (adLoaded && adViewInstance != null) {
        AndroidView(
            factory = { adViewInstance!! },
            modifier = modifier,
            update = { view ->
                // Update view if needed
            }
        )
    }
}

// Usage in Composable
@Composable
fun HomeScreen() {
    Column(
        modifier = Modifier.fillMaxSize()
    ) {
        Text(
            text = "Welcome to Home Screen",
            modifier = Modifier.padding(16.dp)
        )

        // Banner at bottom
        BannerAdView(
            spaceName = "ADMOB_Banner_Home",
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        )
    }
}
```

### Advanced Composable with State Management

```kotlin
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView

sealed class BannerAdState {
    object Loading : BannerAdState()
    data class Loaded(val adView: AdView) : BannerAdState()
    data class Failed(val message: String) : BannerAdState()
    object Idle : BannerAdState()
}

@Composable
fun AdvancedBannerAd(
    spaceName: String,
    modifier: Modifier = Modifier,
    placeholderHeight: Int = 50
) {
    var adState by remember { mutableStateOf<BannerAdState>(BannerAdState.Idle) }

    // Load ad when state is idle
    LaunchedEffect(spaceName) {
        if (adState == BannerAdState.Idle) {
            adState = BannerAdState.Loading

            SpaceBanner.load(
                space = spaceName,
                callback = object : BannerCallback {
                    override fun onLoaded(adView: AdView, space: String) {
                        Timber.d("Banner loaded: $space")
                        adState = BannerAdState.Loaded(adView)
                    }

                    override fun onFailed(space: String, error: BannerError) {
                        Timber.e("Banner failed: $space - ${error.message}")
                        adState = BannerAdState.Failed(error.message)
                    }

                    override fun onImpression(space: String) {
                        if (BuildConfig.DEBUG) {
                            Timber.d("Banner impression: $space")
                        }
                    }

                    override fun onClicked(space: String) {
                        if (BuildConfig.DEBUG) {
                            Timber.d("Banner clicked: $space")
                        }
                    }

                    override fun onPaid(space: String, revenue: AdRevenue) {
                        if (BuildConfig.DEBUG) {
                            Timber.d("Banner revenue: $space - ${revenue.value} ${revenue.currencyCode}")
                        }
                    }

                    override fun onCollapsed(space: String, position: CollapsiblePosition) {
                        Timber.d("Banner collapsed: $space at $position")
                    }
                }
            )
        }
    }

    // Cleanup
    DisposableEffect(Unit) {
        onDispose {
            Timber.d("Cleaning up banner: $spaceName")
            SpaceBanner.clearCache(spaceName)
            adState = BannerAdState.Idle
        }
    }

    // Render based on state
    when (val state = adState) {
        is BannerAdState.Loading -> {
            Box(
                modifier = modifier
                    .fillMaxWidth()
                    .height(placeholderHeight.dp)
                    .background(Color.LightGray.copy(alpha = 0.3f)),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        }

        is BannerAdState.Loaded -> {
            AndroidView(
                factory = { state.adView },
                modifier = modifier
            )
        }

        is BannerAdState.Failed -> {
            if (BuildConfig.DEBUG) {
                Box(
                    modifier = modifier
                        .fillMaxWidth()
                        .height(placeholderHeight.dp)
                        .background(Color.Red.copy(alpha = 0.1f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "Ad failed: ${state.message}",
                        color = Color.Red,
                        modifier = Modifier.padding(8.dp)
                    )
                }
            }
        }

        BannerAdState.Idle -> {
            // Initial state, will trigger load
        }
    }
}
```

### Collapsible Banner in Compose

```kotlin
import com.admob.adspace.banner.CollapsiblePosition

@Composable
fun CollapsibleBannerAd(
    spaceName: String,
    position: CollapsiblePosition = CollapsiblePosition.BOTTOM,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var container by remember { mutableStateOf<FrameLayout?>(null) }
    var isAdLoaded by remember { mutableStateOf(false) }

    LaunchedEffect(spaceName) {
        Timber.d("Loading collapsible banner: $spaceName at $position")

        container = FrameLayout(context).apply {
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.WRAP_CONTENT
            )
        }

        container?.let { frameLayout ->
            SpaceBanner.showCollapsible(
                space = spaceName,
                viewGroup = frameLayout,
                position = position,
                forceRefresh = false,
                center = true,
                callback = object : BannerCallback {
                    override fun onLoaded(adView: AdView, space: String) {
                        Timber.d("Collapsible banner loaded: $space")
                        isAdLoaded = true
                    }

                    override fun onFailed(space: String, error: BannerError) {
                        Timber.e("Collapsible banner failed: ${error.message}")
                        isAdLoaded = false
                    }

                    override fun onCollapsed(space: String, position: CollapsiblePosition) {
                        Timber.d("Banner collapsed: $space at $position")
                        isAdLoaded = false
                    }

                    override fun onImpression(space: String) {}
                    override fun onClicked(space: String) {}
                    override fun onPaid(space: String, revenue: AdRevenue) {}
                }
            )
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            Timber.d("Cleaning up collapsible banner: $spaceName")
            SpaceBanner.clearCache(spaceName)
        }
    }

    if (isAdLoaded && container != null) {
        AndroidView(
            factory = { container!! },
            modifier = modifier
        )
    }
}
```

### Best Practices for Compose

1. **Use AndroidView wrapper** - AdView is a View, not a Compose component
2. **LaunchedEffect for one-time operations** - Load ad on first composition with spaceName as key
3. **DisposableEffect for cleanup** - Clear cache to prevent memory leaks when composable leaves composition
4. **State management** - Track ad load status with remember and mutableStateOf
5. **Debug logging** - Use Timber.d() with BuildConfig.DEBUG checks for production safety
6. **Loading states** - Show placeholder while ad loads to improve UX
7. **Error handling** - Handle failures gracefully with fallback UI or retry logic
8. **Avoid recomposition** - Use LaunchedEffect keys wisely to prevent unnecessary ad reloads

## Advanced Features

### Preload Banner

```kotlin
SpaceBanner.preload(
    space = "ADMOB_Banner_Home",
    forceRefresh = false,
    callback = callback
)
```

### Check if Banner is Loaded

```kotlin
if (SpaceBanner.isLoaded("ADMOB_Banner_Home")) {
    // Banner is ready
}
```

### Clear Cache

```kotlin
// Clear specific space
SpaceBanner.clearCache("ADMOB_Banner_Home")

// Clear all banner cache
SpaceBanner.clearAllCache()
```

## Configuration

In `assets/ads_config.json`:

```json
{
  "space": "ADMOB_Banner_Home",
  "adsType": "banner",
  "ids": [
    "ca-app-pub-3940256099942544/6300978111",
    "ca-app-pub-3940256099942544/2934735716"
  ],
  "enable": true,
  "minInterval": 30000
}
```

## Best Practices

### 1. Always Clear Cache in onDestroy()

**WHY**: Prevents memory leaks by releasing AdView references and ad resources. AdViews hold strong references to Context and ad assets.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onDestroy() {
        super.onDestroy()
        Timber.d("Clearing banner cache")
        SpaceBanner.clearCache("ADMOB_Banner_Home")
    }
}
```

**In Compose**:
```kotlin
DisposableEffect(Unit) {
    onDispose {
        Timber.d("Clearing banner cache: $spaceName")
        SpaceBanner.clearCache(spaceName)
    }
}
```

### 2. Hide Container on Failure

**WHY**: Prevents empty whitespace from appearing when ads fail to load, maintaining clean UI.

```kotlin
SpaceBanner.showInlineAdaptive(
    space = "ADMOB_Banner_Home",
    viewGroup = binding.bannerContainer,
    callback = object : BannerCallback {
        override fun onLoaded(adView: AdView, space: String) {
            binding.bannerContainer.visibility = View.VISIBLE
        }

        override fun onFailed(space: String, error: BannerError) {
            Timber.e("Banner failed: ${error.message}")
            binding.bannerContainer.visibility = View.GONE
        }
    }
)
```

### 3. Use Adaptive Banners Instead of Fixed Sizes

**WHY**: Adaptive banners automatically adjust to screen width, providing better fill rates and user experience across devices.

```kotlin
// GOOD - Adaptive banner
SpaceBanner.showInlineAdaptive(
    space = "ADMOB_Banner_Home",
    viewGroup = binding.bannerContainer,
    forceRefresh = false,
    center = true,
    callback = callback
)

// AVOID - Fixed size banner (unless specific requirements)
SpaceBanner.show(
    space = "ADMOB_Banner_Home",
    viewGroup = binding.bannerContainer,
    adSize = AdSize.BANNER, // Fixed 320x50
    callback = callback
)
```

### 4. Center Banners for Better Visual Appearance

**WHY**: Centered banners look more professional and consistent across different screen sizes.

```kotlin
SpaceBanner.showInlineAdaptive(
    space = "ADMOB_Banner_Home",
    viewGroup = binding.bannerContainer,
    center = true, // Always center the banner
    callback = callback
)
```

### 5. Don't Create Too Many Banner Instances

**WHY**: Multiple banner instances consume memory and can cause performance issues. Reuse existing banners when possible.

```kotlin
// GOOD - Single banner instance
class MainActivity : AppCompatActivity() {
    private val bannerSpace = "ADMOB_Banner_Home"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        SpaceBanner.showInlineAdaptive(
            space = bannerSpace,
            viewGroup = binding.bannerContainer,
            callback = callback
        )
    }
}

// AVOID - Multiple instances for same space
class BadExample : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Creating multiple instances wastes resources
        SpaceBanner.showInlineAdaptive(space = "ADMOB_Banner_Home", ...)
        SpaceBanner.showInlineAdaptive(space = "ADMOB_Banner_Home", ...)
    }
}
```

### 6. Respect Min Interval Configuration

**WHY**: The SDK enforces min_interval to prevent excessive ad requests. Respect this to avoid rate limiting and poor UX.

```kotlin
// SDK automatically enforces min_interval
// Current min interval: 30 seconds (default)

// Check if enough time has passed
if (SpaceBanner.canShow("ADMOB_Banner_Home")) {
    SpaceBanner.showInlineAdaptive(...)
} else {
    Timber.d("Min interval not elapsed, skipping ad show")
}
```

### 7. Check Premium Status Before Showing Ads

**WHY**: Premium users should not see ads. Always check user status before displaying ads.

```kotlin
fun showBannerIfEligible() {
    // Check if user is premium
    if (UserManager.isPremium()) {
        Timber.d("User is premium, skipping ad")
        binding.bannerContainer.visibility = View.GONE
        return
    }

    // Check global enable flag
    if (!AdSpaceSDK.isGlobalEnabled()) {
        Timber.d("Ads globally disabled")
        return
    }

    // Check space-specific enable flag
    if (!AdSpaceSDK.isSpaceEnabled("ADMOB_Banner_Home")) {
        Timber.d("Banner space disabled")
        return
    }

    // Show ad
    SpaceBanner.showInlineAdaptive(
        space = "ADMOB_Banner_Home",
        viewGroup = binding.bannerContainer,
        callback = callback
    )
}
```

### 8. Add Comprehensive Logging

**WHY**: Logging helps debug ad issues in production and track ad lifecycle events.

```kotlin
SpaceBanner.showInlineAdaptive(
    space = "ADMOB_Banner_Home",
    viewGroup = binding.bannerContainer,
    callback = object : BannerCallback {
        override fun onLoaded(adView: AdView, space: String) {
            if (BuildConfig.DEBUG) {
                Timber.d("Banner loaded: $space")
            }
        }

        override fun onFailed(space: String, error: BannerError) {
            Timber.e("Banner failed: $space - code: ${error.code}, message: ${error.message}")
        }

        override fun onImpression(space: String) {
            if (BuildConfig.DEBUG) {
                Timber.d("Banner impression: $space")
            }
        }

        override fun onClicked(space: String) {
            if (BuildConfig.DEBUG) {
                Timber.d("Banner clicked: $space")
            }
        }

        override fun onPaid(space: String, revenue: AdRevenue) {
            Timber.i("Banner revenue: $space - ${revenue.value} ${revenue.currencyCode}")
        }

        override fun onCollapsed(space: String, position: CollapsiblePosition) {
            Timber.d("Banner collapsed: $space at $position")
        }
    }
)
```

### 9. Handle Configuration Changes

**WHY**: Preserve ad state during screen rotations and configuration changes to avoid reloading ads.

```kotlin
class MainActivity : AppCompatActivity() {
    private var adView: AdView? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Restore ad view if exists
        if (savedInstanceState != null) {
            adView = savedInstanceState.getSerializable("adView") as? AdView
        }

        if (adView == null) {
            loadBanner()
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putSerializable("adView", adView)
    }

    private fun loadBanner() {
        SpaceBanner.showInlineAdaptive(
            space = "ADMOB_Banner_Home",
            viewGroup = binding.bannerContainer,
            callback = object : BannerCallback {
                override fun onLoaded(adView: AdView, space: String) {
                    this@MainActivity.adView = adView
                }
                // ... other callbacks
            }
        )
    }
}
```

### 10. Use Test Devices During Development

**WHY**: Test devices ensure you can see ads without violating AdMob policies during development.

```kotlin
// In AdSpaceSDKConfig
val config = AdSpaceSDKConfig(
    context = this,
    configRes = R.raw.ads_config,
    testDevices = listOf(
        "33BE2250B43518CCDA7DE426D04EE231", // Your device hash
        "ABCDEF0123456789ABCDEF0123456789"  // Additional test devices
    )
)

// Enable test mode
if (BuildConfig.DEBUG) {
    RequestConfiguration.Builder()
        .setTestDeviceIds(config.testDevices)
        .build()
}
```

### 11. Monitor Ad Performance

**WHY**: Tracking ad performance helps optimize fill rates and revenue.

```kotlin
class BannerPerformanceTracker {
    private var loadCount = 0
    private var successCount = 0
    private var failCount = 0

    fun recordLoad() {
        loadCount++
    }

    fun recordSuccess() {
        successCount++
    }

    fun recordFailure() {
        failCount++
    }

    fun getFillRate(): Double {
        return if (loadCount > 0) {
            (successCount.toDouble() / loadCount) * 100
        } else {
            0.0
        }
    }

    fun logReport() {
        Timber.i("Banner Performance: " +
                "Loads: $loadCount, " +
                "Success: $successCount, " +
                "Failed: $failCount, " +
                "Fill Rate: ${String.format("%.2f", getFillRate())}%")
    }
}

// Usage
val tracker = BannerPerformanceTracker()

SpaceBanner.showInlineAdaptive(
    space = "ADMOB_Banner_Home",
    viewGroup = binding.bannerContainer,
    callback = object : BannerCallback {
        override fun onLoaded(adView: AdView, space: String) {
            tracker.recordSuccess()
        }

        override fun onFailed(space: String, error: BannerError) {
            tracker.recordFailure()
        }
    }
)
```

### 12. Handle Collapsible Banners Properly

**WHY**: Collapsible banners need special handling to avoid layout issues when expanded/collapsed.

```kotlin
SpaceBanner.showCollapsible(
    space = "ADMOB_Banner_Home",
    viewGroup = binding.bannerContainer,
    position = CollapsiblePosition.BOTTOM,
    callback = object : BannerCallback {
        override fun onLoaded(adView: AdView, space: String) {
            // Make container visible when loaded
            binding.bannerContainer.visibility = View.VISIBLE
            Timber.d("Collapsible banner loaded")
        }

        override fun onCollapsed(space: String, position: CollapsiblePosition) {
            // Handle collapse - adjust layout if needed
            Timber.d("Banner collapsed at $position")
            // Optionally hide container or adjust spacing
        }

        override fun onFailed(space: String, error: BannerError) {
            // Hide container on failure
            binding.bannerContainer.visibility = View.GONE
            Timber.e("Collapsible banner failed: ${error.message}")
        }

        // ... other callbacks
    }
)
```

## Common Issues

**Banner not showing?**
- Check space is enabled in config
- Verify AdMob App ID in manifest
- Check min interval hasn't blocked the ad
- Verify test device ID is correct (for testing)

**Memory leak?**
- Always call `clearCache()` in `onDestroy()`
- Don't hold references to AdView

**Wrong size?**
- Use `showInlineAdaptive()` for scrollable content
- Use `showAnchoredAdaptive()` for fixed position
- Ensure container has proper layout params
