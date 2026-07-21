---
name: wavelet-analysis
description: "Analyse par ondelettes (wavelets) — CWT, DWT, paquets d'ondelettes, familles Haar/Daubechies/Symlet/Coiflet, lifting scheme, débruitage, compression, multi-résolution, implémentations Python/C."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [wavelet, ondelette, cwt, dwt, multi-resolution, haar, daubechies, symlet, coiflet, biorthogonal, lifting, denoising, compression, jpeg2000, time-frequency, pywavelets, python, scipy, matlab]
    related_skills: [dsp-fundamentals, fft-algorithms, signal-processing-digital]
---

# Analyse par Ondelettes (Wavelets)

## Vue d'ensemble

L'analyse par ondelettes (wavelet transform) est un outil temps-fréquence qui décompose un signal en composantes localisées à la fois dans le temps et en fréquence. Contrairement à la FFT (résolution fréquentielle parfaite, temporelle nulle) et à la STFT (résolution fixe), la transformée en ondelettes offre une **résolution adaptative** : haute résolution temporelle aux hautes fréquences, haute résolution fréquentielle aux basses fréquences.

### FFT vs STFT vs Wavelets

| Transformée | Résolution temporelle | Résolution fréquentielle | Signal adapté |
|:---|---|---|---|
| **FFT** | Aucune | Parfaite | Stationnaire |
| **STFT** | Fixe (taille fenêtre) | Fixe | Quasi-stationnaire |
| **CWT** (continue) | Adaptative | Adaptative | Non-stationnaire |
| **DWT** (discrète) | Dyadique (2^j) | Dyadique | Non-stationnaire, compression |

### Applications

| Domaine | Application |
|:---|---|
| **Débruitage** | ECG, EEG, audio, images |
| **Compression** | JPEG 2000 (ondelettes biorthogonales 9/7) |
| **Détection de singularités** | Transitoires, pics, sauts, défauts mécaniques |
| **Analyse fractale** | Estimation de l'exposant de Hurst, dimension fractale |
| **Géophysique** | Analyse sismique, prospection pétrolière |
| **Biomédical** | Analyse ECG (ondes P, QRS, T), EEG (rythmes), EMG |
| **Finance** | Détection de changements de régime, multi-résolution |

---

## 1. Transformée en Ondelettes Continue (CWT)

### 1.1 Définition

$$W_x(a, b) = \frac{1}{\sqrt{a}} \int_{-\infty}^{\infty} x(t) \cdot \psi^*\left(\frac{t - b}{a}\right) dt$$

où :
- $\psi(t)$ : ondelette mère (prototype)
- $a > 0$ : facteur d'échelle (inverse de la fréquence)
- $b$ : translation (temps)
- $1/\sqrt{a}$ : normalisation d'énergie

```python
import numpy as np
import pywt
import matplotlib.pyplot as plt

def cwt_scalogramme(signal, fs=1000, frequencies=None):
    """
    Calcule le scalogramme CWT (temps-fréquence).

    Paramètres :
        signal      : signal d'entrée
        fs          : fréquence d'échantillonnage
        frequencies : fréquences à analyser (None = auto)

    Retourne : t, freq, coefs (matrice complexe)
    """
    if frequencies is None:
        # Échelle logarithmique pour la résolution adaptative
        frequencies = np.logspace(np.log10(1), np.log10(fs / 2), 100)

    # Conversion fréquences → échelles (ondelette de Morse par défaut)
    scales = pywt.frequency2scale('morse', frequencies, fs)

    # CWT
    coefs, _ = pywt.cwt(signal, scales, 'morse', sampling_period=1/fs)

    t = np.arange(len(signal)) / fs
    return t, frequencies, coefs

# Exemple : chirp (fréquence croissante)
t = np.linspace(0, 1, 1000)
signal = np.sin(2 * np.pi * (50 + 200 * t) * t)
t_cwt, f, coefs = cwt_scalogramme(signal, fs=1000)
```

### 1.2 Ondelettes mères principales

```python
# PyWavelets fournit de nombreuses familles
pywt.families()
# ['haar', 'db', 'sym', 'coif', 'bior', 'rbio',
#  'dmey', 'gaus', 'mexh', 'morl', 'cgau', 'shan',
#  'fbsp', 'cmor', 'morse']

# Ondelettes de base :
# 'morl'  : Morlet (gaussienne modulée) — CWT, analyse EEG
# 'mexh'  : Mexican Hat / Ricker — CWT, détection de pics
# 'gaus'  : Dérivées de gaussienne — CWT, détection de contours
# 'cmor'  : Complexe Morlet — CWT, phase instantanée
# 'morse' : Ondelette de Morse généralisée — défaut recommandé

# Pour la DWT (discrète) :
# 'haar'  : La plus simple, détection de sauts brusques
# 'db'    : Daubechies (db2-db38), orthogonal
# 'sym'   : Symlet (sym2-sym20), proche de db, plus symétrique
# 'coif'  : Coiflet (coif1-coif5), moments nuls sur la mise à l'échelle
# 'bior'  : Biorthogonal (biorX.Y), JPEG 2000 utilise bior4.4
```

### 1.3 Ondelette de Morlet

$$\psi(t) = \frac{1}{\sqrt{\pi f_b}} e^{j2\pi f_c t} e^{-t^2 / f_b}$$

Où $f_c$ = fréquence centrale, $f_b$ = paramètre de largeur de bande.

```python
# Ondelette de Morse (recommandée pour CWT)
# Paramètres : gamma (symétrie), beta (bande passante)

# Complex Morlet : bonne résolution temps-fréquence
coefs, _ = pywt.cwt(signal, scales, 'cmor1.5-1.0', sampling_period=1/fs)
```

---

## 2. Transformée en Ondelettes Discrète (DWT)

### 2.1 Définition et multi-résolution

La DWT décompose le signal en **coefficients d'approximation** (basses fréquences) et **coefficients de détail** (hautes fréquences), de manière récursive.

```
Niveau 1 :  x[n] ──→ [H (passe-haut)] ─→ cD1 (détails, N/2)
                  ─→ [L (passe-bas)]  ─→ cA1 (approximation, N/2)

Niveau 2 :  cA1 ─→ [H] ─→ cD2 (détails, N/4)
                ─→ [L] ─→ cA2 (approximation, N/4)

... récursivement jusqu'au niveau J
```

```python
def decomposition_multi_niveaux(signal, wavelet='db4', niveau=4):
    """
    Décomposition DWT multi-niveaux avec visualisation.

    Retourne : cA_n (approximation finale), [cD_1, ..., cD_n] (détails)
    """
    # Décomposition par paquets
    coeffs = pywt.wavedec(signal, wavelet, level=niveau)
    # coeffs[0] = cA_n (approximation au niveau n)
    # coeffs[1] = cD_n (détails au niveau n)
    # coeffs[2] = cD_{n-1}
    # ...
    # coeffs[n] = cD_1 (détails au niveau 1)
    return coeffs

# Reconstruction
signal_reconstruit = pywt.waverec(coeffs, wavelet)

# Vérification
print(f"Erreur de reconstruction : {np.max(np.abs(signal - signal_reconstruit)):.2e}")
```

### 2.2 Filtres miroirs en quadrature (QMF)

La DWT utilise deux filtres :
- **Filtre passe-bas** $L$ (échelle) : $h[n]$
- **Filtre passe-haut** $H$ (ondelette) : $g[n] = (-1)^n h[L-1-n]$

Condition de reconstruction parfaite (Perfect Reconstruction) :

$$H(z)L(z) + H(-z)L(-z) = 2$$

```python
# Affichage des coefficients du filtre pour Daubechies 4
wavelet = pywt.Wavelet('db4')
print("Filtre d'échelle (LP) :", wavelet.rec_lo)   # Reconstruction LP
print("Filtre d'ondelette (HP) :", wavelet.rec_hi)  # Reconstruction HP
print("Filtre décomposition LP :", wavelet.dec_lo)  # Décomposition LP
print("Filtre décomposition HP :", wavelet.dec_hi)  # Décomposition HP
```

### 2.3 Familles d'ondelettes discrètes

| Famille | Propriétés | Nombre de moments nuls | Usage |
|:---|---|---|---|
| **Haar** ($db1$) | Orthogonale, discontinue | 1 | Détection de sauts, pédagogique |
| **Daubechies** ($dbN$) | Orthogonale, support compact | $N$ | Usage général (db4, db8) |
| **Symlet** ($symN$) | Orthogonale, quasi-symétrique | $N$ | Meilleure que db pour symétrie |
| **Coiflet** ($coifN$) | Orthogonale, moments nuls sur échelle et ondelette | $2N$ | Analyse de signaux lisses |
| **Biorthogonale** ($biorX.Y$) | Linéaire, symétrique | Variable | **JPEG 2000** (bior4.4) |

```python
# Sélection de l'ondelette selon l'application
configs = {
    "débruitage ECG":       "db6",
    "débruitage audio":     "sym8",
    "compression image":    "bior4.4",  # JPEG 2000
    "détection transitoire": "db2",
    "analyse EEG":          "db4",
    "détection défauts mécaniques": "db10",
}
```

---

## 3. Applications Pratiques

### 3.1 Débruitage par Seuillage (Wavelet Denoising)

Principe : les coefficients de détail à petite échelle contiennent surtout du bruit. En seuillant ces coefficients, on élimine le bruit tout en préservant les transitoires.

```python
def debruitage_wavelet(signal, wavelet='sym8', niveau=5, mode='soft'):
    """
    Débruitage par seuillage wavelet (Donoho & Johnstone).

    mode : 'soft' (continu) ou 'hard' (discontinu)
    """
    # Décomposition
    coeffs = pywt.wavedec(signal, wavelet, level=niveau)

    # Estimation du seuil (VisuShrink : sigma * sqrt(2*log(N)))
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745  # Est. robuste du bruit
    seuil = sigma * np.sqrt(2 * np.log(len(signal)))

    # Seuillage des coefficients de détail (pas l'approximation)
    for i in range(1, len(coeffs)):
        coeffs[i] = pywt.threshold(coeffs[i], seuil, mode=mode)

    # Reconstruction
    return pywt.waverec(coeffs, wavelet)

# Comparaison avec un filtre passe-bas
signal_bruite = signal_propre + 0.5 * np.random.randn(len(signal_propre))
signal_debruite = debruitage_wavelet(signal_bruite)

print(f"SNR avant : {10*np.log10(np.var(signal_propre)/np.var(signal_bruite-signal_propre)):.1f} dB")
print(f"SNR après : {10*np.log10(np.var(signal_propre)/np.var(signal_debruite-signal_propre)):.1f} dB")
```

### 3.2 Compression par ondelettes

```python
def compression_wavelet(signal, wavelet='bior4.4', niveau=5, ratio=0.1):
    """
    Compression par ondelettes : garder les X% plus grands coefficients.
    Utilisé dans JPEG 2000, ECW, etc.
    """
    coeffs = pywt.wavedec(signal, wavelet, level=niveau)
    coeffs_array = np.concatenate([c.flatten() for c in coeffs])

    # Garder les plus grands coefficients
    seuil = np.percentile(np.abs(coeffs_array), 100 * (1 - ratio))

    # Seuillage dur
    coeffs_comp = [pywt.threshold(c, seuil, mode='hard') for c in coeffs]
    signal_comp = pywt.waverec(coeffs_comp, wavelet)

    # Ratio de compression et distorsion
    n_coeffs_originaux = len(coeffs_array)
    n_coeffs_gardes = np.sum(np.abs(coeffs_array) > seuil)
    snr = 10 * np.log10(np.var(signal) / np.var(signal - signal_comp))

    return signal_comp, {
        "ratio": n_coeffs_gardes / n_coeffs_originaux,
        "snr_db": snr,
    }
```

### 3.3 Détection de singularités (transitoires, pics)

Les coefficients de détail à petite échelle (haute fréquence) sont très sensibles aux singularités :

```python
def detecter_transitoires(signal, wavelet='db2'):
    """
    Détecte les transitoires et sauts dans un signal.
    """
    coeffs = pywt.wavedec(signal, wavelet, level=3)
    cD1 = coeffs[1]  # Détails niveau 1
    cD2 = coeffs[2]  # Détails niveau 2

    # Les pics dans les détails indiquent des transitoires
    seuil = 3 * np.std(cD1)  # 3 sigma
    pics = np.where(np.abs(cD1) > seuil)[0]

    # Lissage multi-échelle : un transitoire apparaît à plusieurs niveaux
    return pics, cD1, cD2

# Application : détection de complexes QRS en ECG
pics_qrs, _, _ = detecter_transitoires(ecg_signal, 'db4')
```

### 3.4 Analyse multi-échelle (MRA)

Reconstruire le signal à partir d'un sous-ensemble de niveaux de détail :

```python
def analyse_multi_echelle(signal, wavelet='db4', niveau=6):
    """
    Analyse multi-échelle : visualiser les composantes à chaque échelle.

    Retourne : approximation_J, [détail_J, ..., détail_1]
    """
    coeffs = pywt.wavedec(signal, wavelet, level=niveau)
    mra = []

    # Reconstruction à partir d'UN SEUL niveau de détail
    for i in range(1, len(coeffs)):
        # Zéro-partout sauf au niveau i
        coeffs_i = [np.zeros_like(c) for c in coeffs]
        coeffs_i[i] = coeffs[i]
        detail = pywt.waverec(coeffs_i, wavelet)
        mra.append(detail[:len(signal)])

    # Approximation finale
    coeffs_approx = [coeffs[0]] + [np.zeros_like(c) for c in coeffs[1:]]
    approx = pywt.waverec(coeffs_approx, wavelet)[:len(signal)]

    return approx, mra

# Visualisation : le signal EEG décomposé en bandes Delta, Theta, Alpha, Beta, Gamma
approx_details, details = analyse_multi_echelle(eeg_signal, 'db6', 6)
```

### 3.5 Détection de défauts mécaniques (vibratoire)

```python
def detecter_defaut_vibratoire(vibration, fs, rpm, wavelet='db10'):
    """
    Détection de défauts de roulements par ondelettes.
    Les défauts créent des impulsions périodiques aux hautes fréquences.
    """
    # Décomposition DWT
    coeffs = pywt.wavedec(vibration, wavelet, level=5)

    # Le détail de niveau 1-2 contient les impulsions de défaut
    detail = coeffs[1]  # cD1

    # Enveloppe de Hilbert sur le détail
    from scipy.signal import hilbert
    enveloppe = np.abs(hilbert(detail))

    # Spectre de l'enveloppe
    f, Sxx = spectrogram(enveloppe, fs=fs)
    # Chercher les harmoniques de la fréquence de défaut (BPFI, BPFO, BSF, FTF)
    return enveloppe, f, Sxx
```

---

## 4. Paquets d'Ondelettes (Wavelet Packet Transform — WPT)

La WPT décompose aussi les coefficients de détail (pas seulement l'approximation), donnant un arbre complet.

```python
def arbre_paquets(signal, wavelet='db4', niveau_max=4):
    """
    Décomposition complète par paquets d'ondelettes.
    """
    wp = pywt.WaveletPacket(signal, wavelet, maxlevel=niveau_max)

    # Liste de tous les nœuds
    noeuds = [n.path for n in wp.get_level(niveau_max, 'freq')]
    # Les nœuds sont ordonnés par fréquence croissante

    # Extraction d'un nœud spécifique
    energie = {}
    for path in noeuds:
        node = wp[path]
        energie[path] = np.sum(node.data**2)

    return wp, energie

# Application : meilleure sélection de base (best basis)
# Algorithme de Coifman-Wickerhauser : minimisation de l'entropie
def meilleure_base(wp, cout='entropy'):
    """
    Sélection de la meilleure base par minimisation de l'entropie.
    """
    return pywt.WaveletPacket.best_tree(wp, cost_function=cout)
```

Avantages de la WPT :
- Résolution fréquentielle uniforme à chaque étage
- Sélection adaptative de la base optimale (best basis)
- Meilleure pour les signaux à composantes tonales (FFT-like)

---

## 5. Lifting Scheme (Second Generation Wavelets)

Construction d'ondelettes dans le domaine temporel sans FFT, idéal pour l'embarqué et les signaux de longueur quelconque.

```
Étapes du lifting :
1. SPLIT : diviser en pairs (x_even) et impairs (x_odd)
2. PREDICT : prédire les impairs à partir des pairs
   d[n] = x_odd[n] - P(x_even[n])
3. UPDATE : mettre à jour les pairs à partir des détails
   c[n] = x_even[n] + U(d[n])
```

```python
def lifting_haar_forward(x):
    """Transformée de Haar par lifting (en place)."""
    N = len(x)
    if N % 2 != 0:
        x = np.append(x, x[-1])
        N += 1

    even = x[0::2].copy()
    odd = x[1::2].copy()

    # Predict : d = odd - even
    detail = odd - even

    # Update : c = even + d/2
    approx = even + detail / 2

    return approx, detail

def lifting_haar_inverse(approx, detail):
    """Transformée inverse de Haar par lifting."""
    even = approx - detail / 2
    odd = detail + even
    
    x = np.zeros(2 * len(approx))
    x[0::2] = even
    x[1::2] = odd
    return x
```

Avantages du lifting :
- Pas de multiplication (décalages binaires pour Haar)
- Transformation in-place (économie mémoire)
- Longueur de signal quelconque (pas besoin de puissance de 2)
- Version entière possible (lossless, compression sans perte)

---

## 6. Implémentations et Outils

### 6.1 PyWavelets (Python)

```bash
pip install PyWavelets
```

```python
import pywt

# Liste des ondelettes disponibles
print(pywt.families(short=False))

# Visualisation d'une ondelette
wavelet = pywt.Wavelet('db4')
phi, psi, x = wavelet.wavefun(level=5)  # phi = scaling, psi = wavelet

print(f"Support de db4 : {wavelet.rec_len}")
print(f"Moment nul : le premier {wavelet.vanishing_moments_psi} moments de psi sont nuls")
```

### 6.2 MATLAB / Octave

```matlab
% Wavelet Toolbox
[C, L] = wavedec(x, 5, 'db4');
d1 = wrcoef('d', C, L, 'db4', 1);  % Détail niveau 1
a5 = wrcoef('a', C, L, 'db4', 5);  % Approximation niveau 5

x_denoised = wdenoise(x, 5, 'Wavelet', 'sym8', ...
    'DenoisingMethod', 'Bayes');
```

### 6.3 Implémentation C embarqué

```c
// Haar lifting en C (sans multiplications, décalage binaire)
void haar_forward(const float *x, float *approx, float *detail, int n) {
    for (int i = 0; i < n / 2; i++) {
        float even = x[2 * i];
        float odd = x[2 * i + 1];
        detail[i] = odd - even;            // Predict
        approx[i] = even + detail[i] / 2;  // Update
    }
}

// Daubechies 4 lifting (plus complexe, nécessite des multiplications)
// Utiliser la bibliothèque wavelib (open source C) pour DWT avancée
```

---

## 7. Propriétés Mathématiques

### 7.1 Moments nuls

Une ondelette a $p$ moments nuls si :

$$\int_{-\infty}^{\infty} t^k \psi(t) dt = 0 \quad \text{pour } k = 0, 1, \dots, p-1$$

- $p$ moments nuls → polynômes de degré $<p$ parfaitement représentés par l'approximation
- Plus $p$ est grand, meilleure est la compression des signaux lisses
- Daubechies $dbN$ a $N$ moments nuls

### 7.2 Analyse fractale

```python
def exposant_hurst_wavelet(signal):
    """
    Estimation de l'exposant de Hurst par l'énergie des coefficients d'ondelettes.
    H > 0.5 : signal persistant (tendance)
    H < 0.5 : signal antipersistant (moyenne régressive)
    H = 0.5 : bruit blanc
    """
    coeffs = pywt.wavedec(signal, 'db4', level=8)
    variances = [np.var(c) for c in coeffs[1:]]  # Variance des détails
    echelles = 2 ** np.arange(1, len(variances) + 1)

    # log2(var) ≈ (2H - 1) * log2(scale) + const
    from scipy.stats import linregress
    slope, _, _, _, _ = linregress(np.log2(echelles), np.log2(variances))
    H = (slope + 1) / 2
    return H
```

---

## Pièges Courants

1. **Mauvaise ondelette pour l'application :** Pour la détection de transitoires, utiliser une ondelette courte (db2, Haar). Pour l'analyse de signaux lents, une ondelette longue (db10, sym8).
2. **Jouer sur la reconstruction :** Les ondelettes orthogonales (db, sym) garantissent la reconstruction parfaite. Les biorthogonales (bior, rbio) aussi, mais pas les CWT (morlet, mexh).
3. **Seuillage agressif :** Un seuil trop élevé supprime les détails fins. Utiliser le seuil universel de Donoho $\sigma\sqrt{2\log N}$ comme point de départ.
4. **Artefacts de bord (boundary effect) :** Les coefficients DWT aux bords sont moins fiables. Utiliser `mode='periodization'` ou `'symmetric'` pour les réduire.

---

## Liste de vérification (Checklist)

- [ ] Ondelettes adaptée au type de signal : courte pour transitoires, longue pour signaux lents.
- [ ] Débruitage : seuillage mou (soft) préféré au dur (hard) pour la continuité.
- [ ] Compression : ondelette biorthogonale (JPEG 2000), seuillage par énergie.
- [ ] Analyse multi-échelle : interprétation physique des niveaux de détail.
- [ ] Reconstruction parfaite vérifiée (erreur ~ machine).
- [ ] Mode de prolongement aux bords choisi (symmetric, zero, periodic).