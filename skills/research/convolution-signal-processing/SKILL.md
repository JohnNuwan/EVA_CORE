---
name: convolution-signal-processing
description: "Convolution et corrélation en traitement du signal — convolution linéaire, circulaire, FFT, overlap-add, overlap-save, déconvolution, corrélation croisée, autocorrélation, implémentations Python/C/GPU."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [convolution, correlation, lineaire, circulaire, fft-convolution, overlap-add, overlap-save, deconvolution, autocorrelation, cross-correlation, matched-filter, python, numpy, scipy, cuda, cudnn, cmsis-dsp]
    related_skills: [dsp-fundamentals, fft-algorithms, fir-iir-filters, signal-processing-digital]
---

# Convolution et Corrélation en Traitement du Signal

## Vue d'ensemble

La convolution et la corrélation sont les opérations fondamentales du traitement du signal. La convolution modélise la sortie d'un système LTI, tandis que la corrélation mesure la similarité entre deux signaux en fonction du décalage temporel.

### Applications

| Opération | Application |
|:---|---|
| **Convolution** | Filtrage FIR, réverbération, modélisation de canal |
| **Corrélation croisée** | Détection radar/sonar, synchronisation, localisation |
| **Autocorrélation** | Détection de périodicité, pitch tracking, LPC |
| **Déconvolution** | Égalisation de canal, restauration d'image, sismique |

---

## 1. Convolution Linéaire

### 1.1 Définition

$$(x * h)[n] = \sum_{k=-\infty}^{\infty} x[k] \cdot h[n-k]$$

Pour des signaux de longueur finie $N_x$ et $N_h$, le résultat a pour longueur $N_x + N_h - 1$.

```python
import numpy as np

def convolution_lineaire(x, h):
    """Convolution linéaire directe O(N²) — but pédagogique."""
    Nx, Nh = len(x), len(h)
    Ny = Nx + Nh - 1
    y = np.zeros(Ny)
    for n in range(Ny):
        for k in range(max(0, n - Nh + 1), min(n + 1, Nx)):
            y[n] += x[k] * h[n - k]
    return y

# Vérification
x = np.random.randn(1000)
h = np.random.randn(200)
y1 = convolution_lineaire(x, h)
y2 = np.convolve(x, h)
print(f"Erreur max : {np.max(np.abs(y1 - y2)):.2e}")
```

### 1.2 Propriétés

| Propriété | Expression |
|:---|---|
| Commutativité | $x * h = h * x$ |
| Associativité | $(x * h_1) * h_2 = x * (h_1 * h_2)$ |
| Distributivité | $x * (h_1 + h_2) = x * h_1 + x * h_2$ |
| Élément neutre | $x * \delta = x$ |
| Décalage | $\delta[n - k] * x[n] = x[n - k]$ |
| Convolution et convolution | $(x * h)[n] \xleftrightarrow{\mathcal{F}} X[k] \cdot H[k]$ |

---

## 2. Convolution par FFT

### 2.1 Principe

$$x * h = \mathcal{F}^{-1}\{\mathcal{F}\{x\} \cdot \mathcal{F}\{h\}\}$$

Complexité : $O(N \log N)$ au lieu de $O(N^2)$.

### 2.2 Zero-padding nécessaire

La multiplication des FFT réalise une **convolution circulaire**. Pour obtenir une convolution linéaire, il faut zero-padder à $M \geq N_x + N_h - 1$.

```python
from scipy.fft import fft, ifft

def convolution_fft(x, h):
    """Convolution linéaire par FFT en O(N log N)."""
    Nx, Nh = len(x), len(h)
    M = Nx + Nh - 1  # Taille FFT minimale

    # Zero-padding
    X = fft(x, M)
    H = fft(h, M)

    # Multiplication dans le domaine fréquentiel
    y = ifft(X * H)

    return y.real  # Le résultat est réel si x et h sont réels

# Comparaison de performance
import time
x = np.random.randn(100000)
h = np.random.randn(1000)

t0 = time.time()
y_direct = np.convolve(x, h)
t1 = time.time()
y_fft = convolution_fft(x, h)
t2 = time.time()

print(f"Direct : {t1-t0:.3f}s, FFT : {t2-t1:.3f}s")
print(f"Erreur : {np.max(np.abs(y_direct - y_fft)):.2e}")
```

### 2.3 Quand utiliser la FFT ?

| Taille $N_x$ | Taille $N_h$ | Méthode recommandée |
|:---:|---:|---:|
| Petit (< 100) | Petit (< 100) | Directe |
| Très grand | Petit (< 100) | Directe (optimisée) |
| Grand (> 1000) | Grand (> 1000) | **FFT** |
| Temps réel | Fixe | Overlap-add/save |

**Seuil empirique :** La FFT devient rentable quand $N_h > \log_2(N_x)$.

---

## 3. Convolution par Blocs (Temps Réel)

Pour les flux infinis (streaming audio, SDR), on ne peut pas attendre tout le signal.

### 3.1 Overlap-Add (OLA)

```python
def overlap_add(x, h, block_size=1024):
    """
    Convolution par blocs avec la méthode Overlap-Add.
    Idéale pour le filtrage FIR en streaming.
    """
    Nh = len(h)
    M = block_size + Nh - 1  # Taille FFT
    H = fft(h, M)

    output_len = len(x) + Nh - 1
    y = np.zeros(output_len)

    # Traitement par blocs
    for start in range(0, len(x), block_size):
        block = x[start:start + block_size]
        if len(block) < block_size:
            block = np.pad(block, (0, block_size - len(block)))

        X_block = fft(block, M)
        Y_block = ifft(X_block * H)

        # Addition avec recouvrement
        end = min(start + M, output_len)
        y[start:end] += Y_block[:end - start]

    return y
```

### 3.2 Overlap-Save (OLS)

```python
def overlap_save(x, h, block_size=1024):
    """
    Convolution par blocs avec Overlap-Save.
    Évite l'addition de recouvrement au prix d'un garbage.
    """
    Nh = len(h)
    M = 2 * block_size  # Taille FFT (2x block)
    H = fft(h, M)

    # Préparation : préfixer avec (Nh - 1) zéros pour l'état initial
    x_padded = np.concatenate([np.zeros(Nh - 1), x])
    output_len = len(x) + Nh - 1
    y = np.zeros(output_len)

    for start in range(0, len(x), block_size):
        # Prendre un bloc de taille M avec (block_size) de recouvrement
        block = x_padded[start:start + M]
        if len(block) < M:
            block = np.pad(block, (0, M - len(block)))

        X_block = fft(block, M)
        Y_block = ifft(X_block * H)

        # Garder seulement les block_size échantillons valides
        out_start = start
        out_end = min(start + block_size, output_len)
        y[out_start:out_end] = Y_block[Nh-1:Nh-1 + out_end - out_start]

    return y
```

---

## 4. Convolution Circulaire

### 4.1 Définition

$$(x \circledast h)[n] = \sum_{k=0}^{N-1} x[k] \cdot h[(n-k) \bmod N]$$

Utile pour le filtrage dans le domaine fréquentiel, les OFDM, la FFT.

```python
def convolution_circulaire(x, h):
    """Convolution circulaire de même taille N."""
    N = len(x)
    y = np.zeros(N, dtype=complex)
    X = fft(x)
    H = fft(h, N)
    return ifft(X * H)
```

### 4.2 Multiplication polynomiale

La convolution des coefficients est la multiplication polynomiale :

$$(a_0 + a_1 x + \dots)(b_0 + b_1 x + \dots) = \sum_n \left(\sum_k a_k b_{n-k}\right) x^n$$

---

## 5. Corrélation Croisée

### 5.1 Définition

Mesure de similarité entre $x$ et $y$ en fonction du décalage $\tau$ :

$$R_{xy}[\tau] = \sum_{n} x[n] \cdot y[n + \tau]$$

```python
from scipy.signal import correlate, correlation_lags

def correlation_normalisee(x, y):
    """Corrélation croisée normalisée (coefficient de corrélation)."""
    r = correlate(x, y, mode='full')
    lags = correlation_lags(len(x), len(y), mode='full')
    # Normalisation [-1, 1]
    r_norm = r / (np.linalg.norm(x) * np.linalg.norm(y))
    return lags, r_norm

# Détection du décalage temporel entre deux microphones
# pour la localisation de source sonore
x = micro1  # Signal microphone 1
y = micro2  # Signal microphone 2 (décalé)
lags, r = correlation_normalisee(x, y)
lag_estimate = lags[np.argmax(np.abs(r))]
# TDOA = lag_estimate / fs (secondes)
```

### 5.2 Filtrage Adapté (Matched Filter)

Utilise la corrélation croisée pour détecter un motif connu dans un signal bruité (radar, sonar, communications).

```python
def matched_filter(received, template):
    """
    Filtre adapté : maximise le SNR pour la détection d'un motif.

    received : signal reçu (contenant le motif + bruit)
    template : motif connu à détecter

    Retourne : indice du pic, SNR estimé
    """
    # Le filtre adapté est la corrélation croisée
    # avec la version retournée du template
    h = template[::-1]  # Conjugué retourné (time-reversed conjugate)
    correlation = np.convolve(received, h, mode='same')

    peak_idx = np.argmax(np.abs(correlation))
    peak_val = np.abs(correlation[peak_idx])

    # Estimation du bruit en dehors de la zone du pic
    threshold = 0.5 * peak_val
    noise_samples = correlation[np.abs(correlation) < threshold]
    noise_floor = np.std(noise_samples) if len(noise_samples) > 0 else 1e-10
    snr_db = 20 * np.log10(peak_val / noise_floor)

    return peak_idx, snr_db, correlation

# Exemple : séquence d'entraînement dans un canal bruité
N = 1000
template = np.random.randn(100)  # Séquence d'apprentissage
channel = np.random.randn(200) * 0.1
received = np.convolve(template, channel)[:len(template)] + 0.5 * np.random.randn(len(template))

idx, snr, corr = matched_filter(received, template)
print(f"Pic à l'indice #{idx}, SNR = {snr:.1f} dB")
```

### 5.3 Corrélation par FFT

```python
def correlation_fft(x, y):
    """Corrélation croisée par FFT (O(N log N))."""
    N = len(x) + len(y) - 1
    X = fft(x, N)
    Y = fft(y, N)
    # R_xy = ifft(X * conj(Y))
    return ifft(X * np.conj(Y)).real
```

---

## 6. Autocorrélation

### 6.1 Définition

Corrélation d'un signal avec lui-même :

$$R_{xx}[\tau] = \sum_n x[n] \cdot x[n + \tau]$$

Propriétés :
- $R_{xx}[0] = \text{énergie du signal}$
- $R_{xx}[\tau] \leq R_{xx}[0]$ (maximum à $\tau = 0$)
- $R_{xx}[-\tau] = R_{xx}[\tau]$ (paire)

```python
def detecter_periode(signal, fs, f_min=20, f_max=2000):
    """
    Détecte la période fondamentale d'un signal par autocorrélation.
    Utilisé pour : pitch tracking, détection de rythme, analyse vibratoire.
    """
    r = np.correlate(signal, signal, mode='full')
    r = r[len(r) // 2:]  # Moitié positive

    # Ignorer τ = 0 et les petites valeurs
    r[:int(fs / f_max)] = 0
    r[int(fs / f_min):] = 0

    # Premier pic non-nul
    peak_idx = np.argmax(r)
    if r[peak_idx] < 0.1 * r[0]:
        return None  # Signal non périodique

    f0 = fs / peak_idx
    return f0, peak_idx

# Détection de la fréquence fondamentale d'un son
f0, _ = detecter_periode(audio, fs=44100, f_min=50, f_max=1000)
print(f"Fréquence fondamentale : {f0:.1f} Hz")
```

### 6.2 AMDF (Average Magnitude Difference Function)

Alternative à l'autocorrélation, moins coûteuse :

```python
def amdf(signal):
    """Average Magnitude Difference Function pour la détection de pitch."""
    N = len(signal)
    d = np.zeros(N // 2)
    for tau in range(1, N // 2):
        d[tau] = np.mean(np.abs(signal[:-tau] - signal[tau:]))
    return d

# Le minimum de AMDF indique la période (τ où le signal est le plus similaire à lui-même)
```

---

## 7. Déconvolution

### 7.1 Déconvolution par FFT (inverse filtering)

```python
def deconvolution_fft(y, h, epsilon=1e-3):
    """
    Déconvolution simple : x = F^{-1}(Y / H).
    epsilon évite la division par zéro (régularisation de base).
    """
    H = fft(h, len(y))
    Y = fft(y)
    H_masked = np.where(np.abs(H) > epsilon, H, epsilon)
    X = Y / H_masked
    return ifft(X).real
```

### 7.2 Déconvolution de Wiener

Déconvolution optimale au sens MMSE (bruit gaussien) :

```python
def wiener_deconvolution(y, h, snr_db=30):
    """
    Déconvolution de Wiener : estime x à partir de y = x*h + n.

    H_w = conj(H) / (|H|^2 + 1/SNR)
    """
    H = fft(h, len(y))
    snr = 10**(snr_db / 10)
    H_w = np.conj(H) / (np.abs(H)**2 + 1/snr)
    Y = fft(y)
    return ifft(Y * H_w).real
```

### 7.3 Déconvolution aveugle (Blind Deconvolution)

Quand $h$ est inconnu : estimer simultanément $x$ et $h$ à partir de $y = x * h$.

- **Méthode :** Algorithme EM (Expectation-Maximisation), gradient conjugué
- **Applications :** Défloutage d'image, restauration audio, sismique
- **Contrainte :** Problème mal posé, nécessite une régularisation (Renyi, TV)

---

## 8. Implémentations Haute Performance

### 8.1 NVIDIA cuDNN (convolution pour Deep Learning)

```c
// Convolution 1D via cuDNN (batch = B, canaux = C)
cudnnConvolutionDescriptor_t conv_desc;
cudnnCreateConvolutionDescriptor(&conv_desc);
cudnnSetConvolutionMathType(conv_desc, CUDNN_TENSOR_OP_MATH);

// Les convolutions DL utilisent implicit_gemm (Winograd pour 3x3)
cudnnConvolutionForward(cudnn_handle, ...);
```

### 8.2 CMSIS-DSP (ARM Cortex-M)

```c
#include "arm_math.h"

// Corrélation
arm_correlate_f32(inputA, lenA, inputB, lenB, result);

// Convolution FIR
arm_fir_f32(&instance, input, output, block_size);
```

### 8.3 Implémentation GPU via PyTorch

```python
import torch

def convolution_gpu(x, h):
    """Convolution 1D sur GPU via PyTorch."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    x_t = torch.tensor(x, dtype=torch.float32, device=device)
    h_t = torch.tensor(h, dtype=torch.float32, device=device)

    # PyTorch utilise cuDNN (Winograd/implicit GEMM)
    x_reshaped = x_t.view(1, 1, -1)
    h_reshaped = h_t.view(1, 1, -1)
    y = torch.nn.functional.conv1d(x_reshaped, h_reshaped, padding=len(h)-1)
    return y.squeeze().cpu().numpy()
```

---

## Pièges Courants

1. **FFT sans zero-padding :** La multiplication dans le domaine fréquentiel réalise une convolution circulaire, pas linéaire. Toujours zero-padder à $M \geq N_x + N_h - 1$.
2. **Corrélation non normalisée :** Un pic fort peut être dû à une grande amplitude, pas à une bonne corrélation. Normaliser par l'énergie ($\|x\|\|y\|$).
3. **Déconvolution naïve amplifiant le bruit :** $Y/H$ explose quand $H \approx 0$. Toujours régulariser (Wiener, Tikhonov, epsilon).
4. **Latence d'overlap-add :** La latence est d'au moins un bloc. Pour les applications temps réel critiques, réduire la taille du bloc.
5. **Débordement mémoire en corrélation :** Une corrélation croisée de deux signaux de 1M échantillons produit 2M-1 points de sortie.

---

## Liste de vérification (Checklist)

- [ ] Zero-padding appliqué pour la convolution linéaire par FFT ($M \geq N_x + N_h - 1$).
- [ ] Overlap-add ou overlap-save utilisé pour le filtrage FIR en streaming.
- [ ] Corrélation normalisée pour la détection robuste.
- [ ] Régularisation appliquée à la déconvolution (Wiener, Tikhonov).
- [ ] Bloc overlap-add dimensionné pour la latence cible.
- [ ] Test sur signaux synthétiques (sinusoïdes, Dirac) avant signaux réels.
- [ ] GPU utilisé pour N > 100k et bibliothèque optimisée (cuDNN, cuFFT).