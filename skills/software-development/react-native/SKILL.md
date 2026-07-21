---
name: react-native
description: Développement cross-platform React Native — Expo, RN CLI, navigation, state management, modules natifs, perf, déploiement
---

# Skill: React Native (Cross-Platform)

## Vue d'ensemble
Développement mobile cross-platform avec React Native, couvrant les frameworks Expo & RN CLI, la navigation, la gestion d'état, les modules natifs, l'optimisation des performances et le déploiement iOS/Android.

## 1. Frameworks & Setup

### 1.1 Expo vs RN CLI
| Critère | Expo (SDK 52+) | RN CLI |
|---------|---------------|--------|
| Setup | Zero config | Xcode + Android Studio |
| OTA Updates | Built-in (EAS Update) | CodePush/Self-hosted |
| Native Modules | Expo Modules API / Dev Client | React Native Turbo Modules |
| App Store Builds | EAS Build | Fastlane + manual |
| Debugging | Expo Dev Tools | Hermes + Flipper |
| **Recommandé** | **Nouveaux projets** | **Modifications natives lourdes** |

### 1.2 Setup Projet
```bash
# Expo (recommended)
npx create-expo-app@latest MyApp --template
npx expo start  # Dev server

# RN CLI (legacy)
npx @react-native-community/cli init MyApp
cd ios && pod install
npx react-native run-ios

# Expo avec modifs natives
npx create-expo-app@latest MyApp
npx expo run:ios  # Ouvre le projet Xcode complet
```

## 2. Navigation

### 2.1 React Navigation 7
```tsx
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

type RootStackParamList = {
  Home: undefined;
  Profile: { userId: string };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerStyle: { backgroundColor: '#tomato' } }}>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Profile" component={ProfileScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

### 2.2 Navigation Patterns
- **Native Stack** — `createNativeStackNavigator` (meilleures perfs)
- **Bottom Tabs** — `createBottomTabNavigator` avec badges/animation
- **Drawer** — `createDrawerNavigator` avec gesture handler
- **Material Top Tabs** — swipeable tabs, `lazy: true`
- **Deep Linking** — `linking.config.screens`, Universal Links / App Links

## 3. État & State Management

### 3.1 Options
```tsx
// Zustand (recommandé)
import { create } from 'zustand';

interface UserStore {
  users: User[];
  loading: boolean;
  fetchUsers: () => Promise<void>;
}

const useUserStore = create<UserStore>((set) => ({
  users: [],
  loading: false,
  fetchUsers: async () => {
    set({ loading: true });
    const users = await api.getUsers();
    set({ users, loading: false });
  },
}));

// TanStack Query (server state)
import { useQuery } from '@tanstack/react-query';

function UserList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => api.getUsers(),
    staleTime: 5 * 60 * 1000,  // 5 min cache
  });
}
```

### 3.2 Patterns État
| Library | Usage | Idéal pour |
|---------|-------|-----------|
| Zustand | Store global simple | UI state, panier |
| TanStack Query | Cache serveur | API data, mutations |
| Jotai | Atoms atomiques | Formulaires, toggles |
| Redux Toolkit | Store complexe | Legacy, équipes |
| MMKV | Persistance rapide | AsyncStorage remplacement |

## 4. UI & Theming

### 4.1 Styling
```tsx
// StyleSheet (RN natif)
import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#fff',
  },
  card: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,  // Android
  },
});

// NativeWind (Tailwind pour RN)
// <View className="flex-1 p-4 bg-white">
```

### 4.2 Frameworks UI
- **React Native Paper** — Material Design 3 components
- **NativeBase** — composants modulaires
- **Tamagui** — compilateur CSS-in-JS + design system
- **Restyle** (Shopify) — theme type-safe
- **Unistyles** — styles réactifs, performants

## 5. Modules Natifs & Bridge

### 5.1 Turbo Modules (Fabric - New Architecture)
```kotlin
// Android — MyModule.kt
@ReactModule(name = MyModule.NAME)
class MyModule(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {
    override fun getName() = NAME
    
    @ReactMethod
    fun doSomething(param: String, promise: Promise) {
        try {
            val result = NativeService.process(param)
            promise.resolve(result)
        } catch (e: Exception) {
            promise.reject("ERROR", e.message)
        }
    }
    
    companion object {
        const val NAME = "MyModule"
    }
}
```

### 5.2 Expo Modules API
```swift
// iOS — MyModule.swift
import ExpoModulesCore

public class MyModule: Module {
    public func definition() -> ModuleDefinition {
        Name("MyModule")
        
        Function("doSomething") { (param: String) -> String in
            return try NativeService.process(param)
        }
        
        View(MyView.self) {
            Prop("color") { (view: MyView, color: UIColor) in
                view.backgroundColor = color
            }
        }
    }
}
```

### 5.3 Native Modules Clés
- **react-native-camera** / `expo-camera` — caméra, barcode scanning
- **react-native-maps** / `expo-location` — cartes, géolocalisation
- **react-native-reanimated** — animations UI thread (60fps)
- **react-native-gesture-handler** — gestures, pan/pinch/swipe
- **react-native-blur** / `expo-blur` — effets de flou
- **react-native-svg** — rendu SVG natif
- **react-native-webview** — WebView intégré

## 6. Performance

### 6.1 Optimisations Clés
```tsx
// Hermes Engine (JavaScript engine optimisé)
// activé par défaut dans RN 0.70+

// Fast Refresh — hot reload préservant l'état
// Memoization
const ExpensiveComponent = React.memo(({ data }: Props) => {
  return <Text>{data.name}</Text>;
});

// useMemo / useCallback
const sortedList = useMemo(() => 
  data.sort((a, b) => a.name.localeCompare(b.name)),
  [data]
);

// FlatList optimisé
<FlatList
  data={items}
  renderItem={renderItem}
  keyExtractor={item => item.id}
  windowSize={10}
  maxToRenderPerBatch={10}
  removeClippedSubviews={true}
  initialNumToRender={7}
/>
```

### 6.2 Profilage
- **React DevTools** — profiler components
- **Flipper** — réseau, logs, React DevTools
- **Expo DevTools** — metro bundler, network, debug
- **Hermes Profiler** — `.cpuprofile` pour Chrome DevTools
- **Performance Monitor** — FPS, JS thread, UI thread

### 6.3 Bundle Size
- **Metro bundler** — tree shaking, `__DEV__` dead code
- **Code splitting** — lazy loading routes (Expo Router)
- **Assets** — compress PNG, utiliser SVG, `expo-optimize`
- **Native modules** — importer seulement ce qui est utilisé

## 7. Tests

### 7.1 Testing Library
```tsx
import { render, fireEvent } from '@testing-library/react-native';

test('should increment counter', () => {
  const { getByText } = render(<Counter />);
  const button = getByText('Incrémenter');
  fireEvent.press(button);
  expect(getByText('1')).toBeTruthy();
});
```

### 7.2 E2E (Detox / Maestro)
```yaml
# Maestro flow
appId: com.example.app
---
- launchApp
- tapOn: "Connexion"
- inputText: "user@example.com" into: "email"
- tapOn: "Se connecter"
- assertVisible: "Dashboard"
```

## 8. Déploiement

### 8.1 EAS (Expo Application Services)
```bash
eas build --platform ios       # Build iOS
eas build --platform android   # Build Android
eas submit --platform ios      # Upload App Store Connect
eas submit --platform android  # Upload Play Console
eas update --branch production # OTA Update
```

### 8.2 CodePush / EAS Update
```tsx
import * as Updates from 'expo-updates';

async function checkForUpdate() {
  const update = await Updates.checkForUpdateAsync();
  if (update.isAvailable) {
    await Updates.fetchUpdateAsync();
    await Updates.reloadAsync();
  }
}
```

### 8.3 CI/CD (GitHub Actions)
```yaml
- name: EAS Build
  run: npx eas build --platform all --non-interactive
  env:
    EXPO_TOKEN: ${{ secrets.EXPO_TOKEN }}
```

## 9. Pièges Courants

- **Bridge vs JSI** — New Architecture (Fabric/TurboModules) = breaking changes pour les libs non migrées
- **Hermes** — `Proxy` non supporté, `Array.from` limité, attention aux polyfills
- **Expo custom native modules** — nécessite `expo run:ios`/`expo run:android` (dev build)
- **KeyboardAvoidingView** — buggé sur Android, préférer `react-native-keyboard-aware-scroll-view`
- **FlatList inside ScrollView** — VirtualizationList conflit, définir `nestedScrollEnabled`
- **iOS 17+** — `UIViewControllerHierarchyInconsistency` avec `react-native-screens`
- **Android 14+** — `PendingIntent` mutability → `FLAG_IMMUTABLE` / `FLAG_MUTABLE`
- **Metro cache** — `npx react-native start --reset-cache` après mises à jour de libs
- **Apple Silicon** — `npx pod-install` pour `ffi`