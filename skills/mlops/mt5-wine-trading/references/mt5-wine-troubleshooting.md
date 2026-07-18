# Dépannage MT5 sous Wine

Guide complet des erreurs rencontrées et leurs solutions.

## Erreurs Wine courantes

### 1. `ucrtbase.dll.crealf` non implémenté

**Contexte** : NumPy 2.x utilise des fonctions mathématiques C99 non disponibles dans l'implémentation Wine de `ucrtbase.dll`.

**Erreur complète** :
```
wine: Call from 00006FFFFF3FCF77 to unimplemented function ucrtbase.dll.crealf, aborting
wine: Unimplemented function ucrtbase.dll.crealf called at address 00006FFFFF3FCF77
```

**Solution définitive** :
```bash
export WINEPREFIX=~/.wine_mt5
WIN_PYTHON="$WINEPREFIX/drive_c/users/$USER/AppData/Local/Programs/Python/Python312/python.exe"

# Supprimer NumPy 2.x
wine "$WIN_PYTHON" -m pip uninstall -y numpy

# Installer NumPy 1.26.x (dernière version compatible Wine)
wine "$WIN_PYTHON" -m pip install "numpy==1.26.4"
```

**Vérification** :
```bash
wine "$WIN_PYTHON" -c "import numpy; print(numpy.__version__)"
# Doit afficher: 1.26.4
```

### 2. IPC Timeout (-10005)

**Contexte** : L'API MetaTrader5 Python communique avec le terminal via IPC (Inter-Process Communication). Si MT5 n'est pas prêt, la connexion échoue.

**Causes identifiées** :
1. MT5 pas encore démarré (démarrage très lent sous Wine)
2. MT5 crashé en arrière-plan
3. Plusieurs instances MT5 en conflit
4. Xvfb pas démarré ou crashé

**Diagnostic** :
```bash
# Vérifier si MT5 tourne
pgrep -f terminal64

# Vérifier Xvfb
pgrep Xvfb

# Vérifier les logs Wine
tail -f /tmp/mt5.log
```

**Solution robuste** :
```python
import MetaTrader5 as mt5
import time
import subprocess

def wait_mt5_ready(max_wait=120):
    """Attend que MT5 soit prêt avec retry."""
    for i in range(max_wait):
        try:
            if mt5.initialize():
                info = mt5.terminal_info()
                if info is not None:
                    print(f"MT5 prêt après {i}s")
                    return True
        except:
            pass
        
        if i % 10 == 0:
            print(f"Attente MT5... {i}s")
        time.sleep(1)
    
    return False

# Utilisation
if not wait_mt5_ready():
    print("MT5 pas prêt, redémarrage...")
    subprocess.run(["pkill", "-9", "-f", "terminal64"])
    time.sleep(5)
    # Relancer MT5...
```

### 3. MT5 démarre mais ne répond pas

**Symptôme** : `pgrep -f terminal64` retourne un PID, mais `mt5.initialize()` timeout.

**Cause** : MT5 sous Wine peut prendre 3-5 minutes à initialiser complètement son interface IPC.

**Solution** : Attendre plus longtemps et vérifier la présence de la fenêtre MT5 :

```python
import time
import subprocess

def start_mt5_and_wait():
    # Démarrer MT5
    env = os.environ.copy()
    env["WINEPREFIX"] = os.path.expanduser("~/.wine_mt5")
    env["DISPLAY"] = ":99"
    
    proc = subprocess.Popen(
        ["wine", MT5_PATH, "/skipupdate"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print(f"MT5 démarré (PID {proc.pid})")
    print("Attente initialisation (peut prendre 3-5 minutes)...")
    
    # Attendre jusqu'à 5 minutes
    for i in range(300):
        if not subprocess.run(["pgrep", "-f", "terminal64"], capture_output=True).returncode == 0:
            print("MT5 s'est arrêté")
            return False
        
        # Tester la connexion toutes les 10s
        if i % 10 == 0:
            try:
                if mt5.initialize():
                    print(f"MT5 prêt après {i}s")
                    return True
            except:
                pass
        
        time.sleep(1)
    
    return False
```

### 4. Display non disponible

**Erreur** :
```
err:winediag:nodrv_CreateWindow Application tried to create a window, but no driver could be loaded.
err:winediag:nodrv_CreateWindow L"Make sure that your display server is running and that its variables are set."
```

**Solution** : Toujours utiliser Xvfb :

```bash
# Méthode 1: xvfb-run (recommandé)
xvfb-run -a wine terminal64.exe

# Méthode 2: Xvfb manuel
Xvfb :99 -screen 0 1024x768x16 &
export DISPLAY=:99
wine terminal64.exe
```

**Note** : Sur les systèmes avec GPU NVIDIA, Xvfb peut afficher des warnings GBM mais fonctionne quand même :
```
src/nv_gbm.c:288: GBM-DRV error (nv_gbm_create_device_native): nv_common_gbm_create_device failed (ret=-1)
```
Ces warnings sont **normaux et sans conséquence**.

### 5. Erreur NTLM

**Erreur** :
```
err:winediag:ntlm_check_version ntlm_auth was not found. Make sure that ntlm_auth >= 3.0.25 is in your path.
err:ntlm:ntlm_LsaApInitializePackage no NTLM support, expect problems
```

**Impact** : Aucun pour MT5. L'authentification NTLM n'est pas utilisée par MT5.

**Solution** : Ignorer, ou installer winbind :
```bash
sudo apt install winbind
```

## Optimisations

### Réduire le temps de démarrage MT5

1. **Désactiver les mises à jour** : Toujours utiliser `/skipupdate`
2. **Mode portable** : Créer un raccourci vers `terminal64.exe /portable`
3. **Préfixe Wine léger** : Éviter d'installer trop de packages dans le préfixe MT5

### Améliorer la stabilité IPC

```python
# Dans le script Python Windows
import MetaTrader5 as mt5

# Augmenter le timeout IPC (si supporté)
# mt5.initialize(timeout=60000)  # 60s en ms

# Alternative: retry pattern
max_retries = 5
for attempt in range(max_retries):
    try:
        if mt5.initialize():
            break
    except Exception as e:
        print(f"Tentative {attempt + 1}/{max_retries} échouée: {e}")
        time.sleep(5)
```

## Checklist de démarrage

Avant de lancer un script d'extraction :

- [ ] Xvfb tourne (`pgrep Xvfb`)
- [ ] DISPLAY=:99 est exporté
- [ ] Aucune instance MT5 précédente (`pgrep -f terminal64` vide)
- [ ] WINEPREFIX est correctement défini
- [ ] Python Windows a numpy<2.0 installé
- [ ] Timeout suffisant (minimum 120s pour l'init MT5)
