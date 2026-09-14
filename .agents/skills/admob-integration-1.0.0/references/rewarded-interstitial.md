# Rewarded Interstitial Ads Integration

Rewarded interstitial ads are full-screen ads that give users rewards for watching.

## Package Imports

```kotlin
import com.admob.adspace.rewardedinterstitial.SpaceRewardedInterstitial
import com.admob.adspace.rewardedinterstitial.RewardedInterstitialCallback
import com.admob.adspace.rewardedinterstitial.RewardedInterstitialError
```

## Basic Implementation

```kotlin
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import com.admob.adspace.rewardedinterstitial.SpaceRewardedInterstitial
import com.admob.adspace.rewardedinterstitial.RewardedInterstitialCallback
import com.admob.adspace.rewardedinterstitial.RewardedInterstitialError

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Preload rewarded interstitial
        preloadRewardedInterstitial()

        binding.btnShowAd.setOnClickListener {
            showRewardedInterstitial()
        }
    }

    private fun preloadRewardedInterstitial() {
        SpaceRewardedInterstitial.preload(
            space = "ADMOB_RewardedInterstitial_General",
            forceRefresh = false,
            callback = object : RewardedInterstitialCallback {
                override fun onLoaded(space: String) {
                    // Ad loaded
                }

                override fun onFailed(space: String, error: RewardedInterstitialError) {
                    // Failed to load
                }

                override fun onShowed(space: String) {
                    // Ad displayed
                }

                override fun onDismissed(space: String) {
                    // Preload next ad
                    preloadRewardedInterstitial()
                }

                override fun onEarnedReward(space: String, type: String, amount: Int) {
                    // Give reward to user
                    giveUserReward(type, amount)
                }

                override fun onClicked(space: String) {
                    // Ad clicked
                }

                override fun onImpression(space: String) {
                    // Impression recorded
                }

                override fun onPaid(space: String, revenue: AdRevenue) {
                    // Revenue received
                }
            }
        )
    }

    private fun showRewardedInterstitial() {
        SpaceRewardedInterstitial.show(
            space = "ADMOB_RewardedInterstitial_General",
            activity = this,
            forceShow = false,
            loadIfNotAvailable = true,
            showLoading = true,
            callback = object : RewardedInterstitialCallback {
                override fun onLoaded(space: String) {}
                override fun onFailed(space: String, error: RewardedInterstitialError) {}
                override fun onShowed(space: String) {}
                override fun onDismissed(space: String) {}
                override fun onEarnedReward(space: String, type: String, amount: Int) {
                    giveUserReward(type, amount)
                }
                override fun onClicked(space: String) {}
                override fun onImpression(space: String) {}
                override fun onPaid(space: String, revenue: AdRevenue) {}
            }
        )
    }

    private fun giveUserReward(type: String, amount: Int) {
        // Implement reward logic
    }
}
```

## Configuration

In `assets/ads_config.json`:

```json
{
  "space": "ADMOB_RewardedInterstitial_General",
  "adsType": "reward_inter",
  "ids": [
    "ca-app-pub-3940256099942544/5354046379"
  ],
  "enable": true,
  "minInterval": 60000,
  "mute": false
}
```

## Difference from Rewarded Ads

**Rewarded Interstitial** vs **Rewarded**:
- Rewarded Interstitial: Full-screen, can be skipped after a few seconds
- Rewarded: Must watch entire video to get reward

Use rewarded interstitial when you want to give users the option to skip but still earn a reward.

## Best Practices

Same as Rewarded Ads - see [rewarded.md](rewarded.md) for detailed best practices.

---

## Jetpack Compose Integration

AdSpaceSDK supports Jetpack Compose for showing rewarded interstitial ads.

### Basic Implementation

```kotlin
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.admob.adspace.rewardedinterstitial.SpaceRewardedInterstitial
import com.admob.adspace.rewardedinterstitial.RewardedInterstitialCallback
import com.admob.adspace.rewardedinterstitial.RewardedInterstitialError

@Composable
fun RewardedInterstitialAdScreen(
    spaceName: String = "ADMOB_RewardedInterstitial_General",
    onRewardEarned: (type: String, amount: Int) -> Unit = { _, _ -> }
) {
    val context = LocalContext.current
    var adLoaded by remember { mutableStateOf(false) }
    var rewardAmount by remember { mutableIntStateOf(0) }
    var rewardType by remember { mutableStateOf("") }

    // Lifecycle observer for cleanup
    val lifecycleOwner = LocalLifecycleOwner.current
    androidx.compose.runtime.DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_DESTROY) {
                SpaceRewardedInterstitial.clearCache(spaceName)
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }

    // Load ad on first composition
    LaunchedEffect(Unit) {
        SpaceRewardedInterstitial.load(
            space = spaceName,
            callback = object : RewardedInterstitialCallback {
                override fun onLoaded(space: String) {
                    adLoaded = true
                }

                override fun onFailed(space: String, error: RewardedInterstitialError) {
                    adLoaded = false
                }
            }
        )
    }

    // Show ad button
    Button(
        onClick = {
            if (adLoaded) {
                SpaceRewardedInterstitial.show(
                    activity = context as Activity,
                    space = spaceName,
                    callback = object : RewardedInterstitialCallback {
                        override fun onLoaded(space: String) {}

                        override fun onShowed(space: String) {
                            adLoaded = false
                        }

                        override fun onDismissed(space: String) {
                            // Preload next ad
                            SpaceRewardedInterstitial.preload(spaceName, null)
                        }

                        override fun onEarnedReward(space: String, type: String, amount: Int) {
                            rewardType = type
                            rewardAmount = amount
                            onRewardEarned(type, amount)
                        }

                        override fun onFailed(space: String, error: RewardedInterstitialError) {
                            // Handle failure
                        }

                        override fun onClicked(space: String) {}

                        override fun onImpression(space: String) {}

                        override fun onPaid(space: String, revenue: AdRevenue) {}
                    }
                )
            }
        },
        enabled = adLoaded
    ) {
        Text("Watch Ad for Reward")
    }

    // Display reward info
    if (rewardAmount > 0) {
        Text("You earned: $rewardAmount $rewardType")
    }
}
```

### Advanced Compose Pattern with Reward State

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.admob.adspace.rewardedinterstitial.SpaceRewardedInterstitial
import com.admob.adspace.rewardedinterstitial.RewardedInterstitialCallback
import com.admob.adspace.rewardedinterstitial.RewardedInterstitialError
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class RewardState(
    val type: String = "",
    val amount: Int = 0,
    val isEarned: Boolean = false
)

class RewardedInterstitialAdViewModel(
    private val spaceName: String = "ADMOB_RewardedInterstitial_General"
) : ViewModel() {

    private val _adState = MutableStateFlow<AdState>(AdState.Idle)
    val adState: StateFlow<AdState> = _adState.asStateFlow()

    private val _rewardState = MutableStateFlow(RewardState())
    val rewardState: StateFlow<RewardState> = _rewardState.asStateFlow()

    sealed class AdState {
        object Idle : AdState()
        object Loading : AdState()
        object Loaded : AdState()
        object Showing : AdState()
        data class Error(val message: String) : AdState()
    }

    init {
        preloadAd()
    }

    fun preloadAd() {
        viewModelScope.launch {
            _adState.value = AdState.Loading
            SpaceRewardedInterstitial.load(
                space = spaceName,
                callback = object : RewardedInterstitialCallback {
                    override fun onLoaded(space: String) {
                        _adState.value = AdState.Loaded
                    }

                    override fun onFailed(space: String, error: RewardedInterstitialError) {
                        _adState.value = AdState.Error(error.message)
                    }
                }
            )
        }
    }

    fun showAd(activity: Activity, onComplete: () -> Unit) {
        _adState.value = AdState.Showing
        SpaceRewardedInterstitial.show(
            space = spaceName,
            activity = activity,
            callback = object : RewardedInterstitialCallback {
                override fun onShowed(space: String) {
                    _adState.value = AdState.Showing
                }

                override fun onDismissed(space: String) {
                    _adState.value = AdState.Idle
                    onComplete()
                    preloadAd()
                }

                override fun onEarnedReward(space: String, type: String, amount: Int) {
                    _rewardState.value = RewardState(
                        type = type,
                        amount = amount,
                        isEarned = true
                    )
                }

                override fun onFailed(space: String, error: RewardedInterstitialError) {
                    _adState.value = AdState.Error(error.message)
                    onComplete()
                    preloadAd()
                }
            }
        )
    }

    fun resetReward() {
        _rewardState.value = RewardState()
    }
}

@Composable
fun RewardedInterstitialAdScreenWithViewModel(
    viewModel: RewardedInterstitialAdViewModel = viewModel(),
    onRewardEarned: (type: String, amount: Int) -> Unit = { _, _ -> }
) {
    val context = LocalContext.current
    val adState by viewModel.adState.collectAsState()
    val rewardState by viewModel.rewardState.collectAsState()

    Column(
        modifier = Modifier.padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Button(
            onClick = {
                viewModel.showAd(context as Activity) {
                    // Handle ad completion
                }
            },
            enabled = adState is AdState.Loaded
        ) {
            when (adState) {
                is AdState.Loading -> Text("Loading Ad...")
                is AdState.Loaded -> Text("Watch Ad for Reward")
                is AdState.Showing -> Text("Showing Ad...")
                else -> Text("Load Ad")
            }
        }

        // Show reward notification
        if (rewardState.isEarned) {
            Spacer(modifier = Modifier.height(16.dp))
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "🎉 Reward Earned!",
                        style = MaterialTheme.typography.titleLarge
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "${rewardState.amount} ${rewardState.type}",
                        style = MaterialTheme.typography.bodyLarge
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Button(onClick = { viewModel.resetReward() }) {
                        Text("Claim")
                    }
                }
            }
            // Notify parent component
            LaunchedEffect(rewardState.isEarned) {
                if (rewardState.isEarned) {
                    onRewardEarned(rewardState.type, rewardState.amount)
                }
            }
        }
    }
}
```

### Best Practices for Compose

1. **Reward state management** - Track reward earned status clearly
2. **User feedback** - Show visual confirmation when reward is earned
3. **Reactive UI** - Update UI based on ad state changes
4. **Cleanup on destroy** - Clear ad cache to prevent memory leaks
5. **Automatic preloading** - Preload next ad after dismiss
6. **Error handling** - Handle ad failures gracefully
7. **ViewModel integration** - Use ViewModel for complex reward state
8. **Lifecycle awareness** - Respect Compose lifecycle for cleanup
9. **State persistence** - Consider saving reward state if needed
10. **Accessibility** - Provide clear feedback for screen readers
