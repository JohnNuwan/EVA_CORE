---
name: signal-processing-digital
description: "Traiter des signaux numériques en temps réel et hors ligne — filtres FIR/IIR, transformée de Fourier (FFT), analyse spectrale, convolution, échantillonnage, décimation/interpolation, corrélation et méthodes adaptatives."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [traitement-signal, dsp, digital-signal-processing, fft, fir, iir, filtre-numérique, convolution, échantillonnage, décimation, interpolation, corrélation, spectre, python, numpy, scipy, c-plus-plus, arm-dsp, fixed-point, adaptive-filter]
    related_skills: [esp32-iot, stm32-arm-cortex, embedded-systems-firmware, fpga-verilog-vhdl, electronique-analogique]
---

# Traitement Numérique du Signal (DSP)

## Vue d'ensemble

Le traitement numérique du signal (DSP — Digital Signal Processing) analyse et manipule des signaux numériques (échantillons temporels) pour extraire de l'information, filtrer le bruit, compresser des données, ou démoduler des signaux. Cette compétence couvre les techniques fondamentales et avancées du DSP, exécutables sur CPU, DSP dédié, FPGA ou microcontrôleur (ARM Cortex-M4 avec FPU et instructions SIMD).

### Domaines d'application

| Domaine | Applications DSP |
|:---|---|
| **Audio** | Filtrage audio, égaliseurs, réduction de bruit, compression MP3/AAC, détection de tonalités (DTMF) |
| **Instrumentation** | Analyse vibratoire (FFT des accéléromètres), mesures de fréquence, lock-in amplifier |
| **Télécommunications** | Modulation/démodulation (QPSK, QAM), correction d'erreur, filtrage adaptatif (écho) |
| **Biomédical** | ECG (filtrage des artefacts), EEG (bandes alpha/bêta), analyse de pouls |
| **Industrie** | Détection d'anomalies par signature fréquentielle, analyse harmonique des courants moteurs, commande de puissance (MLI) |
| **Radar/Sonar** | Compression d'impulsion, filtrage adapté (matched filter), Doppler |

### Chaîne de traitement typique

```
Signal analogique → [Anti-aliasing] → [ADC] → [Échantillonnage] → [Prétraitement]
    ↓
[Filtrage] → [Analyse fréquentielle (FFT)] → [Extraction de features] → [Décision]
    ↓
[Synthèse/DAC] → [Signal analogique de sortie]
```

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Concevoir un filtre numérique (passe-bas, passe-haut, passe-bande, coupe-bande) pour éliminer le bruit d'un signal.
- Calculer la FFT d'un signal pour analyser son contenu spectral (fréquences dominantes, harmoniques).
- Implémenter un algorithme de traitement du signal en temps réel sur microcontrôleur (STM32, ESP32) avec ARM CMSIS-DSP.
- Réaliser une corrélation croisée pour détecter un motif connu dans un signal bruité (détection de préambule, radar).
- Mettre en œuvre un filtre adaptatif (LMS, NLMS) pour la réduction de bruit active ou l'annulation d'écho.
- Traiter des signaux audio (filtrage, analyse temps-fréquence, feature extraction MFCC).
- Convertir la fréquence d'échantillonnage (décimation, interpolation, resampling).

Ne pas utiliser pour : l'analyse statistique de données (utiliser `data-analysis-exploration`), le traitement d'image (préférer OpenCV), l'apprentissage profond sur signaux (préférer PyTorch/TensorFlow).

---

## 1. Fondamentaux du DSP

### 1.1 Échantillonnage et théorème de Nyquist

```python
import numpy as np
import matplotlib.pyplot as plt

# Théorème de Nyquist-Shannon :
# f_échantillonnage >= 2 × f_max (fréquence maximale du signal)

# Exemple : Si f_max = 5 kHz, alors f_s >= 10 kHz
f_max = 5000  # Hz
f_ech = 20000 # Hz (Nyquist OK : 2× f_max)
T_ech = 1 / f_ech

print(f"Fréquence d'échantillonnage : {f_ech} Hz")
print(f"Période d'échantillonnage : {T_ech*1e6:.1f} µs")
print(f"Fréquence de Nyquist : {f_ech/2} Hz")

# Conséquence du repliement spectral (aliasing)
# Si f_s < 2×f_max, les fréquences > f_s/2 se replient
# dans la bande base (aliasing), créant des artefacts.

def check_aliasing(f_signal, f_ech):
    """Vérifie si un signal est correctement échantillonné."""
    f_nyquist = f_ech / 2
    if f_signal < f_nyquist:
        return "OK — fréquence mesurable"
    else:
        f_aliased = abs(f_signal - f_ech * round(f_signal / f_ech))
        return f"ALIASING — la fréquence mesurée sera fausse : ~{f_aliased:.1f} Hz"

cas = [
    ("1 kHz signal, 10 kHz échantillonnage", 1000, 10000),
    ("8 kHz signal, 10 kHz échantillonnage", 8000, 10000),  # > Nyquist !
    ("22 kHz signal, 44.1 kHz CD audio", 22000, 44100),
]
for desc, f_sig, f_s in cas:
    print(f"{desc}: {check_aliasing(f_sig, f_s)}")
```

**Règle pratique :** Pour un ADC, placer un filtre anti-aliasing (analogique, passe-bas) en amont, avec une fréquence de coupure $f_c < f_s / 2$.

### 1.2 Transformée de Fourier Rapide (FFT)

```python
import numpy as np
from scipy.fft import fft, fftfreq

def compute_spectrum(signal: np.ndarray, fs: float) -> dict:
    """
    Calcule le spectre de fréquence d'un signal.

    Paramètres :
        signal : tableau d'échantillons
        fs     : fréquence d'échantillonnage (Hz)

    Retourne :
        fréquences (Hz), amplitudes, phase (rad), résolution fréquentielle
    """
    N = len(signal)
    f_res = fs / N  # Résolution fréquentielle (Hz/bin)

    # FFT et normalisation
    X = fft(signal)
    X = X[:N // 2]  # Symétrie : ne garder que la moitié positive
    amplitudes = 2.0 / N * np.abs(X)   # Amplitude réelle
    phase = np.angle(X)                 # Phase en radians
    freq = fftfreq(N, 1/fs)[:N // 2]   # Vecteur de fréquences

    return {
        "freq": freq,
        "amplitude": amplitudes,
        "phase": phase,
        "resolution_hz": f_res,
        "n_fft": N,
        "bin_max": np.argmax(amplitudes),
        "freq_max_hz": freq[np.argmax(amplitudes)],
    }

# Signal synthétique : 50 Hz + 120 Hz + bruit
fs = 1000  # Hz
t = np.arange(0, 1.0, 1/fs)
signal = 0.7 * np.sin(2 * np.pi * 50 * t) + \
         0.3 * np.sin(2 * np.pi * 120 * t) + \
         0.1 * np.random.randn(len(t))

spectrum = compute_spectrum(signal, fs)
print(f"Fréquence dominante : {spectrum['freq_max_hz']:.1f} Hz")
print(f"Résolution fréquentielle : {spectrum['resolution_hz']:.2f} Hz")
```

### 1.3 Fenêtrage (Windowing)

```python
import numpy as np

# Le fenêtrage réduit les fuites spectrales (spectral leakage)
# causées par la troncature brutale du signal à N échantillons.

def apply_window(N: int, window_type: str = "hann") -> np.ndarray:
    """
    Génère une fenêtre pour la FFT.

    Types : hann, hamming, blackman, kaiser (beta=14), flattop.
    """
    windows = {
        "rect": np.ones(N),                            # Aucune fenêtre (fuite max)
        "hann": 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(N) / (N - 1)),
        "hamming": 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(N) / (N - 1)),
        "blackman": 0.42 - 0.5 * np.cos(2 * np.pi * np.arange(N) / (N - 1)) +
                   0.08 * np.cos(4 * np.pi * np.arange(N) / (N - 1)),
        "flattop": (0.2156 - 0.4160 * np.cos(2 * np.pi * np.arange(N) / (N - 1)) +
                    0.2781 * np.cos(4 * np.pi * np.arange(N) / (N - 1)) -
                    0.0836 * np.cos(6 * np.pi * np.arange(N) / (N - 1)) +
                    0.0069 * np.cos(8 * np.pi * np.arange(N) / (N - 1))),
    }
    return windows.get(window_type, windows["hann"])

# Choix de la fenêtre selon l'application
# | Fenêtre | Largeur lobe principal | Atténuation lobe secondaire | Usage |
# |:---|---|---:|---:|
# | Rect | 0.89 bins | -13 dB | Transitoires, calibration |
# | Hann | 1.44 bins | -31 dB | Usage général, audio |
# | Hamming | 1.30 bins | -43 dB | Communication, proche de pics |
# | Blackman | 1.68 bins | -58 dB | Haute dynamique, analyse fine |
# | Flat-top | 2.94 bins | -74 dB | Mesure précise d'amplitude |

# Application de la fenêtre avant FFT
N = 1024
window = apply_window(N, "hann")
signal_fenetre = signal[:N] * window
```

---

## 2. Filtres Numériques

### 2.1 Filtres RIF (FIR — Réponse Impulsionnelle Finie)

```python
from scipy import signal as sp_signal
import numpy as np

def design_fir(fs: float, f_pass: float, f_stop: float,
               a_pass_db: float = 0.5, a_stop_db: float = 60) -> dict:
    """
    Conception d'un filtre FIR passe-bas par la méthode de Parks-McClellan.

    Paramètres :
        fs       : fréquence d'échantillonnage (Hz)
        f_pass   : fréquence de la bande passante (Hz)
        f_stop   : fréquence du début de la bande atténuée (Hz)
        a_pass_db: ondulation max dans la bande passante (dB)
        a_stop_db: atténuation minimum dans la bande arrêtée (dB)

    Retourne :
        coefficients b, ordre N, délai de groupe
    """
    # Normalisation des fréquences
    f = np.array([0, f_pass, f_stop, fs / 2]) / (fs / 2)
    a = np.array([1, 1, 0, 0])  # 1 = passe, 0 = coupe

    # Estimation de l'ordre (formule de Kaiser)
    delta_f = (f_stop - f_pass) / fs
    N_est = int((a_stop_db - 7.95) / (14.36 * delta_f) + 1)

    # Conception par remez (Parks-McClellan)
    b = sp_signal.remez(N_est, f, a, [1, a_pass_db / a_stop_db],
                        fs=fs)
    N = len(b) - 1  # Ordre du filtre
    delay = N // 2   # Délai de groupe (échantillons)

    return {"b": b, "order": N, "delay": delay}

# Exemple : filtre FIR passe-bas, fc = 100 Hz, fs = 1000 Hz
result = design_fir(fs=1000, f_pass=90, f_stop=110)
print(f"Ordre du FIR : {result['order']}")
print(f"Délai de groupe : {result['delay']} échantillons")
# 102 coefficients pour cet exemple

# Application du filtre
filtered = sp_signal.convolve(signal, result["b"], mode="same")

# Avantages des FIR :
# - Toujours stables (pas de pôles)
# - Phase linéaire (pas de distorsion de phase)
# - Implémentation facile (convolutions + mémoire)
```

### 2.2 Filtres RII (IIR — Réponse Impulsionnelle Infinie)

```python
def design_iir(fs: float, f_cut: float, f_type: str = "lowpass",
               order: int = 4, ripple_db: float = 0.5) -> dict:
    """
    Conception d'un filtre IIR (Butterworth, Chebyshev, Elliptique).

    Paramètres :
        fs       : fréquence d'échantillonnage (Hz)
        f_cut    : fréquence de coupure (Hz)
        f_type   : lowpass, highpass, bandpass, bandstop
        order    : ordre du filtre
        ripple_db: ondulation max (Chebyshev/Elliptique)

    Retourne :
        coefficients b, a, type, ordre
    """
    wn = f_cut / (fs / 2)  # Normalisation

    # Butterworth : réponse maximale plate en bande passante
    b, a = sp_signal.butter(order, wn, btype=f_type)

    return {"b": b, "a": a, "type": "butterworth", "order": order}

# Exemple : filtre IIR passe-bas Butterworth, fc = 50 Hz, ordre 4
result = design_iir(fs=1000, f_cut=50, order=4)
filtered_iir = sp_signal.filtfilt(result["b"], result["a"], signal)

# Comparaison FIR vs IIR
# | Critère | FIR | IIR |
# |:---|---|---:|
# | Ordre nécessaire | Élevé (100-1000) | Faible (4-12) |
# | Stabilité | Toujours stable | Potentiellement instable |
# | Phase | Linéaire (pas de distorsion) | Non-linéaire (distorsion) |
# | Quantification | Robuste | Sensible (débordement possible) |
# | Mémoire nécessaire | N × N_coeffs | N × O(ordre) |
# | Latence | N_coeffs/2 échantillons | Faible |
```

### 2.3 Implémentation sur microcontrôleur (CMSIS-DSP)

```c
#include "arm_math.h"

// Coefficients FIR pré-calculés (exemple : fc = 1 kHz, fs = 8 kHz)
#define FIR_NUM_TAPS 32
float32_t fir_coeffs[FIR_NUM_TAPS] = { /* ... */ };

// État du filtre FIR (nécessite FIR_NUM_TAPS + block_size échantillons)
arm_fir_instance_f32 fir_instance;
static float32_t fir_state[FIR_NUM_TAPS + 256];  // 256 = taille du bloc

void fir_init(void) {
    arm_fir_init_f32(&fir_instance, FIR_NUM_TAPS,
                     fir_coeffs, fir_state, 256);
}

// Bloc de 256 échantillons traité en une fois
void process_block(float32_t *input, float32_t *output, uint32_t block_size) {
    arm_fir_f32(&fir_instance, input, output, block_size);
}

// Remplacer par une fonction de filtrage CMSIS-DSP optimisée :
// - arm_fir_f32() : 16 cycles/échantillon sur Cortex-M4F
// - arm_fir_q31() : version virgule fixe 32 bits (sans FPU)
// - arm_biquad_cascade_df1_f32() : filtre IIR biquad
```

---

## 3. Techniques Avancées

### 3.1 Transformée de Fourier à Court Terme (STFT)

```python
from scipy.signal import spectrogram

def compute_stft(signal: np.ndarray, fs: float,
                 nperseg: int = 1024, noverlap: int = 768) -> dict:
    """
    Calcule le spectrogramme (STFT) pour l'analyse temps-fréquence.

    Paramètres :
        signal  : signal temporel
        fs      : fréquence d'échantillonnage
        nperseg : longueur de chaque segment (fenêtre)
        noverlap: recouvrement entre segments (75% = 768 pour 1024)

    Retourne :
        t (temps), f (fréquences), Sxx (spectrogramme en dB)
    """
    f, t, Sxx = spectrogram(signal, fs, nperseg=nperseg,
                            noverlap=noverlap, scaling='density')
    Sxx_dB = 10 * np.log10(Sxx + 1e-10)  # Conversion dB

    return {"t": t, "f": f, "Sxx_dB": Sxx_dB}

# Usage : visualiser l'évolution spectrale d'un signal
# Utile pour : analyse de parole, vibratoire, battements cardiaques
```

### 3.2 Corrélation croisée et filtrage adapté (Matched Filter)

```python
def matched_filter(received_signal: np.ndarray, template: np.ndarray) -> dict:
    """
    Filtrage adapté : maximise le SNR pour détecter un motif connu.

    Utilisé en radar, sonar, communications (détection de préambule).

    Retourne :
        corrélation, indice du pic, SNR estimé
    """
    correlation = np.correlate(received_signal, template, mode='same')
    peak_idx = np.argmax(np.abs(correlation))
    peak_value = correlation[peak_idx]

    # Estimation du bruit en dehors du pic
    noise_floor = np.median(np.abs(correlation[correlation < 0.8 * peak_value]))
    snr_est = 20 * np.log10(peak_value / (noise_floor + 1e-10))

    return {
        "correlation": correlation,
        "peak_index": peak_idx,
        "peak_value": peak_value,
        "snr_estime_db": snr_est,
    }

# Exemple : séquence d'entraînement dans un signal
template = np.sin(2 * np.pi * 100 * np.arange(0, 0.01, 1/1000))  # 100 Hz, 10 ms
received = np.concatenate([np.random.randn(400), template * 1.5,
                           np.random.randn(600)])
result = matched_filter(received, template)
print(f"Pic de corrélation à l'échantillon #{result['peak_index']}")
```

### 3.3 Filtrage adaptatif (LMS — Least Mean Squares)

```python
def lms_filter(desired: np.ndarray, reference: np.ndarray,
               mu: float = 0.01, order: int = 32) -> np.ndarray:
    """
    Algorithme LMS pour l'annulation adaptative de bruit.

    Paramètres :
        desired  : signal souhaité (contenant le bruit à annuler)
        reference: signal de référence (bruit seul, corrélé)
        mu       : pas d'adaptation (learning rate)
        order    : ordre du filtre adaptatif

    Retourne :
        signal débruité
    """
    N = len(desired)
    w = np.zeros(order)     # Coefficients du filtre
    output = np.zeros(N)    # Signal de sortie (débruité)

    for n in range(order, N):
        # Vecteur d'entrée (fenêtre glissante)
        x = reference[n:n-order:-1]

        # Sortie du filtre adaptatif
        y = np.dot(w, x)

        # Erreur (signal débruité)
        e = desired[n] - y
        output[n] = e

        # Mise à jour des coefficients (LMS)
        w += 2 * mu * e * x / (np.dot(x, x) + 1e-6)  # Normalisé (NLMS)

    return output

# Usage : annulation de bruit 50 Hz (ronflement secteur)
# desired = signal utile + bruit 50 Hz
# reference = bruit 50 Hz pur (généré par un capteur de référence)
```

### 3.4 Traitement en virgule fixe (Q-format)

```c
// Les microcontrôleurs sans FPU (Cortex-M0/M3) et les DSP
// n'ont pas d'unité de calcul flottant.
// Le traitement en virgule fixe (Q-format) est nécessaire.

#include <stdint.h>

// Format Q15 : entier signé 16 bits, plage -1.0 à 0.99997
// Résolution : 1/32768 ≈ 3.05e-5

// Conversion
float q15_to_float(int16_t q) {
    return (float)q / 32768.0f;
}

int16_t float_to_q15(float f) {
    // Saturation : [-1.0, 1.0]
    if (f > 0.99997f) return 32767;
    if (f < -1.0f) return -32768;
    return (int16_t)(f * 32768.0f);
}

// Multiplication Q15 (résultat en Q15)
int16_t q15_mul(int16_t a, int16_t b) {
    // Résultat sur 32 bits, puis décalage de 15 bits
    int32_t prod = (int32_t)a * (int32_t)b;
    return (int16_t)(prod >> 15);  // Troncature vers Q15
}

// MAC (Multiply-Accumulate) en Q15
int32_t q15_mac(int32_t acc, int16_t a, int16_t b) {
    return acc + ((int32_t)a * (int32_t)b);
}

// Utilisation : CMSIS-DSP fournit toutes les opérations Q15/Q31
// optimisées en assembleur (SIMD) :
// arm_mult_q15(), arm_fir_q15(), arm_cfft_q15()
```

---

## 4. DSP Temps Réel sur Microcontrôleur

### 4.1 Configuration d'un buffer circulaire DMA + ADC sur STM32

```c
#include "arm_math.h"

// Double buffer DMA pour l'acquisition audio
#define ADC_BUFFER_SIZE 1024
uint16_t adc_buffer1[ADC_BUFFER_SIZE];
uint16_t adc_buffer2[ADC_BUFFER_SIZE];
volatile uint8_t buffer_ready = 0;

// Coefficients du filtre FIR (pré-calculés par scipy)
#define FIR_ORDER 64
float32_t fir_coeffs[FIR_ORDER + 1];  // À charger depuis une table
arm_fir_instance_f32 fir;
float32_t fir_state[FIR_ORDER + ADC_BUFFER_SIZE];
float32_t adc_float[ADC_BUFFER_SIZE];
float32_t filtered[ADC_BUFFER_SIZE];

// Callback de fin de demi-transfert DMA
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef* hadc) {
    // Traiter buffer1 pendant que le DMA remplit buffer2
    buffer_ready = 1;
}

void process_adc_data(uint16_t *raw, float32_t *out, uint32_t size) {
    // Conversion uint16_t ADC → float32_t (0-4095 → -1.0 à 1.0)
    for (uint32_t i = 0; i < size; i++) {
        adc_float[i] = (raw[i] - 2048) / 2048.0f;
    }

    // Filtrage FIR temps réel
    arm_fir_f32(&fir, adc_float, out, size);
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_ADC1_Init();

    // Lancer l'acquisition DMA en continu (mode circulaire)
    HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_buffer1, ADC_BUFFER_SIZE);
    // Le DMA alterne entre buffer1 et buffer2 automatiquement

    arm_fir_init_f32(&fir, FIR_ORDER + 1, fir_coeffs, fir_state,
                     ADC_BUFFER_SIZE);

    while (1) {
        if (buffer_ready) {
            buffer_ready = 0;
            // Le buffer le plus récent est traité
            process_adc_data(adc_buffer1, filtered, ADC_BUFFER_SIZE);
        }
    }
}
```

### 4.2 FFT temps réel sur ESP32 (ESP-DSP)

```cpp
#include <esp_dsp.h>

#define SAMPLE_RATE 16000  // 16 kHz
#define FFT_SIZE 1024

float input[FFT_SIZE * 2];  // Complexe : partie réelle + imaginaire
float wind[FFT_SIZE];

void fft_init() {
    // Génération de la fenêtre Hann
    dsps_wind_hann_f32(wind, FFT_SIZE);
}

void compute_fft(float *samples, float *magnitude) {
    // Copie des échantillons dans le buffer complexe
    for (int i = 0; i < FFT_SIZE; i++) {
        input[i * 2] = samples[i] * wind[i];      // Partie réelle (fenêtrée)
        input[i * 2 + 1] = 0;                     // Partie imaginaire
    }

    // FFT en virgule flottante optimisée ESP32
    dsps_fft2r_fc32(input, FFT_SIZE);
    // Bit reversal
    dsps_bit_rev_fc32(input, FFT_SIZE);

    // Calcul du module
    for (int i = 0; i < FFT_SIZE / 2; i++) {
        float re = input[i * 2];
        float im = input[i * 2 + 1];
        magnitude[i] = sqrtf(re * re + im * im) / FFT_SIZE;
    }
}
```

---

## Pièges Courants

1. **Aliasing (repliement spectral) :** Échantillonner un signal à $f_s$ sans filtre anti-aliasing en amont de l'ADC. Les fréquences $> f_s/2$ se replient dans la bande utile. Toujours placer un filtre analogique passe-bas avant l'ADC (fréquence de coupure $f_c \leq f_s/2$).

2. **Fuite spectrale (spectral leakage) :** Appliquer une FFT sans fenêtrage (fenêtre rectangulaire). Les lobes latéraux importants (-13 dB) masquent les petites amplitudes proches de pics forts. Toujours fenêtrer (Hann, Blackman, Kaiser) avant la FFT.

3. **Instabilité des filtres IIR :** Les coefficients IIR quantifiés (passage en virgule fixe) peuvent rendre le filtre instable (pôles hors du cercle unité). Vérifier la stabilité après quantification : tous les $|p_k| < 1$.

4. **Wrap-around en convolution circulaire :** Implémenter une convolution (FIR) dans le domaine fréquentiel par FFT sans zero-padding. La multiplication des FFT est une convolution circulaire ; le zero-padding (taille FFT $\geq$ N_échantillons + N_coeffs) est nécessaire pour une convolution linéaire.

5. **Dépassement arithmétique (overflow) en virgule fixe :** L'addition de deux nombres Q15 peut dépasser $[-1, 1[$, causant un wrap. Prévoir une marge de saturation (headroom) ou utiliser des accumulateurs 32 bits (Q31) avec saturation.

6. **Latence excessive dans le pipeline temps réel :** Un buffer DMA de grande taille augmente la latence entre l'acquisition et la sortie. Choisir la taille de buffer la plus petite possible compatible avec le temps de traitement : $T_{traitement} < \frac{T_{échantillon} \times N_{buffer}}{2}$ (pour un double buffer).

---

## Liste de vérification (Checklist)

- [ ] La fréquence d'échantillonnage respecte le théorème de Nyquist ($f_s \geq 2 \times f_{max}$).
- [ ] Un filtre anti-aliasing analogique est placé en amont de l'ADC.
- [ ] Une fenêtre appropriée (Hann/Blackman/Kaiser) est appliquée avant la FFT.
- [ ] Les coefficients du filtre numérique sont vérifiés (stabilité pour IIR, phase linéaire pour FIR).
- [ ] La quantification en virgule fixe (si utilisée) est validée sans débordement.
- [ ] Le temps de traitement est inférieur au budget temps réel (deadline).
- [ ] Les buffers DMA sont dimensionnés avec double buffer pour zéro perte d'échantillon.
- [ ] La latence du pipeline (ADC → DSP → DAC) est mesurée et documentée.
- [ ] Les tests sur données synthétiques (sinusoïdes pures) sont passés avant les données réelles.
- [ ] Le code DSP sur microcontrôleur utilise les optimisations SIMD (CMSIS-DSP, ESP-DSP).