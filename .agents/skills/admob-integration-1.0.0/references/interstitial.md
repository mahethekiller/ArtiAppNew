# Interstitial Ads Integration

Interstitial ads are full-screen ads that cover the interface of the app.

## Package Imports

```kotlin
// Standard Interstitial
import com.admob.adspace.interstitial.SpaceInterstitial
import com.admob.adspace.interstitial.InterstitialCallback
import com.admob.adspace.interstitial.InterstitialError

// Splash Screen Interstitial
import com.admob.adspace.interstitial.SpaceInterstitialSplash

// Resume Interstitial
import com.admob.adspace.interstitial.SpaceInterstitialResume
```

## Basic Implementation

```kotlin
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import com.admob.adspace.interstitial.SpaceInterstitial
import com.admob.adspace.interstitial.InterstitialCallback
import com.admob.adspace.interstitial.InterstitialError

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Preload interstitial
        preloadInterstitial()

        // Show on button click
        binding.btnShowAd.setOnClickListener {
            showInterstitial()
        }
    }

    private fun preloadInterstitial() {
        SpaceInterstitial.preload(
            space = "ADMOB_Interstitial_General",
            forceRefresh = false,
            callback = object : InterstitialCallback {
                override fun onLoaded(space: String) {
                    // Ad loaded and ready
                }

                override fun onFailed(space: String, error: InterstitialError) {
                    // Failed to load
                }

                override fun onShowed(space: String) {
                    // Ad displayed
                }

                override fun onDismissed(space: String) {
                    // Ad dismissed, preload next ad
                    preloadInterstitial()
                }

                override fun onClicked(space: String) {
                    // Ad clicked
                }

                override fun onImpression(space: String) {
                    // Impression recorded
                }

                override fun onPaid(space: String, revenue: AdRevenue) {
                    // Revenue: revenue.value
                }
            }
        )
    }

    private fun showInterstitial() {
        SpaceInterstitial.show(
            space = "ADMOB_Interstitial_General",
            activity = this,
            forceShow = false,
            loadIfNotAvailable = true,
            showLoading = true,
            customLoadingView = null,
            callback = object : InterstitialCallback {
                override fun onLoaded(space: String) {}
                override fun onFailed(space: String, error: InterstitialError) {}
                override fun onShowed(space: String) {}
                override fun onDismissed(space: String) {
                    // Continue app flow
                }
                override fun onClicked(space: String) {}
                override fun onImpression(space: String) {}
                override fun onPaid(space: String, revenue: AdRevenue) {}
            }
        )
    }
}
```

## Show Methods

### Show with Auto-Load

Automatically loads ad if not available:

```kotlin
SpaceInterstitial.show(
    space = "ADMOB_Interstitial_General",
    activity = this,
    forceShow = false,
    loadIfNotAvailable = true,
    showLoading = true,
    callback = callback
)
```

### Show Only if Loaded

Only shows if ad is already loaded:

```kotlin
SpaceInterstitial.show(
    space = "ADMOB_Interstitial_General",
    activity = this,
    forceShow = false,
    loadIfNotAvailable = false,
    showLoading = false,
    callback = callback
)
```

### Force Show (Bypass Min Interval)

```kotlin
SpaceInterstitial.show(
    space = "ADMOB_Interstitial_General",
    activity = this,
    forceShow = true, // Bypass min interval check
    loadIfNotAvailable = true,
    showLoading = true,
    callback = callback
)
```

### Custom Loading View

```kotlin
val customLoading = layoutInflater.inflate(R.layout.custom_loading, null)

SpaceInterstitial.show(
    space = "ADMOB_Interstitial_General",
    activity = this,
    forceShow = false,
    loadIfNotAvailable = true,
    showLoading = true,
    customLoadingView = customLoading,
    callback = callback
)
```

## Advanced Features

### Check if Ad is Ready

```kotlin
if (SpaceInterstitial.isLoaded("ADMOB_Interstitial_General")) {
    // Ad is ready to show
    showInterstitial()
} else {
    // Preload ad
    preloadInterstitial()
}
```

### Clear Cache

```kotlin
SpaceInterstitial.clearCache("ADMOB_Interstitial_General")
```

## Configuration

In `assets/ads_config.json`:

```json
{
  "space": "ADMOB_Interstitial_General",
  "adsType": "interstitial",
  "ids": [
    "ca-app-pub-3940256099942544/1033173712",
    "ca-app-pub-3940256099942544/8691691433"
  ],
  "enable": true,
  "minInterval": 60000
}
```

## Best Practices

1. **Preload early** - Load ads before you need them
2. **Show at natural breaks** - Between levels, after actions
3. **Reload after dismiss** - Preload next ad immediately
4. **Use loading dialog** - Better UX while loading
5. **Respect min interval** - Don't spam users with ads
6. **Check if loaded** - Before showing to avoid delays
7. **Handle failures gracefully** - Continue app flow if ad fails

## Common Patterns

### Show Between Levels

```kotlin
fun onLevelComplete() {
    // Show interstitial after level
    SpaceInterstitial.show(
        space = "ADMOB_Interstitial_Level",
        activity = this,
        loadIfNotAvailable = true,
        showLoading = true,
        callback = object : InterstitialCallback {
            override fun onDismissed(space: String) {
                // Continue to next level
                startNextLevel()
            }
            override fun onFailed(space: String, error: InterstitialError) {
                // Continue anyway
                startNextLevel()
            }
            // ... other callbacks
        }
    )
}
```

### Preload on App Start

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Initialize SDK
        AdSpaceSDK.initialize(this, config)

        // Preload interstitial
        SpaceInterstitial.preload(
            space = "ADMOB_Interstitial_General",
            callback = callback
        )
    }
}
```

## Common Issues

**Ad not showing?**
- Check if ad is loaded with `isLoaded()`
- Verify min interval hasn't blocked the ad
- Check space is enabled in config
- Ensure Activity is not finishing

**Loading takes too long?**
- Preload ads early
- Use loading dialog for better UX
- Consider waterfall with multiple ad unit IDs

**Ad shows too frequently?**
- Increase `minInterval` in config
- Don't use `forceShow = true` unless necessary

---

## Jetpack Compose Integration

AdSpaceSDK supports Jetpack Compose for showing interstitial ads.

### Basic Implementation

```kotlin
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.admob.adspace.interstitial.SpaceInterstitial
import com.admob.adspace.interstitial.InterstitialCallback
import com.admob.adspace.interstitial.InterstitialError

@Composable
fun InterstitialAdScreen(
    spaceName: String = "ADMOB_Interstitial_General"
) {
    val context = LocalContext.current
    var adLoaded by remember { mutableStateOf(false) }
    var lastShowTime by remember { mutableStateOf(0L) }

    // Lifecycle observer for cleanup
    val lifecycleOwner = LocalLifecycleOwner.current
    androidx.compose.runtime.DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_DESTROY) {
                SpaceInterstitial.clearCache(spaceName)
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }

    // Load ad on first composition
    LaunchedEffect(Unit) {
        SpaceInterstitial.load(
            space = spaceName,
            callback = object : InterstitialCallback {
                override fun onLoaded(space: String) {
                    adLoaded = true
                }

                override fun onFailed(space: String, error: InterstitialError) {
                    adLoaded = false
                }
            }
        )
    }

    // Show ad button
    Button(
        onClick = {
            if (adLoaded && System.currentTimeMillis() - lastShowTime > 30000) {
                SpaceInterstitial.show(
                    activity = context as Activity,
                    space = spaceName,
                    callback = object : InterstitialCallback {
                        override fun onShowed(space: String) {
                            lastShowTime = System.currentTimeMillis()
                            adLoaded = false
                        }

                        override fun onDismissed(space: String) {
                            // Preload next ad
                            SpaceInterstitial.preload(spaceName, null)
                        }
                    }
                )
            }
        },
        enabled = adLoaded
    ) {
        Text("Show Ad")
    }
}
```

### Advanced Compose Pattern with ViewModel

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.admob.adspace.interstitial.SpaceInterstitial
import com.admob.adspace.interstitial.InterstitialCallback
import com.admob.adspace.interstitial.InterstitialError
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class InterstitialAdViewModel(
    private val spaceName: String = "ADMOB_Interstitial_General"
) : ViewModel() {

    private val _adState = MutableStateFlow<AdState>(AdState.Idle)
    val adState: StateFlow<AdState> = _adState.asStateFlow()

    sealed class AdState {
        object Idle : AdState()
        object Loading : AdState()
        object Loaded : AdState()
        data class Error(val message: String) : AdState()
    }

    init {
        preloadAd()
    }

    fun preloadAd() {
        viewModelScope.launch {
            _adState.value = AdState.Loading
            SpaceInterstitial.load(
                space = spaceName,
                callback = object : InterstitialCallback {
                    override fun onLoaded(space: String) {
                        _adState.value = AdState.Loaded
                    }

                    override fun onFailed(space: String, error: InterstitialError) {
                        _adState.value = AdState.Error(error.message)
                    }
                }
            )
        }
    }

    fun showAd(activity: Activity, onComplete: () -> Unit) {
        SpaceInterstitial.show(
            space = spaceName,
            activity = activity,
            callback = object : InterstitialCallback {
                override fun onShowed(space: String) {
                    _adState.value = AdState.Idle
                }

                override fun onDismissed(space: String) {
                    onComplete()
                    preloadAd()
                }

                override fun onFailed(space: String, error: InterstitialError) {
                    onComplete()
                    preloadAd()
                }
            }
        )
    }
}

@Composable
fun InterstitialAdScreenWithViewModel(
    viewModel: InterstitialAdViewModel = viewModel()
) {
    val context = LocalContext.current
    val adState by viewModel.adState.collectAsState()

    Button(
        onClick = {
            viewModel.showAd(context as Activity) {
                // Handle ad completion
            }
        },
        enabled = adState is AdState.Loaded
    ) {
        when (adState) {
            is AdState.Loading -> Text("Loading...")
            is AdState.Loaded -> Text("Show Ad")
            else -> Text("Load Ad")
        }
    }
}
```

### Best Practices for Compose

1. **Use DisposableEffect for cleanup** - Clear ad cache in ON_DESTROY
2. **LaunchedEffect for one-time operations** - Load ads on first composition
3. **State management** - Track ad load status with remember/mutableStateOf
4. **Lifecycle awareness** - Respect Compose lifecycle
5. **Context handling** - Use LocalContext.current appropriately
6. **ViewModel integration** - Use ViewModel for complex ad state management
7. **Reactive updates** - Use StateFlow/Flow for ad state changes
8. **Memory management** - Clear resources in DisposableEffect onDispose

---

## SpaceInterstitialSplash

Interstitial ads for splash screen with timeout support. Automatically loads, shows ad, and calls nextAction when ad is dismissed or timeout reached.

### Basic Implementation

```kotlin
import android.app.Activity
import com.admob.adspace.interstitial.SpaceInterstitialSplash

class SplashActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        // Show splash ad with timeout
        SpaceInterstitialSplash.show(
            space = "ADMOB_Interstitial_Splash",
            activity = this,
            timeoutMs = 15_000L, // 15 seconds timeout
            showLoading = false,
            customLoadingView = null,
            showAdCallback = null,
            nextAction = {
                // Navigate to main screen
                navigateToMain()
            }
        )
    }

    private fun navigateToMain() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
}
```

### With Custom Callback

```kotlin
SpaceInterstitialSplash.show(
    space = "ADMOB_Interstitial_Splash",
    activity = this,
    timeoutMs = 10_000L,
    showLoading = false,
    showAdCallback = object : InterstitialCallback {
        override fun onLoaded(space: String) {
            Timber.d("Splash ad loaded")
        }

        override fun onFailed(space: String, error: InterstitialError) {
            Timber.e("Splash ad failed: ${error.message}")
            // Will still call nextAction
        }

        override fun onImpression(space: String) {
            Timber.d("Splash ad impression")
        }

        override fun onClicked(space: String) {
            Timber.d("Splash ad clicked")
        }

        override fun onPaid(space: String, revenue: AdRevenue) {
            Timber.d("Splash ad revenue: ${revenue.value}")
        }

        override fun onDismissed(space: String) {
            Timber.d("Splash ad dismissed")
        }

        override fun onAdLeftApplication(space: String) {
            Timber.d("Splash ad left application")
        }
    },
    nextAction = {
        navigateToMain()
    }
)
```

### With Custom Loading View

```kotlin
// Create custom loading view
val customLoading = layoutInflater.inflate(R.layout.custom_splash_loading, null)

SpaceInterstitialSplash.show(
    space = "ADMOB_Interstitial_Splash",
    activity = this,
    timeoutMs = 15_000L,
    showLoading = true,
    customLoadingView = customLoading,
    showAdCallback = null,
    nextAction = {
        navigateToMain()
    }
)
```

### API Methods

| Method | Parameters | Return | Description |
|--------|------------|--------|-------------|
| `show()` | space, activity, timeoutMs, showLoading, customLoadingView, showAdCallback, nextAction | Unit | Show splash ad with timeout |
| `isLoaded()` | space: String | Boolean | Check if ad is loaded |
| `clearCache()` | space: String | Unit | Clear cached ad |
| `cancel()` | - | Unit | Cancel current splash operation |

### Best Practices

1. **Appropriate timeout** - Use 10-15 seconds for splash ads
2. **Handle timeout gracefully** - Always call nextAction even if timeout
3. **Don't block app** - App should work without splash ad
4. **Preload if possible** - Load ad before splash screen starts
5. **Use loading dialog** - Better UX while waiting for ad

### Configuration

In `assets/ads_config.json`:

```json
{
  "space": "ADMOB_Interstitial_Splash",
  "adsType": "interstitial",
  "ids": [
    "ca-app-pub-3940256099942544/1033173712"
  ],
  "enable": true,
  "minInterval": 300000
}
```

**Note**: Use higher `minInterval` (5 minutes) for splash ads to avoid showing on every app start.

---

## SpaceInterstitialResume

Interstitial ads that automatically show when app returns from background (resume mode).

### Basic Implementation

```kotlin
import android.app.Application
import com.admob.adspace.AdSpaceSDK
import com.admob.adspace.interstitial.SpaceInterstitialResume

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Initialize SDK
        AdSpaceSDK.initialize(this, config)

        // Register and load interstitial resume ads
        SpaceInterstitialResume.registerAndLoad(
            space = "ADMOB_Interstitial_Resume",
            callback = object : InterstitialCallback {
                override fun onLoaded(space: String) {
                    Timber.d("Interstitial resume ad loaded")
                }

                override fun onFailed(space: String, error: InterstitialError) {
                    Timber.e("Interstitial resume ad failed: ${error.message}")
                }

                override fun onImpression(space: String) {
                    Timber.d("Interstitial resume impression")
                }

                override fun onClicked(space: String) {
                    Timber.d("Interstitial resume clicked")
                }

                override fun onPaid(space: String, revenue: AdRevenue) {
                    Timber.d("Interstitial resume revenue: ${revenue.value}")
                }

                override fun onDismissed(space: String) {
                    Timber.d("Interstitial resume dismissed")
                }

                override fun onAdLeftApplication(space: String) {
                    Timber.d("Interstitial resume left application")
                }
            }
        )
    }
}
```

### Exclude Activities

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        AdSpaceSDK.initialize(this, config)

        // Enable interstitial resume ads
        SpaceInterstitialResume.registerAndLoad(
            space = "ADMOB_Interstitial_Resume",
            callback = callback
        )

        // Exclude activities from showing resume ads
        AdSpaceSDK.setIgnoreAdResume(SplashActivity::class.java)
        AdSpaceSDK.setIgnoreAdResume(LoginActivity::class.java)
        AdSpaceSDK.setIgnoreAdResume(OnboardingActivity::class.java)
    }
}
```

### Skip Next Show

```kotlin
class PaymentActivity : AppCompatActivity() {

    private fun processPayment() {
        // Skip next resume ad after payment
        AdSpaceSDK.skipNextShow()

        // Process payment
        processPaymentInternal()
    }
}
```

### Check Status

```kotlin
// Check if ad is loaded
val isLoaded = SpaceInterstitialResume.isLoaded("ADMOB_Interstitial_Resume")

// Check if ad is ready (loaded + interval passed)
val isReady = SpaceInterstitialResume.isReady("ADMOB_Interstitial_Resume")

// Get detailed status
val status = SpaceInterstitialResume.getStatus()
Timber.d("Interstitial resume status: $status")
```

### Unregister Resume Mode

```kotlin
// Disable interstitial resume ads
SpaceInterstitialResume.unregister()

// Or use AdSpaceSDK API
AdSpaceSDK.setResumeMode(AdSpaceSDK.ResumeMode.NONE, "")
```

### API Methods

| Method | Parameters | Return | Description |
|--------|------------|--------|-------------|
| `registerAndLoad()` | space: String, callback: InterstitialCallback? | Unit | Register and load ad for automatic showing |
| `unregister()` | - | Unit | Unregister from resume mode |
| `isLoaded()` | space: String | Boolean | Check if ad is loaded |
| `isReady()` | space: String | Boolean | Check if ad is ready to show |
| `clearCache()` | space: String | Unit | Clear cached ad |
| `skipNextShow()` | - | Unit | Skip the next resume ad show |
| `getStatus()` | - | String | Get detailed status information |

### Configuration

In `assets/ads_config.json`:

```json
{
  "space": "ADMOB_Interstitial_Resume",
  "adsType": "interstitial",
  "ids": [
    "ca-app-pub-3940256099942544/1033173712"
  ],
  "enable": true,
  "minInterval": 180000
}
```

**Note**: Use 3-4 minutes (180000-240000ms) for `minInterval` to avoid annoying users.

### Best Practices

1. **Higher min interval** - 3-4 minutes recommended
2. **Exclude key screens** - Don't show on splash, login, payment
3. **Use skipNextShow()** - Skip after critical user actions
4. **Monitor metrics** - Track user retention and session length
5. **Test thoroughly** - Verify ads don't disrupt critical flows

### Common Patterns

#### Pattern 1: Exclude Multiple Activities

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        AdSpaceSDK.initialize(this, config)

        // Enable interstitial resume ads
        SpaceInterstitialResume.registerAndLoad(
            space = "ADMOB_Interstitial_Resume",
            callback = callback
        )

        // Exclude multiple activities
        val excludedActivities = listOf(
            SplashActivity::class.java,
            LoginActivity::class.java,
            OnboardingActivity::class.java,
            PaymentActivity::class.java,
            VideoPlayerActivity::class.java
        )

        excludedActivities.forEach { activityClass ->
            AdSpaceSDK.setIgnoreAdResume(activityClass)
        }
    }
}
```

#### Pattern 2: Skip After User Action

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onDestroy() {
        super.onDestroy()

        // Skip next resume ad after user completes important action
        if (userCompletedImportantAction) {
            AdSpaceSDK.skipNextShow()
        }
    }
}
```

#### Pattern 3: Dynamic Toggle

```kotlin
class SettingsActivity : AppCompatActivity() {

    private fun updateResumeAdSettings(enabled: Boolean) {
        if (enabled) {
            // Re-enable with default space
            SpaceInterstitialResume.registerAndLoad(
                space = "ADMOB_Interstitial_Resume",
                callback = null
            )
        } else {
            // Disable resume ads
            SpaceInterstitialResume.unregister()
        }
    }
}
```

### SpaceInterstitialResume vs SpaceOpenResume

| Feature | SpaceInterstitialResume | SpaceOpenResume |
|---------|------------------------|------------------|
| **Ad Type** | Interstitial ads | Open app ads |
| **Resume Mode** | `ResumeMode.INTERSTITIAL` | `ResumeMode.OPEN_ADS` |
| **Use Case** | Regular interstitial on resume | Campaign/open app ads |
| **Welcome Dialog** | Shows "Welcome back" dialog | No dialog |
| **Revenue** | Standard interstitial revenue | Typically higher |
| **User Experience** | More intrusive | Less intrusive |

### Common Issues

**Resume ads showing too frequently?**
- Increase `minInterval` to 240000 (4 minutes) or higher
- SDK enforces min interval automatically

**Resume ads showing on wrong screens?**
- Use `AdSpaceSDK.setIgnoreAdResume()` to exclude activities
- Exclude splash, login, payment, video player screens

**Resume ads not showing?**
- Check resume mode is set correctly via `AdSpaceSDK.getActiveResumeMode()`
- Verify space is enabled in config
- Check min interval hasn't blocked the ad
- Ensure activity is not in excluded list
- Check ad is loaded with `isLoaded()` and ready with `isReady()`

**Welcome dialog not dismissing?**
- Dialog auto-dismisses after 500ms when ad completes
- Check logs for dialog dismiss errors
- Ensure activity is not destroyed during ad show
