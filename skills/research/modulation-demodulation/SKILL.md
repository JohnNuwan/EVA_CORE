---
name: modulation-demodulation
description: "Techniques de modulation et démodulation numériques et analogiques — AM, FM, PM, ASK, FSK, PSK, QAM, APSK, GMSK, OFDM, synchronisation, récupération de porteuse, timing recovery, égalisation, implémentations Python liquid-dsp."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [modulation, demodulation, am, fm, pm, ask, fsk, psk, qam, apsk, gmsk, ofdm, costas, gardner, mueller-muller, carrier-recovery, timing-recovery, equalization, lms-equalizer, cma, liquid-dsp, python, numpy, scipy, ber, ebn0, snr, evm]
    related_skills: [dsp-fundamentals, fft-algorithms, fir-iir-filters, sdr-advanced, gnu-radio, signal-processing-digital, radio-sdr]
---

# Modulation et Démodulation

## Vue d'ensemble

La modulation est le processus qui modifie un signal porteur (généralement sinusoïdal) pour transmettre de l'information. La démodulation est l'opération inverse qui récupère l'information. On distingue deux grandes familles :

- **Modulations analogiques** : AM, FM, PM — information continue
- **Modulations numériques** : ASK, FSK, PSK, QAM, OFDM — information discrète (bits)

### Hiérarchie des performances

```
Basse efficacité spectrale                Haute efficacité spectrale
(bits/s/Hz)                                (bits/s/Hz)
    │                                              │
    ▼                                              ▼
 BPSK → QPSK → 8PSK → 16QAM → 32QAM → 64QAM → 256QAM
  (1 b/s/Hz)                      (6 b/s/Hz)      (8 b/s/Hz)
    │                                              │
    ↓                                              ↓
 Faible SNR requis                    Haut SNR requis
  (~8 dB pour BER=10⁻⁴)              (~25 dB pour 64QAM)
```

---

## 1. Modulations Analogiques

### 1.1 AM (Amplitude Modulation)

$$s(t) = [A_c + m(t)] \cdot \cos(2\pi f_c t)$$

```python
import numpy as np

def moduler_am(message, fc, fs, Ac=1.0, indice=0.8):
    """Modulation AM. indice < 1 pour éviter la surmodulation."""
    t = np.arange(len(message)) / fs
    porteuse = np.cos(2 * np.pi * fc * t)
    return (Ac + indice * message) * porteuse

def demoduler_am(signal, fs, fc):
    """Démodulation AM cohérente."""
    t = np.arange(len(signal)) / fs
    # Multiplier par la porteuse locale
    lo = np.cos(2 * np.pi * fc * t)
    I = signal * lo

    # Filtre passe-bas
    from scipy.signal import butter, filtfilt
    b, a = butter(4, fc / (fs / 2))
    envelope = 2 * filtfilt(b, a, I)  # ×2 pour compenser la perte
    return envelope
```

### 1.2 FM (Frequency Modulation)

$$s(t) = A_c \cos\left(2\pi f_c t + 2\pi k_f \int_0^t m(\tau) d\tau\right)$$

```python
def moduler_fm(message, fc, fs, deviation=75000):
    """Modulation FM. deviation = 75 kHz pour FM broadcast."""
    t = np.arange(len(message)) / fs
    phase_instant = 2 * np.pi * fc * t + 2 * np.pi * deviation * np.cumsum(message) / fs
    return np.cos(phase_instant)

def demoduler_fm(signal_iq, fs):
    """Démodulation FM par différentiation de phase."""
    phase = np.unwrap(np.angle(signal_iq))
    return np.diff(phase) * fs / (2 * np.pi)
```

| Paramètre | FM Broadcast | NBFM (radioamateur) | WBFM (audio) |
|:---|---|---:|---:|
| Déviation | ±75 kHz | ±5 kHz | ±200 kHz |
| Bande passante | ~200 kHz | ~12.5 kHz | ~400 kHz |
| Désaccentuation | 75 µs | Pas de | 75 µs |

### 1.3 PM (Phase Modulation)

$$s(t) = A_c \cos(2\pi f_c t + k_p \cdot m(t))$$

```python
def moduler_pm(message, fc, fs, kp=1.0):
    t = np.arange(len(message)) / fs
    return np.cos(2 * np.pi * fc * t + kp * message)
```

---

## 2. Modulations Numériques

### 2.1 Mapping de symboles

```python
def mapper(symboles, modulation='qpsk'):
    """Convertit des bits en symboles complexes."""
    configs = {
        'bpsk':   lambda b: 1 - 2*b,                  # {0→+1, 1→-1}
        'qpsk':   lambda b: (1-2*b[::2]) + 1j*(1-2*b[1::2]),
        '8psk':   lambda b: np.exp(2j*np.pi/8 * (4*b[::3] + 2*b[1::3] + b[2::3])),
        '16qam':  lambda b: mapper_qam_16(b),
        '64qam':  lambda b: mapper_qam_64(b),
    }
    return configs[modulation](symboles)

def mapper_qam_16(bits):
    """Mapping 16-QAM (Gray coding)."""
    # bits = [b0,b1,b2,b3] avec b0b1 = I, b2b3 = Q
    # Grey : 00→-3, 01→-1, 11→+1, 10→+3
    grey = {0: -3, 1: -1, 3: 1, 2: 3}
    I = np.array([grey[bits[i]*2 + bits[i+1]] for i in range(0, len(bits), 4)])
    Q = np.array([grey[bits[i]*2 + bits[i+1]] for i in range(2, len(bits)-2, 4)])
    return (I + 1j*Q) / np.sqrt(10)  # Normalisation d'énergie
```

### 2.2 Constellation (diagramme)

```python
# Diagramme de constellation pour QPSK/QAM
def afficher_constellation(symboles, title="Constellation"):
    """Visualisation du diagramme de constellation."""
    import matplotlib.pyplot as plt
    plt.figure(figsize=(6, 6))
    plt.scatter(symboles.real, symboles.imag, s=10, alpha=0.5)
    plt.grid(True, alpha=0.3)
    plt.axhline(0, color='gray', lw=0.5)
    plt.axvline(0, color='gray', lw=0.5)
    plt.axis('equal')
    plt.xlim(-2, 2); plt.ylim(-2, 2)
    plt.title(title)
    plt.xlabel('In-Phase (I)')
    plt.ylabel('Quadrature (Q)')
    plt.show()
```

### 2.3 Formation d'impulsion (Pulse Shaping)

```python
def rrc_pulse(beta, span, sps):
    """
    Root Raised Cosine filter impulse response.

    beta : roll-off factor (0 = rect, 1 = sinc)
    span : durée du filtre en symboles
    sps  : samples per symbol
    """
    N = span * sps + 1
    t = np.arange(-N//2 + 1, N//2 + 1) / sps
    h = np.zeros(N)

    for i, ti in enumerate(t):
        if ti == 0:
            h[i] = 1 - beta + 4 * beta / np.pi
        elif abs(ti) == 1/(4*beta) and beta > 0:
            h[i] = (beta/np.sqrt(2)) * (
                (1+2/np.pi)*np.sin(np.pi/(4*beta)) +
                (1-2/np.pi)*np.cos(np.pi/(4*beta)))
        else:
            num = np.sin(np.pi*ti*(1-beta)) + 4*beta*ti*np.cos(np.pi*ti*(1+beta))
            den = np.pi*ti*(1 - (4*beta*ti)**2)
            h[i] = num / den

    return h / np.sqrt(np.sum(h**2))  # Normalisation énergie
```

### 2.4 Chaîne de transmission complète

```python
def emettre_numerique(bits, modulation='qpsk', sps=8, beta=0.35, fc=1000, fs=8000):
    """Chaîne complète d'émission numérique."""
    # 1. Mapping bits → symboles
    symboles = mapper(bits, modulation)

    # 2. Upsampling + pulse shaping
    impulsions = np.zeros(len(symboles) * sps)
    impulsions[::sps] = symboles
    h = rrc_pulse(beta, span=8, sps=sps)
    signal_mise_en_forme = np.convolve(impulsions, h)

    # 3. Modulation sur porteuse
    t = np.arange(len(signal_mise_en_forme)) / fs
    porteuse = np.exp(2j * np.pi * fc * t)
    signal_emis = signal_mise_en_forme * porteuse

    return signal_emis

def recevoir_numerique(signal, modulation='qpsk', sps=8, beta=0.35, fc=1000, fs=8000):
    """Chaîne complète de réception numérique."""
    # 1. DDC (descente en bande de base)
    t = np.arange(len(signal)) / fs
    signal_bb = signal * np.exp(-2j * np.pi * fc * t)

    # 2. Filtrage adapté (matched filter)
    h = rrc_pulse(beta, span=8, sps=sps)
    signal_filtre = np.convolve(signal_bb, h[::-1], mode='same')

    # 3. Downsampling (au meilleur instant d'échantillonnage)
    # En pratique : synchronisation de rythme (Gardner, Mueller&Muller)
    # Ici : simple downsampling au milieu du symbole
    delay = len(h) // 2
    symboles_recus = signal_filtre[delay::sps]

    return symboles_recus
```

---

## 3. Modulations Spécifiques

### 3.1 GMSK (Gaussian Minimum Shift Keying)

Utilisée dans GSM, Bluetooth, DECT.

```python
def moduler_gmsk(bits, fs, sps=8, BT=0.5):
    """
    Modulation GMSK.
    BT : produit Bande × Temps (GSM: 0.3, Bluetooth: 0.5)
    """
    # 1. Impulsions NRZ
    nrz = 2 * np.repeat(bits, sps) - 1  # {0→-1, 1→+1}

    # 2. Filtre gaussien (faconne les transitions)
    B = BT / sps
    sigma = np.sqrt(np.log(2)) / (2 * np.pi * B)
    t = np.arange(-3*sps, 3*sps + 1) / sps
    gauss = 1 / (np.sqrt(2*np.pi)*sigma) * np.exp(-t**2 / (2*sigma**2))
    gauss = gauss / np.sum(gauss)  # Normalisation

    # 3. Convolution NRZ + gaussien
    filtred = np.convolve(nrz, gauss, mode='same')

    # 4. Intégration → phase continue
    phase = np.cumsum(filtred) * (np.pi / 2) / sps

    # 5. IQ
    return np.cos(phase) + 1j * np.sin(phase)
```

### 3.2 OFDM (Orthogonal Frequency Division Multiplexing)

Utilisé dans WiFi (802.11a/g/n/ac/ax), DVB-T, 4G/5G.

```python
def moduler_ofdm(symboles_qam, N_fft=64, N_cp=16, pilots=None):
    """
    Modulation OFDM : IFFT + cyclic prefix.
    
    Paramètres :
        symboles_qam : symboles QAM sur N_fft sous-porteuses
        N_fft : taille de la FFT
        N_cp  : longueur du préfixe cyclique
        pilots : indices des sous-porteuses pilotes
    """
    N_sym = len(symboles_qam) // N_fft
    trame = []

    for i in range(N_sym):
        blk = symboles_qam[i * N_fft:(i + 1) * N_fft]

        # IFFT
        symbole_fft = np.fft.ifft(blk) * np.sqrt(N_fft)

        # Cyclic prefix
        cp = symbole_fft[-N_cp:]
        trame.extend(np.concatenate([cp, symbole_fft]))

    return np.array(trame)

def demoduler_ofdm(trame, N_fft=64, N_cp=16):
    """Démodulation OFDM : retrait CP + FFT."""
    N_par_symbole = N_fft + N_cp
    N_sym = len(trame) // N_par_symbole
    symboles = []

    for i in range(N_sym):
        blk = trame[i * N_par_symbole + N_cp:(i + 1) * N_par_symbole]
        symbole = np.fft.fft(blk) / np.sqrt(N_fft)
        symboles.extend(symbole)

    # Égalisation simple par pilotes
    # ...
    return np.array(symboles)
```

### 3.3 QPSK / OQPSK / π/4-QPSK

```python
# QPSK standard : sauts de ±180° possibles → forte PAPR
# OQPSK : décalage de 1/2 symbole entre I et Q → pas de saut > 90°
# π/4-QPSK : rotation de 45° à chaque symbole → sauts max ±135°

def moduler_oqpsk(bits):
    """Offset QPSK : I et Q décalés d'1/2 symbole."""
    symboles = mapper(bits, 'qpsk')
    # Décaler Q d'1/2 symbole
    I = symboles.real
    Q = np.roll(symboles.imag, 1)
    return I + 1j * Q
```

---

## 4. Synchronisation

### 4.1 Récupération de porteuse (Carrier Recovery)

```python
def costas_loop(signal, fs, loop_bw=100, mod='bpsk'):
    """
    Boucle de Costas pour la récupération de porteuse.
    
    Mod : 'bpsk', 'qpsk', 'qam'
    """
    N = len(signal)
    phase = 0.0
    freq = 0.0
    alpha = 2 * loop_bw / fs
    beta = alpha**2 / 2

    sortie = np.zeros(N, dtype=complex)
    for n in range(N):
        # VCO
        lo = np.exp(-1j * phase)
        sortie[n] = signal[n] * lo

        # Détection de phase (selon modulation)
        if mod == 'bpsk':
            phase_error = np.real(sortie[n]) * np.imag(sortie[n])
        elif mod == 'qpsk':
            phase_error = np.sign(np.real(sortie[n])) * np.imag(sortie[n]) \
                        - np.sign(np.imag(sortie[n])) * np.real(sortie[n])
        else:  # QAM
            phase_error = np.real(sortie[n]) * np.imag(sortie[n]) * \
                         (np.real(sortie[n])**2 - np.imag(sortie[n])**2)

        # Filtre de boucle (proportionnel + intégral)
        freq += beta * phase_error
        phase += freq + alpha * phase_error

    return sortie, phase
```

### 4.2 Récupération de rythme (Timing Recovery)

```python
def gardner_timing(signal, sps):
    """
    Algorithme de Gardner pour la synchronisation de rythme.

    Indépendant de la phase porteuse.
    Met à jour le point d'échantillonnage optimal.
    """
    N = len(signal)
    samples_out = []
    mu = 0.0  # Fractional delay
    n = 0

    while n + 2 * sps < N:
        # Trois échantillons
        y_early = signal[n + int(mu)]
        y_mid = signal[n + sps + int(mu)]
        y_late = signal[n + 2 * sps + int(mu)]

        # Erreur de timing (Gardner)
        error = np.real(y_mid) * (np.real(y_late) - np.real(y_early)) + \
                np.imag(y_mid) * (np.imag(y_late) - np.imag(y_early))

        # Boucle de premier ordre
        mu += 0.01 * error
        mu = np.clip(mu, 0, sps - 1)

        samples_out.append(y_mid)
        n += sps

    return np.array(samples_out)
```

### 4.3 Égalisation adaptative

```python
def cma_equalizer(signal, order=16, mu=0.001, radius=1.0):
    """
    Égaliseur aveugle CMA (Constant Modulus Algorithm).
    Corrige les distorsions de canal sans séquence d'apprentissage.
    """
    N = len(signal)
    w = np.zeros(order, dtype=complex)
    w[order // 2] = 1.0  # Centre-tap initialization

    output = np.zeros(N, dtype=complex)
    for n in range(order, N):
        x = signal[n - order + 1:n + 1][::-1]  # Delay line
        y = np.dot(w, x)
        output[n] = y

        # CMA error : |y|^2 - R^2
        error = (np.abs(y)**2 - radius**2) * y
        w -= mu * error * np.conj(x)  # Gradient descent

    return output, w
```

### 4.4 Détection différentielle

```python
def demoduler_dbpsk(symboles):
    """
    Démodulation DBPSK (différentielle).
    Compare la phase du symbole courant avec la précédente.
    """
    phase_diff = np.angle(symboles[1:] * np.conj(symboles[:-1]))
    bits = (phase_diff > 0).astype(int)
    return bits
```

---

## 5. Métriques de Performance

### 5.1 BER (Bit Error Rate) vs Eb/N0

```python
def ber_awgn(ebn0_db, modulation='qpsk'):
    """
    BER théorique en canal AWGN.
    """
    ebn0 = 10**(ebn0_db / 10)
    from scipy.special import erfc

    configs = {
        'bpsk': lambda x: 0.5 * erfc(np.sqrt(x)),
        'qpsk': lambda x: erfc(np.sqrt(x / 2)) - 0.25 * erfc(np.sqrt(x / 2))**2,
        '8psk': lambda x: 2/3 * erfc(np.sqrt(3 * x * np.sin(np.pi/8)**2)),
    }
    return configs.get(modulation, configs['qpsk'])(ebn0)

def comparer_modulations():
    """Comparaison des BER pour différentes modulations."""
    ebn0_db = np.arange(0, 20, 1)
    for mod in ['bpsk', 'qpsk', '8psk']:
        ber = [ber_awgn(e, mod) for e in ebn0_db]
        # Tracer : semilogy(EbN0_dB, BER)
    # Résultat : pour BER=10⁻⁴ :
    # BPSK: ~8 dB, QPSK: ~8 dB, 8PSK: ~14 dB, 16QAM: ~18 dB
```

### 5.2 EVM (Error Vector Magnitude)

```python
def evm(symboles_recus, symboles_emission):
    """
    Error Vector Magnitude.
    EVM (%) = RMS(erreur) / RMS(constellation) * 100
    """
    erreur = symboles_recus - symboles_emission
    evm_rms = np.sqrt(np.mean(np.abs(erreur)**2) / np.mean(np.abs(symboles_emission)**2))
    return evm_rms * 100  # en %

# Relation EVM → SNR (approximative)
# SNR_dB ≈ -20 * log10(EVM/100)
```

### 5.3 Table des efficacités spectrales

| Modulation | Bits/symbole | Efficacité (b/s/Hz) | SNR pour BER=10⁻⁴ |
|:---:|:---:|:---:|---:|
| BPSK | 1 | 1.0 | ~8 dB |
| QPSK | 2 | 2.0 | ~8 dB |
| 8-PSK | 3 | 3.0 | ~14 dB |
| 16-QAM | 4 | 4.0 | ~18 dB |
| 32-QAM | 5 | 5.0 | ~20 dB |
| 64-QAM | 6 | 6.0 | ~23 dB |
| 256-QAM | 8 | 8.0 | ~30 dB |

---

## Pièges Courants

1. **Démodulation AM non cohérente :** Sans PLL, la porteuse locale doit être parfaitement synchronisée. L'enveloppe simple (|signal|) fonctionne mieux pour l'AM avec porteuse forte.
2. **Phase non déroulée en FM :** `np.angle()` donne $[-\pi, \pi]$. Utiliser `np.unwrap()` avant différenciation.
3. **Filtre adapté non utilisé en réception :** Sans matched filter (RRC), le SNR est réduit et l'ISI augmente.
4. **Échantillonnage au mauvais instant :** Sans synchronisation de rythme, le SNR dégradé peut atteindre 3 dB.
5. **EVM trop optimiste :** Moyenner sur au moins 1000 symboles, retirer le biais DC et la rotation de phase.

---

## Liste de vérification (Checklist)

- [ ] Filtre RRC en émission ET en réception (matched filter).
- [ ] PLL (Costas loop) pour la récupération de porteuse cohérente.
- [ ] Timing recovery (Gardner, Mueller&Muller) pour l'échantillonnage optimal.
- [ ] Égaliseur (LMS, CMA) si canal sélectif en fréquence.
- [ ] Mapping Gray pour minimiser le BER (1 bit d'erreur par symbole adjacent).
- [ ] Puissance normalisée de la constellation ($E_s = 1$).
- [ ] Filtre de canal modélisé avant le déploiement.
- [ ] BER mesuré sur au moins $10^4$ bits pour une estimation fiable à $10^{-3}$.