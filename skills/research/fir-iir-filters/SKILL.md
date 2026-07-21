---
name: fir-iir-filters
description: "Conception et implémentation de filtres numériques FIR et IIR — méthodes de synthèse, structures, quantification, filtres adaptatifs, implémentations Python/C/FPGA."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [fir, iir, filtre-numerique, remez, parks-mcclellan, butterworth, chebyshev, elliptic, biquad, lattice, lms, nmls, rls, cmsis-dsp, fpga, virgule-fixe, phase-lineaire, passe-bas, passe-haut, passe-bande, coupe-bande, adaptive-filter]
    related_skills: [dsp-fundamentals, fft-algorithms, convolution-signal-processing, signal-processing-digital, modulation-demodulation]
---

# Filtres Numériques FIR et IIR

## Vue d'ensemble

Les filtres numériques sont les briques fondamentales du DSP. Deux grandes familles existent :

- **FIR (Finite Impulse Response)** : Réponse impulsionnelle finie, toujours stables, phase linéaire possible.
- **IIR (Infinite Impulse Response)** : Réponse impulsionnelle infinie, plus économes en coefficients, mais potentiellement instables et phase non-linéaire.

### FIR vs IIR — Comparaison

| Critère | FIR | IIR |
|:---|---|---|
| **Ordre nécessaire** | Élevé (100-1000) | Faible (4-12) |
| **Stabilité** | Toujours stable | Potentiellement instable |
| **Phase linéaire** | Possible (symétrie des coefficients) | Impossible (sauf Bessel approx) |
| **Complexité calcul** | $O(N \cdot L)$ (L=longueur FIR) | $O(N \cdot P)$ (P=ordre IIR) |
| **Mémoire** | $L$ coefficients + état | $2P$ coefficients + $2P$ état |
| **Quantification** | Robuste | Sensible (pôles se déplacent) |
| **Latence** | $L/2$ échantillons (phase linéaire) | Faible |
| **Filtrage adaptatif** | LMS, NLMS, RLS | Difficile (stabilité) |

**Règle empirique :** Pour une atténuation donnée, l'ordre FIR est ~10× l'ordre IIR.

---

## 1. Filtres FIR (RIF — Réponse Impulsionnelle Finie)

### 1.1 Définition

$$y[n] = \sum_{k=0}^{L-1} b_k \cdot x[n-k] = b_0 x[n] + b_1 x[n-1] + \dots + b_{L-1} x[n-L+1]$$

où $L$ est la longueur du filtre (nombre de coefficients), $\mathbf{b} = [b_0, b_1, \dots, b_{L-1}]$ les coefficients.

### 1.2 Types de FIR à phase linéaire

La symétrie des coefficients garantit la phase linéaire (pas de distorsion) :

| Type | Symétrie | $L$ | Usage |
|:---|---|---|---|
| **Type I** | Paire : $b_k = b_{L-1-k}$ | Impair | Passe-bas, passe-haut |
| **Type II** | Paire : $b_k = b_{L-1-k}$ | Pair | Passe-bas uniquement ($H(\pi)=0$) |
| **Type III** | Impaire : $b_k = -b_{L-1-k}$ | Impair | Différentiateur, Hilbert |
| **Type IV** | Impaire : $b_k = -b_{L-1-k}$ | Pair | Hilbert, différentiateur ($H(0)=0$) |

### 1.3 Méthode des fenêtres

La méthode la plus simple : tronquer la réponse impulsionnelle idéale $h_d[n]$ par une fenêtre $w[n]$.

```python
import numpy as np
from scipy.signal import freqz

def fir_fenetre(fs, fc, N, fenetre='hann'):
    """
    FIR passe-bas par méthode des fenêtres.

    Paramètres :
        fs      : fréquence d'échantillonnage (Hz)
        fc      : fréquence de coupure (Hz)
        N       : nombre de coefficients (doit être impair pour type I)
        fenetre : 'hann', 'hamming', 'blackman', 'kaiser'

    Retourne : coefficients b
    """
    if N % 2 == 0:
        N += 1  # Forcer impair

    M = N - 1
    n = np.arange(N) - M / 2
    wc = 2 * np.pi * fc / fs

    # Réponse impulsionnelle idéale (sinc)
    h = np.sinc(wc * n / np.pi)  # sinc(x) = sin(pi*x)/(pi*x)
    h[M // 2] = wc / np.pi       # n=0 : remplacer la division par 0

    # Fenêtrage
    fenetres = {
        'hann': np.hanning(N),
        'hamming': np.hamming(N),
        'blackman': np.blackman(N),
        'kaiser': np.kaiser(N, beta=8),
    }
    w = fenetres.get(fenetre, np.hanning(N))

    return h * w

# Exemple : fc = 500 Hz, fs = 4000 Hz, N = 51
b = fir_fenetre(fs=4000, fc=500, N=51, fenetre='hamming')

# Vérification
w, H = freqz(b, worN=8000)
print(f"Atténuation à 600 Hz : {20*np.log10(np.abs(H[w > 2*np.pi*600/4000][0])):.1f} dB")
```

### 1.4 Méthode de Parks-McClellan (Remez)

Algorithme de **minimax** : minimise l'erreur maximale entre la réponse idéale et réelle (équi-ondulation).

```python
from scipy.signal import remez

def fir_remez(fs, f_pass, f_stop, a_pass_db=0.5, a_stop_db=60):
    """
    FIR optimal par algorithme de Parks-McClellan (Remez).

    Paramètres :
        fs        : fréquence d'échantillonnage
        f_pass    : fin de la bande passante (Hz)
        f_stop    : début de la bande atténuée (Hz)
        a_pass_db : ondulation max en bande passante (dB)
        a_stop_db : atténuation minimale en bande arrêtée (dB)

    Retourne : coefficients b, ordre
    """
    # Estimation de l'ordre (formule de Kaiser)
    delta_f = (f_stop - f_pass) / fs
    delta1 = (10**(a_pass_db / 20) - 1) / (10**(a_pass_db / 20) + 1)
    delta2 = 10**(-a_stop_db / 20)
    N_est = int((-20 * np.log10(np.sqrt(delta1 * delta2)) - 13) / (14.6 * delta_f) + 1)

    # Arrondir à l'impair supérieur pour phase linéaire type I
    if N_est % 2 == 0:
        N_est += 1

    bands = [0, f_pass, f_stop, fs / 2]
    desired = [1, 1, 0, 0]
    weight = [a_stop_db / a_pass_db, 1.0]

    b = remez(N_est, bands, desired, weight, fs=fs)

    return b, len(b) - 1

# Exemple : filtre FIR passe-bas, 100 Hz → 120 Hz, fs = 1000 Hz
b, order = fir_remez(fs=1000, f_pass=100, f_stop=120)
print(f"Ordre FIR estimé : {order}")
```

### 1.5 Méthode par moindres carrés (LS)

Minimise l'erreur quadratique intégrée (meilleur au sens RMS que Remez).

```python
from scipy.signal import firls

# Moindres carrés : meilleur RMS, mais ondulation non constante
b = firls(51, [0, 0.2, 0.25, 1], [1, 1, 0, 0], fs=2.0)
```

### 1.6 Réponse impulsionnelle idéale (table de référence)

| Type | $h_{ideal}[n]$ (sauf n=0) | $h_{ideal}[0]$ |
|:---|---|---|
| Passe-bas | $\frac{\sin(\omega_c n)}{\pi n}$ | $\frac{\omega_c}{\pi}$ |
| Passe-haut | $-\frac{\sin(\omega_c n)}{\pi n}$ | $1 - \frac{\omega_c}{\pi}$ |
| Passe-bande | $\frac{\sin(\omega_{c2} n) - \sin(\omega_{c1} n)}{\pi n}$ | $\frac{\omega_{c2} - \omega_{c1}}{\pi}$ |
| Coupe-bande | $\frac{\sin(\omega_{c1} n) - \sin(\omega_{c2} n)}{\pi n}$ | $1 - \frac{\omega_{c2} - \omega_{c1}}{\pi}$ |
| Hilbert | $\frac{2\sin^2(\pi n / 2)}{\pi n}$ | 0 |

---

## 2. Structures d'Implémentation FIR

### 2.1 Forme directe (transversale)

```c
float fir_direct(const float *coeffs, float *state,
                 int order, float input) {
    float acc = 0.0f;

    // Décalage du registre d'état
    for (int i = order; i > 0; i--)
        state[i] = state[i - 1];
    state[0] = input;

    // Accumulation
    for (int i = 0; i <= order; i++)
        acc += coeffs[i] * state[i];

    return acc;
}
```

### 2.2 Forme directe transposée (pipeline-friendly)

```c
void fir_transposed(const float *b, float *state,
                    const float *input, float *output,
                    int order, int block_size) {
    for (int n = 0; n < block_size; n++) {
        float y = b[0] * input[n] + state[0];
        for (int i = 0; i < order; i++)
            state[i] = b[i + 1] * input[n] + state[i + 1];
        state[order] = b[order] * input[n];
        output[n] = y;
    }
}
// Avantage : pas de bullage pipeline, parallélisable
```

### 2.3 FIR symétrique (phase linéaire, coefficients réduits de moitié)

```c
float fir_symmetric(const float *coeffs_half, float *state,
                    int half_order, float input) {
    // b[0..L-1] est symétrique : b[i] = b[L-1-i]
    // On n'en stocke que la moitié
    for (int i = half_order; i > 0; i--)
        state[i] = state[i - 1];
    state[0] = input;

    float acc = 0.0f;
    for (int i = 0; i < half_order; i++)
        acc += coeffs_half[i] * (state[i] + state[2 * half_order - i]);
    acc += coeffs_half[half_order] * state[half_order];

    return acc;
}
```

### 2.4 FIR en polyphase (décimation/interpolation)

```python
def fir_polyphase_decimate(x, b, M):
    """
    Décimation par M avec filtre FIR polyphase.
    Chaque phase ne traite que 1/M des échantillons.
    """
    L = len(b)
    # Banque de M sous-filtres
    phases = [b[p::M] for p in range(M)]

    y = []
    for i in range(0, len(x) - L, M):
        phase_idx = i % M
        h = phases[phase_idx]
        y.append(np.dot(x[i:i+len(h)], h))
    return np.array(y)
```

---

## 3. Filtres IIR (RII — Réponse Impulsionnelle Infinie)

### 3.1 Définition (équation aux différences)

$$y[n] = \sum_{k=0}^{P} b_k x[n-k] - \sum_{k=1}^{P} a_k y[n-k]$$

Fonction de transfert en Z :

$$H(z) = \frac{\sum_{k=0}^{P} b_k z^{-k}}{1 + \sum_{k=1}^{P} a_k z^{-k}}$$

### 3.2 Types de filtres IIR

```python
from scipy.signal import butter, cheby1, cheby2, ellip, bessel

# Butterworth — maximally flat passband
b, a = butter(4, 0.2, btype='low')

# Chebyshev Type I — ondulation en bande passante
b, a = cheby1(4, 0.5, 0.2, btype='low')  # 0.5 dB ripple

# Chebyshev Type II — ondulation en bande atténuée
b, a = cheby2(4, 40, 0.25, btype='low')  # 40 dB stopband

# Elliptic (Cauer) — ondulation dans les deux bandes
b, a = ellip(4, 0.5, 40, 0.2, btype='low')  # 0.5 dB ripple, 40 dB stop

# Bessel — phase linéaire approx., préservation de forme
b, a = bessel(4, 0.2, btype='low')
```

### 3.3 Comparaison des réponses

| Type | Réponse BP | Réponse BA | Phase | Ordre pour même sélectivité |
|:---|---|---|---:|---:|
| Butterworth | Maximale plate | -20P dB/déc | Modérée | Référence |
| Chebyshev I | Ondulation | -6P dB/déc (après fc) | Médiocre | ~30% < Butterworth |
| Chebyshev II | Plate | Ondulation | Médiocre | ~30% < Butterworth |
| Elliptic | Ondulation | Ondulation | Mauvaise | ~50% < Butterworth |
| Bessel | Dégradée | -6P dB/déc | **Linéaire** (passe-bas) | > Butterworth |

### 3.4 Ordre nécessaire par spécification

```python
def ordre_iir_necessaire(fs, f_pass, f_stop, a_pass=0.5, a_stop=60, type_filtre='butter'):
    """
    Estime l'ordre IIR nécessaire.
    """
    wp = 2 * f_pass / fs  # Normalisé
    ws = 2 * f_stop / fs

    from scipy.signal import buttord, cheb1ord, cheb2ord, ellipord
    ordres = {
        'butter': buttord,
        'cheby1': cheb1ord,
        'cheby2': cheb2ord,
        'ellip': ellipord,
    }
    func = ordres.get(type_filtre, buttord)
    N, wn = func(wp, ws, a_pass, a_stop)
    return N

# Comparaison pour spécification identique :
# BP : 0-100 Hz, BA : 120 Hz+, fs = 1000 Hz, a_pass=0.5dB, a_stop=60dB
for nom in ['butter', 'cheby1', 'cheby2', 'ellip']:
    N = ordre_iir_necessaire(1000, 100, 120, 0.5, 60, nom)
    print(f"{nom}: ordre {N}")
```

---

## 4. Structures d'Implémentation IIR

### 4.1 Forme directe type I (DF-I)

```python
def iir_df1(b, a, x):
    """Forme directe type I : zéros d'abord, puis pôles."""
    P = len(a) - 1
    Q = len(b) - 1
    w = np.zeros(max(P, Q) + 1)
    y = np.zeros(len(x))

    for n in range(len(x)):
        # Zéros (FIR part)
        w[0] = x[n]
        v = b[0] * w[0]
        for k in range(1, Q + 1):
            v += b[k] * w[k]

        # Pôles (feedback part)
        for k in range(P, 0, -1):
            w[k] = w[k - 1]

        y[n] = v - sum(a[k] * y[n - k] for k in range(1, P + 1) if n >= k)

    return y
```

### 4.2 Forme directe type II (DF-II) — transposée canonique

```python
def iir_df2(b, a, x):
    """Forme directe type II : économique en mémoire."""
    P = len(a) - 1
    state = np.zeros(P)
    y = np.zeros(len(x))

    for n in range(len(x)):
        # Combinaison des pôles et zéros
        v = x[n] - sum(a[k] * state[k - 1] for k in range(1, P + 1))
        y[n] = b[0] * v + sum(b[k] * state[k - 1] for k in range(1, P + 1))

        # Mise à jour de l'état
        for k in range(P - 1, 0, -1):
            state[k] = state[k - 1]
        state[0] = v

    return y
```

### 4.3 Structure Biquad (second ordre, SOS — Second Order Section)

La structure Biquad est **essentielle** pour les IIR d'ordre élevé : elle éclate $H(z)$ en une cascade de cellules d'ordre 2, chacune insensible à la quantification.

```python
from scipy.signal import sosfilt, zpk2sos

# Conversion en SOS (cascade de biquads)
z, p, k = signal.tf2zpk(b, a)
sos = zpk2sos(z, p, k, pairing='nearest')

# Filtrage par SOS (recommandé !)
y = sosfilt(sos, x)

# Structure Biquad (un seul étage) :
# H(z) = (b0 + b1*z^-1 + b2*z^-2) / (1 + a1*z^-1 + a2*z^-2)
```

```c
// Biquad DF-II transposée (la plus stable en virgule fixe)
typedef struct {
    float b0, b1, b2;
    float a1, a2;
    float s1, s2;  // State
} biquad_t;

float biquad_process(biquad_t *f, float x) {
    float y = f->b0 * x + f->s1;
    f->s1 = f->b1 * x - f->a1 * y + f->s2;
    f->s2 = f->b2 * x - f->a2 * y;
    return y;
}

// Filtre IIR d'ordre 8 = cascade de 4 biquads
biquad_t stages[4];
float biquad_cascade(biquad_t stages[], int n_stages, float x) {
    float y = x;
    for (int i = 0; i < n_stages; i++)
        y = biquad_process(&stages[i], y);
    return y;
}

// CMSIS-DSP équivalent :
// arm_biquad_cascade_df2T_f32(&filtre, input, output, block_size);
```

### 4.4 Structure Lattice (ARMA)

```python
# Structure lattice pour la stabilité garantie et la quantification robuste
# Utilisée en synthèse vocale (LPC), égaliseurs adaptatifs
# Coefficients : k[0..P-1] (réflecteurs, |k[i]| < 1 → stable)
```

---

## 5. Quantification et Implémentation Virgule Fixe

### 5.1 Effet de la quantification des coefficients

La quantification des coefficients $b_k, a_k$ déplace les pôles/zéros. Pour les IIR, un pôle peut sortir du cercle unité → **instabilité**.

```python
def verifier_stabilite_quantifie(b, a, bits=16):
    """Vérifie la stabilité après quantification des coefficients."""
    # Quantification
    scale = 2**(bits - 1)
    b_q = np.round(b * scale) / scale
    a_q = np.round(a * scale) / scale

    poles = np.roots(np.concatenate([[1], a_q[1:]]))
    stable = all(np.abs(p) < 0.995 for p in poles)  # Marge 0.5%
    return stable, poles
```

### 5.2 Bruit de quantification (sortie)

Le bruit de quantification à la sortie d'un IIR est amplifié par le gain du filtre :

$$\sigma_y^2 = \sigma_q^2 \cdot \frac{1}{2\pi} \oint |H(z)|^2 \frac{dz}{z}$$

```python
def bruit_quantification_sortie(b, a):
    """Calcule le gain de bruit d'un filtre IIR."""
    from scipy.signal import freqz
    w, H = freqz(b, a)
    gain_bruit = np.sum(np.abs(H)**2) / len(H)  # Approximation
    return 10 * np.log10(gain_bruit)  # dB

# Un IIR peut amplifier le bruit de quantification de 20-40 dB !
```

### 5.3 Scaling pour éviter le débordement

```python
# Règle : le signal interne ne doit jamais dépasser 1.0 en virgule fixe.
# Facteur de sécurité : ||H(z)||_inf < 1 pour chaque biquad

def scaling_biquad(b, a):
    """Calcule le facteur de scaling pour éviter le débordement."""
    w, H = freqz(b, a)
    norm_inf = np.max(np.abs(H))  # Norme infinie
    scale = 1.0 / norm_inf
    return scale

# Appliquer : b_scaled = b * scale, puis compenser le gain final
```

---

## 6. Filtres Adaptatifs

### 6.1 LMS (Least Mean Squares)

```python
def lms_filtre(desired, reference, mu=0.01, order=32):
    """
    Filtre adaptatif LMS pour l'annulation de bruit.

    desired   : signal souhaité = signal utile + bruit corrélé
    reference : bruit de référence (corrélé au bruit dans desired)
    mu        : pas d'apprentissage
    order     : ordre du filtre adaptatif
    """
    N = len(desired)
    w = np.zeros(order)
    y = np.zeros(N)
    error = np.zeros(N)

    for n in range(order, N):
        x = reference[n:n-order:-1]
        y[n] = np.dot(w, x)
        error[n] = desired[n] - y[n]
        w += 2 * mu * error[n] * x  / (np.dot(x, x) + 1e-6)  # NLMS

    return error, w

# Usage : desired = voix + bruit_50Hz, reference = bruit_50Hz pur
# error = voix débruitée
```

### 6.2 RLS (Recursive Least Squares)

Convergence plus rapide que LMS mais $O(P^2)$ au lieu de $O(P)$.

```python
def rls_filtre(desired, reference, order=32, lam=0.99, delta=1.0):
    """
    Filtre adaptatif RLS. Convergence rapide, coût O(P^2).
    lam : facteur d'oubli (0.95-1.0)
    """
    N = len(desired)
    w = np.zeros(order)
    P_inv = (1.0 / delta) * np.eye(order)
    error = np.zeros(N)

    for n in range(order, N):
        x = reference[n:n-order:-1]
        # Gain de Kalman
        z = P_inv @ x
        g = z / (lam + np.dot(x, z))
        # Erreur a priori
        e = desired[n] - np.dot(w, x)
        error[n] = e
        # Mise à jour
        w += g * e
        P_inv = (P_inv - np.outer(g, z)) / lam

    return error, w
```

### 6.3 Applications des filtres adaptatifs

| Application | Signal utile | Bruit/référence | Algorithme |
|:---|---|---|---|
| **Annulation d'écho acoustique** (AEC) | Microphone (voix + écho HP) | Signal HP | NLMS |
| **Réduction de bruit active** (ANC) | Intérieur casque | Microphone externe | FxLMS |
| **Égalisation adaptative** (télécom) | Signal reçu | Séquence d'apprentissage | LMS, RLS |
| **Débruitage ECG** | ECG + bruit 50 Hz | Secteur 50 Hz | LMS |
| **Identification système** | Sortie inconnue | Entrée connue | LMS, RLS |
| **Prédiction linéaire** (LPC) | Échantillon futur | Échantillons passés | Levinson-Durbin |

---

## 7. Filtres Spéciaux

### 7.1 Filtre de Hilbert (déphaseur 90°)

```python
# Transformée de Hilbert : déphasage de 90° de toutes les fréquences
from scipy.signal import hilbert

signal_analytique = hilbert(x)  # x + j * hilbert(x)
enveloppe = np.abs(signal_analytique)
phase_instantannee = np.unwrap(np.angle(signal_analytique))
freq_instantannee = np.diff(phase_instantannee) * fs / (2 * np.pi)
```

### 7.2 Filtre de CIC (Cascaded Integrator-Comb)

Filtre sans multiplicateurs, idéal pour la décimation/interpolation dans les ADC sigma-delta.

```python
def cic_decimate(x, R, N=3):
    """
    Filtre CIC de décimation par R, N étages.
    Utilisé dans : ADC ΔΣ, SDR (RTL-SDR), DSP large bande.
    """
    # Intégrateurs
    for stage in range(N):
        y = np.zeros(len(x))
        for i in range(1, len(x)):
            y[i] = y[i-1] + x[i]
        x = y

    # Décimation
    x = x[::R]

    # Comb (différentiateurs)
    for stage in range(N):
        y = np.zeros(len(x))
        for i in range(1, len(x)):
            y[i] = x[i] - x[i-1]
        x = y

    return x
```

### 7.3 Filtre en peigne (Comb filter)

```python
# Peigne feed-forward (FF) : H(z) = 1 - g*z^{-D}
# Utilisé pour : annulation de résonances, réverbération
# Peigne feed-back (FB) : H(z) = 1 / (1 + g*z^{-D})
# Utilisé pour : génération de résonances, synthèse sonore

def comb_ff(x, delay, gain=0.5):
    """Peigne feed-forward : annule une fréquence et ses harmoniques."""
    y = np.copy(x)
    for n in range(delay, len(x)):
        y[n] = x[n] - gain * x[n - delay]
    return y
```

---

## Pièges Courants

1. **Instabilité IIR en cascade :** Éclater en biquads (SOS) — ne jamais implémenter un IIR d'ordre > 2 en forme directe.
2. **Phase non-linéaire IIR pour données biologiques :** Utiliser `filtfilt` (filtrage aller + retour) pour une phase nulle.
3. **Ondulation excessive Chebyshev :** 0.1 dB suffit pour la plupart des usages ; 0.5 dB max pour l'audio.
4. **Réponse transitoire en tête/baisse :** Le filtre doit s'initialiser avec l'état `zi = lfilter_zi(b, a)` pour un démarrage sans transitoire.
5. **Oubli du facteur de scaling en virgule fixe :** Le débordement en accumulation détruit le SNR. Utiliser `arm_scale_f32`.

---

## Liste de vérification (Checklist)

- [ ] FIR utilisé quand la phase linéaire ou la stabilité absolue est critique.
- [ ] IIR utilisé quand l'efficacité calculatoire prime et que la phase non-linéaire est acceptable.
- [ ] IIR d'ordre > 2 toujours implémenté en cascade biquads (SOS).
- [ ] Stabilité vérifiée après quantification des coefficients.
- [ ] Fenêtrage adapté au cahier des charges (Kaiser pour compromis atténuation/sélectivité).
- [ ] Facteur de scaling appliqué en virgule fixe.
- [ ] LMS/NLMS testé avec un pas mu suffisamment petit (0.01 max pour commencer).
- [ ] `filtfilt` utilisé pour la réponse en phase nulle (traitement hors ligne).