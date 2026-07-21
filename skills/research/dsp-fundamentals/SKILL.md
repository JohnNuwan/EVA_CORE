---
name: dsp-fundamentals
description: "Fondamentaux du Traitement Numérique du Signal (DSP) — échantillonnage, quantification, transformée en Z, systèmes LTI, analyse temps-fréquence, implémentations Python/C embarqué."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [dsp, traitement-signal, numerique, echantillonnage, nyquist, quantification, transformee-z, lti, temps-frequence, python, numpy, scipy, c-plus-plus, temps-reel, anti-aliasing]
    related_skills: [fft-algorithms, fir-iir-filters, convolution-signal-processing, wavelet-analysis, sdr-advanced, gnu-radio, modulation-demodulation, signal-processing-digital]
---

# Traitement Numérique du Signal — Fondamentaux

## Vue d'ensemble

Le Traitement Numérique du Signal (DSP) est la discipline qui étudie la manipulation de signaux numériques — séquences d'échantillons représentant des grandeurs physiques (son, vibration, tension, RF). Cette compétence couvre les fondations théoriques et pratiques sur lesquelles reposent toutes les techniques avancées (FFT, filtrage, ondelettes, SDR).

### Domaines d'application

| Domaine | Exemples DSP |
|:---|---|
| **Audio** | Échantillonnage CD 44.1 kHz, quantification 16/24 bit, filtrage |
| **Télécom** | Conversion A/N, shaping d'impulsions, synchronisation |
| **Biomédical** | ECG 250 Hz–1 kHz, EEG 128–1024 Hz, EMG |
| **Instrumentation** | Acquisition 10 kHz–100 MHz, analyse vibratoire |
| **Radar/SDR** | Échantillonnage IQ 20–80 MSps, quantification large bande |

---

## 1. Échantillonnage et Théorème de Shannon-Nyquist

### 1.1 Échantillonnage idéal

Un signal continu $x_c(t)$ échantillonné à la période $T_s = 1/f_s$ produit la séquence discrète :

$$x[n] = x_c(nT_s), \quad n \in \mathbb{Z}$$

Dans le domaine fréquentiel, le spectre du signal échantillonné est une répétition périodique du spectre original :

$$X_s(f) = \frac{1}{T_s} \sum_{k=-\infty}^{\infty} X_c(f - k f_s)$$

```python
import numpy as np

def echantillonner(signal_continu, t, fs):
    Ts = 1 / fs
    t_ech = np.arange(t[0], t[-1], Ts)
    x_ech = signal_continu(t_ech)
    return t_ech, x_ech

# Exemple : sinusoïde 100 Hz échantillonnée à 1 kHz
fs = 1000
t = np.linspace(0, 0.1, 10000)
x_cont = lambda t: np.sin(2 * np.pi * 100 * t)
t_ech, x_ech = echantillonner(x_cont, t, fs)
```

### 1.2 Théorème de Shannon-Nyquist

**Énoncé :** Un signal $x(t)$ dont le spectre est nul pour $|f| > f_{max}$ peut être parfaitement reconstruit à partir de ses échantillons si :

$$f_s \geq 2 \cdot f_{max}$$

$f_{max} = f_s/2$ est appelée **fréquence de Nyquist**.

```python
def verifier_nyquist(f_signal, f_ech):
    f_nyquist = f_ech / 2
    if f_signal < f_nyquist:
        return "OK"
    else:
        f_aliased = abs(f_signal - f_ech * round(f_signal / f_ech))
        return f"ALIASING : fréquence mesurée ≈ {f_aliased:.1f} Hz"

cas = [
    ("1 kHz, fs=10 kHz", 1000, 10000),
    ("8 kHz, fs=10 kHz", 8000, 10000),
    ("20 kHz, fs=44.1 kHz", 20000, 44100),
    ("30 kHz, fs=44.1 kHz", 30000, 44100),
]
for desc, f_sig, f_s in cas:
    print(f"{desc}: {verifier_nyquist(f_sig, f_s)}")
```

### 1.3 Repliement spectral (Aliasing)

Quand $f_s < 2 f_{max}$, les hautes fréquences se replient dans la bande $[0, f_s/2]$, créant des artefacts impossibles à distinguer du signal utile.

**Règle absolue :** Toujours placer un **filtre anti-aliasing analogique (passe-bas)** en amont de l'ADC, avec $f_c \leq f_s/2$.

### 1.4 Reconstruction et théorème d'interpolation

La reconstruction idéale utilise la fonction sinc :

$$x_c(t) = \sum_{n=-\infty}^{\infty} x[n] \cdot \mathrm{sinc}\left(\frac{t - nT_s}{T_s}\right)$$

où $\mathrm{sinc}(x) = \frac{\sin(\pi x)}{\pi x}$.

En pratique : reconstruction par **CIC (Cascaded Integrator-Comb)** + filtre FIR de lissage.

---

## 2. Quantification

### 2.1 Quantification uniforme

Un convertisseur A/N sur $B$ bits quantifie l'amplitude sur $2^B$ niveaux. Pas de quantification :

$$\Delta = \frac{V_{ref}}{2^B}$$

Erreur de quantification (bruit) uniformément distribuée sur $[-\Delta/2, \Delta/2]$ :

$$e_q[n] = x_q[n] - x[n]$$

```python
def quantifier(signal, bits=16, v_ref=1.0):
    niveaux = 2 ** bits
    delta = 2 * v_ref / niveaux
    signal_q = np.round(signal / delta) * delta
    signal_q = np.clip(signal_q, -v_ref, v_ref)
    return signal_q

bits_range = [8, 12, 16, 24]
for b in bits_range:
    sqnr = 6.02 * b + 1.76  # dB (signal sinusoïdal pleine échelle)
    print(f"SQNR {b}-bit : {sqnr:.1f} dB")
```

**SQNR théorique :** $\mathrm{SQNR_{dB}} = 6.02B + 1.76\ \text{dB}$ (pour sinusoïde pleine échelle).

| Bits | SQNR (dB) | Usage typique |
|:---:|:---:|---|
| 8 | 49.9 | Audio basse qualité, téléphonie |
| 12 | 74.0 | Acquisition rapide, oscilloscopes |
| 16 | 98.1 | Audio CD, instrumentation |
| 24 | 146.3 | Audio studio, mesures précises |

### 2.2 Bruit de quantification et dithering

```python
def ajouter_dither(signal, amplitude=0.5):
    dither = np.random.uniform(-amplitude, amplitude, size=signal.shape)
    return signal + dither
```

### 2.3 Companding (loi A / loi µ)

Utilisé en téléphonie pour améliorer le SQNR des petits signaux :

- **Loi µ** (Amérique du Nord, Japon) : $\mu = 255$
- **Loi A** (Europe, reste du monde) : $A = 87.6$

```python
def loi_a_compresser(x, A=87.6):
    Ax = np.abs(x)
    y = np.where(Ax < 1/A, A * Ax, 1 + np.log(A * Ax)) / (1 + np.log(A))
    return np.sign(x) * y

def loi_a_decompresser(y, A=87.6):
    Ay = np.abs(y)
    x = np.where(Ay < 1/(1+np.log(A)),
                 Ay / A * (1 + np.log(A)),
                 np.exp(Ay * (1 + np.log(A)) - 1) / A)
    return np.sign(y) * x
```

---

## 3. Systèmes Linéaires Invariants dans le Temps (LTI)

### 3.1 Réponse impulsionnelle et convolution

Un système LTI discret est entièrement caractérisé par sa réponse impulsionnelle $h[n]$ :

$$y[n] = x[n] * h[n] = \sum_{k=-\infty}^{\infty} x[k] \cdot h[n-k]$$

```python
def convolution_directe(x, h):
    Nx, Nh = len(x), len(h)
    y = np.zeros(Nx + Nh - 1)
    for n in range(len(y)):
        for k in range(max(0, n-Nh+1), min(n+1, Nx)):
            y[n] += x[k] * h[n-k]
    return y
```

### 3.2 Stabilité et causalité

- **BIBO stable :** $\sum_{n=-\infty}^{\infty} |h[n]| < \infty$
- **Causal :** $h[n] = 0$ pour $n < 0$

### 3.3 Transformée en Z

$$X(z) = \sum_{n=-\infty}^{\infty} x[n] z^{-n}, \quad z = re^{j\omega}$$

**Propriétés clés :**
- **Région de convergence (RDC)** : Détermine la stabilité. Un système causal stable a tous ses pôles à l'intérieur du cercle unité $|z| < 1$.
- **Retard :** $x[n-k] \leftrightarrow z^{-k} X(z)$
- **Convolution :** $x[n] * h[n] \leftrightarrow X(z) H(z)$

```python
def poles_zeros_stabilite(b, a):
    zeros = np.roots(b)
    poles = np.roots(a)
    stable = all(np.abs(p) < 1 for p in poles)
    return zeros, poles, stable
```

### 3.4 Réponse en fréquence

$$H(e^{j\omega}) = \sum_{n=-\infty}^{\infty} h[n] e^{-j\omega n}$$

```python
from scipy.signal import freqz
omega, H = freqz(b, a)
```

---

## 4. Structures de base en DSP Temps Réel

### 4.1 Buffer circulaire

```c
typedef struct {
    float *buffer;
    uint32_t size;
    uint32_t head;
    uint32_t tail;
    uint32_t count;
} ring_buffer_t;

void rb_init(ring_buffer_t *rb, float *mem, uint32_t size) {
    rb->buffer = mem;
    rb->size = size;
    rb->head = 0;
    rb->tail = 0;
    rb->count = 0;
}

int rb_write(ring_buffer_t *rb, float sample) {
    if (rb->count == rb->size) return -1;
    rb->buffer[rb->head] = sample;
    rb->head = (rb->head + 1) % rb->size;
    rb->count++;
    return 0;
}

int rb_read(ring_buffer_t *rb, float *sample) {
    if (rb->count == 0) return -1;
    *sample = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) % rb->size;
    rb->count--;
    return 0;
}
```

### 4.2 Double buffer DMA

```c
#define BUF_SIZE 1024
uint16_t buf_a[BUF_SIZE];
uint16_t buf_b[BUF_SIZE];
volatile uint8_t buf_ready = 0;

void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef* hadc) {
    buf_ready = 1;
}

while (1) {
    if (buf_ready) {
        buf_ready = 0;
        process_buffer(buf_a, BUF_SIZE);
    }
}
```

### 4.3 Décimation et interpolation

**Décimation :** Réduire $f_s$ par un facteur $M$. Nécessite un filtre anti-aliasing avant le sous-échantillonnage.

**Interpolation :** Augmenter $f_s$ par un facteur $L$. Insérer $L-1$ zéros entre chaque échantillon, puis filtrer passe-bas.

```python
from scipy.signal import decimate, resample
x_dec = decimate(x, q=4, ftype='fir')
x_res = resample(x, int(len(x) * L / M))
```

---

## 5. Architecture d'une chaîne DSP

```
Monde analogique → [Capteur] → [Conditionnement] → [Anti-aliasing] → [ADC]
                                                                        |
                                                                    [Numérisation]
                                                                        |
                                                              [Prétraitement]
                                                              - DC removal
                                                              - Normalisation
                                                              - Fenêtrage
                                                                        |
                                                              [Traitement central]
                                                              - Filtrage FIR/IIR
                                                              - FFT/analyse spectrale
                                                              - Démodulation
                                                              - Détection
                                                                        |
                                                              [Post-traitement]
                                                              - DAC / Affichage
                                                              - Décision / Stockage
```

---

## 6. Outils et Bibliothèques

### Python

| Bibliothèque | Usage |
|:---|---|
| `numpy` | Opérations vectorielles, FFT (`np.fft`) |
| `scipy.signal` | Conception de filtres, convolution, STFT, corrélation |
| `sounddevice` | Acquisition/lecture audio temps réel |
| `librosa` | Analyse audio avancée (MFCC, chroma) |

### C/C++ embarqué

| Bibliothèque | Usage |
|:---|---|
| **ARM CMSIS-DSP** | FIR, IIR, FFT, matrices sur Cortex-M |
| **ESP-DSP** | FFT, filtres, matrices sur ESP32 |
| **libfixmath** | Virgule fixe 32 bits sans FPU |
| **liquid-dsp** | DSP pour SDR (modulation, synchronisation) |

---

## Pièges Courants

1. **Pas de filtre anti-aliasing :** Toute fréquence $> f_s/2$ se replie dans la bande utile.
2. **FFT sans fenêtrage :** Fuite spectrale (spectral leakage) — lobes latéraux à -13 dB.
3. **Instabilité IIR en virgule fixe :** La quantification déplace les pôles — vérifier $|p_k| < 1$ après quantification.
4. **Wrap-around en convolution circulaire :** Toujours zero-padder à $N \geq N_x + N_h - 1$ avant FFT.
5. **Dépassement en accumulation fixe :** Un accumulateur 32 bits peut déborder avec >32768 échantillons en Q15.

---

## Liste de vérification (Checklist)

- [ ] Fréquence d'échantillonnage $f_s \geq 2 f_{max}$.
- [ ] Filtre anti-aliasing analogique en amont de l'ADC ($f_c \leq f_s/2$).
- [ ] Quantification suffisante pour la dynamique du signal (SNR cible).
- [ ] Stabilité vérifiée (pôles dans le cercle unité pour les IIR).
- [ ] Fenêtrage appliqué avant analyse FFT.
- [ ] Double buffer DMA configuré (pas de perte d'échantillon).
- [ ] Budget temps réel : $T_{\text{traitement}} < T_{\text{ech}} \times N_{\text{buffer}}$.
- [ ] Test sur sinusoïdes pures avant signaux réels.
- [ ] Code optimisé SIMD (CMSIS-DSP, ESP-DSP) sur cible embarquée.