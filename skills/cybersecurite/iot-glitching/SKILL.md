---
name: iot-glitching
title: "Glitching / Fault Injection — Voltage, Clock, EM"
description: "Guide complet pour les attaques par injection de fautes (fault injection) sur les dispositifs IoT : glitching de tension (VCC), glitching d'horloge (clock), injection électromagnétique (EM). Couvre les équipements (ChipWhisperer, CW-Lite, PicoScope), les techniques de déclenchement, l'effet sur les Secure Boot, et la récupération de clés cryptographiques."
category: cybersecurite
---

# Glitching / Fault Injection — Voltage, Clock, EM

## Vue d'Ensemble

Le glitching (injection de fautes) consiste à perturber intentionnellement le fonctionnement normal d'un microcontrôleur pour contourner ses protections. En injectant des anomalies très courtes (ns-µs) sur l'alimentation, l'horloge ou via un champ EM, on peut corrompre une instruction, sauter une vérification de sécurité, ou révéler des données protégées.

### Objectifs
- Contourner Secure Boot (sauter la vérification de signature)
- Bypasser les protections de lecture flash (RDP, OTP)
- Extraire des clés cryptographiques (AES, RSA lors de l'exécution)
- Forcer le passage dans un état non autorisé (debug mode)
- Révéler des chemins de code cachés (fault-based test)

---

## Types de Glitching

### Voltage Glitching (VCC Glitch)
Principe : baisser la tension d'alimentation très brièvement pendant une opération sensible.

```
VCC normal ────┬───┬───┬───┬───┬───
               │   │   │   │   │
Glitch ────────┘   └───┘   └───┘
                  ↓ VCC
             (nanosecondes)
```

**Équipement** :
- ChipWhisperer (CW1173, CW-Lite, CW-Pro)
- MOSFET + FPGA (glitch custom)
- PicoScope + AWG (générateur de signaux)
- Raspberry Pi Pico + transistor (DIY approach)

### Clock Glitching
Principe : injecter une impulsion d'horloge supplémentaire (ou sauter un cycle) pour corrompre le pipeline CPU.

```
Horloge normale ──┬──┬──┬──┬──┬──┬──┬──┬──
                  │  │  │  │  │  │  │  │  │
Glitch ───────────┘  └──┘  └──┘  └──┘
                 ↑ cycle supplémentaire
```

**Équipement** :
- ChipWhisperer CWLite (clock glitch natif)
- FPGA avec PLL (phase-locked loop)
- Signal generator avec modulation de phase

### EM Glitching (Electromagnetic Fault Injection)
Principe : générer une impulsion EM puissante à un endroit précis du die pour corrompre une instruction.

**Équipement** :
- EM probe (coil cuivre + ferrite core)
- Pulse generator (HV, 500V+)
- XYZ table de positionnement micrométrique
- ChipShouter / EM-FI (NewAE)
- Oscilloscope haute vitesse (1GS/s+)

---

## Outils Essentiels

### Kits Professionnels
| Kit | Prix | Capacités |
|-----|------|-----------|
| **ChipWhisperer Lite (CW1173)** | ~$300 | Voltage + clock glitch, 4x trigger, 20ns |
| **ChipWhisperer Pro (CW1200)** | ~$3000 | + EM, side-channel, 4 voies, 1GS/s |
| **ChipShouter (NewAE)** | ~$800 | EM pulse, 500V, portable |
| **Riscure Inspector** | ~$50k | Pro, full automation, AI-assisted |
| **Lecroy/PicoScope** | ~$500+ | Scope + AWG combo |

### DIY / Low Cost
| Composant | Usage |
|-----------|-------|
| **Raspberry Pi Pico + FET** | Voltage glitch simple (10-100ns) |
| **Arduino Due + MOSFET** | Clock glitch, 84MHz |
| **AD9833 + DDS** | Clock generation + glitch |
| **IRF520 / IRFZ44N** | MOSFET pour voltage glitch |
| **Coil EM** | 5-10 tours fil 0.2mm sur ferrite |
| **Flyback transformer** | HV pulse pour EM (dangereux) |

### Logiciels
| Outil | Usage |
|-------|-------|
| `ChipWhisperer` (Python) | Framework complet, capture + glitch + side-channel |
| `Jupyter Notebook` | Analyse des résultats, sweep automation |
| `PulseView` / `sigrok` | Trigger timing, mesure précise |
| `PicoScope SDK` | Automatisation PicoScope pour glitch |
| `OpenADC` | Capture analogique (ChipWhisperer) |

---

## Méthodologie

### Phase 1 : Setup et Calibration

#### ChipWhisperer Lite Setup
```python
# Installation
pip install chipwhisperer

# Setup basic capture
import chipwhisperer as cw
scope = cw.scope()
scope.gain.gain = 25         # Amplification ADC
scope.adc.samples = 1000     # Nombre d'échantillons
scope.adc.offset = 0         # Offset ADC
scope.adc.basic_mode = "rising_edge"

# Configuration glitch
scope.glitch.clk_src = "clkgen"    # Clock source
scope.glitch.repeat = 5             # Nombre de glitches
scope.glitch.width = 20             # Largeur (ns)
scope.glitch.offset = 100           # Décalage (ns)
scope.glitch.ext_offset = 0
scope.glitch.output = "clock_xor"   # Mode glitch
```

#### Calibration du Trigger
```python
# Trouver le bon moment pour glitcher
# Utiliser un GPIO du device pour signaler une opération sensible
# (ex: vérification de signature, boucle de déchiffrement)

# 1. Setup trigger sur l'oscilloscope
# 2. Observer le signal de l'opération cible
# 3. Mesurer :
#    - Décalage entre le trigger et l'opération
#    - Durée de l'opération
#    - Fenêtre temporelle pour la faute
```

### Phase 2 : Recherche de Paramètres (Sweep)

```python
# Le glitch est un processus probabiliste : il faut balayer
# plusieurs paramètres pour trouver la fenêtre de vulnérabilité

# Paramètres à balayer :
# 1. Offset — décalage temporel du glitch (ns → µs)
# 2. Width — largeur du glitch (ns → quelques ns)
# 3. Repeat — nombre d'impulsions (1-50)
# 4. Ext offset — offset externe lié à un trigger

# Exemple de sweep
for offset in range(0, 1000, 10):      # 0-1000ns par pas de 10
    for width in range(5, 50, 5):      # 5-50ns par pas de 5
        scope.glitch.offset = offset
        scope.glitch.width = width
        
        # Envoyer reset + trigger
        scope.io.pio = 'low'
        time.sleep(0.1)
        scope.io.pio = 'high'
        
        # Lire le résultat
        # Succès = boot bypassé
        # Reset = device reboot
        # Hang = device bloqué
```

### Phase 3 : Bypass de Secure Boot

```python
# Cible classique : boucle de vérification de signature
# while(verify_signature(firmware) != OK) { reset(); }
# On veut sauter l'instruction juste APRÈS la comparaison

# 1. Identifier le moment de la vérification
#    - GPIO du device qui pulse pendant la vérification
#    - Consommation de courant (mesure de shunt)
#    - Sortie UART (debug messages)

# 2. Synchroniser le glitch
#    - Trigger sur le début de la vérification
#    - Glitcher pendant l'instruction de comparaison (CMP, BNE)

# 3. Vérifier le succès :
#    - Le device boot (LED allumée, service réseau)
#    - Accès shell via UART
#    - Flash dumpable via JTAG/SWD

# Taux de succès typique : 0.1% - 10%
# → Automatiser des milliers de tentatives
```

### Phase 4 : Analyse des Résultats

```python
# Catégoriser les résultats :
# - SUCCESS = bypass obtenu (device boot normal malgré firmware invalide)
# - RESET = device a rebooté (glitch trop tôt = reset)
# - HANG = device bloqué (glitch à un mauvais endroit)
# - NO_EFFECT = glitch trop tard ou trop faible

# Visualisation
import matplotlib.pyplot as plt
plt.scatter(offsets, widths, c=results)
plt.xlabel('Offset (ns)')
plt.ylabel('Width (ns)')
plt.colorbar(label='Result: 0=reset, 1=hang, 2=success')
```

---

## Techniques Avancées

### EM Glitch sur Boîtier (Through Package)
```bash
# Avantage : pas besoin de déprotéger le die
# Désavantage : puissance plus élevée nécessaire

# Positionnement :
# 1. Placer la sonde EM à 1-2mm au-dessus du die
# 2. Balayer la surface (XYZ), trouver le point sensible
# 3. Tirer des impulsions HV (500-1000V, 10-100ns)
# 4. La sonde EM peut être déplacée sous un microscope

# Setup EM pulse :
#   Pulse generator → HV amplifier → EM probe → device
#   Trigger sur l'opération cible
#   Délai variable entre trigger et pulse
```

### Double Glitch (Voltage + Clock)
```python
# Combiner les deux types pour plus d'efficacité
# 1. Voltage glitch pour désactiver temporairement
#    le régulateur interne du SoC
# 2. Clock glitch pendant la fenêtre de vulnérabilité
#    pour corrompre l'instruction

scope.glitch.clk_src = "clkgen"
scope.glitch.output = "clock_xor"
# + voltage glitch sur VCC via MOSFET externe
```

### Glitch sur Boucle de Vérification
```python
# Si la vérification est dans une boucle de 100 itérations,
# glitcher UNE SEULE itération suffit
# → synchroniser sur le compteur de boucle

# Technique :  glitch multiple à intervalles réguliers
# pour couvrir toute la fenêtre de la boucle
scope.glitch.repeat = 100    # 100 glitches
scope.glitch.repeat_step = 20  # 20ns entre chaque
```

### Contournement de RDP (STM32 Read Protection)
```bash
# Technique connue sur STM32F0/F1/F3
# 1. Appliquer un voltage glitch pendant la lecture
#    du niveau RDP dans le bootrom
# 2. Le bootrom lit : "RDP Level 1" → arrête le debug
# 3. Glitch → "RDP Level 0" → accès debug complet
# 4. Dumper la flash via SWD

# Timing critique : < 1ms après le reset
# Utiliser un trigger GPIO du bootrom si disponible
# Sinon, mesurer le temps de démarrage et glitcher
# dans une fenêtre de 100µs
```

---

## Pièges & ASTUCES

⚠️ **Le glitch est destructeur** : trop large ou trop puissant, il peut endommager le device (latent damage, parfois non visible immédiatement)
⚠️ **Répétabilité** : le même paramètre ne donne pas toujours le même résultat. Les variations de température, d'alimentation, de vieillissement du composant influencent
⚠️ **Trigger manquant** : sans trigger précis, le glitch est aléatoire. Utiliser un GPIO, une pin de test, ou un signal UART
⚠️ **Protection du régulateur** : certains SoCs ont des régulateurs internes qui filtrent les glitchs VCC. Contournement : glitcher AVANT le régulateur (sur l'alimentation brute)
⚠️ **Bypass partiel** : parfois le device boot mais le firmware est corrompu → il peut planter après quelques secondes
⚠️ **ChipWhisperer isolation** : ne pas connecter la masse du CW à une alim secteur (risque de destruction du CW)
⚠️ **EM Glitch et équipements** : les impulsions EM haute puissance peuvent interférer avec les oscilloscopes et PC à proximité
⚠️ **Fréquence de glitch** : trop de glitches par seconde → le device chauffe, la timing change (drift thermique)

### Check-list de Calibration
```bash
# 1. Vérifier que le trigger fonctionne
#    (oscilloscope sur la ligne de trigger)
# 2. Mesurer le timing de l'opération cible
# 3. Commencer avec des paramètres conservateurs
#    (large glitch, lent, offset large)
# 4. Balayer grossièrement, puis affiner
# 5. Automatiser un sweep de 1000+ tentatives
# 6. Documenter chaque paramètre qui marche
# 7. Toujours avoir un device de backup
```

---

## Références

- **ChipWhisperer** : https://github.com/newaetech/chipwhisperer
- **NewAE Documentation** : https://chipwhisperer.readthedocs.io/
- **Tutorial : Glitch 101** : https://www.newae.com/tutorials/
- **Fault Injection on STM32** : https://aes.cr.yp.to/glitch.html
- **EM Fault Injection on ARM** : https://eprint.iacr.org/2017/652
- **Riscure Glitch Tutorial** : https://www.riscure.com/education/training/
- **Hardware Hacking Handbook** : Ch 9-12 (Glitching & Fault Injection)
- **Practical Glitching (YouTube)** : LiveOverflow, Stack Smashing, Colin O'Flynn