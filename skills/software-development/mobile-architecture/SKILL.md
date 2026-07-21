---
name: mobile-architecture
description: Architecture mobile — MVVM, MVI, Clean Architecture, TCA, Redux, modularisation, DI, design patterns, offline-first
---

# Skill: Architecture Mobile

## Vue d'ensemble
Patterns architecturaux pour applications mobiles : MVVM, MVI, Clean Architecture, TCA (The Composable Architecture), Redux, modularisation par feature, injection de dépendances, et stratégies offline-first.

## 1. Patterns Architecturaux

### 1.1 MVVM (Model-View-ViewModel)
```swift
// iOS (SwiftUI) — MVVM natif
@Observable
final class UserViewModel {
    private let repository: UserRepository
    var users: [User] = []
    var error: Error?
    
    init(repository: UserRepository) {
        self.repository = repository
    }
    
    @MainActor
    func loadUsers() async {
        do {
            users = try await repository.fetchUsers()
        } catch {
            self.error = error
        }
    }
}

struct UserListView: View {
    @State private var viewModel = UserViewModel(repository: UserRepository())
    var body: some View {
        List(viewModel.users) { user in
            Text(user.name)
        }
        .task { await viewModel.loadUsers() }
    }
}
```

```kotlin
// Android (ViewModel + StateFlow)
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState<List<User>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<User>>> = _uiState.asStateFlow()
    
    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val users = repository.fetchUsers()
                _uiState.value = UiState.Success(users)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Erreur")
            }
        }
    }
}
```

### 1.2 MVI (Model-View-Intent)
```kotlin
// State sealed class
sealed interface UserIntent {
    data object LoadUsers : UserIntent
    data class SearchUsers(val query: String) : UserIntent
    data class SelectUser(val userId: String) : UserIntent
}

// ViewModel = state reducer
class UserViewModel : ViewModel() {
    private val _state = MutableStateFlow(UserState())
    val state: StateFlow<UserState> = _state.asStateFlow()
    
    fun process(intent: UserIntent) {
        when (intent) {
            UserIntent.LoadUsers -> loadUsers()
            is UserIntent.SearchUsers -> search(intent.query)
            is UserIntent.SelectUser -> selectUser(intent.userId)
        }
    }
    
    private fun loadUsers() {
        _state.update { it.copy(isLoading = true) }
        viewModelScope.launch {
            val users = repository.fetchUsers()
            _state.update { it.copy(isLoading = false, users = users) }
        }
    }
}
```

### 1.3 TCA (The Composable Architecture — iOS)
```swift
import ComposableArchitecture

@Reducer
struct UserFeature {
    @ObservableState
    struct State: Equatable {
        var users: [User] = []
        var isLoading = false
    }
    
    enum Action {
        case loadUsers
        case usersLoaded([User])
        case loadFailed(Error)
    }
    
    @Dependency(\.userClient) var userClient
    
    var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .loadUsers:
                state.isLoading = true
                return .run { send in
                    let users = try await userClient.fetchUsers()
                    await send(.usersLoaded(users))
                } catch: { error, send in
                    await send(.loadFailed(error))
                }
                
            case .usersLoaded(let users):
                state.isLoading = false
                state.users = users
                return .none
                
            case .loadFailed:
                state.isLoading = false
                return .none
            }
        }
    }
}
```

## 2. Clean Architecture

### 2.1 Couches
```
┌─────────────────────────────────┐
│         UI Layer (Presentation)  │ ← SwiftUI / Compose / Widgets
├─────────────────────────────────┤
│      Domain Layer (UseCases)     │ ← Business logic (pure Kotlin/Swift)
├─────────────────────────────────┤
│       Data Layer (Repository)    │ ← API + DB mappers
├─────────────────────────────────┤
│   External (API / DB / Platform) │ ← Retrofit, Room, CoreData
└─────────────────────────────────┘
```

### 2.2 Domain Layer (Pure logic, zéro dépendance framework)
```kotlin
// Domain — Entité
data class User(
    val id: String,
    val name: String,
    val email: String
)

// Domain — Use Case
class GetUsersUseCase(
    private val repository: UserRepository
) {
    suspend operator fun invoke(): Result<List<User>> {
        return try {
            Result.success(repository.fetchUsers())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Domain — Repository Interface
interface UserRepository {
    suspend fun fetchUsers(): List<User>
    suspend fun createUser(name: String, email: String): User
}
```

### 2.3 Data Layer
```kotlin
// Data — DTO
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    val name: String,
    val email: String
)

// Data — Repository Implementation
class UserRepositoryImpl(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {
    override suspend fun fetchUsers(): List<User> {
        val cached = dao.getAllUsers()
        return if (cached.isNotEmpty()) {
            cached.map { it.toDomain() }
        } else {
            val remote = api.getUsers().map { it.toEntity() }
            dao.insertAll(remote)
            remote.map { it.toDomain() }
        }
    }
}
```

## 3. Modularisation par Feature

### 3.1 Structure Multi-Module (Android)
```
app/
├── :app                      # Application shell (DI + navigation)
├── :core:ui                  # Composants UI partagés
├── :core:network             # Client HTTP, intercepteurs
├── :core:database            # Room, DAOs, migrations
├── :core:domain              # Entités, Use Cases (pure Kotlin)
├── :core:testing             # Mocks, test doubles
├── :feature:auth             # Login, register, forgot password
│   ├── :feature:auth:domain
│   ├── :feature:auth:data
│   └── :feature:auth:presentation
├── :feature:users            # User list, profiles
├── :feature:dashboard        # Dashboard, analytics
└── :feature:settings         # Settings, about
```

### 3.2 Structure Feature Layer (iOS SPM)
```
Sources/
├── App/
│   └── App.swift
├── Core/
│   ├── Networking/
│   ├── Database/
│   └── UI/
├── Features/
│   ├── Auth/
│   │   ├── AuthFeature.swift
│   │   ├── AuthView.swift
│   │   └── AuthClient.swift
│   ├── Users/
│   └── Dashboard/
└── Shared/
    └── Models/
```

### 3.3 Module Boundaries
```kotlin
// Règle stricte : feature X ne peut pas dépendre de feature Y
// Feature X → :core:domain ✓
// Feature X → :feature:Y ✗ (cross-feature coupling)
// Solution : interface partagée dans :core:domain ou événements
```

## 4. Injection de Dépendances

### 4.1 Hilt (Android)
```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides @Singleton
    fun provideOkHttp(): OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor())
        .build()
    
    @Provides @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit = Retrofit.Builder()
        .baseUrl(BuildConfig.API_URL)
        .client(client)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
}

@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUsersUseCase: GetUsersUseCase
) : ViewModel() { ... }
```

### 4.2 Swinject (iOS)
```swift
let container = Container()
container.register(UserRepository.self) { _ in UserRepositoryImpl() }
container.register(GetUsersUseCase.self) { r in
    GetUsersUseCase(repository: r.resolve(UserRepository.self)!)
}
container.register(UserViewModel.self) { r in
    UserViewModel(getUsersUseCase: r.resolve(GetUsersUseCase.self)!)
}
```

### 4.3 Factory (SwiftUI)
```swift
@Observable
final class AppDependencies {
    let userRepository: UserRepository = UserRepositoryImpl()
    let authRepository: AuthRepository = AuthRepositoryImpl()
    lazy var userViewModel = UserViewModel(repository: userRepository)
}

struct AppView: View {
    @State private var deps = AppDependencies()
    var body: some View {
        UserListView(viewModel: deps.userViewModel)
            .environment(\.authRepository, deps.authRepository)
    }
}
```

## 5. Offline-First Architecture

### 5.1 Stratégies
| Stratégie | Usage | Complexité |
|-----------|-------|------------|
| Cache-then-network | Affiche cache → rafraîchir | ★☆☆ |
| Network-only | Toujours connecté | ★☆☆ |
| Offline-first | DB locale, sync en background | ★★★ |
| Optimistic updates | UI update immédiat, rollback si échec | ★★★ |

### 5.2 Repository Pattern Offline
```swift
actor UserRepositoryImpl: UserRepository {
    private let remote: UserApi
    private let local: UserDatabase
    private let monitor: NetworkMonitor
    
    func fetchUsers() async throws -> [User] {
        if await monitor.isConnected {
            do {
                let users = try await remote.getUsers()
                try await local.saveUsers(users)
                return users
            } catch {
                return try await local.getAllUsers()
            }
        } else {
            return try await local.getAllUsers()
        }
    }
}
```

### 5.3 Sync Strategy
```kotlin
class SyncManager(
    private val api: UserApi,
    private val dao: UserDao
) {
    suspend fun sync() {
        // 1. Push pending changes (local → remote)
        val pending = dao.getPendingChanges()
        pending.forEach { change ->
            try {
                api.syncChange(change)
                dao.markSynced(change.id)
            } catch (e: Exception) {
                // Queue for retry
            }
        }
        
        // 2. Pull remote changes (remote → local)
        val lastSync = dao.getLastSyncTimestamp()
        val changes = api.getChanges(since = lastSync)
        dao.applyChanges(changes)
        dao.setLastSyncTimestamp(System.currentTimeMillis())
    }
}
```

## 6. Navigation Architecture

### 6.1 Deep Linking & Universal Links
```kotlin
// Android — Navigation Compose deep links
composable(
    route = "profile/{userId}",
    deepLinks = listOf(navDeepLink { uriPattern = "https://example.com/user/{userId}" })
)

// iOS — SwiftUI deep links
struct AppView: View {
    var body: some View {
        ContentView()
            .onOpenURL { url in
                guard url.host == "example.com" else { return }
                // Parse path → naviguer
            }
    }
}
```

### 6.2 Navigation State Machine
```swift
enum AppScreen: Hashable {
    case splash
    case onboarding
    case auth
    case home
    case profile(User.ID)
}

@Observable
final class NavigationState {
    var path: [AppScreen] = [.splash]
    
    func navigate(to screen: AppScreen) {
        path.append(screen)
    }
    
    func popToRoot() {
        path = [.home]
    }
}
```

## 7. Error Handling & Resilience

### 7.1 Result Pattern
```swift
enum AppError: LocalizedError {
    case networkError(Error)
    case serverError(statusCode: Int, message: String)
    case notFound
    case unauthorized
    case decodingError(Error)
    case unknown
    
    var errorDescription: String? {
        switch self {
        case .networkError: "Pas de connexion internet"
        case .serverError(_, let msg): msg
        case .notFound: "Élément introuvable"
        case .unauthorized: "Session expirée"
        case .decodingError: "Erreur de données"
        case .unknown: "Erreur inconnue"
        }
    }
}

typealias AppResult<T> = Result<T, AppError>
```

### 7.2 Retry & Backoff
```kotlin
suspend fun <T> retryWithBackoff(
    maxRetries: Int = 3,
    initialDelay: Long = 1000L,
    maxDelay: Long = 10000L,
    factor: Double = 2.0,
    block: suspend () -> T
): T {
    var currentDelay = initialDelay
    repeat(maxRetries) { attempt ->
        try {
            return block()
        } catch (e: Exception) {
            if (attempt == maxRetries - 1) throw e
            delay(currentDelay)
            currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelay)
        }
    }
    return block() // Last attempt
}
```

## 8. Pièges Courants

- **ViewModel lifecycle** — recréation après configuration change, `SavedStateHandle`
- **Cross-feature coupling** — feature A dépend de feature B = build time + coupling
- **Offline sync conflicts** — même objet modifié localement ET distamment → CRDT / last-write-wins
- **DI scope** — Singleton vs Feature scope, mémoire leak si scope trop large
- **State inflation** — trop d'état dans ViewModel, préférer des states composables
- **Unidirectional data flow violation** — ViewModel qui écrit dans UI qui écrit dans ViewModel
- **Too many UseCases** — un UseCase par méthode = boilerplate, grouper logiquement
- **Navigation state dupliqué** — ViewModel + NavigationContainer = deux sources de vérité
- **Coroutine scope leak** — `viewModelScope` oublié → opération en background après destruction
- **TCA performance** — trop d'actions dans un reducer → split en reducers enfants