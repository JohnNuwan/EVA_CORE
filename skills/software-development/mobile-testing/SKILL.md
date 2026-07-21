---
name: mobile-testing
description: Tests mobiles — unitaires, UI, intégration, E2E, snapshot, performance, screenshot testing, CI pipelines iOS/Android/RN/Flutter
---

# Skill: Tests Mobiles (iOS / Android / Cross-Platform)

## Vue d'ensemble
Stratégie de test pour applications mobiles couvrant les tests unitaires, UI, intégration (API/db), E2E, screenshot regression, performance, et intégration CI/CD pour toutes les plateformes.

## 1. Stratégie de Test (Test Pyramid)

### 1.1 Pyramide Mobile
```
         /\        E2E (Maestro / Detox / XCUITest / Espresso)
        /  \       5-10% — parcours critiques
       /    \
      /      \     UI & Screenshot Tests  15-20%
     /        \    (Compose Testing / SwiftUI Previews / RN Testing Library)
    /          \
   /____________\  Integration Tests      25-30%
  /              \  (ViewModel + Repository + DB + API mocks)
 /________________\
/  Unit Tests (40-50%)  — Modèles, logique métier, validations, utils
```

## 2. iOS — XCTest & XCUITest

### 2.1 XCTest (Unit Tests)
```swift
@testable import App
import XCTest

final class UserViewModelTests: XCTestCase {
    var sut: UserViewModel!
    var mockAPI: MockAPIClient!
    
    override func setUp() {
        mockAPI = MockAPIClient()
        sut = UserViewModel(api: mockAPI)
    }
    
    func testLoadUsersSuccess() async throws {
        mockAPI.stubFetchUsers(result: [.mock])
        await sut.loadUsers()
        
        XCTAssertEqual(sut.state, .loaded([.mock]))
        XCTAssertFalse(sut.isLoading)
    }
    
    func testEmptyState() async throws {
        mockAPI.stubFetchUsers(result: [])
        await sut.loadUsers()
        
        guard case .loaded(let users) = sut.state else {
            return XCTFail("Expected loaded state")
        }
        XCTAssertTrue(users.isEmpty)
    }
}
```

### 2.2 XCUITest (UI Tests)
```swift
final class LoginFlowTests: XCTestCase {
    let app = XCUIApplication()
    
    override func setUp() {
        continueAfterFailure = false
        app.launch()
    }
    
    func testSuccessfulLogin() {
        let emailField = app.textFields["email"]
        emailField.tap()
        emailField.typeText("user@example.com")
        
        let passwordField = app.secureTextFields["password"]
        passwordField.tap()
        passwordField.typeText("password123")
        
        app.buttons["Se connecter"].tap()
        
        let dashboard = app.staticTexts["Dashboard"]
        XCTAssertTrue(dashboard.waitForExistence(timeout: 5))
    }
    
    func testLoginShowsError() {
        app.textFields["email"].tap()
        app.textFields["email"].typeText("invalid")
        app.buttons["Se connecter"].tap()
        
        let errorLabel = app.staticTexts["Email invalide"]
        XCTAssertTrue(errorLabel.waitForExistence(timeout: 2))
    }
}
```

### 2.3 Snapshot Testing (SwiftSnapshotTesting)
```swift
import SnapshotTesting

final class UserCardSnapshotTests: XCTestCase {
    func testUserCardLight() {
        let view = UserCard(user: .mock)
        assertSnapshot(of: view, as: .image(on: .iPhone16Pro))
    }
    
    func testUserCardDark() {
        let view = UserCard(user: .mock)
            .environment(\.colorScheme, .dark)
        assertSnapshot(of: view, as: .image(on: .iPhone16Pro))
    }
    
    func testUserCardLocalized() {
        let view = UserCard(user: .mock)
            .environment(\.locale, Locale(identifier: "fr"))
        assertSnapshot(of: view, as: .image(on: .iPhone16Pro))
    }
}
```

## 3. Android — JUnit5 + Compose Testing

### 3.1 Unit Tests (MockK)
```kotlin
class UserViewModelTest {
    private val repository: UserRepository = mockk()
    private val savedStateHandle: SavedStateHandle = mockk()
    private lateinit var viewModel: UserViewModel
    
    @BeforeEach
    fun setup() {
        MockKAnnotations.init(this)
        every { savedStateHandle.get<Any>(any()) } returns null
        viewModel = UserViewModel(repository, savedStateHandle)
    }
    
    @Test
    fun `loadUsers - success state`() = runTest {
        val expectedUsers = listOf(testUser)
        coEvery { repository.fetchUsers() } returns expectedUsers
        
        viewModel.loadUsers()
        
        val state = viewModel.uiState.value
        assertIs<UiState.Success<List<User>>>(state)
        assertEquals(expectedUsers, state.data)
    }
    
    @Test
    fun `loadUsers - error state`() = runTest {
        coEvery { repository.fetchUsers() } throws IOException("Network error")
        
        viewModel.loadUsers()
        
        val state = viewModel.uiState.value
        assertIs<UiState.Error>(state)
    }
}
```

### 3.2 Compose UI Tests
```kotlin
@Test
fun testUserCardClick() {
    composeTestRule.setContent {
        UserCard(
            user = testUser,
            onUserClick = { clickedUser = it }
        )
    }
    
    composeTestRule
        .onNodeWithText("John Doe")
        .assertIsDisplayed()
    
    composeTestRule
        .onNodeWithTag("user_card")
        .performClick()
    
    assertEquals(testUser, clickedUser)
}

@Test
fun testLoadingState() {
    composeTestRule.setContent {
        UserList(
            state = UiState.Loading,
            onRetry = {}
        )
    }
    
    composeTestRule
        .onNodeWithTag("loading_indicator")
        .assertExists()
}
```

### 3.3 Screenshot (Roborazzi)
```kotlin
@Test
fun captureUserCard() {
    composeTestRule.setContent {
        EATTheme { UserCard(user = testUser) }
    }
    composeTestRule.onRoot().captureRoboImage("user_card.png")
}
```

## 4. React Native Testing

### 4.1 Unit Tests
```tsx
import { renderHook, act } from '@testing-library/react-native';
import useCounter from '../useCounter';

test('counter increments', () => {
  const { result } = renderHook(() => useCounter());
  act(() => result.current.increment());
  expect(result.current.count).toBe(1);
});

// MSW (Mock Service Worker)
import { server } from '../mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('loads users', async () => {
  server.use(
    http.get('/api/users', () => {
      return HttpResponse.json([{ id: 1, name: 'Alice' }]);
    })
  );
  const { findByText } = render(<UserList />);
  expect(await findByText('Alice')).toBeTruthy();
});
```

### 4.2 Component Tests
```tsx
test('fires callback on press', () => {
  const onPress = jest.fn();
  const { getByTestId } = render(
    <UserCard user={mockedUser} onPress={onPress} />
  );
  fireEvent.press(getByTestId('user-card'));
  expect(onPress).toHaveBeenCalledWith(mockedUser.id);
});
```

## 5. Flutter Testing

### 5.1 Unit Tests
```dart
void main() {
  group('UserRepository', () {
    late MockAPIClient mockApi;
    late UserRepository repo;
    
    setUp(() {
      mockApi = MockAPIClient();
      repo = UserRepository(api: mockApi);
    });
    
    test('returns users from API', () async {
      when(() => mockApi.getUsers()).thenAnswer((_) async => [testUser]);
      final users = await repo.fetchUsers();
      expect(users, hasLength(1));
      expect(users.first.name, 'Alice');
    });
    
    test('throws on network error', () async {
      when(() => mockApi.getUsers()).thenThrow(TimeoutException('timeout'));
      expect(() => repo.fetchUsers(), throwsA(isA<TimeoutException>()));
    });
  });
}
```

### 5.2 Widget Tests
```dart
void main() {
  testWidgets('UserCard renders correctly', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: UserCard(
            user: testUser,
            onTap: () {},
          ),
        ),
      ),
    );
    
    expect(find.text('Alice'), findsOneWidget);
    expect(find.text('alice@example.com'), findsOneWidget);
  });
  
  testWidgets('UserCard tap fires callback', (tester) async {
    var tapped = false;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: UserCard(
            user: testUser,
            onTap: () => tapped = true,
          ),
        ),
      ),
    );
    
    await tester.tap(find.byType(UserCard));
    expect(tapped, isTrue);
  });
}
```

### 5.3 Golden Tests (Screenshot)
```dart
testWidgets('UserCard golden test light', (tester) async {
  await tester.pumpWidget(MaterialApp(home: UserCard(user: testUser)));
  await expectLater(find.byType(UserCard), matchesGoldenFile('user_card_light.png'));
});
```

## 6. E2E Testing

### 6.1 Detox (React Native)
```bash
# Installation
npm install --save-dev detox
detox init

# Configuration .detoxrc.js
{
  "testRunner": "jest",
  "apps": {
    "ios.release": { "type": "ios.app", "binaryPath": "ios/build/Build/Products/Release-iphonesimulator/App.app" }
  },
  "devices": {
    "simulator": { "type": "ios.simulator", "device": { "type": "iPhone 16 Pro" } }
  },
  "configurations": {
    "ios.sim.release": { "device": "simulator", "app": "ios.release" }
  }
}
```

```js
describe('Login Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  it('should log in successfully', async () => {
    await element(by.id('email')).typeText('user@example.com');
    await element(by.id('password')).typeText('password123');
    await element(by.id('login-button')).tap();
    await expect(element(by.id('dashboard'))).toBeVisible();
  });
});
```

### 6.2 Maestro (Cross-Platform)
```yaml
# login.yaml
appId: com.example.app
---
- launchApp
- tapOn: "email"
- inputText: "user@example.com"
- tapOn: "Connexion"
- assertVisible: "Tableau de bord"
- takeScreenshot: "login_success"
```

### 6.3 Kaspresso (Android E2E)
```kotlin
@Test
fun loginTest() = run {
    step("Open login screen") {
        screen {
            loginButton { isVisible(); click() }
        }
    }
    step("Enter credentials") {
        screen {
            emailField { typeText("user@example.com") }
            loginButton { click() }
        }
    }
    step("Verify dashboard") {
        screen {
            dashboardTitle { isVisible(); hasText("Tableau de bord") }
        }
    }
}
```

## 7. Performance Testing

### 7.1 iOS — XCTMetrics
```swift
func testScrollPerformance() throws {
    let metrics: [XCTMetric] = [
        XCTClockMetric(),
        XCTMemoryMetric(),
        XCTCPUMetric(),
        XCTStorageMetric()
    ]
    let measureOptions = XCTMeasureOptions.default
    measure(metrics: metrics, options: measureOptions) {
        scrollThroughList()
    }
}
```

### 7.2 Android — Macrobenchmark
```kotlin
@ExperimentalBaselineProfilesApi
@Test
fun startup() = benchmarkRule.measureRepeated(
    packageName = "com.example.app",
    metrics = listOf(StartupTimingMetric()),
    iterations = 10,
    startupMode = StartupMode.COLD,
) {
    pressHome()
    startActivityAndWait(Intent().setClassName("com.example.app", "com.example.app.MainActivity"))
}
```

### 7.3 Flutter — DevTools
```bash
flutter run --profile
# DevTools → Performance → frame rendering graph
# Check: jank (frame > 16ms), shader compilation, rebuild counts
```

## 8. CI Integration

### 8.1 GitHub Actions — iOS Tests
```yaml
- name: Tests iOS
  run: |
    xcodebuild test \
      -scheme App \
      -destination 'platform=iOS Simulator,name=iPhone 16 Pro' \
      -resultBundlePath TestResults.xcresult \
      | xcbeautify
- name: Upload Results
  uses: kishikawakatsumi/xcresulttool@v1
  with:
    path: TestResults.xcresult
```

### 8.2 GitHub Actions — Android Tests
```yaml
- name: Unit Tests
  run: ./gradlew testDebugUnitTest
- name: UI Screenshot Tests
  run: ./gradlew verifyRoborazziDebug
- name: Upload Reports
  uses: actions/upload-artifact@v4
  with:
    name: test-reports
    path: app/build/reports/
```

## 9. Pièges Courants

- **Timing** — `waitForExistence` / `pumpAndSettle` nécessaires pour animations asynchrones
- **Locale-sensitive** — les snapshots diffèrent entre locales (formats dates, langues)
- **Xcode Cloud Test** — simulator unique, pas de parallélisation native
- **Android test orchestrator** — `ANDROIDX_TEST_ORCHESTRATOR_ENABLED=true` pour isolation
- **Flipper in tests** — Flipper désactivé en test (env `FLIPPER_ENABLED=0`)
- **Roborazzi CI** — nécessite un DPI/écran cohérent (GitHub Actions OK)
- **Snapshot flakiness** — flou, antialiasing, font diff → `precision: 0.99` tolérance
- **Detox iOS** — builds lents (20-40 min), cache `ios/build/` dans CI
- **MockWebServer** — reset entre tests, sinon états partagés
- **Async test timeouts** — `@Test(timeout = 5000)` / `XCTestCase.defaultTestSuite` timeout