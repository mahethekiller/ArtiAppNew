# Android Target SDK Requirement

When building or configuring an Android project (including Capacitor, React Native, Flutter, or native), always ensure that the `targetSdkVersion` meets Google Play's latest requirements.

As of August 31, 2024, Google Play requires all new apps and app updates to target at least **API level 34 (Android 14)**.

- **Capacitor**: Update `android/variables.gradle` to set `targetSdkVersion = 34` (and usually `compileSdkVersion = 34`).
- **Native Android**: Update `app/build.gradle` or `app/build.gradle.kts`.

Always document this in any Android setup or conversion plans.
