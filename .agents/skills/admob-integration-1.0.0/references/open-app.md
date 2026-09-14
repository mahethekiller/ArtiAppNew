# Open App Ads Integration

Open app ads are shown when users open or return to your app. AdSpaceSDK provides two types:

1. **SpaceOpenSplash** - For splash screen with timeout support
2. **SpaceOpenResume** - For automatic show on app resume

## Package Imports

```kotlin
// Splash Screen Open App Ads
import com.admob.adspace.open.SpaceOpenSplash
import com.admob.adspace.open.OpenCallback
import com.admob.adspace.open.OpenError

// Resume Open App Ads
import com.admob.adspace.open.SpaceOpenResume
```

## SpaceOpenSplash

Open app ads for splash screen with timeout support. Automatically loads, shows ad, and calls nextAction when ad is dismissed or timeout reached.

### Basic Implementation

```kotlin
import android.app.Activity
import com.admob.adspace.open.SpaceOpenSplash

class SplashActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        // Show open app splash ad with timeout
        SpaceOpenSplash.show(
            space = "ADMOB_Open_Splash",
            activity = this,
            timeoutMs = 15_000L, // 15 seconds timeout
            callback = null,
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
SpaceOpenSplash.show(
    space = "ADMOB_Open_Splash",
    activity = this,
    timeoutMs = 10_000L,
    callback = object : OpenCallback {
        override fun onLoaded(space: String) {
            Timber.d("Open app splash ad loaded")
        }

        override fun onFailed(space: String, error: OpenError) {
            Timber.e("Open app splash ad failed: ${error.message}")
            // Will still call nextAction
        }

        override fun onImpression(space: String) {
            Timber.d("Open app splash ad impression")
        }

        override fun onClicked(space: String) {
            Timber.d("Open app splash ad clicked")
        }

        override fun onPaid(space: String, revenue: AdRevenue) {
            Timber.d("Open app splash ad revenue: ${revenue.value}")
        }

        override fun onDismissed(space: String) {
            Timber.d("Open app splash ad dismissed")
        }

        override fun onAdLeftApplication(space: String) {
            Timber.d("Open app splash ad left application")
        }
    },
    nextAction = {
        navigateToMain()
    }
)
```

### Cancel Splash Operation

```kotlin
override fun onDestroy() {
    super.onDestroy()
    // Cancel splash ad operation if activity is destroyed
    SpaceOpenSplash.cancel()
}
```

### Check if Ad is Loaded

```kotlin
if (SpaceOpenSplash.isLoaded("ADMOB_Open_Splash")) {
    // Ad is loaded and ready to show
}
```

### API Methods

| Method | Parameters | Return | Description |
|--------|------------|--------|-------------|
| `show()` | space, activity, timeoutMs, callback, nextAction | Unit | Show splash ad with timeout |
| `isLoaded()` | space: String | Boolean | Check if ad is loaded |
| `cancel()` | - | Unit | Cancel current splash operation |

### Configuration

In `assets/ads_config.json`:

```json
{
  "space": "ADMOB_Open_Splash",
  "adsType": "open_app",
  "ids": [
    "ca-app-pub-3940256099942544/9257395921"
  ],
  "enable": true,
  "minInterval": 300000
}
```

**Note**: Use higher `minInterval` (5 minutes) for open app splash ads.

---

## SpaceOpenResume

Open app ads that automatically show when app returns from background (resume mode).

### Basic Implementation

```kotlin
import android.app.Application
import com.admob.adspace.AdSpaceSDK
import com.admob.adspace.open.SpaceOpenResume

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Initialize SDK
        AdSpaceSDK.initialize(this, config)

        // Register and load open app resume ads
        SpaceOpenResume.registerAndLoad(
            space = "ADMOB_Open_Resume",
            callback = object : OpenCallback {
                override fun onLoaded(space: String) {
                    Timber.d("Open app resume ad loaded")
                }

                override fun onFailed(space: String, error: OpenError) {
                    Timber.e("Open app resume ad failed: ${error.message}")
                }

                override fun onImpression(space: String) {
                    Timber.d("Open app resume impression")
                }

                override fun onClicked(space: String) {
                    Timber.d("Open app resume clicked")
                }

                override fun onPaid(space: String, revenue: AdRevenue) {
                    Timber.d("Open app resume revenue: ${revenue.value}")
                }

                override fun onDismissed(space: String) {
                    Timber.d("Open app resume dismissed")
                }

                override fun onAdLeftApplication(space: String) {
                    Timber.d("Open app resume left application")
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

        // Enable open app resume ads
        SpaceOpenResume.registerAndLoad(
            space = "ADMOB_Open_Resume",
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
val isLoaded = SpaceOpenResume.isLoaded("ADMOB_Open_Resume")

// Check if ad is ready (loaded + interval passed)
val isReady = SpaceOpenResume.isReady("ADMOB_Open_Resume")
```

### Unregister Resume Mode

```kotlin
// Disable open app resume ads
SpaceOpenResume.unregister()

// Or use AdSpaceSDK API
AdSpaceSDK.setResumeMode(AdSpaceSDK.ResumeMode.NONE, "")
```

### Preload Manually

```kotlin
// Preload open app ad without showing
SpaceOpenResume.preload(
    space = "ADMOB_Open_Resume",
    forceRefresh = false,
    callback = callback
)
```

### Clear Cache

```kotlin
// Clear specific space
SpaceOpenResume.clearCache("ADMOB_Open_Resume")

// Clear all cache
SpaceOpenResume.clearAllCache()
```

### API Methods

| Method | Parameters | Return | Description |
|--------|------------|--------|-------------|
| `registerAndLoad()` | space: String, callback: OpenCallback? | Unit | Register and load ad for automatic showing |
| `unregister()` | - | Unit | Unregister from resume mode |
| `preload()` | space, forceRefresh, callback | Unit | Preload ad without showing |
| `onAppResume()` | activity: Activity, onComplete: OnShowAdCompleteListener | Unit | Called automatically on app resume |
| `skipNextShow()` | - | Unit | Skip the next resume ad show |
| `isLoaded()` | space: String | Boolean | Check if ad is loaded |
| `isReady()` | space: String | Boolean | Check if ad is ready to show |
| `clearCache()` | space: String | Unit | Clear cached ad |
| `clearAllCache()` | - | Unit | Clear all cache |
| `getSpaceName()` | - | String? | Get current space name |
| `getResumeMode()` | - | ResumeMode | Get resume mode (OPEN_ADS) |

### Configuration

In `assets/ads_config.json`:

```json
{
  "space": "ADMOB_Open_Resume",
  "adsType": "open_app",
  "ids": [
    "ca-app-pub-3940256099942544/9257395921"
  ],
  "enable": true,
  "minInterval": 240000
}
```

**Note**: Use 3-4 minutes (240000ms) for `minInterval` to avoid annoying users.

## SpaceOpenSplash vs SpaceOpenResume

| Feature | SpaceOpenSplash | SpaceOpenResume |
|---------|-----------------|-----------------|
| **Use Case** | Splash screen on app cold start | App resume from background |
| **Timeout** | Yes (configurable, default 15s) | No timeout |
| **Next Action** | Required callback | Automatic via resume mode |
| **Manual Control** | Show manually | Automatic show on resume |
| **Lifecycle** | Single show per call | Can show multiple times |
| **Cache** | No caching between calls | Caches ad for resume |

## Best Practices

### SpaceOpenSplash

1. **Appropriate timeout** - Use 10-15 seconds
2. **Handle timeout gracefully** - Always call nextAction even if timeout
3. **Don't block app** - App should work without splash ad
4. **Cancel on destroy** - Call `cancel()` in Activity.onDestroy()

### SpaceOpenResume

1. **Higher min interval** - 3-4 minutes recommended
2. **Exclude key screens** - Don't show on splash, login, payment
3. **Use skipNextShow()** - Skip after critical user actions
4. **Monitor metrics** - Track user retention and session length
5. **Test thoroughly** - Verify ads don't disrupt critical flows

## Common Patterns

### Pattern 1: Exclude Multiple Activities

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        AdSpaceSDK.initialize(this, config)

        // Enable open app resume ads
        SpaceOpenResume.registerAndLoad(
            space = "ADMOB_Open_Resume",
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

### Pattern 2: Skip After User Action

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

### Pattern 3: Dynamic Toggle

```kotlin
class SettingsActivity : AppCompatActivity() {

    private fun updateResumeAdSettings(enabled: Boolean) {
        if (enabled) {
            // Re-enable with default space
            SpaceOpenResume.registerAndLoad(
                space = "ADMOB_Open_Resume",
                callback = null
            )
        } else {
            // Disable resume ads
            SpaceOpenResume.unregister()
        }
    }
}
```

### Pattern 4: Splash with Fallback

```kotlin
class SplashActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        // Try to show splash ad with timeout
        SpaceOpenSplash.show(
            space = "ADMOB_Open_Splash",
            activity = this,
            timeoutMs = 10_000L,
            callback = createSplashCallback(),
            nextAction = {
                // Always navigate to main, with or without ad
                navigateToMain()
            }
        )
    }

    private fun navigateToMain() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }

    override fun onDestroy() {
        super.onDestroy()
        SpaceOpenSplash.cancel()
    }
}
```

## Common Issues

**Open app ads showing too frequently?**
- Increase `minInterval` to 240000 (4 minutes) or higher
- SDK enforces min interval automatically

**Open app ads showing on wrong screens?**
- Use `AdSpaceSDK.setIgnoreAdResume()` to exclude activities
- Exclude splash, login, payment, video player screens

**Open app ads not showing?**
- Check resume mode is set correctly via `AdSpaceSDK.getActiveResumeMode()`
- Verify space is enabled in config
- Check min interval hasn't blocked the ad
- Ensure activity is not in excluded list
- Check ad is loaded with `isLoaded()` and ready with `isReady()`

**Splash timeout not working?**
- Timeout is in milliseconds (15_000 = 15 seconds)
- nextAction is always called, even on timeout
- Cancel operation with `SpaceOpenSplash.cancel()` if needed

**Resume ads showing immediately after cold start?**
- This is expected behavior on first resume
- Use higher min interval to avoid
- Exclude splash activity from resume ads

## Comparison: Open App vs Interstitial Resume

| Feature | SpaceOpenResume | SpaceInterstitialResume |
|---------|-----------------|-------------------------|
| **Ad Type** | Open app ads | Interstitial ads |
| **Resume Mode** | `ResumeMode.OPEN_ADS` | `ResumeMode.INTERSTITIAL` |
| **Welcome Dialog** | No dialog | Shows "Welcome back" dialog |
| **User Experience** | Less intrusive, more natural | More intrusive |
| **Revenue** | Typically higher (campaign ads) | Standard interstitial revenue |
| **Use Case** | General app resuming | When you want more control |

---

## Jetpack Compose Integration

AdSpaceSDK supports Jetpack Compose for showing open app ads.

### SpaceOpenSplash in Compose

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
import com.admob.adspace.open.SpaceOpenSplash
import com.admob.adspace.open.OpenCallback
import com.admob.adspace.open.OpenError

@Composable
fun OpenAppSplashScreen(
    spaceName: String = "ADMOB_Open_Splash",
    timeoutMs: Long = 15_000L,
    onSplashComplete: () -> Unit
) {
    val context = LocalContext.current
    var splashCompleted by remember { mutableStateOf(false) }

    // Lifecycle observer for cleanup
    val lifecycleOwner = LocalLifecycleOwner.current
    androidx.compose.runtime.DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_DESTROY) {
                SpaceOpenSplash.cancel()
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }

    // Show splash ad
    LaunchedEffect(Unit) {
        SpaceOpenSplash.show(
            space = spaceName,
            activity = context as Activity,
            timeoutMs = timeoutMs,
            callback = object : OpenCallback {
                override fun onLoaded(space: String) {
                    // Splash ad loaded
                }

                override fun onFailed(space: String, error: OpenError) {
                    // Will still call nextAction
                }

                override fun onImpression(space: String) {}

                override fun onClicked(space: String) {}

                override fun onPaid(space: String, revenue: AdRevenue) {}

                override fun onDismissed(space: String) {
                    splashCompleted = true
                }

                override fun onAdLeftApplication(space: String) {}
            },
            nextAction = {
                splashCompleted = true
                onSplashComplete()
            }
        )
    }

    // Show loading UI while waiting
    if (!splashCompleted) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                CircularProgressIndicator()
                Spacer(modifier = Modifier.height(16.dp))
                Text("Loading...")
            }
        }
    }
}
```

### SpaceOpenSplash with Custom Loading UI

```kotlin
@Composable
fun CustomOpenAppSplashScreen(
    spaceName: String = "ADMOB_Open_Splash",
    timeoutMs: Long = 10_000L,
    onSplashComplete: () -> Unit
) {
    val context = LocalContext.current
    var splashCompleted by remember { mutableStateOf(false) }
    var elapsedTime by remember { mutableStateOf(0L) }

    // Track elapsed time for progress
    LaunchedEffect(Unit) {
        val startTime = System.currentTimeMillis()
        while (!splashCompleted && elapsedTime < timeoutMs) {
            kotlinx.coroutines.delay(100)
            elapsedTime = System.currentTimeMillis() - startTime
        }
    }

    // Show splash ad
    LaunchedEffect(Unit) {
        SpaceOpenSplash.show(
            space = spaceName,
            activity = context as Activity,
            timeoutMs = timeoutMs,
            callback = null,
            nextAction = {
                splashCompleted = true
                onSplashComplete()
            }
        )
    }

    // Custom splash UI with progress
    if (!splashCompleted) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(MaterialTheme.colorScheme.primary),
            contentAlignment = Alignment.Center
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                // App logo
                Icon(
                    painter = painterResource(id = R.drawable.ic_launcher_foreground),
                    contentDescription = "App Logo",
                    modifier = Modifier.size(120.dp),
                    tint = Color.White
                )

                Spacer(modifier = Modifier.height(32.dp))

                // App name
                Text(
                    text = "My App",
                    style = MaterialTheme.typography.headlineMedium,
                    color = Color.White
                )

                Spacer(modifier = Modifier.height(48.dp))

                // Progress indicator
                LinearProgressIndicator(
                    progress = { elapsedTime.toFloat() / timeoutMs.toFloat() },
                    modifier = Modifier
                        .fillMaxWidth(0.6f)
                        .height(4.dp),
                    color = Color.White,
                )

                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    text = "Loading ${(elapsedTime / 1000).toInt()}s",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.White.copy(alpha = 0.8f)
                )
            }
        }
    }
}
```

### SpaceOpenResume Integration in Compose

```kotlin
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.admob.adspace.open.SpaceOpenResume

@Composable
fun OpenAppResumeHandler(
    spaceName: String = "ADMOB_Open_Resume",
    enabled: Boolean = true
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    // Register/unregister based on enabled state
    SideEffect {
        if (enabled) {
            SpaceOpenResume.registerAndLoad(
                space = spaceName,
                callback = object : OpenCallback {
                    override fun onLoaded(space: String) {}

                    override fun onFailed(space: String, error: OpenError) {}

                    override fun onImpression(space: String) {}

                    override fun onClicked(space: String) {}

                    override fun onPaid(space: String, revenue: AdRevenue) {}

                    override fun onDismissed(space: String) {}

                    override fun onAdLeftApplication(space: String) {}
                }
            )
        } else {
            SpaceOpenResume.unregister()
        }
    }

    // Cleanup on dispose
    androidx.compose.runtime.DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_DESTROY) {
                SpaceOpenResume.clearCache(spaceName)
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
            if (enabled) {
                SpaceOpenResume.unregister()
            }
        }
    }
}

// Usage in MainActivity
@Composable
fun MainScreen() {
    val context = LocalContext.current

    // Enable open app resume ads
    OpenAppResumeHandler(
        spaceName = "ADMOB_Open_Resume",
        enabled = true
    )

    // Your app content
    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Welcome to My App")
    }
}
```

### OpenAppResumeManager for Compose

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.admob.adspace.open.SpaceOpenResume
import com.admob.adspace.open.OpenCallback
import com.admob.adspace.open.OpenError
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class OpenAppResumeManager(
    private val spaceName: String = "ADMOB_Open_Resume"
) : ViewModel() {

    private val _isRegistered = MutableStateFlow(false)
    val isRegistered: StateFlow<Boolean> = _isRegistered.asStateFlow()

    private val _isLoaded = MutableStateFlow(false)
    val isLoaded: StateFlow<Boolean> = _isLoaded.asStateFlow()

    fun register() {
        viewModelScope.launch {
            SpaceOpenResume.registerAndLoad(
                space = spaceName,
                callback = object : OpenCallback {
                    override fun onLoaded(space: String) {
                        _isLoaded.value = true
                    }

                    override fun onFailed(space: String, error: OpenError) {
                        _isLoaded.value = false
                    }

                    override fun onImpression(space: String) {}

                    override fun onClicked(space: String) {}

                    override fun onPaid(space: String, revenue: AdRevenue) {}

                    override fun onDismissed(space: String) {}

                    override fun onAdLeftApplication(space: String) {}
                }
            )
            _isRegistered.value = true
        }
    }

    fun unregister() {
        SpaceOpenResume.unregister()
        _isRegistered.value = false
        _isLoaded.value = false
    }

    fun clearCache() {
        SpaceOpenResume.clearCache(spaceName)
        _isLoaded.value = false
    }

    fun skipNextShow() {
        SpaceOpenResume.skipNextShow()
    }

    override fun onCleared() {
        super.onCleared()
        unregister()
    }
}

@Composable
fun OpenAppResumeSettings(
    manager: OpenAppResumeManager = viewModel()
) {
    val isRegistered by manager.isRegistered.collectAsState()
    val isLoaded by manager.isLoaded.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        Text(
            text = "Open App Resume Ads",
            style = MaterialTheme.typography.titleLarge
        )

        Spacer(modifier = Modifier.height(16.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Enable Resume Ads")
            Switch(
                checked = isRegistered,
                onCheckedChange = { enabled ->
                    if (enabled) {
                        manager.register()
                    } else {
                        manager.unregister()
                    }
                }
            )
        }

        if (isRegistered) {
            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Ad Status")
                Text(
                    text = if (isLoaded) "Ready" else "Loading...",
                    color = if (isLoaded) {
                        MaterialTheme.colorScheme.primary
                    } else {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    }
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = { manager.skipNextShow() },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Skip Next Show")
            }
        }
    }
}
```

### Best Practices for Compose

1. **SideEffect for registration** - Use SideEffect for one-time operations like registerAndLoad
2. **DisposableEffect for cleanup** - Clear cache and unregister on dispose
3. **State management** - Track ad status with StateFlow/remember
4. **Lifecycle awareness** - Respect Compose lifecycle
5. **Loading UI** - Show progress indicator during splash timeout
6. **Custom splash UI** - Create branded splash screens with progress
7. **ViewModel integration** - Use ViewModel for complex resume ad management
8. **Error handling** - Handle ad failures gracefully without blocking UI
9. **Timeout handling** - Always respect timeout and call nextAction
10. **Memory management** - Clear resources in DisposableEffect onDispose
