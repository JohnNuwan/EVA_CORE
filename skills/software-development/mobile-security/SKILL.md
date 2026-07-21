---
name: mobile-security
description: Sécurité mobile — OWASP MASVS/MSTG, reverse engineering iOS/Android, jailbreak detection, SSL pinning, cryptographie, hardening
---

# Skill: Sécurité Mobile

## Vue d'ensemble
Sécurité des applications mobiles iOS et Android, couvrant l'OWASP Mobile Application Security Verification Standard (MASVS) v2, le pentest mobile, le reverse engineering, l'obfuscation, et le hardening.

## 1. OWASP MASVS v2 — Standards

### 1.1 Niveaux de Sécurité
| Niveau | Description | Usage |
|--------|-------------|-------|
| **MASVS-L1** | Sécurité standard | Apps sans données sensibles |
| **MASVS-L2** | Protection des données sensibles | Banking, santé, ID |
| **MASVS-R** | Anti-reverse engineering | DRM, jeux, protection IP |

### 1.2 Contrôles Clés (MASVS-STORAGE)
- **MSTG-STORAGE-1** — Données sensibles chiffrées au repos
- **MSTG-STORAGE-2** — Clipboard désactivé pour champs sensibles
- **MSTG-STORAGE-3** — Pas de logs contenant des données sensibles
- **MSTG-STORAGE-4** — Keychain (iOS) / EncryptedSharedPreferences (Android)
- **MSTG-STORAGE-6** — Screenshot blocking pour vues sensibles
- **MSTG-STORAGE-7** — Cache/WebView cache nettoyé après logout

## 2. iOS Security

### 2.1 Keychain
```swift
import Security

struct KeychainManager {
    static func save(key: String, data: Data) -> OSStatus {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            kSecUseDataProtectionKeychain as String: true  // iOS 12+
        ]
        SecItemDelete(query as CFDictionary)  // Supprime existant
        return SecItemAdd(query as CFDictionary, nil)
    }
    
    static func read(key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        return status == errSecSuccess ? result as? Data : nil
    }
}
```

### 2.2 Jailbreak Detection
```swift
func isJailbroken() -> Bool {
    // 1. Fichiers systèmes modifiés
    let jailbreakFiles = [
        "/Applications/Cydia.app",
        "/Applications/Sileo.app",
        "/Library/MobileSubstrate",
        "/bin/sh", "/usr/libexec/sftp-server",
        "/private/var/lib/apt", "/etc/apt"
    ]
    for path in jailbreakFiles where FileManager.default.fileExists(atPath: path) {
        return true
    }
    
    // 2. Sandbox violation test
    do {
        try "test".write(toFile: "/private/jailbreak.txt", atomically: true, encoding: .utf8)
        return true  // Permet d'écrire hors sandbox = jailbroken
    } catch {}
    
    // 3. Fork test (sandbox deny)
    if fork() != -1 { return true }
    
    return false
}
```

### 2.3 App Transport Security (ATS)
```xml
<!-- Info.plist — NE PAS désactiver complètement -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSExceptionDomains</key>
    <dict>
        <key>api.example.com</key>
        <dict>
            <key>NSIncludesSubdomains</key>
            <true/>
            <key>NSTemporaryExceptionMinimumTLSVersion</key>
            <string>TLSv1.3</string>
        </dict>
    </dict>
</dict>
```

## 3. Android Security

### 3.1 EncryptedSharedPreferences
```kotlin
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val prefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

prefs.edit().putString("api_token", token).apply()
```

### 3.2 Root Detection
```kotlin
fun isDeviceRooted(): Boolean {
    // Build.TAGS
    if (Build.TAGS?.contains("test-keys") == true) return true
    
    // Fichiers su
    val suPaths = listOf(
        "/sbin/su", "/system/bin/su", "/system/xbin/su",
        "/data/local/xbin/su", "/data/local/bin/su",
        "/system/sd/xbin/su", "/system/bin/failsafe/su",
        "/data/local/su"
    )
    for (path in suPaths) {
        if (File(path).exists()) return true
    }
    
    // Command su accessible
    return try {
        Runtime.getRuntime().exec(arrayOf("which", "su")).inputStream
            .bufferedReader().readText().isNotEmpty()
    } catch (e: Exception) {
        false
    }
}
```

### 3.3 SafetyNet / Play Integrity
```kotlin
val integrityManager = IntegrityManagerFactory.create(context)

// App Integrity API (remplace SafetyNet Attestation)
val tokenResponse = integrityManager.requestIntegrityToken(
    IntegrityTokenRequest.builder()
        .setCloudProjectNumber(projectNumber)
        .build()
)
// Vérifier côté serveur : nonce, ctsProfileMatch, basicIntegrity, deviceRecency
```

### 3.4 SSL Pinning (OkHttp)
```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .add("api.example.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")  // Backup
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

## 4. Network Security

### 4.1 TLS & Certificate Pinning
```swift
// iOS — TrustKit
let trustKitConfig = [
    kTSKSwizzleNetworkDelegates: false,
    kTSKPinnedDomains: [
        "api.example.com": [
            kTSKExpirationDate: "2026-12-01",
            kTSKPublicKeyHashes: [
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
                "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=",
            ]
        ]
    ]
]
TrustKit.initSharedInstance(withConfiguration: trustKitConfig)
```

### 4.2 Certificate Transparency (iOS 15+)
Utiliser `SecTrustSetOCSPResponse` et `SecTrustEvaluateWithError` pour certificate transparency.

## 5. Reverse Engineering — Pentest

### 5.1 iOS Pentest Toolkit
| Outil | Usage |
|-------|-------|
| **Frida** | Hook runtime, `frida-trace`, `frida-ps` |
| **Objection** | Bypass jailbreak, SSL pinning, dump keychain |
| **MachoView / Ghidra** | Analyse binaire .ipa, class-dump |
| **Needle** | Framework pentest iOS automatisé |
| **Burp Suite** | Proxy + Repeater, intercepter TLS |
| **Cycript** | Runtime injection Objective-C |

```bash
# Objection
objection --gadget "com.example.app" explore
  ios jailbreak disable
  ios sslpinning disable
  ios keychain dump
  ios pasteboard disable
```

### 5.2 Android Pentest Toolkit
| Outil | Usage |
|-------|-------|
| **Frida** | Hook, `Java.perform`, trace methods |
| **APKTool** | `apktool d app.apk`, reverse resources |
| **JADX / jadx-gui** | Décompilation bytecode → Java |
| **dex2jar** | Dalvik → JAR pour analyse |
| **Objection** | Bypass root, SSL pinning |
| **adb** | `adb shell`, `adb backup`, `adb install -g` |
| **MobSF** | Static + dynamic analysis automatisée |

```bash
# Décompilation
apktool d app.apk -o app_src
jadx-gui app.apk

# Frida hook Android
frida -U -f com.example.app -l bypass.js
```

## 6. Hardening & Obfuscation

### 6.1 Android ProGuard/R8
```
# proguard-rules.pro
-keep class com.example.app.data.** { *; }  # Data classes
-keepclassmembers class * implements java.io.Serializable { *; }
-dontwarn com.example.**
-optimizationpasses 5
-allowaccessmodification
-repackageclasses 'com.e.a'
-flattenpackagehierarchy
```

### 6.2 iOS Obfuscation
```swift
// Swift shield / ppiOS-Confuse
// 1. String encryption
static func decryptString(encrypted: [UInt8], key: [UInt8]) -> String {
    var decrypted: [UInt8] = []
    for (i, byte) in encrypted.enumerated() {
        decrypted.append(byte ^ key[i % key.count])
    }
    return String(bytes: decrypted, encoding: .utf8) ?? ""
}

// 2. Control flow flattening (compile-time)
// 3. Symbol obfuscation (Xcode post-build script)
```

### 6.3 Code Protection
- **Integrity checks** — `applicationInfo.sourceDir` SHA256 verification
- **Debug detection** — `android.os.Debug.isDebuggerConnected()`
- **Emulator detection** — Build.FINGERPRINT, Build.HARDWARE, IMEI patterns
- **Anti-Frida** — détection `frida-server`, port 27042 closed
- **Anti-Hooking** — `ptrace(PTRACE_TRACEME)` sur Linux
- **Resource encryption** — assets/assets chiffrés, decrypt at runtime

## 7. Biometrics & Auth

### 7.1 iOS (LocalAuthentication)
```swift
let context = LAContext()
context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: nil)
context.evaluatePolicy(
    .deviceOwnerAuthenticationWithBiometrics,
    localizedReason: "Authentifiez-vous pour accéder aux données"
) { success, error in
    if success { /* accès autorisé */ }
}
```

### 7.2 Android (BiometricPrompt)
```kotlin
val biometricPrompt = BiometricPrompt(
    this,
    executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
            // Accès autorisé
        }
    }
)

val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Authentification")
    .setSubtitle("Vérification d'identité")
    .setAllowedAuthenticators(
        BiometricManager.Authenticators.BIOMETRIC_STRONG or
        BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )
    .build()
```

## 8. Secure Storage & Cryptographie

### 8.1 Android — Android Keystore
```kotlin
val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
val keySpec = KeyGenParameterSpec.Builder(
    "secure_key",
    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
)
    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
    .setUserAuthenticationRequired(true)
    .setInvalidatedByBiometricEnrollment(true)
    .build()
keyGenerator.init(keySpec)
```

### 8.2 iOS — CryptoKit (iOS 13+)
```swift
import CryptoKit

let key = SymmetricKey(size: .bits256)
let sealedBox = try AES.GCM.seal(plaintext, using: key)
let ciphertext = sealedBox.combined  // nonce + ciphertext + tag
let opened = try AES.GCM.open(sealedBox, using: key)
```

### 8.3 API Key Protection
- **Envoy proxy / App Attest** — pas de clés côté client
- **OAuth 2.0 PKCE** — Proof Key for Code Exchange
- **Device attestation** — App Attest (iOS 14+) / Play Integrity
- **Nonce** — un par requête, côté serveur vérifie

## 9. Pièges Courants

- **Hardcoded secrets** — strings dans le binaire reverse-engineerables
- **NSLog / Logcat** — logs en production contenant des tokens
- **WebView JavaScript bridge** — injection XSS → RCE si non isolé
- **Clipboard accès** — `UIPasteboard` / `ClipboardManager` accessible en background
- **Backup vulnéré** — `android:allowBackup=true` + `NSFileProtectionNone`
- **Deep link hijacking** — `android:autoVerify=true` manquant, Universal Links vérification
- **SharedPreferences non chiffrées** — `MODE_PRIVATE` ≠ chiffré
- **Certificate pinning bypass** — root CA proxy, Frida, VirtualXposed
- **Timing attacks** — constant-time comparison pour tokens
- **URL credential extraction** — `Credentials` dans URL = leak via logs/referrer