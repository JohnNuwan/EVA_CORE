---
name: fft-algorithms
description: "Algorithmes de Transformée de Fourier Rapide (FFT) — Cooley-Tukey, Radix-2/4, Rader, Bluestein, Goertzel, analyse spectrale, fenêtrage, STFT, DCT, MDCT, implémentations CPU/GPU."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [fft, fast-fourier-transform, cooley-tukey, radix-2, radix-4, rader, bluestein, goertzel, spectre, fenetrage, stft, dct, mdct, spectral-analysis, python, numpy, scipy, cuda, cufft, vkfft, cmsis-dsp, ESP-DSP]
    related_skills: [dsp-fundamentals, fir-iir-filters, convolution-signal-processing, wavelet-analysis, modulation-demodulation, signal-processing-digital]
---

# Algorithmes FFT et Analyse Spectrale

## Vue d'ensemble

La Transformée de Fourier Rapide (FFT) est un algorithme qui calcule la Transformée de Fourier Discrète (TFD) en $O(N \log N)$ au lieu de $O(N^2)$. C'est l'un des algorithmes les plus importants du XXe siècle, fondamental pour l'analyse spectrale, les télécommunications, le traitement audio, le radar et la SDR.

### Complexité algorithmique

| Algorithme | Complexité | Usage |
|:---|---:|---|
| TFD naïve | $O(N^2)$ | Pédagogique, très petites séquences |
| **FFT Radix-2** | $O(N \log_2 N)$ | Standard, N puissance de 2 |
| **FFT Radix-4** | $O(N \log_4 N)$ | ~25% plus rapide que Radix-2, DSP optimisé |
| **Split-Radix** | $O(N \log_2 N)$ | Meilleur ratio multiplications/additions connu |
| **Rader** | $O(N \log N)$ | N premier |
| **Bluestein** | $O(N \log N)$ | N quelconque (zero-padded FFT) |
| **Goertzel** | $O(N \cdot M)$ | Extraction de M fréquences spécifiques |

---

## 1. Transformée de Fourier Discrète (TFD)

### 1.1 Définition

$$X[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-j2\pi kn/N}, \quad k = 0, 1, \dots, N-1$$

Transformée inverse (TFD⁻¹) :

$$x[n] = \frac{1}{N} \sum_{k=0}^{N-1} X[k] \cdot e^{j2\pi kn/N}, \quad n = 0, 1, \dots, N-1$$

```python
import numpy as np

def tfd_naive(x):
    """TFD en O(N²) — but pédagogique uniquement."""
    N = len(x)
    X = np.zeros(N, dtype=complex)
    for k in range(N):
        for n in range(N):
            X[k] += x[n] * np.exp(-2j * np.pi * k * n / N)
    return X
```

### 1.2 Propriétés fondamentales

| Propriété | Domaine temporel | Domaine fréquentiel |
|:---|---|---|
| Linéarité | $ax_1 + bx_2$ | $aX_1 + bX_2$ |
| Décalage temporel | $x[n - n_0]$ | $X[k] \cdot e^{-j2\pi kn_0/N}$ |
| Décalage fréquentiel | $x[n] \cdot e^{j2\pi k_0 n/N}$ | $X[k - k_0]$ |
| Convolution | $x * h$ | $X \cdot H$ |
| Multiplication | $x \cdot h$ | $\frac{1}{N} X * H$ (circulaire) |
| Symétrie conj. (x réel) | $x[n] \in \mathbb{R}$ | $X[-k] = X^*[k]$ |
| Parseval | $\sum\|x[n]\|^2$ | $\frac{1}{N}\sum\|X[k]\|^2$ |

---

## 2. Algorithme de Cooley-Tukey (Radix-2)

### 2.1 Principe Diviser pour Régner

La TFD de taille $N = 2^m$ est divisée en deux TFD de taille $N/2$ :

$$X[k] = \sum_{n=0}^{N/2-1} x[2n] \cdot e^{-j2\pi kn/(N/2)} + e^{-j2\pi k/N} \sum_{n=0}^{N/2-1} x[2n+1] \cdot e^{-j2\pi kn/(N/2)}$$

$$X[k] = E[k] + W_N^k \cdot O[k]$$

où $W_N^k = e^{-j2\pi k/N}$ est le **twiddle factor**, $E[k]$ la TFD des pairs, $O[k]$ la TFD des impairs.

### 2.2 Implémentation récursive

```python
def fft_radix2(x):
    """FFT Radix-2 récursive. N doit être une puissance de 2."""
    N = len(x)
    if N <= 1:
        return x

    # Diviser : indices pairs et impairs
    even = fft_radix2(x[0::2])
    odd = fft_radix2(x[1::2])

    # Twiddle factors (pré-calculer pour performance)
    W = np.exp(-2j * np.pi * np.arange(N // 2) / N)

    # Combiner
    return np.concatenate([even + W * odd, even - W * odd])

# Vérification
x = np.random.randn(1024) + 1j * np.random.randn(1024)
X1 = fft_radix2(x)
X2 = np.fft.fft(x)
print(f"Erreur max : {np.max(np.abs(X1 - X2)):.2e}")
```

### 2.3 Implémentation itérative (in-place, bit-reversal)

```python
def fft_radix2_iterative(x):
    """FFT Radix-2 itérative in-place."""
    N = len(x)

    # Bit-reversal permutation
    j = 0
    for i in range(1, N):
        bit = N >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            x[i], x[j] = x[j], x[i]

    # Boucle FFT (butterfly)
    length = 2
    while length <= N:
        angle = -2 * np.pi / length
        wlen = complex(np.cos(angle), np.sin(angle))
        for i in range(0, N, length):
            w = 1 + 0j
            for j in range(i, i + length // 2):
                u = x[j]
                v = x[j + length // 2] * w
                x[j] = u + v
                x[j + length // 2] = u - v
                w *= wlen
        length <<= 1
    return x
```

### 2.4 Butterfly Radix-2

```
Entrée : a = E[k], b = W_N^k · O[k]
Sortie  : A = a + b   (branche supérieure)
          B = a - b   (branche inférieure)

Représentation :
    a ──→ (+)── A = a + b
            ↑
    b ──→ (+)── B = a - b
```

---

## 3. Variantes de FFT

### 3.1 Radix-4

Au lieu de diviser en 2 sous-problèmes, divise en 4. Nécessite $N = 4^m$.

- Avantage : ~25% moins de multiplications que Radix-2
- Utilisé dans : **ARM CMSIS-DSP** (`arm_cfft_radix4_f32`), **FFTW**

```c
// CMSIS-DSP : FFT Radix-4 flottant
arm_cfft_instance_f32 fft;
arm_cfft_init_f32(&fft, 1024);   // Taille de FFT
arm_cfft_f32(&fft, buffer, 0, 1); // 0=forward, 1=bit-reversal
```

### 3.2 Split-Radix

Mélange Radix-2 et Radix-4. Meilleur ratio multiplications/additions connu pour N puissance de 2 (~33% moins d'opérations que Radix-2).

- Utilisé dans : **FFTW** (planification automatique)

### 3.3 Algorithme de Rader (N premier)

Pour $N$ premier, réorganise la TFD en une convolution cyclique via une racine primitive modulo $N$, calculable par FFT ($O(N \log N)$).

### 3.4 Algorithme de Bluestein (N quelconque)

Transforme toute TFD de taille $N$ en une convolution de taille $M \geq 2N - 1$ (puissance de 2), calculable par FFT.

```python
def fft_bluestein(x):
    """FFT chirp Z-transform (Bluestein) pour N quelconque."""
    N = len(x)
    M = 1
    while M < 2 * N - 1:
        M <<= 1

    # Chirp factors
    W = np.exp(-1j * np.pi * np.arange(N)**2 / N)

    # Signal étendu + zero-padded
    a = x * W
    a = np.pad(a, (0, M - N))

    # Filtre chirp
    b = np.exp(1j * np.pi * np.arange(M)**2 / N)
    b = np.pad(b, (0, M - len(b)))

    # Convolution par FFT
    A = np.fft.fft(a)
    B = np.fft.fft(b)
    conv = np.fft.ifft(A * B)

    return W.conj() * conv[:N]

# Test : N = 1000 (pas une puissance de 2)
x = np.random.randn(1000)
X1 = fft_bluestein(x)
X2 = np.fft.fft(x)
print(f"Erreur Bluestein : {np.max(np.abs(X1 - X2)):.2e}")
```

### 3.5 Algorithme de Goertzel (M fréquences)

Idéal pour détecter quelques fréquences spécifiques (DTMF, tonalités) sans calculer toute la FFT.

```python
def goertzel(x, target_freq, fs):
    """
    Détecte une fréquence spécifique dans un signal.

    Paramètres :
        x           : signal d'entrée
        target_freq : fréquence à détecter (Hz)
        fs          : fréquence d'échantillonnage (Hz)

    Retourne : amplitude et phase à target_freq
    """
    N = len(x)
    k = int(0.5 + N * target_freq / fs)  # Bin le plus proche
    omega = 2 * np.pi * k / N
    coeff = 2 * np.cos(omega)

    s0, s1, s2 = 0.0, 0.0, 0.0
    for n in range(N):
        s0 = x[n] + coeff * s1 - s2
        s2 = s1
        s1 = s0

    # Calcul de l'amplitude et de la phase
    real = s1 - s2 * np.cos(omega)
    imag = s2 * np.sin(omega)
    amplitude = np.sqrt(real**2 + imag**2) / N
    phase = np.arctan2(imag, real)

    return amplitude, phase

# Détection DTMF : touche '5' = 770 Hz + 1336 Hz
```

**DTMF avec Goertzel :** Chaque touche émet 2 fréquences simultanées. 8 fréquences totales, 8 appels à Goertzel suffisent — beaucoup plus efficace qu'une FFT complète.

---

## 4. Fenêtrage (Windowing)

### 4.1 Pourquoi fenêtrer ?

Une FFT sur N échantillons tronque brutalement le signal (fenêtre rectangulaire). Cette troncature crée des **lobes latéraux** (spectral leakage) qui masquent les petites amplitudes près de pics forts.

```python
def generer_fenetre(N, type_fenetre="hann"):
    fenetres = {
        "rect": np.ones(N),
        "hann": 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(N) / (N - 1)),
        "hamming": 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(N) / (N - 1)),
        "blackman": (0.42 - 0.5 * np.cos(2 * np.pi * np.arange(N) / (N - 1))
                     + 0.08 * np.cos(4 * np.pi * np.arange(N) / (N - 1))),
        "kaiser": np.kaiser(N, beta=14),
        "flattop": (0.2156 - 0.4160 * np.cos(2 * np.pi * np.arange(N) / (N - 1))
                    + 0.2781 * np.cos(4 * np.pi * np.arange(N) / (N - 1))
                    - 0.0836 * np.cos(6 * np.pi * np.arange(N) / (N - 1))
                    + 0.0069 * np.cos(8 * np.pi * np.arange(N) / (N - 1))),
    }
    return fenetres.get(type_fenetre, fenetres["hann"])
```

### 4.2 Comparaison des fenêtres

| Fenêtre | Lobe princ. (bins) | Lobe lat. max | Atténuation | Usage |
|:---|---|---|---:|---|
| Rectangulaire | 0.89 | -13 dB | 6 dB/oct | Transitoires |
| Hann | 1.44 | -31 dB | 18 dB/oct | Usage général |
| Hamming | 1.30 | -43 dB | 6 dB/oct | Communications |
| Blackman | 1.68 | -58 dB | 18 dB/oct | Haute dynamique |
| Kaiser ($\beta$=14) | 1.80 | -60 dB | Ajustable | Arbitraire (réglage $\beta$) |
| Flat-top | 2.94 | -74 dB | 6 dB/oct | Mesure précise d'amplitude |

### 4.3 Perte de gain cohérent (coherent gain)

```python
# La fenêtre réduit l'amplitude mesurée. Facteur de correction :
def coherent_gain(fenetre):
    return np.mean(fenetre)

# Exemple : Hann a un gain cohérent de 0.5
# Pour compenser : amplitude_corrigee = amplitude / coherent_gain
```

### 4.4 Recouvrement (overlap) pour STFT

Pour l'analyse temps-fréquence (spectrogramme), on applique la FFT sur des segments fenêtrés avec recouvrement :

- **50% overlap** : Standard (Hann)
- **75% overlap** : Haute résolution temporelle
- **0% overlap** : Pas de redondance, artefact aux bords

```python
from scipy.signal import spectrogram

f, t, Sxx = spectrogram(signal, fs=44100,
                        window='hann',
                        nperseg=2048,
                        noverlap=1536,  # 75%
                        scaling='density')
Sxx_dB = 10 * np.log10(Sxx + 1e-10)
```

---

## 5. Transformées Connexes

### 5.1 DCT (Discrete Cosine Transform)

Utilisée en compression (JPEG, MPEG, MP3, AAC) et filtrage.

$$X[k] = \sum_{n=0}^{N-1} x[n] \cdot \cos\left[\frac{\pi}{N}\left(n + \frac{1}{2}\right)k\right]$$

```python
from scipy.fft import dct, idct

# DCT type II (le plus courant)
X_dct = dct(x, type=2, norm='ortho')
x_rec = idct(X_dct, type=2, norm='ortho')

# Propriété : excellent compactage d'énergie
# Les premiers coefficients DCT concentrent ~95% de l'énergie
```

**Avantage sur FFT :** Pas de discontinuité aux bords (extension paire implicite) → moins de fuite spectrale pour les signaux naturels (images, audio).

### 5.2 MDCT (Modified Discrete Cosine Transform)

Transformée à recouvrement utilisée dans les codecs audio modernes (AAC, Opus, Vorbis, MP3) :

- Fenêtre sinusoïdale avec 50% de recouvrement
- Condition de **perfect reconstruction** (PR)
- Réduction des artefacts de bloc (blocking artifacts)

```python
# Principe MDCT (simplifié)
N = 2048  # Taille de la fenêtre
hop = N // 2  # 50% overlap

for start in range(0, len(signal) - N, hop):
    block = signal[start:start + N]
    windowed = block * np.sin(np.pi * (np.arange(N) + 0.5) / N)
    # MDCT : DCT-IV sur la moitié
    mdct_coeffs = dct(windowed, type=4)[:N//2]
```

### 5.3 FFT 2D (traitement d'image)

```python
from scipy.fft import fft2, ifft2, fftshift

# FFT 2D d'une image
image = np.random.randn(256, 256)
F = fft2(image)
F_shifted = fftshift(F)  # DC au centre

# Filtrage dans le domaine fréquentiel
rows, cols = image.shape
crow, ccol = rows // 2, cols // 2
mask = np.zeros((rows, cols))
r = 30
Y, X = np.ogrid[:rows, :cols]
mask_area = (X - ccol)**2 + (Y - crow)**2 <= r**2
mask[mask_area] = 1  # Passe-bas

F_filtered = F_shifted * mask
image_filtered = ifft2(fftshift(F_filtered)).real
```

---

## 6. Implémentations Haute Performance

### 6.1 FFTW (Fastest Fourier Transform in the West)

La bibliothèque FFT la plus rapide au monde. Planification automatique :

```c
#include <fftw3.h>

fftw_complex *in, *out;
fftw_plan p;

in = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * N);
out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * N);

// Planification (mesure = optimal, ~secondes)
p = fftw_plan_dft_1d(N, in, out, FFTW_FORWARD, FFTW_MEASURE);

// Exécution
fftw_execute(p);

// Pour SDR temps réel : FFTW_PATIENT (optimal) ou FFTW_ESTIMATE (rapide)
fftw_destroy_plan(p);
fftw_free(in);
fftw_free(out);
```

### 6.2 cuFFT (NVIDIA GPU)

```c
#include <cufft.h>

cufftHandle plan;
cufftComplex *d_data;

cudaMalloc(&d_data, N * sizeof(cufftComplex));
cufftPlan1d(&plan, N, CUFFT_C2C, 1);
cufftExecC2C(plan, d_data, d_data, CUFFT_FORWARD);
cudaDeviceSynchronize();
cufftDestroy(plan);
```

### 6.3 VkFFT (GPU multi-vendeur)

FFT sur GPU via Vulkan Compute. Supporte AMD, NVIDIA, Intel, Apple Silicon.

```c
// Configuration VkFFT
VkFFTConfiguration config = {};
config.FFTdim = 1;
config.size[0] = 1024;
config.performR2C = 1;  // Real-to-complex

VkFFTApplication app;
initializeVkFFT(&app, config);
VkFFTLaunchParams params = {};
app.VkFFT(&params, 0, 1);
```

### 6.4 CMSIS-DSP (ARM Cortex-M)

```c
// FFT 1024 points, flottant, Radix-4
arm_cfft_instance_f32 fft;
arm_cfft_init_f32(&fft, 1024);
arm_cfft_f32(&fft, input, 0, 1);       // Forward
arm_cmplx_mag_f32(input, magnitude, 1024);  // Magnitude

// Version virgule fixe Q15 (sans FPU)
arm_cfft_instance_q15 fft_q15;
arm_cfft_init_q15(&fft_q15, 1024);
arm_cfft_q15(&fft_q15, input_q15, 0, 1);
```

### 6.5 ESP-DSP (ESP32)

```c
#include <esp_dsp.h>

float data[FFT_SIZE * 2];  // Interleaved complex
float window[FFT_SIZE];

dsps_wind_hann_f32(window, FFT_SIZE);
// Fenêtrage + FFT
for (int i = 0; i < FFT_SIZE; i++) {
    data[i * 2] = samples[i] * window[i];
    data[i * 2 + 1] = 0;
}
dsps_fft2r_fc32(data, FFT_SIZE);
dsps_bit_rev_fc32(data, FFT_SIZE);
// Magnitude
dsps_cplx2re_fc32(data, FFT_SIZE);
```

---

## 7. Analyse Spectrale Avancée

### 7.1 Zero-padding

Ajouter des zéros avant FFT pour interpoler le spectre (meilleure visualisation, pas de résolution réelle) :

```python
N = 1024
x = signal[:512]  # 512 échantillons réels
x_padded = np.pad(x, (0, 1536))  # Zero-pad à 2048
X = np.fft.fft(x_padded)  # Résolution : fs/2048 au lieu de fs/512
```

### 7.2 Zoom FFT

Analyse fine d'une bande étroite : décaler (hétérodyne) + filtrer passe-bas + décimer + FFT.

```python
def zoom_fft(signal, fs, f_center, bandwidth, N_fft=1024):
    """
    Zoom FFT : analyse haute résolution d'une bande étroite.
    """
    # Hétérodyne : décaler f_center vers DC
    t = np.arange(len(signal)) / fs
    decal = signal * np.exp(-2j * np.pi * f_center * t)

    # Filtre passe-bas (largeur = bandwidth/2)
    # ...

    # Décimation
    M = int(fs / bandwidth)
    decimated = decal[::M]

    # FFT sur la bande réduite
    X = np.fft.fft(decimated[:N_fft])
    return X
```

### 7.3 Méthodes paramétriques (haute résolution)

Quand la résolution de la FFT est insuffisante (signaux sinusoïdaux proches) :

| Méthode | Avantage | Inconvénient |
|:---|---|---|
| **Burg** (AR) | Haute résolution, signaux courts | Artefacts (spurious peaks) |
| **MUSIC** | Résolution infinie, bruit blanc | Coût calculatoire élevé |
| **ESPRIT** | Idem MUSIC, plus rapide | Moins robuste au bruit |
| **Capon** | Bon compromis | Résolution limitée |

```python
from scipy.signal import periodogram, welch, lombscargle

# Welch : PSD moyennée (périodogramme modifié)
f, Pxx = welch(signal, fs=fs, nperseg=1024, noverlap=768)

# Lomb-Scargle : spectre d'échantillons non-uniformément espacés
f, Pxx = lombscargle(t_irregulier, signal, f)
```

---

## 8. Métriques de l'Analyse Spectrale

| Métrique | Formule | Signification |
|:---|---:|---|
| Résolution fréquentielle | $\Delta f = f_s / N$ | Plus petit écart de fréquence distinguable |
| Résolution temporelle | $\Delta t = N / f_s$ | Durée de la fenêtre d'analyse |
| SNR (pic au bruit) | $10\log_{10}(A_{pic}^2 / \sigma_{bruit}^2)$ | Qualité de détection |
| SFDR (Spurious Free Dynamic Range) | $A_{pic} / A_{spur\_max}$ | Pureté spectrale (ADC/DAC) |
| ENOB (Effective Number Of Bits) | $(SFDR - 1.76)/6.02$ | Performance réelle ADC |
| THD (Total Harmonic Distortion) | $\sqrt{\sum A_{harm}^2} / A_{fond}$ | Distorsion non-linéaire |

---

## Pièges Courants

1. **FFT sans fenêtrage :** Fuite spectrale massive (-13 dB). Toujours fenêtrer.
2. **Zero-padding pour résolution :** N'augmente pas la résolution réelle — seulement l'interpolation. La résolution vient de $N_{échantillons}$.
3. **N non puissance de 2 (FFT lente) :** La FFT naïve sur N non-puissance-de-2 peut être $O(N^2)$. Utiliser Bluestein ou FFTW.
4. **CREST factor non respecté :** Un ADC avec $V_{ref}=1V$ écrête un signal à 0 dBFS. Laisser 12-20 dB de headroom pour les signaux réels.
5. **Phase non déroulée (unwrapped) :** `np.angle()` retourne dans $[-\pi, \pi]$. Utiliser `np.unwrap()` pour la phase continue.
6. **FFT 2D non centrée :** Le DC est aux coins. Utiliser `fftshift()` pour centrer.

---

## Liste de vérification (Checklist)

- [ ] Fenêtrage appliqué avant FFT (sauf analyse transitoire).
- [ ] N puissance de 2 pour Radix-2, ou Bluestein/FFTW pour N quelconque.
- [ ] Zero-padding utilisé uniquement pour l'interpolation, pas pour la résolution.
- [ ] Headroom ADC suffisant (pas d'écrêtage).
- [ ] Overlap approprié pour la STFT (75% standard).
- [ ] Phase déroulée pour l'analyse de phase continue.
- [ ] FFTW planifié (MEASURE/PATIENT) pour applications temps réel.
- [ ] cuFFT/VkFFT utilisé si GPU disponible et N ≥ 4096.
- [ ] Fonction de transfert calibrée (compensation de la fenêtre).