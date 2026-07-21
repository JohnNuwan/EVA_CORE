---
name: kotlin-android
description: Développement Android natif avec Kotlin — Jetpack Compose, Gradle, Material Design 3, Android SDK, Play Store
---

# Skill: Développement Android/Kotlin

## Vue d'ensemble
Développement d'applications Android natives avec Kotlin, couvrant Jetpack Compose, Material Design 3, les Android Jetpack Libraries, Gradle build system, et le déploiement Play Store.

## 1. Kotlin — Langage et Fondamentaux

### 1.1 Syntaxe Moderne
```kotlin
// Coroutines & Flow
class UserRepository(private val api: UserApi) {
    fun fetchUsers(): Flow<List<User>> = flow {
        emit(api.getUsers())
    }.flowOn(Dispatchers.IO)
    
    suspend fun saveUser(user: User) = withContext(Dispatchers.IO) {
        api.createUser(user)
    }
}

// Sealed classes pour états
sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String, val exception: Throwable? = null) : UiState<Nothing>
}

// Extension functions
fun String.isValidEmail(): Boolean = matches(Regex("^[A-Za-z0-9+_.-]+@(.+)$"))

// Type-safe builders (DSL)
fun Context.showToast(message: String) = 
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
```

### 1.2 Coroutines & Flow
- **CoroutineScope** — `viewModelScope`, `lifecycleScope`, custom scopes
- **Dispatchers** — `Main`, `IO`, `Default`, `Unconfined`
- **Flow** — `stateFlow`, `sharedFlow`, `callbackFlow`, `channelFlow`
- **StateFlow vs SharedFlow** — état vs événements one-shot
- **Channels** — `Channel<T>`, `BroadcastChannel`, `ConflatedBroadcastChannel`
- **Structured Concurrency** — `coroutineScope`, `supervisorScope`, `Job`
- **Exception handling** — `try/catch`, `catch {}` operator, `CoroutineExceptionHandler`

### 1.3 Patterns Avancés
- **Delegation** — `by lazy`, `by Delegates.observable`, `by map`
- **Inline classes** — `@JvmInline value class Email(val value: String)`
- **Context receivers** (Kotlin 1.6+) — `context(Context)` pour l'injection
- **Contracts** — `@Contract` pour l'inférence de smart cast
- **Multiplatform** — `expect`/`actual` pour KMP
- **Serialization** — `@Serializable`, `kotlinx.serialization` vs Gson/Moshi

## 2. Jetpack Compose

### 2.1 Composables Fondamentaux
```kotlin
@Composable
fun UserCard(
    user: User,
    onUserClick: (User) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = { onUserClick(user) },
        modifier = modifier.fillMaxWidth().padding(8.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "Avatar",
                modifier = Modifier.size(48.dp).clip(CircleShape)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column {
                Text(text = user.name, style = MaterialTheme.typography.titleMedium)
                Text(text = user.email, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
```

### 2.2 State Management
```kotlin
// ViewModel avec StateFlow
class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState<List<User>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<User>>> = _uiState.asStateFlow()
    
    init { loadUsers() }
    
    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val users = repository.fetchUsers()
                _uiState.value = UiState.Success(users)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Erreur inconnue")
            }
        }
    }
}

// Collect dans Compose
@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    
    when (val s = state) {
        is UiState.Loading -> Box(modifier = Modifier.fillMaxSize()) { CircularProgressIndicator() }
        is UiState.Success -> UserList(s.data)
        is UiState.Error -> ErrorMessage(s.message)
    }
}
```

### 2.3 Layout & Theming
- **Modifier system** — chaine de modifieurs (padding, clickable, background, etc.)
- **Material Design 3** — `MaterialTheme`, `ColorScheme`, `Typography`, `Shapes`
- **Dynamic colors** — Android 12+ Material You (Monet)
- **ConstraintLayout Compose** — layouts complexes relationnels
- **LazyColumn/LazyRow** — RecyclerView-like, keys, sticky headers
- **Pager** — `HorizontalPager`, `VerticalPager` (HorizontalPager 1.5+)

### 2.4 Animations
- **AnimatedVisibility** — entrée/sortie, `fadeIn`, `slideInVertically`
- **AnimatedContent** — transition entre contenus, `SizeTransform`
- **animateXAsState** — `animateFloatAsState`, `animateColorAsState`
- **AnimationSpec** — `tween`, `spring`, `keyframes`, `repeatable`
- **Transition** — `updateTransition` pour animations multi-états
- **Shared element** — `SharedTransitionLayout` (Compose 1.7+)

## 3. Android Jetpack Libraries

### 3.1 Navigation
```kotlin
// Navigation Compose
NavHost(navController, startDestination = "home") {
    composable("home") { HomeScreen(navController) }
    composable(
        route = "user/{userId}",
        arguments = listOf(navArgument("userId") { type = NavType.IntType })
    ) { backStackEntry ->
        val userId = backStackEntry.arguments?.getInt("userId") ?: return@composable
        UserDetailScreen(userId = userId)
    }
}

// Deep links
composable(
    route = "profile/{id}",
    deepLinks = listOf(navDeepLink { uriPattern = "myapp://profile/{id}" })
)
```

### 3.2 Persistance
- **Room** — `@Entity`, `@Dao`, `@Database`, `@Query`, `@Insert`, `@Transaction`
- **DataStore** — `PreferencesDataStore`, `ProtoDataStore` (remplace SharedPreferences)
- **SQLite (Room)** — migrations, FTS4/FTS5, foreign keys, indexes
- **ExoPlayer/Media3** — lecture audio/video locale
- **FileProvider** — `FileProvider.getUriForFile` pour partage de fichiers
- **EncryptedSharedPreferences** — AndroidX Security

### 3.3 Architecture Components
| Component | Usage | Scope |
|-----------|-------|-------|
| ViewModel | State persistant rotation | Activity/Fragment |
| LiveData | Observable data (legacy) | ViewModel |
| Room | DB relationnelle | Repository |
| WorkManager | Tâches différées, périodiques | Application |
| SavedStateHandle | Survie à la destruction | ViewModel |
| Hilt/Dagger | Injection de dépendances | Application |

### 3.4 WorkManager
```kotlin
class SyncWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result = try {
        syncData()
        Result.success()
    } catch (e: Exception) {
        if (runAttemptCount < 3) Result.retry() else Result.failure()
    }
}

// Periodic work (minimum interval: 15 min)
val request = PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
    .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
    .build()
WorkManager.getInstance(context).enqueueUniquePeriodicWork("sync", ExistingPeriodicWorkPolicy.KEEP, request)
```

## 4. Gradle & Build System

### 4.1 Version Catalog (libs.versions.toml)
```toml
[versions]
compose-bom = "2024.12.01"
room = "2.6.1"
hilt = "2.51"

[libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }
hilt-android = { module = "com.google.dagger:hilt-android", version.ref = "hilt" }

[plugins]
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
compose-compiler = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
```

### 4.2 build.gradle.kts
```kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.hilt)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.example.app"
    compileSdk = 35
    defaultConfig {
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
    }
    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}

dependencies {
    implementation(platform(libs.compose.bom))
    implementation(libs.bundles.compose)
    implementation(libs.bundles.hilt)
    ksp(libs.bundles.hilt.compiler)
}
```

## 5. Frameworks & Libraries Essentielles

### 5.1 Networking
- **Retrofit** — `@GET`, `@POST`, `@Path`, `@Query`, `@Body`, Converter.Factory
- **OkHttp** — intercepteurs, caching, WebSocket, TLS config
- **Ktor Client** — client HTTP Kotlin multiplateforme
- **Kotlinx.serialization** — JSON, protobuf, CBOR
- **Coil** — chargement d'images Compose-native
- **Glide/Picasso** — chargement d'images (legacy)

### 5.2 DI (Dependency Injection)
- **Hilt** — `@HiltAndroidApp`, `@AndroidEntryPoint`, `@HiltViewModel`, `@Module`, `@Provides`
- **Koin** — modules DSL, `single`, `factory`, `scoped`
- **Dagger** — `@Component`, `@Module`, `@Inject`, `@Scope`

### 5.3 Image Loading
- **Coil** (recommandé Compose) — `AsyncImage`, `ImageLoader`, disk cache LRU
- **Glide** — `RequestBuilder`, `RequestOptions`, transformations
- **Fresco** — Facebook, drawees, animated images (WebP, GIF)
- **Landscapist** — Coil/Glide/Fresco wrapper Compose

## 6. Material Design 3 (Material You)

### 6.1 Color Scheme
```kotlin
// Dynamic colors Android 12+
val colorScheme = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    dynamicLightColorScheme(context)
} else {
    lightColorScheme(
        primary = Color(0xFF6750A4),
        onPrimary = Color.White,
        primaryContainer = Color(0xFFEADDFF),
        secondary = Color(0xFF625B71),
        surface = Color(0xFFFFFBFE)
    )
}
```

### 6.2 Composants M3
- **NavigationBar** — bottom navigation, NavigationBarItem
- **NavigationRail** — tablette/large screen
- **TopAppBar** — `CenterAlignedTopAppBar`, `LargeTopAppBar`
- **BottomSheet** — `ModalBottomSheet`, `BottomSheetScaffold`
- **SearchBar** — `DockedSearchBar`, `ExpandedSearchBar`
- **DatePicker/TimePicker** — Material 3 pickers

## 7. Tests

### 7.1 Unit Tests (JUnit5 + MockK)
```kotlin
class UserViewModelTest {
    private val repository: UserRepository = mockk()
    private lateinit var viewModel: UserViewModel
    
    @BeforeEach
    fun setup() {
        MockKAnnotations.init(this)
        viewModel = UserViewModel(repository)
    }
    
    @Test
    fun `loadUsers emits success state`() = runTest {
        coEvery { repository.fetchUsers() } returns listOf(mockUser())
        viewModel.loadUsers()
        val state = viewModel.uiState.first { it is UiState.Success }
        assertInstanceOf(UiState.Success::class.java, state)
    }
}
```

### 7.2 UI Tests (Compose Testing)
```kotlin
@Test
fun testUserCardClick() {
    composeTestRule.setContent {
        UserCard(user = testUser, onUserClick = { /* assert */ })
    }
    composeTestRule.onNodeWithText("John Doe").assertIsDisplayed()
    composeTestRule.onNodeWithTag("user_card").performClick()
}
```

### 7.3 Screenshot Tests
- **Roborazzi** — `captureRoboImage` avec Compose
- **Paparazzi** — layout snapshots CI

## 8. Déploiement Play Store

### 8.1 Signing
```bash
# Keystore
keytool -genkey -v -keystore release.keystore -alias app -keyalg RSA -keysize 2048 -validity 10000

# Build APK/AAB
./gradlew bundleRelease  # Android App Bundle
./gradlew assembleRelease  # APK
```

### 8.2 Google Play Console
- **App Signing** — Play App Signing (clé upload + clé de signature)
- **Internal / Closed / Open Testing** — tracks graduels
- **In-app reviews** — `ReviewManager`, `ReviewInfo`
- **In-app updates** — `AppUpdateManager`, `IMMEDIATE` / `FLEXIBLE`
- **Firebase App Distribution** — distribution interne CI
- **Pre-launch reports** — Play Console → tests automatiques Google

### 8.3 CI/CD (GitHub Actions)
```yaml
- name: Build Release
  run: ./gradlew bundleRelease
- name: Sign & Upload to Play Store
  uses: r0adkll/upload-google-play@v1
  with:
    serviceAccountJson: ${{ secrets.PLAY_SERVICE_ACCOUNT }}
    packageName: com.example.app
    releaseFiles: app/build/outputs/bundle/release/app-release.aab
    track: internal
```

## 9. Pièges Courants

- **Memory leaks** — viewModelScope oublié, `collectAsState()` dans parent scope
- **ProGuard/R8** — règles manquantes → crash, réflexion cassée
- **Activity lifecycle** — recréation, configuration changes, `rememberSaveable`
- **Background limitations** — Doze Mode, App Standby Buckets, ANR watchdog
- **Android 14+ scoped storage** — `MediaStore`, `SAF`, `MANAGE_EXTERNAL_STORAGE` déprécié
- **API level compat** — `@RequiresApi`, `Build.VERSION.SDK_INT` checks
- **R8 optimization** — `-keep class` pour réflexion/DI, `@Keep` annotation
- **Multi-module issues** — namespace duplicates, R classes collision
- **64-bit requirement** — tous les NDK .so doivent avoir arm64-v8a