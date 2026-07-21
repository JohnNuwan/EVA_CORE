---
name: app-deployment
description: Déploiement mobile — App Store Connect, Google Play Console, Fastlane, CI/CD, TestFlight, code signing, EAS, monitoring
---

# Skill: Déploiement Mobile (App Store / Play Store)

## Vue d'ensemble
Déploiement complet d'applications mobiles sur l'App Store (iOS) et Google Play (Android), couvrant le code signing, les builds automatisés, les tracks de distribution, le monitoring post-release, et les mises à jour OTA.

## 1. Apple App Store Connect

### 1.1 Certificats & Profils
```bash
# Apple Developer Portal
# Certificats: Apple Development / Apple Distribution
# Profils: Development / Ad Hoc / App Store / Enterprise

# Fastlane Match (recommandé)
fastlane match init
fastlane match development  # Dev profiles
fastlane match appstore     # Distribution profiles

# Génération manuelle
# 1. CSR sur Keychain Access
# 2. Certificates > Create Certificate (Apple Distribution)
# 3. Profiles > Create Profile (App Store)
# 4. Télécharger .mobileprovision
```

### 1.2 App Store Connect Configuration
- **App Information** — name, bundle ID, SKU, primary language
- **Pricing** — price tiers, in-app purchases, subscriptions (SK2)
- **App Privacy** — nutrition label, tracking (ATT), IDFA
- **Export Compliance** — cryptography declaration (EAR/ENC)
- **TestFlight** — internal (25 testers) + external (10,000 via beta review)
- **App Review** — guidelines, pre-release feedback, expedited review

### 1.3 App Metadata
```
Nom: MyApp
Subtitle: L'app qui révolutionne tout
Description: Description détaillée des fonctionnalités
Keywords: keyword1, keyword2, keyword3
Support URL: https://example.com/support
Marketing URL: https://example.com
Privacy Policy URL: https://example.com/privacy
Copyright: 2026 Example Inc.
Screenshots: 6.7" (iPhone 16 Pro Max), 12.9" (iPad Pro)
App Preview: Video 30s max
Rating: 17+ (Medical/Treatment, Unrestricted Web Access)
```

### 1.4 Build Upload & Validation
```bash
# Xcode archive
xcodebuild archive -scheme App -archivePath build/App.xcarchive

# Validation
xcodebuild -exportArchive \
  -archivePath build/App.xcarchive \
  -exportPath build/ \
  -exportOptionsPlist ExportOptions.plist

# Transporter.app / altool (CLI)
xcrun altool --upload-app -f App.ipa -t ios -u user@example.com -p @keychain:AC_PASSWORD

# xcparse (logs)
xcrun xcparse logs --verbose build.xcresult
```

## 2. Google Play Console

### 2.1 Play App Signing
```bash
# Google gère la clé de signature
# Vous fournissez une clé de "upload" pour envoyer les AAB

# Générer clé de upload
keytool -genkey -v -keystore upload-keystore.jks \
  -alias upload -keyalg RSA -keysize 2048 -validity 10000

# Build signé avec clé upload
./gradlew bundleRelease

# Vérifier l'alignement
zipalign -v -p 4 app-release.aab app-release-aligned.aab
```

### 2.2 Play Tracks
| Track | Usage | Review |
|-------|-------|--------|
| Internal Testing | Testeurs internes (100) | Aucune |
| Closed Alpha | Testeurs invités (100K) | ✅ |
| Open Beta | Public (10K+) | ✅ |
| Production | Tous les utilisateurs | ✅ |

### 2.3 Play Console Configuration
- **Store Listing** — title, short/long description, screenshots (2 phone + 2 tablet + 2 TV)
- **Pricing & Distribution** — countries, price, managed products, subscriptions
- **Content Rating** — questionnaire IARC (International Age Rating Coalition)
- **App Integrity** — Play Integrity API (remplace SafetyNet)
- **Data Safety** — section GDPR-like (Play Store listing)

### 2.4 In-App Reviews & Updates
```kotlin
// In-app Review API
val reviewManager = ReviewManagerFactory.create(context)
val request = reviewManager.requestReviewFlow()
request.addOnCompleteListener { task ->
    if (task.isSuccessful) {
        reviewManager.launchReviewFlow(activity, task.result)
    }
}

// In-app Update API
val appUpdateManager = AppUpdateManagerFactory.create(context)
val appUpdateInfo = appUpdateManager.appUpdateInfo.await()
if (appUpdateInfo.updateAvailability() == UpdateAvailability.UPDATE_AVAILABLE
    && appUpdateInfo.isUpdateTypeAllowed(AppUpdateType.IMMEDIATE)) {
    appUpdateManager.startUpdateFlowForResult(
        appUpdateInfo,
        AppUpdateType.IMMEDIATE,
        activity,
        REQUEST_UPDATE
    )
}
```

## 3. Fastlane (Multi-Platform)

### 3.1 iOS Lane
```ruby
lane :release do
  match(type: "appstore", readonly: true)
  
  increment_build_number(
    build_number: latest_testflight_build_number + 1
  )
  
  build_app(
    scheme: "App",
    export_method: "app-store",
    include_bitcode: true,
    include_on_demand_resources: true
  )
  
  upload_to_testflight(
    skip_waiting_for_build_processing: true,
    changelog: get_changelog
  )
  
  upload_to_app_store(
    skip_metadata: true,
    skip_screenshots: true,
    submit_for_review: false
  )
end
```

### 3.2 Android Lane
```ruby
lane :deploy do
  # Build
  gradle(task: "bundleRelease")
  
  # Sign
  upload_to_play_store(
    track: "internal",
    release_status: "draft",
    aab: "app/build/outputs/bundle/release/app-release.aab",
    json_key: "play-service-account.json",
    skip_upload_screenshots: true,
    skip_upload_metadata: true
  )
end
```

### 3.3 Supply (Play Store Upload)
```bash
fastlane supply init
fastlane supply run \
  --aab app.aab \
  --track internal \
  --json_key play-service-account.json \
  --skip_upload_metadata \
  --skip_upload_images
```

## 4. CI/CD Pipelines

### 4.1 GitHub Actions — iOS
```yaml
jobs:
  deploy-ios:
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: '3.3' }
      - run: bundle install
      - run: bundle exec fastlane release
        env:
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          APP_STORE_CONNECT_API_KEY: ${{ secrets.APP_STORE_KEY }}
```

### 4.2 GitHub Actions — Android
```yaml
jobs:
  deploy-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - run: ./gradlew bundleRelease
      - uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJson: ${{ secrets.PLAY_SERVICE_ACCOUNT }}
          packageName: com.example.app
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
```

### 4.3 Expo EAS
```yaml
- name: EAS Build & Submit
  run: |
    npx eas build --platform all --non-interactive --profile production
    npx eas submit --platform ios --non-interactive
    npx eas submit --platform android --non-interactive
  env:
    EXPO_TOKEN: ${{ secrets.EXPO_TOKEN }}
```

## 5. Versioning & Changelog

### 5.1 SemVer + Build Number
```bash
# iOS
# CFBundleShortVersionString = "2.1.3" (SemVer)
# CFBundleVersion = "2026083101" (YYYYMMDD + build)

# Android
# versionName = "2.1.3" (SemVer)
# versionCode = 2026083101 (timestamp int)

# Fastlane
increment_version_number(
  version_number: "2.1.3",
  xcodeproj: "App.xcodeproj"
)
```

## 6. Monitoring & Crash Reporting

### 6.1 Sentry
```swift
// iOS
import Sentry

SentrySDK.start { options in
    options.dsn = "https://..."
    options.debug = false
    options.environment = "production"
    options.tracesSampleRate = 0.2  // 20% des transactions
}

SentrySDK.capture(error: error)
```

```kotlin
// Android
SentryAndroid.init(context) { options ->
    options.dsn = "https://..."
    options.environment = "production"
    options.tracesSampleRate = 0.2
}
```

### 6.2 Firebase Crashlytics
```bash
# Firebase CLI
firebase crashlytics:build:upload mapping.txt app.aab

# Kotlin
FirebaseCrashlytics.getInstance().recordException(e)
FirebaseCrashlytics.getInstance().setCustomKey("user_type", "premium")
```

## 7. OTA Updates

### 7.1 Expo Updates
```bash
eas update --branch production --message "Fix login crash"
```

### 7.2 CodePush (Legacy)
```bash
appcenter codepush release-react -a owner/app -d Production
```

### 7.3 Flutter Shorebird
```bash
shorebird release android --flutter-version 3.24.0
shorebird patch android --flavor production
```

## 8. Release Checklist

### 8.1 Pre-Release
- [ ] Tests unitaires ✅
- [ ] Tests UI ✅
- [ ] Crash-free rate ≥ 99.5%
- [ ] Performance benchmarks (cold start < 2s)
- [ ] Localisation vérifiée
- [ ] Privacy manifest (iOS 17+)
- [ ] SDK versions à jour (pas de deprecated API)
- [ ] Screenshots à jour
- [ ] Description / keywords optimisés ASO
- [ ] Deferred deep links testés
- [ ] Rate limiting API côté serveur ok

### 8.2 Post-Release
- [ ] Crash-free rate monitor (Sentry / Crashlytics)
- [ ] User reviews & ratings monitor
- [ ] ANR / frozen frames metrics
- [ ] Revenue / conversion tracking
- [ ] A/B test results (Firebase Remote Config)
- [ ] Phased rollout monitor (50% → 100%)

## 9. Pièges Courants

- **App Store rejection 2.5.1** — private APIs (UIWebView deprecated, clipboard usage)
- **Export compliance** — crypto declaration absente → app bloquée
- **TestFlight expiry** — builds expirés après 90 jours → nouveaux testers
- **Google Play policy** — target API level (Android 14+ targetSdk 34 min 2024)
- **APK size limit** — 200MB (Android), plus APK Expansion/OBB files
- **Mac mini CI runner** — certificats / comptes Apple limités à 2-3 sessions
- **Fastlane session expiration** — App Store Connect API key + 2FA handling
- **In-app purchases** — SKProductRequest (iOS) / BillingClient.queryProductDetailsAsync (Android) asynchrones
- **App Store Review times** — planifier 24-48h, expedited review (request 1/mois)
- **Phased rollout** — Google Play 7 jours, App Store manuel → phased release 7 jours