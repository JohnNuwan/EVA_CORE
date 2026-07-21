---
name: flutter
description: Développement cross-platform Flutter/Dart — Widget, état, navigation, platform channels, animations, CI/CD, Web
---

# Skill: Flutter/Dart (Cross-Platform)

## Vue d'ensemble
Développement cross-platform avec Flutter et Dart, couvrant le widget tree, la gestion d'état, la navigation, les animations, les platform channels, et le déploiement iOS/Android/Web/Desktop.

## 1. Dart — Langage

### 1.1 Syntaxe Moderne
```dart
// Null safety
class User {
  final String name;
  final String? email;
  final DateTime createdAt = DateTime.now();
  
  const User({required this.name, this.email});
  
  // Named constructor
  User.fromJson(Map<String, dynamic> json)
      : name = json['name'] as String,
        email = json['email'] as String?;
  
  Map<String, dynamic> toJson() => {
        'name': name,
        'email': email,
      };
}

// Pattern matching (Dart 3)
switch (state) {
  case Loading(:final message) => showSpinner(message);
  case Success(:final users) => UserList(users);
  case Error(:final error) => ErrorWidget(error);
}

// Sealed class
sealed class ApiResult<T> {
  const ApiResult();
}
class Success<T> extends ApiResult<T> { final T data; ... }
class Failure<T> extends ApiResult<T> { final String message; ... }
```

### 1.2 Concurrency
- **Future** — `async`, `await`, `Future.wait()`
- **Stream** — `Stream<T>`, `StreamSubscription`, `async*`
- **Isolates** — `Isolate.spawn`, `compute()` pour CPU-bound
- **StreamController** — `StreamController<T>`, broadcast streams
- **Zone** — `runZonedGuarded` pour catch global

### 1.3 Patterns Dart
- **Records** (Dart 3) — `(String name, int age) record = ('Alice', 30);`
- **Patterns** — destructuring, `if-case`, `switch expression`, `for-in patterns`
- **Augmentation** (Dart 3) — `augment class`, `augment method`
- **Extension methods** — `extension StringParsing on String { int? parseInt() => int.tryParse(this); }`
- **Generics** — `<T>`, `Covariant`, `Contravariant`, `T Function()`

## 2. Widget Tree & UI

### 2.1 Composition Widget
```dart
class UserCard extends StatelessWidget {
  final User user;
  final VoidCallback onTap;
  
  const UserCard({super.key, required this.user, required this.onTap});
  
  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              CircleAvatar(backgroundImage: NetworkImage(user.avatarUrl)),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(user.name, style: Theme.of(context).textTheme.titleMedium),
                    Text(user.email ?? '', style: Theme.of(context).textTheme.bodySmall),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### 2.2 Layouts Clés
- **Row/Column** — flex direction, MainAxisAlignment, CrossAxisAlignment
- **Stack** — superposition, Positioned, FractionallySizedBox
- **Flex/Expanded** — ratios flexibles
- **GridView** — items en grille, SliverGrid, crossAxisCount
- **ListView** — builder/separated/custom, lazy loading
- **CustomScrollView** — slivers combinés (app bar, grid, list)
- **LayoutBuilder** — responsive, BoxConstraints, maxWidth
- **MediaQuery** — `MediaQuery.sizeOf(context)`, orientation

### 2.3 Theming
```dart
MaterialApp(
  theme: ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFF6750A4),
      brightness: Brightness.light,
    ),
    typography: Typography.material2021(),
  ),
  darkTheme: ThemeData.dark(),
  themeMode: ThemeMode.system,
);
```

## 3. Gestion d'État

### 3.1 Approches
| Approche | Usage | Idéal pour |
|----------|-------|-----------|
| StatefulWidget | État local simple | Formulaires, UI state |
| Provider | DI + ChangeNotifier | Petite app |
| Riverpod | Compile-safe Provider | **Nouveaux projets** |
| Bloc/Cubit | Event-driven | Apps complexes |
| GetX | Tout-en-un | Rapidité (mais controversé) |

### 3.2 Riverpod (Recommandé)
```dart
// Providers
final userRepositoryProvider = Provider<UserRepository>((ref) => UserRepository());
final fetchUsersProvider = FutureProvider.family<List<User>, String>(
  (ref, query) => ref.read(userRepositoryProvider).fetchUsers(query),
);

// StateNotifierProvider
final userListProvider = StateNotifierProvider<UserListNotifier, AsyncValue<List<User>>>((ref) {
  return UserListNotifier(ref.read(userRepositoryProvider));
});

class UserListNotifier extends StateNotifier<AsyncValue<List<User>>> {
  final UserRepository _repo;
  UserListNotifier(this._repo) : super(const AsyncValue.loading());
  
  Future<void> load() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _repo.fetchUsers());
  }
}

// Usage dans le widget
final users = ref.watch(userListProvider);
users.when(
  data: (users) => UserList(users),
  loading: () => const CircularProgressIndicator(),
  error: (err, stack) => ErrorWidget(err.toString()),
);
```

## 4. Navigation

### 4.1 GoRouter (Recommandé)
```dart
final router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomeScreen(),
      routes: [
        GoRoute(
          path: 'user/:id',
          builder: (context, state) => UserDetailScreen(
            userId: state.pathParameters['id']!,
          ),
        ),
      ],
    ),
  ],
);

// Dans MaterialApp.router
MaterialApp.router(routerConfig: router);
```

### 4.2 Deep Linking
```dart
GoRouter(
  routes: [...],
  initialLocation: '/',
  debugLogDiagnostics: true,
);
// AndroidManifest.xml intent filter
// Info.plist CFBundleURLTypes
```

## 5. Animations

### 5.1 Implicit Animations
```dart
AnimatedContainer(
  duration: const Duration(milliseconds: 300),
  curve: Curves.easeInOut,
  width: isExpanded ? 200 : 100,
  height: isExpanded ? 200 : 100,
  color: isExpanded ? Colors.blue : Colors.red,
)

AnimatedOpacity(
  opacity: isVisible ? 1.0 : 0.0,
  duration: const Duration(milliseconds: 200),
  child: content,
)
```

### 5.2 Explicit Animations
```dart
class _MyWidgetState extends State<MyWidget> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    duration: const Duration(milliseconds: 500),
    vsync: this,
  );
  late final Animation<double> _animation = CurvedAnimation(
    parent: _controller,
    curve: Curves.easeInOut,
  );
  
  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _animation,
      child: ScaleTransition(
        scale: Tween<double>(begin: 0, end: 1).animate(_animation),
        child: content,
      ),
    );
  }
}
```

### 5.3 Rive / Lottie
- **Rive** — animations vectorielles interactives, `RiveAnimation.asset`
- **Lottie** — animations After Effects, `Lottie.asset`, `Lottie.repeat`
- **Flutter Animations** — `Hero` (shared element), `TweenAnimationBuilder`

## 6. Platform Channels & Native

### 6.1 Method Channels
```dart
// Dart
const platform = MethodChannel('com.example.app/battery');
final batteryLevel = await platform.invokeMethod<int>('getBatteryLevel');

// iOS (Swift)
FlutterMethodChannel(name: "com.example.app/battery", binaryMessenger: controller.binaryMessenger)
  .setMethodCallHandler { call, result in
    if call.method == "getBatteryLevel" {
      result(UIDevice.current.batteryLevel)
    }
  }

// Android (Kotlin)
MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "com.example.app/battery")
  .setMethodCallHandler { call, result ->
    if (call.method == "getBatteryLevel") {
      result.success(batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY))
    }
  }
```

### 6.2 Pigeon (Type-safe)
```dart
// Fichier .dart pigeon, génère code natif typé
@HostApi()
abstract class BatteryApi {
  int getBatteryLevel();
}
```

## 7. Performance

### 7.1 Optimisation
- **RepaintBoundary** — isoler les widgets qui ne se repeignent pas
- **const constructors** — widgets const = moins de garbage collection
- **AnimatedBuilder** vs setState — rebuild minimal
- **ListView.builder** — lazy loading vs ListView (tout charge)
- **ImageCache** — `PaintingBinding.instance.imageCache.maximumSize = 500`
- **Isolate** — `compute()` pour traitement lourd (JSON parsing, crypto)
- **DevTools** — Performance view, Memory view, CPU profiler

### 7.2 App Size
- **Tree shaking** — Flutter compile-time, dead code éliminé
- **Obfuscation** — `--obfuscate --split-debug-info`
- **Assets** — compress PNG, AVIF pour images, utiliser des SVG/Icon
- **Fonts** — `fontVariations` vs plusieurs fichiers .ttf
- **Shared libraries** — `.so` size pour Flutter engine (ARM64 ≈ 6MB)

## 8. Tests

### 8.1 Unit Tests
```dart
void main() {
  group('UserRepository', () {
    late MockApiClient mockApi;
    late UserRepository repository;
    
    setUp(() {
      mockApi = MockApiClient();
      repository = UserRepository(api: mockApi);
    });
    
    test('fetchUsers returns list', () async {
      when(() => mockApi.getUsers()).thenAnswer((_) async => [testUser]);
      final users = await repository.fetchUsers();
      expect(users, hasLength(1));
    });
  });
}
```

### 8.2 Widget Tests
```dart
testWidgets('UserCard displays correctly', (tester) async {
  await tester.pumpWidget(MaterialApp(
    home: UserCard(user: testUser, onTap: () {}),
  ));
  
  expect(find.text('John Doe'), findsOneWidget);
  await tester.tap(find.byType(InkWell));
});
```

### 8.3 Integration Tests
```dart
test('login flow', () async {
  await app.tap(find.text('Connexion'));
  await app.enterText(find.byType(TextField).first, 'user@example.com');
  await app.tap(find.text('Valider'));
  await app.pumpAndSettle();
  expect(find.text('Dashboard'), findsOneWidget);
});
```

## 9. Multi-Platform

### 9.1 Build Targets
```bash
flutter build ios --release        # iOS IPA
flutter build apk --release        # Android APK
flutter build appbundle --release  # Android AAB
flutter build web --release        # PWA/Web
flutter build macos --release      # macOS DMG
flutter build linux --release      # Linux AppImage
flutter build windows --release    # Windows MSI
```

### 9.2 Platform-Specific
- **flutter_platform_widgets** — widgets adaptatifs (Cupertino ↔ Material)
- **Platform.isIOS / Platform.isAndroid** — `dart:io` Platform
- **Web** — CanvasKit vs HTML renderer, `kIsWeb`
- **Desktop** — `window_manager`, menu bar, tray, keyboard shortcuts

## 10. Déploiement

### 10.1 CI/CD (Codemagic / GitHub Actions)
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.24'
      - run: flutter pub get
      - run: flutter build appbundle --release
```

### 10.2 App Store / Play Store
- **Fastlane** — `fastlane match`, `fastlane deliver`, `fastlane supply`
- **Codemagic** — Git → test → build → deploy intégré
- **App Store Connect** — TestFlight, export compliance, IDFA
- **Play Console** — tracks (internal/closed/open/production)

## 11. Pièges Courants

- **Hot reload ≠ hot restart** — hot reload rate parfois avec `late final` fields, faire hot restart
- **const constructors oubliés** — `const` manquant = rebuild constants inutiles
- **ScrollPhysics** — `BouncingScrollPhysics` vs `ClampingScrollPhysics` iOS/Android
- **PlatformView** (WebView/Map) — retards au rendu, `hybridComposition` sur Android
- **Image loading** — sans cache-control, réseau → widget flash
- **Flutter version** — pub.dev constraints, `flutter pub outdated`, `dart fix --apply`
- **Android Fullscreen** — `SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky)`
- **iOS 17 privacy** — `PHPhotoLibrary`, `CLLocationManager` permission changes