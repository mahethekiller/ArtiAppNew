# Rewarded Ads Integration

Rewarded ads give users rewards (coins, lives, etc.) for watching video ads.

## Package Imports

```kotlin
import com.admob.adspace.rewarded.SpaceRewarded
import com.admob.adspace.rewarded.RewardedCallback
import com.admob.adspace.rewarded.RewardedError
```

## Basic Implementation

```kotlin
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import com.admob.adspace.rewarded.SpaceRewarded
import com.admob.adspace.rewarded.RewardedCallback
import com.admob.adspace.rewarded.RewardedError

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Preload rewarded ad
        preloadRewardedAd()

        // Show on button click
        binding.btnWatchAd.setOnClickListener {
            showRewardedAd()
        }
    }

    private fun preloadRewardedAd() {
        SpaceRewarded.preload(
            space = "ADMOB_Rewarded_Video",
            forceRefresh = false,
            callback = object : RewardedCallback {
                override fun onLoaded(space: String) {
                    // Ad loaded and ready
                    binding.btnWatchAd.isEnabled = true
                }

                override fun onFailed(space: String, error: RewardedError) {
                    // Failed to load
                    binding.btnWatchAd.isEnabled = false
                }

                override fun onShowed(space: String) {
                    // Ad displayed
                }

                override fun onDismissed(space: String) {
                    // Ad dismissed, preload next
                    preloadRewardedAd()
                }

                override fun onEarnedReward(space: String, type: String, amount: Int) {
                    // User earned reward!
                    giveUserReward(type, amount)
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

    private fun showRewardedAd() {
        SpaceRewarded.show(
            space = "ADMOB_Rewarded_Video",
            activity = this,
            forceShow = false,
            loadIfNotAvailable = true,
            showLoading = true,
            callback = object : RewardedCallback {
                override fun onLoaded(space: String) {}
                override fun onFailed(space: String, error: RewardedError) {
                    // Show error message
                    showToast("Ad not available")
                }
                override fun onShowed(space: String) {}
                override fun onDismissed(space: String) {}
                override fun onEarnedReward(space: String, type: String, amount: Int) {
                    // Give reward to user
                    giveUserReward(type, amount)
                }
                override fun onClicked(space: String) {}
                override fun onImpression(space: String) {}
                override fun onPaid(space: String, revenue: AdRevenue) {}
            }
        )
    }

    private fun giveUserReward(type: String, amount: Int) {
        // Implement your reward logic
        when (type) {
            "coins" -> addCoins(amount)
            "lives" -> addLives(amount)
            else -> addCoins(amount)
        }
    }
}
```

## Show Methods

### Show with Auto-Load

```kotlin
SpaceRewarded.show(
    space = "ADMOB_Rewarded_Video",
    activity = this,
    forceShow = false,
    loadIfNotAvailable = true,
    showLoading = true,
    callback = callback
)
```

### Show Only if Loaded

```kotlin
if (SpaceRewarded.isLoaded("ADMOB_Rewarded_Video")) {
    SpaceRewarded.show(
        space = "ADMOB_Rewarded_Video",
        activity = this,
        forceShow = false,
        loadIfNotAvailable = false,
        showLoading = false,
        callback = callback
    )
}
```

## Advanced Features

### Check if Ad is Ready

```kotlin
if (SpaceRewarded.isLoaded("ADMOB_Rewarded_Video")) {
    // Enable watch ad button
    binding.btnWatchAd.isEnabled = true
} else {
    // Disable button and preload
    binding.btnWatchAd.isEnabled = false
    preloadRewardedAd()
}
```

### Clear Cache

```kotlin
SpaceRewarded.clearCache("ADMOB_Rewarded_Video")
```

## Configuration

In `assets/ads_config.json`:

```json
{
  "space": "ADMOB_Rewarded_Video",
  "adsType": "reward",
  "ids": [
    "ca-app-pub-3940256099942544/5224354917",
    "ca-app-pub-3940256099942544/1712485313"
  ],
  "enable": true,
  "minInterval": 60000,
  "mute": false
}
```

**Config options**:
- `mute`: Start video muted (default: false)

## Best Practices

1. **Preload early** - Load before user needs it
2. **Enable/disable button** - Based on ad availability
3. **Always give reward** - Only in `onEarnedReward()` callback
4. **Reload after show** - Preload next ad immediately
5. **Show loading** - Better UX while loading
6. **Validate reward** - Server-side validation recommended
7. **Respect min interval** - Don't spam users

## Common Patterns

### Reward Button with Loading State

```kotlin
class RewardButton(context: Context) : FrameLayout(context) {

    private val button: Button
    private val progressBar: ProgressBar

    init {
        inflate(context, R.layout.reward_button, this)
        button = findViewById(R.id.button)
        progressBar = findViewById(R.id.progress)

        button.setOnClickListener {
            showRewardedAd()
        }

        updateState()
    }

    private fun updateState() {
        if (SpaceRewarded.isLoaded("ADMOB_Rewarded_Video")) {
            button.isEnabled = true
            button.text = "Watch Ad for 100 Coins"
            progressBar.visibility = View.GONE
        } else {
            button.isEnabled = false
            button.text = "Loading..."
            progressBar.visibility = View.VISIBLE
            preloadAd()
        }
    }

    private fun preloadAd() {
        SpaceRewarded.preload(
            space = "ADMOB_Rewarded_Video",
            callback = object : RewardedCallback {
                override fun onLoaded(space: String) {
                    updateState()
                }
                override fun onFailed(space: String, error: RewardedError) {
                    button.text = "Ad Not Available"
                    progressBar.visibility = View.GONE
                }
                // ... other callbacks
            }
        )
    }
}
```

### Server-Side Reward Validation

```kotlin
private fun showRewardedAd() {
    // Generate unique token
    val rewardToken = UUID.randomUUID().toString()

    SpaceRewarded.show(
        space = "ADMOB_Rewarded_Video",
        activity = this,
        callback = object : RewardedCallback {
            override fun onEarnedReward(space: String, type: String, amount: Int) {
                // Validate with server
                validateRewardWithServer(rewardToken, type, amount)
            }
            // ... other callbacks
        }
    )
}

private fun validateRewardWithServer(token: String, type: String, amount: Int) {
    // Call your backend API
    api.validateReward(token, type, amount)
        .enqueue(object : Callback<RewardResponse> {
            override fun onResponse(response: RewardResponse) {
                if (response.isValid) {
                    giveUserReward(type, amount)
                }
            }
            override fun onFailure(error: Throwable) {
                // Handle error
            }
        })
}
```

## Jetpack Compose Integration

```kotlin
@Composable
fun RewardButton(
    space: String,
    rewardAmount: Int,
    onRewardEarned: (String, Int) -> Unit
) {
    var isLoaded by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }
    val context = LocalContext.current

    LaunchedEffect(Unit) {
        SpaceRewarded.preload(
            space = space,
            callback = object : RewardedCallback {
                override fun onLoaded(space: String) {
                    isLoaded = true
                    isLoading = false
                }
                override fun onFailed(space: String, error: RewardedError) {
                    isLoading = false
                }
                // ... other callbacks
            }
        )
    }

    Button(
        onClick = {
            SpaceRewarded.show(
                space = space,
                activity = context as Activity,
                callback = object : RewardedCallback {
                    override fun onEarnedReward(space: String, type: String, amount: Int) {
                        onRewardEarned(type, amount)
                    }
                    // ... other callbacks
                }
            )
        },
        enabled = isLoaded && !isLoading
    ) {
        if (isLoading) {
            CircularProgressIndicator(modifier = Modifier.size(16.dp))
        } else {
            Text("Watch Ad for $rewardAmount Coins")
        }
    }
}
```

## Common Issues

**Reward not given?**
- Only give reward in `onEarnedReward()` callback
- Don't give reward in `onDismissed()` - user may not have watched full ad
- Implement server-side validation for security

**Ad not loading?**
- Check space is enabled in config
- Verify test device ID (for testing)
- Check min interval hasn't blocked the ad

**Button always disabled?**
- Check if preload is being called
- Verify callback is updating UI state
- Check for errors in `onFailed()` callback
