# App Resume Ads

App resume ads automatically show when users return to your app from background.

## Package Imports

```kotlin
import com.admob.adspace.AdSpaceSDK
import com.admob.adspace.AdSpaceSDK.ResumeMode
```

## Resume Modes

AdSpaceSDK supports three resume modes:

1. **NONE** - No resume ads
2. **OPEN_ADS** - Show open app ad on resume
3. **INTERSTITIAL** - Show interstitial ad on resume

Only one mode can be active at a time.

## Setup

### Enable Open App Resume Ads

```kotlin
import android.app.Application
import com.admob.adspace.AdSpaceSDK
import com.admob.adspace.AdSpaceSDK.ResumeMode

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Initialize SDK
        AdSpaceSDK.initialize(this, config)

        // Enable open app resume ads
        AdSpaceSDK.setResumeMode(
            mode = ResumeMode.OPEN_ADS,
            spaceName = "ADMOB_OpenApp_Resume"
        )
    }
}
```

### Enable Interstitial Resume Ads

```kotlin
AdSpaceSDK.setResumeMode(
    mode = ResumeMode.INTERSTITIAL,
    spaceName = "ADMOB_Interstitial_Resume"
)
```

### Disable Resume Ads

```kotlin
AdSpaceSDK.setResumeMode(ResumeMode.NONE)
```

## Exclude Activities

Exclude specific activities from showing resume ads:

```kotlin
import android.app.Application
import com.admob.adspace.AdSpaceSDK

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Initialize SDK
        AdSpaceSDK.initialize(this, config)

        // Enable resume ads
        AdSpaceSDK.setResumeMode(
            mode = ResumeMode.OPEN_ADS,
            spaceName = "ADMOB_OpenApp_Resume"
        )

        // Exclude splash and login screens
        AdSpaceSDK.setIgnoreAdResume(SplashActivity::class.java)
        AdSpaceSDK.setIgnoreAdResume(LoginActivity::class.java)
        AdSpaceSDK.setIgnoreAdResume(OnboardingActivity::class.java)
    }
}
```

## Configuration

### Open App Resume Config

In `assets/ads_config.json`:

```json
{
  "space": "ADMOB_OpenApp_Resume",
  "adsType": "open_app",
  "ids": [
    "ca-app-pub-3940256099942544/9257395921"
  ],
  "enable": true,
  "minInterval": 240000
}
```

### Interstitial Resume Config

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

## Best Practices

1. **Higher min interval** - 3-4 minutes recommended for resume ads
2. **Exclude key screens** - Don't show on splash, login, payment screens
3. **Choose appropriate mode** - Open app for cold starts, interstitial for warm resumes
4. **Test thoroughly** - Verify ads don't disrupt critical flows
5. **Monitor metrics** - Track user retention and session length

## Common Patterns

### Exclude Multiple Activities

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        AdSpaceSDK.initialize(this, config)

        // Enable resume ads
        AdSpaceSDK.setResumeMode(
            mode = ResumeMode.OPEN_ADS,
            spaceName = "ADMOB_OpenApp_Resume"
        )

        // Exclude list of activities
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

### Switch Resume Mode Dynamically

```kotlin
class SettingsActivity : AppCompatActivity() {

    private fun updateResumeAdSettings(enabled: Boolean) {
        if (enabled) {
            AdSpaceSDK.setResumeMode(
                mode = ResumeMode.OPEN_ADS,
                spaceName = "ADMOB_OpenApp_Resume"
            )
        } else {
            AdSpaceSDK.setResumeMode(ResumeMode.NONE)
        }
    }
}
```

## How It Works

1. SDK registers lifecycle observer on initialization
2. When app goes to background, SDK tracks the time
3. When app returns to foreground:
   - Checks if min interval elapsed
   - Checks if current activity is excluded
   - Checks if ad is available
   - Shows ad if all conditions met

## Common Issues

**Resume ads showing too frequently?**
- Increase `minInterval` to 240000 (4 minutes) or higher
- SDK enforces min interval automatically

**Resume ads showing on wrong screens?**
- Use `setIgnoreAdResume()` to exclude activities
- Exclude splash, login, payment, video player screens

**Resume ads not showing?**
- Check resume mode is set correctly
- Verify space is enabled in config
- Check min interval hasn't blocked the ad
- Ensure activity is not in excluded list
