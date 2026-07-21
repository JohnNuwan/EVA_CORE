---
name: swift-ios
description: Développement iOS natif avec Swift — SwiftUI, UIKit, Xcode, frameworks Apple, performance, déploiement
---

# Skill: Développement iOS/Swift

## Vue d'ensemble
Développement d'applications iOS natives avec Swift, couvrant SwiftUI et UIKit, les frameworks système Apple, l'optimisation des performances, et le déploiement sur l'App Store.

## 1. Swift — Langage et Fondamentaux

### 1.1 Syntaxe Moderne
```swift
// Protocol-oriented programming
protocol Repository {
    associatedtype T
    func fetch(id: String) async throws -> T
    func save(_ item: T) async throws
}

// Value semantics avec structs
struct User: Identifiable, Codable {
    let id: UUID
    var name: String
    var email: String
    var createdAt: Date
}

// Result builders pour DSL
@resultBuilder
struct ViewBuilder {
    static func buildBlock<Content: View>(_ content: Content) -> Content
}
```

### 1.2 Concurrency (Swift 5.5+)
- **async/await** — async functions, structured concurrency
- **Task & TaskGroup** — parallélisme structuré
- **Actors** — isolation des données mutables, `@MainActor`
- **AsyncSequence** — AsyncStream, AsyncPublisher
- **Continuations** — `withCheckedContinuation`, `withUnsafeContinuation`

### 1.3 Patterns Avancés
- **Property Wrappers** — `@Published`, `@State`, `@Binding`, `@Environment`, `@AppStorage`
- **Codable** — custom encoding/decoding, `JSONEncoder.KeyEncodingStrategy`
- **Macros** (Swift 5.9+) — `@Observable`, `#Predicate`, macros custom
- **Generics** — associated types, opaque types (`some`), `any` existential

## 2. SwiftUI

### 2.1 Architecture SwiftUI
```swift
@Observable
final class AppViewModel {
    var users: [User] = []
    var isLoading = false
    
    @MainActor
    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        users = try await api.fetchUsers()
    }
}

struct UserListView: View {
    @State private var viewModel = AppViewModel()
    
    var body: some View {
        List(viewModel.users) { user in
            UserRow(user: user)
        }
        .task { await viewModel.loadUsers() }
        .refreshable { await viewModel.loadUsers() }
        .overlay {
            if viewModel.isLoading { ProgressView() }
        }
    }
}
```

### 2.2 Layout & Navigation
- **NavigationStack** (iOS 16+) — programme driven navigation, `.navigationDestination`
- **NavigationSplitView** — iPad/macOS multi-column
- **LazyVStack/LazyHStack** — lazy loading, performance
- **Grid/GridRow** — layouts en grille (iOS 16+)
- **AnyLayout** — layout adaptatif (HStack ↔ VStack)
- **ContainerRelativeFrame** — iOS 17+ sizing

### 2.3 Data Flow
| Pattern | Usage | Scope |
|---------|-------|-------|
| `@State` | Valeurs locales | View |
| `@Binding` | Two-way binding | Parent → Child |
| `@Observable` (iOS 17+) | Observable object | ViewModel |
| `@Environment` | Valeurs partagées | App tree |
| `@AppStorage` | UserDefaults | Persistence |
| SwiftData / CoreData | Persistance | Model layer |

### 2.4 Animations
- `.withAnimation` — animation explicite
- `.animation` — value-based animation
- `matchedGeometryEffect` — transitions fluides
- `PhaseAnimator` (iOS 17+) — animations séquencées
- `KeyframeAnimator` (iOS 17+) — animations keyframe
- Custom transitions — `AnyTransition.asymmetric`

## 3. UIKit (Maintenance & Legacy)

### 3.1 UIKit Interop (UIViewRepresentable)
```swift
struct MapView: UIViewRepresentable {
    let coordinate: CLLocationCoordinate2D
    
    func makeUIView(context: Context) -> MKMapView {
        MKMapView()
    }
    
    func updateUIView(_ uiView: MKMapView, context: Context) {
        uiView.setRegion(MKCoordinateRegion(center: coordinate, span: .init(latitudeDelta: 0.05, longitudeDelta: 0.05)), animated: true)
    }
}
```

### 3.2 UIKit Patterns
- **UICollectionView** — CompositionalLayout, diffable data sources
- **UIViewController** — lifecycle, containment, `UIViewControllerTransitioningDelegate`
- **Auto Layout** — NSLayoutConstraint, UIStackView
- **UIScrollView** — content insets, refresh control, keyboard avoidance
- **UITableViewController** — self-sizing cells, prefetching

## 4. Frameworks Système

### 4.1 Networking
- **URLSession** — async/await, `URLSessionConfiguration.background`, caching
- **URLProtocol** — intercepteur réseau custom
- **WebSocket** — `URLSessionWebSocketTask`
- **Alamofire / Moya** — libraries tierces (quand URLSession ne suffit pas)

### 4.2 Persistance
- **SwiftData** (iOS 17+) — #Model, @Query, @ModelActor
- **CoreData** — NSPersistentContainer, NSManagedObjectContext, CloudKit sync
- **GRDB** — SQLite Swift avec query builder
- **UserDefaults / @AppStorage** — preferences simples
- **Keychain** — `SecItemAdd`, `SecItemCopyMatching`
- **FileManager** — documents directory, cache, temp

### 4.3 Localisation
- **String Catalogs** (Xcode 15+) — `.xcstrings`
- **LocalizedStringResource** — type-safe localization (iOS 16+)
- **Formatters** — DateFormatter, NumberFormatter, ListFormatter
- **RTL** — `.leading`/`.trailing` au lieu de `.left`/`.right`

### 4.4 Frameworks Apple
| Framework | Usage |
|-----------|-------|
| CoreLocation | GPS, geofencing, CLMonitor |
| MapKit | Cartes, annotations, routage |
| CloudKit | Sync iCloud, CKContainer |
| NotificationCenter | Notifications locales/push |
| CoreBluetooth | BLE central/peripheral |
| HealthKit | Santé, HKWorkout, HKSample |
| AVFoundation | Audio, vidéo, capture |
| Vision | Détection faciale, OCR, tracking |
| CoreML | ML on-device, .mlpackage |
| WidgetKit | Widgets, Live Activities |
| StoreKit | In-app purchases, subscriptions |
| WeatherKit | Données météo (iOS 16+) |
| Accelerate | DSP, vectorisation, BNNS |
| Metal | GPU compute, shaders |

## 5. Xcode & Tooling

### 5.1 Configuration Projet
```bash
# xcodebuild ligne de commande
xcodebuild -project App.xcodeproj -scheme App -destination 'platform=iOS Simulator,name=iPhone 16 Pro' test

# Build avec code signing
xcodebuild -workspace App.xcworkspace -scheme App archive -archivePath build/App.xcarchive

# Export IPA
xcodebuild -exportArchive -archivePath build/App.xcarchive -exportPath build/ -exportOptionsPlist ExportOptions.plist
```

### 5.2 Swift Package Manager
```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/pointfreeco/swift-composable-architecture", from: "1.10.0"),
    .package(url: "https://github.com/onevcat/Kingfisher", from: "8.0.0")
]
```

### 5.3 Build Settings
- **Swift Compiler** — strict concurrency checking, whole module optimization
- **Asset Catalogs** — .xcassets, app icons, colors, symbols
- **Info.plist** — permissions (NSCameraUsageDescription, etc.)
- **Entitlements** — capabilities, App Groups, keychain sharing
- **Build Phases** — Run Script, SwiftGen, Sourcery, SwiftLint

## 6. Performance & Optimisation

### 6.1 Memory
- **Leak detection** — Xcode Memory Graph Debugger, Instruments (Leaks, Allocations)
- **Value semantics** — préférer structs aux classes
- **Lazy loading** — images, données, vues
- **COW** (Copy-on-Write) — éviter les copies inutiles
- **Weak references** — `[weak self]` dans les closures

### 6.2 UI Performance
- **Instruments** — Time Profiler, Core Animation, System Trace
- **SwiftUI diffing** — `EquatableView`, `@ViewBuilder` lazy
- **Image caching** — Kingfisher/Nuke, `URLCache`
- **Precomputed layout** — `CGSize` caching, `GeometryReader` minimal
- **Background tasks** — `BGTaskScheduler` pour les tâches différées

### 6.3 App Size
- **App Thinning** — Slicing, Bitcode, On-Demand Resources
- **Asset compression** — ImageOptim, SVG en SF Symbols
- **Dead code stripping** — `-dead_strip`, Swift compiler optimizations
- **XCFramework** — universal binaries

## 7. Tests

### 7.1 XCTest
```swift
final class UserViewModelTests: XCTestCase {
    var sut: UserViewModel!
    var mockAPI: MockAPIClient!
    
    override func setUp() {
        mockAPI = MockAPIClient()
        sut = UserViewModel(api: mockAPI)
    }
    
    func testLoadUsersSuccess() async throws {
        mockAPI.stub(.fetchUsers, return: [.mock])
        await sut.loadUsers()
        XCTAssertEqual(sut.users.count, 1)
        XCTAssertFalse(sut.isLoading)
    }
}
```

### 7.2 UI Tests (XCUITest)
```swift
func testLoginFlow() {
    let app = XCUIApplication()
    app.launch()
    
    let emailField = app.textFields["email"]
    emailField.tap()
    emailField.typeText("user@example.com")
    
    app.buttons["Connexion"].tap()
    XCTAssertTrue(app.staticTexts["Dashboard"].waitForExistence(timeout: 5))
}
```

### 7.3 Snapshot Testing
- **SnapshotTesting** (Point-Free) — `assertSnapshot(of: view, as: .image)`
- **SwiftSnapshotTesting** — layout, text, localisation variants

## 8. Déploiement & CI/CD

### 8.1 Fastlane
```ruby
lane :deploy do
  match(type: "appstore")
  build_app(
    scheme: "App",
    export_method: "app-store"
  )
  upload_to_app_store(
    skip_metadata: true,
    skip_screenshots: true
  )
end
```

### 8.2 GitHub Actions
```yaml
- name: Build & Test
  run: |
    xcodebuild test \
      -scheme App \
      -destination 'platform=iOS Simulator,name=iPhone 16 Pro' \
      -resultBundlePath TestResults.xcresult
```

### 8.3 Code Signing
- **Automatic signing** — Xcode managed profiles
- **Match (Fastlane)** — encrypted profiles in git
- **Manual** — Apple Developer Portal, `security import`

## 9. Pièges Courants

- **MainActor strict** — oublier `@MainActor` sur les mises à jour UI → crash
- **Reference cycles** — closures sans `[weak self]` → leak
- **SwiftUI identity** — `ForEach` sans `.id` → animations cassées
- **Background tasks timeout** — `BGTaskScheduler` 30s max
- **Push notifications** — sandbox vs production APNs
- **App Store review** — guideline 4.2 (minimum functionality), 2.1 (app completeness)
- **iOS 17+ APIs** — availability checks avec `#available(iOS 17, *)`