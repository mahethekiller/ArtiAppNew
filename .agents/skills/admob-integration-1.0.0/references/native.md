# Native Ads Integration

Native ads match the look and feel of your app's content.

## Package Imports

```kotlin
import com.admob.adspace.native.SpaceNative
import com.admob.adspace.native.NativeCallback
import com.admob.adspace.native.NativeError
import com.google.android.libraries.ads.mobile.sdk.nativead.NativeAd
import com.google.android.libraries.ads.mobile.sdk.nativead.NativeAdView
```

## Basic Implementation

### Layout XML

```xml
<FrameLayout
    android:id="@+id/nativeContainer"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:minHeight="200dp"/>
```

### Kotlin Code

```kotlin
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import com.admob.adspace.native.SpaceNative
import com.admob.adspace.native.NativeCallback
import com.admob.adspace.native.NativeError
import com.google.android.libraries.ads.mobile.sdk.nativead.NativeAd
import com.google.android.libraries.ads.mobile.sdk.nativead.NativeAdView

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Show medium native ad
        SpaceNative.showMedium(
            space = "ADMOB_Native_List",
            viewGroup = binding.nativeContainer,
            layoutRes = R.layout.layout_native_medium,
            callback = object : NativeCallback {
                override fun onLoaded(nativeAdView: NativeAdView, nativeAd: NativeAd, space: String) {
                    // Ad loaded successfully
                }

                override fun onFailed(space: String, error: NativeError) {
                    // Hide container on failure
                    binding.nativeContainer.visibility = View.GONE
                }

                override fun onImpression(space: String) {
                    // Impression recorded
                }

                override fun onClicked(space: String) {
                    // Ad clicked
                }

                override fun onPaid(space: String, revenue: NativeRevenue) {
                    // Revenue: revenue.valueMicros
                }
            }
        )
    }

    override fun onDestroy() {
        super.onDestroy()
        SpaceNative.clearCache("ADMOB_Native_List")
    }
}
```

## Native Ad Sizes

### 1. Small Native Ad

Compact layout for lists:

```kotlin
SpaceNative.showSmall(
    space = "ADMOB_Native_List",
    viewGroup = binding.nativeContainer,
    layoutRes = R.layout.layout_native_small,
    callback = callback
)
```

### 2. Medium Native Ad

Standard layout:

```kotlin
SpaceNative.showMedium(
    space = "ADMOB_Native_List",
    viewGroup = binding.nativeContainer,
    layoutRes = R.layout.layout_native_medium,
    callback = callback
)
```

### 3. Large Native Ad

Detailed layout with more content:

```kotlin
SpaceNative.showLarge(
    space = "ADMOB_Native_List",
    viewGroup = binding.nativeContainer,
    layoutRes = R.layout.layout_native_large,
    callback = callback
)
```

### 4. Fullscreen Native Ad

Full-screen layout:

```kotlin
SpaceNative.showFullscreen(
    space = "ADMOB_Native_List",
    viewGroup = binding.nativeContainer,
    layoutRes = R.layout.layout_native_fullscreen,
    callback = callback
)
```

## Custom Native Ad Layout

Create custom layout in `res/layout/layout_native_custom.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<com.google.android.libraries.ads.mobile.sdk.nativead.NativeAdView
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">

        <!-- Icon -->
        <ImageView
            android:id="@+id/ad_app_icon"
            android:layout_width="40dp"
            android:layout_height="40dp"/>

        <!-- Headline -->
        <TextView
            android:id="@+id/ad_headline"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="16sp"
            android:textStyle="bold"/>

        <!-- Body -->
        <TextView
            android:id="@+id/ad_body"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:textSize="14sp"/>

        <!-- Media View -->
        <com.google.android.libraries.ads.mobile.sdk.nativead.MediaView
            android:id="@+id/ad_media"
            android:layout_width="match_parent"
            android:layout_height="200dp"/>

        <!-- Call to Action -->
        <Button
            android:id="@+id/ad_call_to_action"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"/>

    </LinearLayout>
</com.google.android.libraries.ads.mobile.sdk.nativead.NativeAdView>
```

Use custom layout:

```kotlin
SpaceNative.show(
    space = "ADMOB_Native_List",
    viewGroup = binding.nativeContainer,
    layoutRes = R.layout.layout_native_custom,
    callback = callback
)
```

## Jetpack Compose Integration

Native ads work with Compose using AndroidView wrapper. Below are comprehensive patterns for different use cases including LazyColumn integration and preload patterns.

### Basic Native Ad Composable

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
import com.admob.adspace.native.SpaceNative
import com.admob.adspace.native.NativeCallback
import com.admob.adspace.native.NativeError
import com.google.android.libraries.ads.mobile.sdk.nativead.NativeAd
import com.google.android.libraries.ads.mobile.sdk.nativead.NativeAdView
import timber.log.Timber

@Composable
fun NativeAdView(
    spaceName: String = "ADMOB_Native_List",
    layoutRes: Int = R.layout.layout_native_medium,
    modifier: Modifier = Modifier,
    onAdClick: () -> Unit = {},
    onAdLoaded: (() -> Unit)? = null,
    onAdFailed: ((String) -> Unit)? = null
) {
    val context = LocalContext.current
    var nativeAd by remember { mutableStateOf<NativeAd?>(null) }
    var nativeAdView by remember { mutableStateOf<NativeAdView?>(null) }
    var isLoaded by remember { mutableStateOf(false) }

    LaunchedEffect(spaceName) {
        Timber.d("Loading native ad: $spaceName")

        SpaceNative.showMedium(
            space = spaceName,
            viewGroup = android.widget.FrameLayout(context),
            layoutRes = layoutRes,
            callback = object : NativeCallback {
                override fun onLoaded(adView: NativeAdView, ad: NativeAd, space: String) {
                    Timber.d("Native ad loaded: $space")
                    nativeAd = ad
                    nativeAdView = adView
                    isLoaded = true
                    onAdLoaded?.invoke()
                }

                override fun onFailed(space: String, error: NativeError) {
                    Timber.e("Native ad failed: $space - ${error.message}")
                    isLoaded = false
                    onAdFailed?.invoke(error.message)
                }

                override fun onImpression(space: String) {
                    if (BuildConfig.DEBUG) {
                        Timber.d("Native impression: $space")
                    }
                }

                override fun onClicked(space: String) {
                    Timber.d("Native clicked: $space")
                    onAdClick()
                }

                override fun onPaid(space: String, revenue: NativeRevenue) {
                    Timber.i("Native revenue: $space - ${revenue.valueMicros}")
                }
            }
        )
    }

    // Cleanup on dispose
    DisposableEffect(Unit) {
        onDispose {
            Timber.d("Destroying native ad: $spaceName")
            nativeAd?.destroy()
            SpaceNative.clearCache(spaceName)
            nativeAd = null
            nativeAdView = null
        }
    }

    // Show ad when loaded
    nativeAdView?.let { adView ->
        if (isLoaded) {
            AndroidView(
                factory = { adView },
                modifier = modifier,
                update = { view ->
                    // Update view if needed when state changes
                }
            )
        }
    }
}

// Usage
@Composable
fun ArticleScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "Article Content",
            style = MaterialTheme.typography.bodyLarge
        )

        Spacer(modifier = Modifier.height(16.dp))

        NativeAdView(
            spaceName = "ADMOB_Native_Article",
            layoutRes = R.layout.layout_native_medium,
            modifier = Modifier.fillMaxWidth()
        )
    }
}
```

### Native Ad with State Management

```kotlin
sealed class NativeAdState {
    object Idle : NativeAdState()
    object Loading : NativeAdState()
    data class Loaded(val adView: NativeAdView, val ad: NativeAd) : NativeAdState()
    data class Failed(val message: String) : NativeAdState()
}

@Composable
fun StatefulNativeAd(
    spaceName: String,
    layoutRes: Int,
    modifier: Modifier = Modifier,
    placeholderHeight: Int = 200
) {
    var adState by remember { mutableStateOf<NativeAdState>(NativeAdState.Idle) }
    val context = LocalContext.current

    LaunchedEffect(spaceName) {
        adState = NativeAdState.Loading
        Timber.d("Loading stateful native ad: $spaceName")

        SpaceNative.showMedium(
            space = spaceName,
            viewGroup = android.widget.FrameLayout(context),
            layoutRes = layoutRes,
            callback = object : NativeCallback {
                override fun onLoaded(adView: NativeAdView, ad: NativeAd, space: String) {
                    Timber.d("Stateful native loaded: $space")
                    adState = NativeAdState.Loaded(adView, ad)
                }

                override fun onFailed(space: String, error: NativeError) {
                    Timber.e("Stateful native failed: $space - ${error.message}")
                    adState = NativeAdState.Failed(error.message)
                }

                override fun onImpression(space: String) {}
                override fun onClicked(space: String) {}
                override fun onPaid(space: String, revenue: NativeRevenue) {}
            }
        )
    }

    DisposableEffect(Unit) {
        onDispose {
            Timber.d("Cleaning up stateful native ad: $spaceName")
            val currentState = adState
            if (currentState is NativeAdState.Loaded) {
                currentState.ad.destroy()
            }
            SpaceNative.clearCache(spaceName)
            adState = NativeAdState.Idle
        }
    }

    when (val state = adState) {
        is NativeAdState.Loading -> {
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

        is NativeAdState.Loaded -> {
            AndroidView(
                factory = { state.adView },
                modifier = modifier.fillMaxWidth()
            )
        }

        is NativeAdState.Failed -> {
            if (BuildConfig.DEBUG) {
                Box(
                    modifier = modifier
                        .fillMaxWidth()
                        .height(50.dp)
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

        NativeAdState.Idle -> {
            // Initial state
        }
    }
}
```

### Native Ads in LazyColumn

```kotlin
// Preload helper for list performance
object NativeAdPreloader {
    private val preloadedAds = mutableMapOf<String, NativeAd>()

    fun preload(context: Context, spaceName: String, count: Int = 3) {
        repeat(count) { index ->
            Timber.d("Preloading native ad $index for $spaceName")
            SpaceNative.preload(
                space = spaceName,
                layoutRes = R.layout.layout_native_medium,
                callback = object : PreloadCallback {
                    override fun onPreloadSuccess() {
                        Timber.d("Native ad preloaded: $spaceName[$index]")
                    }

                    override fun onPreloadFailed(error: NativeError) {
                        Timber.e("Preload failed: $spaceName[$index] - ${error.message}")
                    }
                }
            )
        }
    }
}

@Composable
fun NativeAdListItem(
    spaceName: String,
    layoutRes: Int = R.layout.layout_native_medium,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var container by remember { mutableStateOf<android.widget.FrameLayout?>(null) }
    var isAdReady by remember { mutableStateOf(false) }

    LaunchedEffect(spaceName) {
        container = android.widget.FrameLayout(context)
        SpaceNative.showMedium(
            space = spaceName,
            viewGroup = container!!,
            layoutRes = layoutRes,
            callback = object : NativeCallback {
                override fun onLoaded(adView: NativeAdView, ad: NativeAd, space: String) {
                    Timber.d("List native ad loaded: $space")
                    isAdReady = true
                }

                override fun onFailed(space: String, error: NativeError) {
                    Timber.e("List native ad failed: $space - ${error.message}")
                    isAdReady = false
                }

                override fun onImpression(space: String) {}
                override fun onClicked(space: String) {}
                override fun onPaid(space: String, revenue: NativeRevenue) {}
            }
        )
    }

    DisposableEffect(Unit) {
        onDispose {
            Timber.d("Disposing list native ad item: $spaceName")
            SpaceNative.clearCache(spaceName)
        }
    }

    if (isAdReady) {
        container?.let { frameLayout ->
            AndroidView(
                factory = { frameLayout },
                modifier = modifier.fillMaxWidth()
            )
        }
    }
}

@Composable
fun ContentListWithNativeAds(
    items: List<ContentItem>,
    adSpaceName: String = "ADMOB_Native_List"
) {
    val AD_FREQUENCY = 5 // Show ad every 5 items

    // Preload ads when entering composition
    LaunchedEffect(Unit) {
        Timber.d("Preloading native ads for list")
        SpaceNative.preload(
            space = adSpaceName,
            layoutRes = R.layout.layout_native_medium,
            callback = object : PreloadCallback {
                override fun onPreloadSuccess() {
                    Timber.d("Native ads preloaded for list")
                }

                override fun onPreloadFailed(error: NativeError) {
                    Timber.e("Failed to preload native ads: ${error.message}")
                }
            }
        )
    }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        itemsIndexed(items) { index, item ->
            // Show native ad at regular intervals
            if (index > 0 && index % AD_FREQUENCY == 0) {
                NativeAdListItem(
                    spaceName = adSpaceName,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp)
                )
            }

            // Regular content item
            ContentListItem(
                item = item,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}

// Usage
@Composable
fun ContentFeedScreen(viewModel: ContentViewModel) {
    val items by viewModel.contentItems.collectAsStateWithLifecycle()

    ContentListWithNativeAds(
        items = items,
        adSpaceName = "ADMOB_Native_Feed"
    )
}
```

### Native Ad with RecyclerView (Compose Interop)

```kotlin
@Composable
fun ComposeWithRecyclerView(
    items: List<ContentItem>
) {
    val context = LocalContext.current
    val AD_FREQUENCY = 5

    AndroidView(
        factory = { ctx ->
            RecyclerView(ctx).apply {
                layoutManager = LinearLayoutManager(ctx)
                adapter = ContentWithAdAdapter(items, AD_FREQUENCY)
            }
        },
        modifier = Modifier.fillMaxSize()
    )
}

class ContentWithAdAdapter(
    private val items: List<ContentItem>,
    private val adFrequency: Int
) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    companion object {
        const val VIEW_TYPE_CONTENT = 0
        const val VIEW_TYPE_AD = 1
    }

    override fun getItemViewType(position: Int): Int {
        return if (position > 0 && position % adFrequency == 0) {
            VIEW_TYPE_AD
        } else {
            VIEW_TYPE_CONTENT
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            VIEW_TYPE_AD -> {
                val view = FrameLayout(parent.context).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                    )
                }
                AdViewHolder(view)
            }
            else -> ContentViewHolder(
                LayoutInflater.from(parent.context).inflate(R.layout.item_content, parent, false)
            )
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (holder) {
            is AdViewHolder -> {
                Timber.d("Loading native ad at position $position")
                SpaceNative.showMedium(
                    space = "ADMOB_Native_List",
                    viewGroup = holder.container,
                    layoutRes = R.layout.layout_native_medium,
                    callback = object : NativeCallback {
                        override fun onLoaded(adView: NativeAdView, ad: NativeAd, space: String) {
                            Timber.d("RecyclerView native ad loaded at $position")
                        }

                        override fun onFailed(space: String, error: NativeError) {
                            Timber.e("RecyclerView native ad failed at $position: ${error.message}")
                            holder.container.visibility = View.GONE
                        }

                        override fun onImpression(space: String) {}
                        override fun onClicked(space: String) {}
                        override fun onPaid(space: String, revenue: NativeRevenue) {}
                    }
                )
            }
            is ContentViewHolder -> {
                // Bind content
                val item = items[position]
                holder.bind(item)
            }
        }
    }

    override fun getItemCount() = items.size

    class AdViewHolder(val container: FrameLayout) : RecyclerView.ViewHolder(container)
    class ContentViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        fun bind(item: ContentItem) {
            // Bind content data to views
        }
    }
}
```

### Best Practices for Compose

1. **Use AndroidView wrapper** - NativeAdView is a View, not a Compose component
2. **LaunchedEffect for one-time load** - Load ad on first composition with spaceName as key
3. **DisposableEffect for cleanup** - Always destroy NativeAd and clear cache when composable leaves composition
4. **State management** - Use sealed classes to track Loading/Loaded/Failed states
5. **Preload for lists** - Preload ads before LazyColumn renders to improve list performance
6. **Logging** - Use Timber.d() with BuildConfig.DEBUG checks for production safety
7. **Memory management** - Destroy NativeAd objects when no longer needed to release resources
8. **Frequency control** - Use AD_FREQUENCY constant to control how often ads appear in lists

## Advanced Features

### Preload Native Ad

```kotlin
SpaceNative.preload(
    space = "ADMOB_Native_List",
    layoutRes = R.layout.layout_native_medium,
    callback = object : PreloadCallback {
        override fun onPreloadSuccess() {
            // Ad preloaded
        }

        override fun onPreloadFailed(error: NativeError) {
            // Failed to preload
        }
    }
)
```

### Clear Cache

```kotlin
// Clear specific space
SpaceNative.clearCache("ADMOB_Native_List")

// Clear all native cache
SpaceNative.clearAllCache()
```

## Configuration

In `assets/ads_config.json`:

```json
{
  "space": "ADMOB_Native_List",
  "adsType": "native",
  "ids": [
    "ca-app-pub-3940256099942544/2247696110",
    "ca-app-pub-3940256099942544/1044960115"
  ],
  "enable": true,
  "minInterval": 30000,
  "adChoicesPosition": "top_right"
}
```

**adChoicesPosition options**: `top_left`, `top_right`, `bottom_left`, `bottom_right`

## Best Practices

### 1. Use Appropriate Native Ad Size

**WHY**: Matching ad size to content context improves user experience and click-through rates. Small ads in dense lists, large ads in detail screens.

```kotlin
// In lists - use small or medium
SpaceNative.showSmall(
    space = "ADMOB_Native_List",
    viewGroup = holder.adContainer,
    layoutRes = R.layout.layout_native_small,
    callback = callback
)

// In detail screens - use large or medium
SpaceNative.showLarge(
    space = "ADMOB_Native_Detail",
    viewGroup = binding.nativeContainer,
    layoutRes = R.layout.layout_native_large,
    callback = callback
)

// For fullscreen placements
SpaceNative.showFullscreen(
    space = "ADMOB_Native_Fullscreen",
    viewGroup = binding.nativeContainer,
    layoutRes = R.layout.layout_native_fullscreen,
    callback = callback
)
```

### 2. Preload Native Ads Before Scrolling

**WHY**: Native ads take time to load. Preloading ensures ads are ready when the user scrolls to them, preventing blank placeholder flickers.

```kotlin
class ContentListFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Preload before RecyclerView renders
        Timber.d("Preloading native ads for list")
        SpaceNative.preload(
            space = "ADMOB_Native_List",
            layoutRes = R.layout.layout_native_medium,
            callback = object : PreloadCallback {
                override fun onPreloadSuccess() {
                    Timber.d("Native ads ready for list")
                    setupRecyclerView()
                }

                override fun onPreloadFailed(error: NativeError) {
                    Timber.e("Native preload failed: ${error.message}")
                    // Setup RecyclerView anyway - ads will load on demand
                    setupRecyclerView()
                }
            }
        )
    }

    private fun setupRecyclerView() {
        binding.recyclerView.adapter = ContentAdapter()
    }
}
```

### 3. Always Clear Cache in onDestroy()

**WHY**: NativeAd objects hold references to media assets and ad data. Not destroying them causes memory leaks that can crash the app.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onDestroy() {
        super.onDestroy()
        Timber.d("Clearing native ad caches")
        SpaceNative.clearCache("ADMOB_Native_List")
        SpaceNative.clearCache("ADMOB_Native_Detail")
    }
}

// For individual NativeAd objects
class AdViewHolder(view: View) : RecyclerView.ViewHolder(view) {
    private var nativeAd: NativeAd? = null

    fun bind(ad: NativeAd) {
        nativeAd?.destroy() // Destroy previous ad
        nativeAd = ad
        // Bind ad to views
    }

    fun recycle() {
        Timber.d("Recycling native ad view")
        nativeAd?.destroy()
        nativeAd = null
    }
}
```

### 4. Hide Container on Failure

**WHY**: Failed ad loads result in an empty space in the layout. Hiding the container maintains clean UI for users.

```kotlin
SpaceNative.showMedium(
    space = "ADMOB_Native_List",
    viewGroup = binding.nativeContainer,
    layoutRes = R.layout.layout_native_medium,
    callback = object : NativeCallback {
        override fun onLoaded(adView: NativeAdView, ad: NativeAd, space: String) {
            Timber.d("Native ad loaded: $space")
            binding.nativeContainer.visibility = View.VISIBLE
        }

        override fun onFailed(space: String, error: NativeError) {
            Timber.e("Native ad failed: $space - ${error.message}")
            binding.nativeContainer.visibility = View.GONE
        }

        // ... other callbacks
    }
)
```

### 5. Create Custom Layouts Matching App Design

**WHY**: Native ads that blend with app design have higher click-through rates and better user experience.

```kotlin
// Create layout that matches your app theme
// res/layout/layout_native_themed.xml

// Use custom layout
SpaceNative.show(
    space = "ADMOB_Native_List",
    viewGroup = binding.nativeContainer,
    layoutRes = R.layout.layout_native_themed, // Custom themed layout
    callback = callback
)
```

**Custom layout tips:**
- Match fonts and colors with your app theme
- Follow AdMob guidelines for required elements (headline, CTA, icon)
- Add "Ad" label to identify sponsored content
- Test different layouts to optimize CTR

### 6. Use ViewHolder Pattern in RecyclerView

**WHY**: ViewHolder pattern prevents creating new ad instances for every item in the list, improving scroll performance.

```kotlin
class ContentAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    companion object {
        const val VIEW_TYPE_CONTENT = 0
        const val VIEW_TYPE_AD = 1
        const val AD_FREQUENCY = 5
    }

    override fun getItemViewType(position: Int): Int {
        return if (position > 0 && position % AD_FREQUENCY == 0) VIEW_TYPE_AD else VIEW_TYPE_CONTENT
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            VIEW_TYPE_AD -> {
                val container = FrameLayout(parent.context).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                    )
                }
                NativeAdViewHolder(container)
            }
            else -> ContentViewHolder(
                LayoutInflater.from(parent.context).inflate(R.layout.item_content, parent, false)
            )
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (holder) {
            is NativeAdViewHolder -> {
                Timber.d("Binding native ad at position $position")
                SpaceNative.showMedium(
                    space = "ADMOB_Native_List",
                    viewGroup = holder.adContainer,
                    layoutRes = R.layout.layout_native_medium,
                    callback = holder.callback
                )
            }
            is ContentViewHolder -> {
                holder.bind(items[position])
            }
        }
    }

    override fun onViewRecycled(holder: RecyclerView.ViewHolder) {
        if (holder is NativeAdViewHolder) {
            Timber.d("Recycling native ad view holder")
            // Clear but don't destroy - SDK manages cache
        }
        super.onViewRecycled(holder)
    }

    class NativeAdViewHolder(val adContainer: FrameLayout) : RecyclerView.ViewHolder(adContainer) {
        val callback = object : NativeCallback {
            override fun onLoaded(adView: NativeAdView, ad: NativeAd, space: String) {
                adContainer.visibility = View.VISIBLE
                Timber.d("RecyclerView native ad loaded at position $adapterPosition")
            }

            override fun onFailed(space: String, error: NativeError) {
                adContainer.visibility = View.GONE
                Timber.e("RecyclerView native ad failed: ${error.message}")
            }

            override fun onImpression(space: String) {}
            override fun onClicked(space: String) {}
            override fun onPaid(space: String, revenue: NativeRevenue) {}
        }
    }
}
```

### 7. Add Comprehensive Logging for Debugging

**WHY**: Native ad loading has many failure points. Detailed logging helps identify issues in production.

```kotlin
SpaceNative.showMedium(
    space = "ADMOB_Native_List",
    viewGroup = binding.nativeContainer,
    layoutRes = R.layout.layout_native_medium,
    callback = object : NativeCallback {
        override fun onLoaded(adView: NativeAdView, ad: NativeAd, space: String) {
            if (BuildConfig.DEBUG) {
                Timber.d("Native loaded: $space | " +
                        "Headline: ${ad.headline} | " +
                        "HasMedia: ${ad.mediaContent != null}")
            }
        }

        override fun onFailed(space: String, error: NativeError) {
            Timber.e("Native failed: $space | " +
                    "Code: ${error.code} | " +
                    "Message: ${error.message}")
        }

        override fun onImpression(space: String) {
            if (BuildConfig.DEBUG) {
                Timber.d("Native impression: $space")
            }
        }

        override fun onClicked(space: String) {
            if (BuildConfig.DEBUG) {
                Timber.d("Native clicked: $space")
            }
        }

        override fun onPaid(space: String, revenue: NativeRevenue) {
            Timber.i("Native revenue: $space - ${revenue.valueMicros} micros")
        }
    }
)
```

### 8. Memory Management Best Practices

**WHY**: Native ads hold references to images, videos, and ad objects. Poor memory management causes OOM errors.

```kotlin
// Destroy NativeAd when no longer needed
class NativeAdManager {
    private val activeAds = mutableListOf<NativeAd>()

    fun registerAd(ad: NativeAd) {
        activeAds.add(ad)
        Timber.d("Registered native ad. Total active: ${activeAds.size}")
    }

    fun destroyAll() {
        Timber.d("Destroying ${activeAds.size} native ads")
        activeAds.forEach { it.destroy() }
        activeAds.clear()
        SpaceNative.clearAllCache()
    }
}

// In Activity
class MainActivity : AppCompatActivity() {
    private val nativeAdManager = NativeAdManager()

    // When ad is loaded
    fun onNativeAdLoaded(ad: NativeAd) {
        nativeAdManager.registerAd(ad)
    }

    override fun onDestroy() {
        super.onDestroy()
        nativeAdManager.destroyAll()
    }
}
```

### 9. Handle Min Interval Configuration

**WHY**: SDK enforces min_interval to prevent excessive ad requests. Respect this to maintain good ad performance.

```kotlin
// Check if enough time has passed
fun showNativeAdIfEligible(space: String, viewGroup: ViewGroup) {
    if (!SpaceNative.canShow(space)) {
        Timber.d("Min interval not elapsed for native ad: $space")
        viewGroup.visibility = View.GONE
        return
    }

    Timber.d("Showing native ad: $space")
    SpaceNative.showMedium(
        space = space,
        viewGroup = viewGroup,
        layoutRes = R.layout.layout_native_medium,
        callback = callback
    )
}
```

### 10. Check Premium Status Before Showing Native Ads

**WHY**: Premium users should not see ads. Always check user status before displaying ads to maintain premium experience.

```kotlin
fun showNativeAdToEligibleUser(space: String, viewGroup: ViewGroup) {
    // Check premium status
    if (UserManager.isPremium()) {
        Timber.d("User is premium, hiding native ad container: $space")
        viewGroup.visibility = View.GONE
        return
    }

    // Check space-specific enable flag
    if (!AdSpaceSDK.isSpaceEnabled(space)) {
        Timber.d("Native ad space disabled: $space")
        viewGroup.visibility = View.GONE
        return
    }

    // Show ad
    Timber.d("Showing native ad to non-premium user: $space")
    SpaceNative.showMedium(
        space = space,
        viewGroup = viewGroup,
        layoutRes = R.layout.layout_native_medium,
        callback = object : NativeCallback {
            override fun onLoaded(adView: NativeAdView, ad: NativeAd, space: String) {
                viewGroup.visibility = View.VISIBLE
            }

            override fun onFailed(space: String, error: NativeError) {
                viewGroup.visibility = View.GONE
            }

            override fun onImpression(space: String) {}
            override fun onClicked(space: String) {}
            override fun onPaid(space: String, revenue: NativeRevenue) {}
        }
    )
}
```

### 11. Performance Optimization for Lists

**WHY**: Loading native ads synchronously in RecyclerView can freeze scroll. Async loading and caching improve scroll performance.

```kotlin
// Preload a pool of native ads for smooth list experience
class NativeAdPool(private val poolSize: Int = 3) {
    private val adQueue = ArrayDeque<NativeAd>()

    fun preload(space: String, layoutRes: Int) {
        if (adQueue.size >= poolSize) {
            Timber.d("Ad pool full: $space (size: ${adQueue.size})")
            return
        }

        Timber.d("Preloading native ad for pool: $space")
        SpaceNative.preload(
            space = space,
            layoutRes = layoutRes,
            callback = object : PreloadCallback {
                override fun onPreloadSuccess() {
                    Timber.d("Native ad added to pool: $space")
                }

                override fun onPreloadFailed(error: NativeError) {
                    Timber.e("Failed to preload for pool: $space - ${error.message}")
                }
            }
        )
    }

    fun getAd(): NativeAd? {
        return adQueue.removeFirstOrNull().also {
            if (it != null) {
                Timber.d("Retrieved ad from pool. Remaining: ${adQueue.size}")
            }
        }
    }

    fun size() = adQueue.size
}

// Usage
class ContentFragment : Fragment() {
    private val adPool = NativeAdPool(poolSize = 3)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Preload pool on fragment creation
        adPool.preload(
            space = "ADMOB_Native_List",
            layoutRes = R.layout.layout_native_medium
        )
    }
}
```

## RecyclerView Integration

```kotlin
class ContentAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    companion object {
        const val VIEW_TYPE_CONTENT = 0
        const val VIEW_TYPE_AD = 1
        const val AD_FREQUENCY = 5 // Show ad every 5 items
    }

    override fun getItemViewType(position: Int): Int {
        return if (position % AD_FREQUENCY == 0) VIEW_TYPE_AD else VIEW_TYPE_CONTENT
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            VIEW_TYPE_AD -> AdViewHolder(/* inflate ad layout */)
            else -> ContentViewHolder(/* inflate content layout */)
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (holder) {
            is AdViewHolder -> {
                SpaceNative.showMedium(
                    space = "ADMOB_Native_List",
                    viewGroup = holder.adContainer,
                    layoutRes = R.layout.layout_native_medium,
                    callback = holder.callback
                )
            }
            is ContentViewHolder -> {
                // Bind content
            }
        }
    }
}
```

## Common Issues

**Native ad not showing?**
- Check layout resource exists
- Verify all required views have correct IDs
- Check space is enabled in config
- Ensure container has proper height

**Layout issues?**
- Use NativeAdView as root element
- Set proper IDs for ad components
- Test with different ad sizes

**Memory leaks?**
- Always clear cache in onDestroy()
- Don't hold references to NativeAdView
- Use ViewHolder pattern in RecyclerView
