# Firebase Remote Config Integration

Firebase Remote Config allows you to remotely control ad behavior without app updates.

## Package Imports

```kotlin
import com.google.firebase.Firebase
import com.google.firebase.remoteconfig.FirebaseRemoteConfig
import com.google.firebase.remoteconfig.remoteConfig
import com.google.firebase.remoteconfig.remoteConfigSettings
```

## Setup

### 1. Add Firebase to Project

Add Firebase dependencies to app module's `build.gradle.kts`:

```kotlin
dependencies {
    implementation("io.github.maichanchinh:adspace-admob:2.0.0")
}
```

Add `google-services.json` to your app module.

### 2. Initialize SDK with Remote Config

```kotlin
import android.app.Application
import com.admob.adspace.AdSpaceSDK
import com.admob.adspace.AdSpaceSDKConfig
import com.google.firebase.Firebase
import com.google.firebase.remoteconfig.remoteConfig
import com.google.firebase.remoteconfig.remoteConfigSettings

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Configure Firebase Remote Config
        val remoteConfig = Firebase.remoteConfig
        val configSettings = remoteConfigSettings {
            minimumFetchIntervalInSeconds = 3600 // 1 hour
        }
        remoteConfig.setConfigSettingsAsync(configSettings)

        // Initialize AdSpaceSDK with Remote Config
        val config = AdSpaceSDKConfig(
            debug = BuildConfig.DEBUG,
            testDevices = emptyList(),
            minInterval = 30L,
            appId = "ca-app-pub-XXXXXXXXXXXXXXXX~YYYYYYYYYY",
            remoteConfig = remoteConfig // Pass Firebase Remote Config
        )

        AdSpaceSDK.initialize(this, config)
    }
}
```

## Remote Config Parameters

### Global Parameters

Set these in Firebase Console:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `ads.global.enable` | Boolean | Global ad kill switch | `true` |
| `ads.global.cmp_auto` | Boolean | Auto-display CMP consent | `true` |
| `ads.global.min_interval` | Number | Global min interval (ms) | `30000` |

### Space-Specific Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `ads.{space}.enable` | Boolean | Enable/disable space | `true` |
| `ads.{space}.min_interval` | Number | Space min interval (ms) | `60000` |
| `ads.{space}.admob_id` | String | Waterfall ad unit IDs | `id1\|id2\|id3` |

**IMPORTANT**: Remote config CANNOT change `adsType`. This is immutable and defined in local config only.

## Remote Config Examples

### Example 1: Global Kill Switch

In Firebase Console, set:
```
ads.global.enable = false
```

This disables ALL ads across the app without requiring an app update.

### Example 2: Disable Specific Space

```
ads.ADMOB_Banner_Home.enable = false
```

This disables only the home banner while keeping other ads active.

### Example 3: Update Ad Unit IDs

```
ads.ADMOB_Interstitial_General.admob_id = "ca-app-pub-XXX/111|ca-app-pub-XXX/222|ca-app-pub-XXX/333"
```

This updates the waterfall ad unit IDs remotely. Use pipe `|` to separate multiple IDs.

### Example 4: Increase Min Interval

```
ads.ADMOB_Interstitial_General.min_interval = 120000
```

This increases the minimum interval to 2 minutes for interstitial ads.

## Config Merge Logic

AdSpaceSDK merges local and remote configs with these rules:

1. **Local config is base** - Always loaded first from `assets/ads_config.json`
2. **Remote overrides allowed fields** - Only specific fields can be overridden
3. **adsType is immutable** - Cannot be changed remotely
4. **Waterfall IDs are replaced** - Remote IDs completely replace local IDs

### Merge Priority

```
Remote Config > Local Config > SDK Defaults
```

## Best Practices

1. **Do not override adsType from remote config** - `adsType` is immutable and must be defined in local config only. Attempting to change it remotely will have no effect and may cause unexpected behavior. Always set `adsType` at build time in `assets/ads_config.json`.

2. **Test remote config changes before production** - Always validate config changes in a staging or debug environment first. Use `minimumFetchIntervalInSeconds = 0` in debug builds and verify ad behavior is correct before rolling out to production users.

3. **Use Firebase rollouts for gradual rollout** - Never push config changes to 100% of users at once. Use Firebase Remote Config's percentage rollout or A/B testing feature to gradually expose changes and monitor metrics before full deployment.

4. **Set reasonable min_interval to avoid ad spam** - Do not set `min_interval` too low. A value below 15000ms (15 seconds) for interstitials risks negative user experience and potential policy violations. Recommended minimums: interstitial >= 30000ms, rewarded >= 15000ms.

5. **Monitor remote config fetch errors** - Track fetch failures in your analytics or crash reporting tool. If remote config cannot be fetched, the SDK falls back to local config, so always ensure local config is complete and valid as a fallback.

6. **Always maintain a complete local fallback config** - Remote config is an optional override layer. The local `assets/ads_config.json` must always be a fully functional standalone config. Never depend solely on remote config for critical ad settings such as `admob_id` or `enable` flags.

7. **Set reasonable fetch interval** - 1 hour (3600s) recommended for production. Use shorter intervals in debug builds only.

8. **Use global kill switch for emergencies** - The `ads.global.enable = false` parameter disables all ads instantly without an app update, making it the fastest response mechanism for ad-related issues in production.

## Testing Remote Config

### Debug Mode

For testing, use shorter fetch interval:

```kotlin
val configSettings = remoteConfigSettings {
    minimumFetchIntervalInSeconds = if (BuildConfig.DEBUG) 0 else 3600
}
```

### Force Fetch

```kotlin
remoteConfig.fetchAndActivate().addOnCompleteListener { task ->
    if (task.isSuccessful) {
        // Config fetched and activated
    }
}
```

## Common Patterns

### A/B Testing Ad Frequency

Use Firebase Remote Config with A/B testing:

1. Create experiment in Firebase Console
2. Set different `min_interval` values for variants
3. Monitor user retention and revenue metrics

### Emergency Ad Disable

```kotlin
// In Firebase Console, set:
ads.global.enable = false

// All ads will be disabled within fetch interval
// No app update required
```

### Seasonal Ad Adjustments

```kotlin
// Black Friday: Increase ad frequency
ads.global.min_interval = 15000

// Post-holiday: Decrease frequency
ads.global.min_interval = 60000
```

## Common Issues

**Remote config not applying?**
- Check fetch interval hasn't blocked update
- Verify parameter names match exactly
- Check Firebase Console for parameter values
- Call `fetchAndActivate()` to force update

**Ads still showing after disabling?**
- Wait for fetch interval to elapse
- Check local config isn't overriding
- Verify `ads.global.enable` is set correctly

**Wrong ad unit IDs?**
- Use pipe `|` separator, not comma
- Verify IDs are correct in Firebase Console
- Check merge logic is working correctly
