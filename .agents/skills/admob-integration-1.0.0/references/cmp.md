# CMP Consent Management

CMP (Consent Management Platform) integration using Google UMP SDK for GDPR/privacy compliance.

## Package Imports

```kotlin
import com.admob.adspace.AdSpaceSDK
import com.admob.adspace.cmp.CMPManager
import com.admob.adspace.cmp.ConsentStatus
import com.google.android.ump.ConsentDebugSettings
import com.google.android.ump.ConsentInformation
import com.google.android.ump.UserMessagingPlatform
```

## Overview

AdSpaceSDK integrates Google's User Messaging Platform (UMP) for GDPR/privacy consent management. CMP consent is **required** before showing ads in regions with privacy regulations (EU/UK/EEA).

### Key Features

- **Automatic consent flow** - SDK handles everything automatically
- **Loading dialog** - Shows while consent form loads
- **Lifecycle-aware** - Properly handles Activity lifecycle
- **Persistent consent** - Saves user choice across sessions
- **Privacy options** - Allows users to change consent settings
- **Debug support** - Test consent flow in any region

## Automatic CMP Flow (Recommended)

By default, SDK handles CMP automatically:

1. **App starts** → `AdSpaceSDK.initialize()` called
2. **Config loads** → `ConfigManager` loads local + remote config
3. **CMP initializes** → `CMPManager.initialize()` prepares consent info
4. **First Activity resume** → CMP consent form shows (if `cmp_auto=true` and consent required)
5. **User interacts** → User accepts/rejects consent
6. **AdMob initializes** → `AdMobManager.initialize()` called after consent
7. **Ads ready** → Ads can now be requested

### Enable Auto CMP

In `assets/ads_config.json`:

```json
{
  "ads": {
    "global": {
      "enable": true,
      "cmp_auto": true,
      "min_interval": 30000
    }
  }
}
```

**cmp_auto options**:
- `true` - SDK automatically shows consent form on first Activity resume (recommended)
- `false` - Manual consent management required

### What Happens Automatically

When `cmp_auto=true`:

1. **Loading dialog appears** - Custom loading dialog shows while consent form loads
2. **Consent form loads** - UMP SDK fetches consent form from Google
3. **Form displays** - User sees consent options
4. **User chooses** - User accepts/rejects consent
5. **Dialog dismisses** - Loading dialog auto-dismisses
6. **AdMob initializes** - SDK initializes AdMob after consent gathered
7. **Callback fires** - `onConsentGathered` callback invoked

## Consent Flow Completed Callback

Receive notifications when the CMP consent flow completes (both auto and manual modes).

### Overview

The consent flow completed callback allows you to react when the consent flow finishes, whether triggered automatically by the SDK or manually via `requestConsent()`. This is useful for:

- Triggering post-consent initialization logic
- Logging consent results for analytics
- Updating UI based on consent status
- Starting ad loading after consent obtained

### Setting the Callback

```kotlin
import com.admob.adspace.AdSpaceSDK

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Set consent flow completed callback
        AdSpaceSDK.setConsentFlowCompletedCallback { canRequestAds ->
            if (canRequestAds) {
                // User consent obtained - ads can be requested
                Timber.d("Consent obtained - ads ready")
                initializeAdSpaces()
            } else {
                // Consent not obtained - ads cannot be requested
                Timber.d("Consent not obtained - ads blocked")
                handleConsentDenied()
            }
        }
    }

    private fun initializeAdSpaces() {
        // Start loading ads
        SpaceBanner.preload("ADMOB_Banner_Home")
        SpaceInterstitial.preload("ADMOB_Interstitial_General")
    }

    private fun handleConsentDenied() {
        // Show non-ad version or alternative monetization
        showPremiumUpgradeDialog()
    }

    override fun onDestroy() {
        super.onDestroy()
        // IMPORTANT: Always clear callback to prevent memory leaks
        AdSpaceSDK.setConsentFlowCompletedCallback(null)
    }
}
```

### Callback Behavior

**When it fires**:
- After auto CMP flow completes (when `cmp_auto=true`)
- After manual `requestConsent()` call completes
- Only once per consent flow session

**Boolean parameter**:
- `true` - Consent obtained, ads can be requested (`canRequestAds() == true`)
- `false` - Consent not obtained, ads cannot be requested

**Thread safety**: Callback is invoked on the main thread.

### Memory Management

**CRITICAL**: Always clear the callback in `onDestroy()` to prevent memory leaks:

```kotlin
override fun onDestroy() {
    super.onDestroy()
    // ALWAYS clear callback to avoid memory leak
    AdSpaceSDK.setConsentFlowCompletedCallback(null)
}
```

### Self-Clearing Pattern

For one-time callbacks, use the self-clearing pattern:

```kotlin
AdSpaceSDK.setConsentFlowCompletedCallback { canRequestAds ->
    // Handle callback
    onConsentFlowCompleted(canRequestAds)

    // Immediately clear callback after invocation
    AdSpaceSDK.setConsentFlowCompletedCallback(null)
}
```

This pattern is useful when you only need to handle the callback once and don't want to track lifecycle manually.

### Best Practices

1. **Always clear in onDestroy** - Prevent memory leaks by clearing callback in Activity/Fragment `onDestroy()`
2. **Check Boolean parameter** - The parameter tells you if ads can be requested, not just that flow completed
3. **Thread-safe** - Callback fires on main thread, safe to update UI directly
4. **Use for analytics** - Log consent results to track user consent rates
5. **Combine with canShowAds()** - For comprehensive ad readiness check

### Example: Application-Level Callback

Set callback in Application class for app-wide consent handling:

```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        val config = AdSpaceSDKConfig(
            debug = BuildConfig.DEBUG,
            testDevices = listOf("33BE2250B4358CC8426CA1F9B3"),
            minInterval = 30L,
            appId = getString(R.string.admob_app_id)
        )

        AdSpaceSDK.initialize(this, config)

        // Set app-wide consent callback
        AdSpaceSDK.setConsentFlowCompletedCallback { canRequestAds ->
            if (canRequestAds) {
                // Notify analytics
                analytics.logEvent("consent_obtained")
                // Start ad preloading
                preloadCriticalAds()
            } else {
                analytics.logEvent("consent_denied")
            }
        }
    }

    private fun preloadCriticalAds() {
        // Preload high-priority ad spaces
        SpaceInterstitial.preload("ADMOB_Interstitial_Main")
    }
}
```

## Manual CMP Management

### Check Consent Status

```kotlin
import com.admob.adspace.AdSpaceSDK
import com.admob.adspace.cmp.ConsentStatus

val cmpManager = AdSpaceSDK.getCMPManager()

// Get current consent status
when (cmpManager.getConsentStatus()) {
    ConsentStatus.UNKNOWN -> {
        // Consent status unknown (before initialization)
    }
    ConsentStatus.REQUIRED -> {
        // Consent required from user
    }
    ConsentStatus.NOT_REQUIRED -> {
        // Consent not required (non-EEA region)
    }
    ConsentStatus.OBTAINED -> {
        // Consent obtained from user
    }
}

// Check if ads can be requested
if (cmpManager.canRequestAds()) {
    // Can show ads
}

// Check if ads can be shown (consent gathered + can request)
if (cmpManager.canShowAds()) {
    // Can show ads
}

// Check if privacy options required
if (cmpManager.isPrivacyOptionsRequired()) {
    // Show privacy options button in settings
}
```

### Request Consent Manually

```kotlin
import android.app.Activity
import com.admob.adspace.AdSpaceSDK

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Request consent manually
        val cmpManager = AdSpaceSDK.getCMPManager()

        cmpManager.requestConsent(
            activity = this,
            onConsentGathered = {
                // Consent flow completed (success or failure)
                // Can now initialize ads
                initializeAds()
            }
        )
    }

    private fun initializeAds() {
        if (cmpManager.canShowAds()) {
            // Load and show ads
        }
    }
}
```

**Important Notes**:
- `requestConsent()` shows loading dialog automatically
- Loading dialog dismisses when consent form loads or on error
- `onConsentGathered` called even if consent fails (to unblock app)
- Consent status persists across app sessions

### Show Privacy Options Form

Allow users to change consent settings:

```kotlin
import com.admob.adspace.AdSpaceSDK

class SettingsActivity : AppCompatActivity() {

    private fun showPrivacySettings() {
        val cmpManager = AdSpaceSDK.getCMPManager()

        // Check if privacy options required
        if (!cmpManager.isPrivacyOptionsRequired()) {
            // Privacy options not available
            return
        }

        // Show privacy options form
        cmpManager.showPrivacyOptionsForm(
            activity = this,
            onDismissed = {
                // Form dismissed
                // Check new consent status
                if (cmpManager.canShowAds()) {
                    // User still consents to ads
                } else {
                    // User revoked consent
                    clearAdsCache()
                }
            }
        )
    }
}
```

## Testing CMP

### Debug Mode Configuration

SDK automatically configures debug mode when `AdSpaceSDK.isDebug = true`:

```kotlin
// In Application.onCreate()
val config = AdSpaceSDKConfig(
    debug = true, // Enables CMP debug mode
    testDevices = listOf("YOUR_TEST_DEVICE_ID"),
    minInterval = 30L,
    appId = "ca-app-pub-XXXXXXXXXXXXXXXX~YYYYYYYYYY"
)

AdSpaceSDK.initialize(this, config)
```

When debug mode enabled, SDK automatically:
- Adds test device IDs to CMP debug settings
- Forces testing mode (`setForceTesting(true)`)
- Sets debug geography to EEA (`DEBUG_GEOGRAPHY_EEA`)

### Manual Debug Configuration

For advanced testing, configure manually:

```kotlin
import com.google.android.ump.ConsentDebugSettings
import com.google.android.ump.ConsentRequestParameters

// Force EEA geography for testing
val debugSettings = ConsentDebugSettings.Builder(context)
    .setDebugGeography(ConsentDebugSettings.DebugGeography.DEBUG_GEOGRAPHY_EEA)
    .addTestDeviceHashedId("33BE2250B4358CC8426CA1F9B3")
    .setForceTesting(true)
    .build()

val params = ConsentRequestParameters.Builder()
    .setConsentDebugSettings(debugSettings)
    .setTagForUnderAgeOfConsent(false)
    .build()
```

**Debug Geography Options**:
- `DEBUG_GEOGRAPHY_DISABLED` - Use actual device location
- `DEBUG_GEOGRAPHY_EEA` - Simulate EEA region (consent required)
- `DEBUG_GEOGRAPHY_NOT_EEA` - Simulate non-EEA region (consent not required)

### Get Test Device ID

To get your test device ID:

1. Run app with `debug = true`
2. Check logcat for message:
   ```
   Use new ConsentDebugSettings.Builder().addTestDeviceHashedId("33BE2250B4358CC8426CA1F9B3")
   ```
3. Copy the device ID and add to `testDevices` list

### Reset Consent (Testing Only)

Reset consent to test flow again:

```kotlin
import com.google.android.ump.UserMessagingPlatform

// Reset consent for testing
UserMessagingPlatform.getConsentInformation(context).reset()

// Then restart app to see consent form again
```

## CMP Flow Diagram

```
App Start
    ↓
AdSpaceSDK.initialize(context, config)
    ↓ (async)
ConfigManager.initialize() - loads local + remote config
    ↓ (async)
CMPManager.initialize() - prepares consent info
    ↓
Activity.onResume() (first time)
    ↓
Need CMP? (ads.global.cmp_auto && consent required)
    ├─ YES → CMPManager.requestConsent()
    │         ↓
    │    Show loading dialog
    │         ↓
    │    Request consent info update
    │         ↓
    │    Consent already obtained?
    │         ├─ YES → Dismiss dialog, initialize AdMob
    │         └─ NO → Load consent form
    │                  ↓
    │             Dismiss loading dialog
    │                  ↓
    │             Show consent form to user
    │                  ↓
    │             User accepts/rejects
    │                  ↓
    │             onConsentGathered() callback
    │                  ↓
    │             AdMobManager.initialize()
    │                  ↓
    │             Ads can be requested
    │
    └─ NO → AdMobManager.initialize() immediately
             ↓
        Ads can be requested
```

## CMPManager API Reference

### Methods

| Method | Parameters | Return | Description |
|--------|------------|--------|-------------|
| `initialize()` | context: Context | suspend Unit | Initialize CMP with application context |
| `requestConsent()` | activity: Activity, onConsentGathered: (() -> Unit)? | Unit | Request user consent (shows form if needed) |
| `canShowAds()` | - | Boolean | Check if ads can be shown (consent gathered + can request) |
| `canRequestAds()` | - | Boolean | Check if ads can be requested from AdMob |
| `isPrivacyOptionsRequired()` | - | Boolean | Check if privacy options entry point required |
| `showPrivacyOptionsForm()` | activity: Activity, onDismissed: () -> Unit | Unit | Show privacy options form |
| `getConsentStatus()` | - | ConsentStatus | Get current consent status |

### ConsentStatus Enum

```kotlin
enum class ConsentStatus {
    UNKNOWN,        // Consent status unknown (before initialization)
    REQUIRED,       // Consent required from user
    NOT_REQUIRED,   // Consent not required (non-EEA region)
    OBTAINED        // Consent obtained from user
}
```

## Loading Dialog

SDK shows a custom loading dialog while consent form loads:

### Features

- **Auto-show** - Appears when `requestConsent()` called
- **Auto-dismiss** - Dismisses when form loads or on error
- **Lifecycle-aware** - Dismisses on Activity destroy
- **Non-cancelable** - User cannot dismiss by tapping outside
- **Custom layout** - Uses `R.layout.dialog_consent_loading`

### Customize Loading Dialog

To customize the loading dialog, override `R.layout.dialog_consent_loading` in your app:

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:background="@drawable/dialog_background"
    android:gravity="center"
    android:orientation="vertical"
    android:padding="24dp">

    <ProgressBar
        android:layout_width="48dp"
        android:layout_height="48dp"
        android:indeterminate="true" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="16dp"
        android:text="Loading consent form..."
        android:textColor="@color/text_primary"
        android:textSize="16sp" />

</LinearLayout>
```

## Best Practices

### ✅ DO

1. **Use auto CMP** - Let SDK handle consent flow automatically
2. **Test in EEA** - Use debug geography to test consent flow
3. **Handle errors gracefully** - App should work without ads if consent fails
4. **Show privacy options** - Add privacy settings button if `isPrivacyOptionsRequired()`
5. **Respect user choice** - Don't repeatedly ask for consent
6. **Check before showing ads** - Always check `canShowAds()` before requesting ads
7. **Clear cache on consent change** - Clear ads cache if user revokes consent

### ❌ DON'T

1. **Don't block app** - App should work without ads if consent denied
2. **Don't spam consent** - Only show consent form when required
3. **Don't ignore consent** - Never show ads without consent in EEA
4. **Don't hardcode geography** - Use actual device location in production
5. **Don't skip testing** - Always test consent flow before release

## Common Patterns

### Pattern 1: Check Consent Before Showing Ads

```kotlin
private fun showInterstitialAd() {
    val cmpManager = AdSpaceSDK.getCMPManager()

    // Check if ads can be shown
    if (!cmpManager.canShowAds()) {
        Timber.w("Cannot show ads - consent not obtained")
        return
    }

    // Show ad
    SpaceInterstitial.load(
        space = "ADMOB_Interstitial_General",
        callback = interstitialCallback
    )
}
```

### Pattern 2: Show Privacy Options in Settings

```kotlin
class SettingsActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        val cmpManager = AdSpaceSDK.getCMPManager()

        // Show/hide privacy options button
        binding.privacyOptionsButton.visibility = if (cmpManager.isPrivacyOptionsRequired()) {
            View.VISIBLE
        } else {
            View.GONE
        }

        binding.privacyOptionsButton.setOnClickListener {
            showPrivacyOptions()
        }
    }

    private fun showPrivacyOptions() {
        val cmpManager = AdSpaceSDK.getCMPManager()

        cmpManager.showPrivacyOptionsForm(
            activity = this,
            onDismissed = {
                // Check if consent changed
                if (!cmpManager.canShowAds()) {
                    // User revoked consent - clear ads
                    clearAllAdsCache()
                }
            }
        )
    }

    private fun clearAllAdsCache() {
        SpaceBanner.clearAllCache()
        SpaceNative.clearAllCache()
        SpaceInterstitial.clearCache()
        SpaceRewarded.clearCache()
    }
}
```

### Pattern 3: Handle Consent in Application

```kotlin
class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        val config = AdSpaceSDKConfig(
            debug = BuildConfig.DEBUG,
            testDevices = listOf("33BE2250B4358CC8426CA1F9B3"),
            minInterval = 30L,
            appId = getString(R.string.admob_app_id)
        )

        AdSpaceSDK.initialize(this, config)

        // CMP will automatically show on first Activity resume
        // No need to manually request consent
    }
}
```

### Pattern 4: Manual Consent Request

```kotlin
class SplashActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        // Manually request consent
        val cmpManager = AdSpaceSDK.getCMPManager()

        cmpManager.requestConsent(
            activity = this,
            onConsentGathered = {
                // Consent flow completed
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

## Remote Config Control

Control CMP behavior remotely via Firebase Remote Config:

```json
{
  "ads.global.cmp_auto": false
}
```

This disables automatic CMP flow without app update. Useful for:
- Temporarily disabling CMP during issues
- A/B testing consent flows
- Regional rollouts

## Common Issues

### Issue 1: Consent form not showing

**Symptoms**: CMP form never appears, ads don't load

**Possible causes**:
- `cmp_auto` is `false` in config
- User not in region requiring consent
- Test device ID incorrect (for testing)
- Consent already obtained in previous session

**Solutions**:
```kotlin
// 1. Check cmp_auto setting
val configManager = AdSpaceSDK.getConfigManager()
val cmpAuto = configManager.getGlobalConfig().cmpAuto
Timber.d("cmp_auto = $cmpAuto")

// 2. Check consent status
val cmpManager = AdSpaceSDK.getCMPManager()
Timber.d("Consent status: ${cmpManager.getConsentStatus()}")
Timber.d("Can request ads: ${cmpManager.canRequestAds()}")

// 3. Reset consent for testing
UserMessagingPlatform.getConsentInformation(context).reset()

// 4. Force EEA geography for testing
// Set debug = true in AdSpaceSDKConfig
```

### Issue 2: Ads not showing after consent

**Symptoms**: Consent obtained but ads still don't load

**Possible causes**:
- AdMob not initialized after consent
- Ad space disabled in config
- Global ads disabled
- Min interval not elapsed

**Solutions**:
```kotlin
// 1. Check if ads can be shown
val cmpManager = AdSpaceSDK.getCMPManager()
if (!cmpManager.canShowAds()) {
    Timber.e("Cannot show ads - consent issue")
}

// 2. Check global enable
if (!AdSpaceSDK.isGlobalEnabled()) {
    Timber.e("Global ads disabled")
}

// 3. Check space enable
val configManager = AdSpaceSDK.getConfigManager()
if (!configManager.isSpaceEnabled("ADMOB_Banner_Home")) {
    Timber.e("Space disabled")
}

// 4. Check AdMob initialization
// Look for log: "AdMob SDK initialized"
```

### Issue 3: Form shows every time

**Symptoms**: Consent form appears on every app launch

**Possible causes**:
- Consent not persisting across sessions
- UMP SDK storage issue
- App storage permissions missing

**Solutions**:
```kotlin
// 1. Check consent status persists
val cmpManager = AdSpaceSDK.getCMPManager()
Timber.d("Consent status: ${cmpManager.getConsentStatus()}")

// 2. Verify UMP SDK configured correctly
// Check AndroidManifest.xml has correct permissions

// 3. Check app storage permissions
// UMP SDK needs storage to persist consent

// 4. Don't reset consent in production
// Remove UserMessagingPlatform.reset() calls
```

### Issue 4: Loading dialog stuck

**Symptoms**: Loading dialog never dismisses

**Possible causes**:
- Network timeout
- UMP SDK error
- Activity destroyed during load

**Solutions**:
```kotlin
// SDK automatically dismisses dialog on:
// - Consent form loaded
// - Error occurred
// - Activity destroyed

// Check logs for errors:
// "CMPManager: Failed to load consent form"
// "CMPManager: Consent info update failed"

// Ensure Activity implements LifecycleOwner
// Dialog auto-dismisses on Activity destroy
```

## Compliance Notes

### GDPR (EU/UK/EEA)

- **Required**: Yes, consent required before showing ads
- **Form type**: Consent form with accept/reject options
- **Persistence**: Consent persists across sessions
- **Revocation**: Users can revoke via privacy options

### CCPA (California)

- **Required**: No, but privacy options should be available
- **Form type**: Privacy options form (not consent)
- **Opt-out**: Users can opt-out of personalized ads

### Other Regions

- **Required**: Varies by region
- **UMP SDK**: Automatically determines if consent required
- **Fallback**: If consent not required, ads show immediately

## References

- [Google UMP SDK Documentation](https://developers.google.com/admob/android/privacy)
- [GDPR Compliance Guide](https://developers.google.com/admob/android/privacy/gdpr)
- [Consent Management Guide](https://support.google.com/admob/answer/10113207)
- AdSpaceSDK Source: `adspace/src/main/java/com/admob/adspace/cmp/`
