---
name: sdr-advanced
description: "Radio Logicielle (SDR) avancée — chaîne de réception/émission, échantillonnage IQ, récepteurs superhétérodynes, DDC/DUC, correction IQ, synchronisation, radioamateur, reverse engineering RF, analyse de protocoles IoT."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [sdr, radio-logicielle, iq-sampling, superheterodyne, ddc, duc, hackrf, limesdr, plutosdr, rtlsdr, rtlsdr, soapysdr, gr-osmosdr, iq-imbalance, doppler, localisation, ads-b, acars, aprs, pocsag, iot, rf, spectrum, sigid]
    related_skills: [dsp-fundamentals, fft-algorithms, gnu-radio, modulation-demodulation, signal-processing-digital, radio-sdr]
---

# Radio Logicielle (SDR) Avancée

## Vue d'ensemble

La radio logicielle (Software-Defined Radio — SDR) remplace les circuits analogiques par du traitement numérique. Les convertisseurs A/N et N/A sont placés le plus près possible de l'antenne, et tout le traitement (filtrage, modulation, démodulation) se fait dans le domaine numérique.

### Chaîne SDR typique

```
Antenne
   ↓
Filtre RF (passe-bande sélectif)
   ↓
LNA (Low Noise Amplifier)
   ↓
Mélangeur → Oscillateur Local (LO)
   ↓
Filtre FI (Fréquence Intermédiaire)
   ↓
ADC (échantillonnage IQ)
   ↓
[Domaine numérique : DDC → Filtrage → Démodulation → Décodage]
```

---

## 1. Échantillonnage IQ

### 1.1 Signal en bande de base complexe

Une radio SDR échantillonne le signal en **IQ (In-phase / Quadrature)** :

$$s(t) = I(t) \cdot \cos(2\pi f_c t) - Q(t) \cdot \sin(2\pi f_c t)$$

Le signal IQ est la représentation en bande de base complexe $z(t) = I(t) + jQ(t)$.

```python
import numpy as np

def generer_iq(fm, fs, duree, f_lo=0):
    """
    Génère un signal IQ à partir d'une modulation de fréquence.

    fm  : fréquence modulante (Hz)
    fs  : fréquence d'échantillonnage IQ (Hz)
    """
    t = np.arange(0, duree, 1/fs)
    # Signal modulant (ex: FM avec déviation)
    message = np.sin(2 * np.pi * fm * t)
    deviation = 5000  # Hz

    # Phase instantanée
    phase = 2 * np.pi * np.cumsum(message) * deviation / fs
    # Correction : retirer la porteuse (f_lo = 0 si centré)
    phase -= 2 * np.pi * f_lo * t

    # IQ
    I = np.cos(phase)
    Q = np.sin(phase)
    return I + 1j * Q

# Le signal IQ échantillonné occupe la bande [-fs/2, fs/2]
# Le débit binaire (BPSK) : fs échantillons complexes par seconde
# Sur USB : 2 * fs * 8 bits (pour I16 + Q16)
```

### 1.2 Taux d'échantillonnage et bande passante

Pour un signal IQ, la bande passante maximale analysable est $BW = f_s$.

- **RTL-SDR** : $f_s$ max = 3.2 MHz (stable à 2.4 MHz) → BW = 2.4 MHz
- **HackRF** : $f_s$ max = 20 MHz → BW = 20 MHz
- **LimeSDR** : $f_s$ max = 61.44 MHz → BW = 61.44 MHz
- **PlutoSDR** : $f_s$ max = 61.44 MHz → BW = 20 MHz (pratique)

### 1.3 Déséquilibre IQ (IQ Imbalance)

Les imperfections analogiques créent un déséquilibre entre I et Q (gain, phase, offset DC).

```python
def corriger_iq(signal_iq, gain_ratio=1.0, phase_offset=0.0, dc_i=0, dc_q=0):
    """
    Corrige le déséquilibre IQ.

    Paramètres :
        signal_iq   : signal IQ brut
        gain_ratio  : rapport de correction de gain Q/I
        phase_offset: correction de phase (radians)
        dc_i, dc_q  : offset DC sur I et Q
    """
    # Correction DC
    I = signal_iq.real - dc_i
    Q = signal_iq.imag - dc_q

    # Correction gain
    Q = Q / gain_ratio

    # Correction phase
    I_corr = I
    Q_corr = Q * np.cos(phase_offset) - I * np.sin(phase_offset)

    return I_corr + 1j * Q_corr

# Estimation automatique du déséquilibre (méthode de la covariance)
def estimer_iq_imbalance(signal_iq):
    """Estime le déséquilibre IQ à partir du signal reçu."""
    I = signal_iq.real
    Q = signal_iq.imag

    gain_ratio = np.std(Q) / np.std(I)
    phase_offset = np.mean(np.arcsin((I * Q) / (np.std(I) * np.std(Q))))
    dc_i = np.mean(I)
    dc_q = np.mean(Q)

    return gain_ratio, phase_offset, dc_i, dc_q
```

---

## 2. Architecture de Récepteur

### 2.1 Superhétérodyne classique vs DDC numérique

```python
# DDC (Digital Down-Converter) : décalage en fréquence numérique
# Principe : multiplier par e^{-j2π f_shift t} + filtrage FIR

def ddc_numerique(signal_iq, f_shift, fs):
    """
    DDC : décalage du spectre vers DC.
    f_shift : décalage en Hz (positif ou négatif)
    fs : fréquence d'échantillonnage
    """
    N = len(signal_iq)
    n = np.arange(N)
    oscillateur = np.exp(-2j * np.pi * f_shift * n / fs)
    return signal_iq * oscillateur

# CIC (Cascaded Integrator-Comb) + FIR : décimation avec filtrage
# Utilisé dans les SDR pour réduire fs et extraire une bande étroite
```

### 2.2 Récepteur FM stéréo complet

```python
def demoduler_fm_stereo(signal_iq, fs, f_dev=75000):
    """
    Démodulation FM stéréo complète.

    Paramètres :
        signal_iq : signal IQ à fs échantillons/s
        fs        : fréquence d'échantillonnage
        f_dev     : déviation max (75 kHz pour FM broadcast)
    """
    # 1. Phase instantanée
    phase = np.unwrap(np.angle(signal_iq))

    # 2. Dérivée → fréquence instantanée
    freq = np.diff(phase) * fs / (2 * np.pi)

    # 3. Désaccentuation (filtre passe-bas 75 µs)
    tau = 75e-6
    alpha = 1 / (1 + fs * tau)
    freq_filtre = [freq[0]]
    for f in freq[1:]:
        freq_filtre.append(alpha * freq_filtre[-1] + (1 - alpha) * f)

    # 4. Audio mono = somme L+R
    audio_mono = np.array(freq_filtre)

    # 5. Stéréo : pilote 19 kHz, L-R à 38 kHz
    # Démodulation de la sous-porteuse 38 kHz
    pilot = signal_iq * np.exp(-2j * np.pi * 19000 / fs)
    # PLL simple pour verrouiller la phase du pilote
    # (implémentation complète : Costas Loop)

    return audio_mono
```

### 2.3 PLL numérique (Costas Loop)

```python
def costas_pll(signal_iq, fs, f_center=0, loop_bw=100):
    """
    Boucle de Costas pour la récupération de porteuse.

    Utilisée en PSK, QAM, FM, etc. pour synchroniser
    l'oscillateur local avec la porteuse reçue.
    """
    N = len(signal_iq)
    phase = 0.0
    freq = 2 * np.pi * f_center / fs
    alpha = 2 * loop_bw / fs
    beta = alpha**2 / 2

    sortie = np.zeros(N, dtype=complex)
    for n in range(N):
        # Oscillateur local
        lo = np.exp(-1j * phase)
        sortie[n] = signal_iq[n] * lo

        # Détection de phase (BPSK)
        phase_error = np.real(sortie[n]) * np.imag(sortie[n])

        # Filtre de boucle (proportionnel + intégral)
        freq += beta * phase_error
        phase += freq + alpha * phase_error
        phase %= 2 * np.pi

    return sortie, phase
```

---

## 3. Analyse Spectrale et Mesures

### 3.1 Densité spectrale de puissance (PSD) d'un signal SDR

```python
from scipy.signal import welch

def psd_sdr(signal_iq, fs, nperseg=4096):
    """
    PSD d'un signal IQ. Utiliser Welch pour la stabilité statistique.
    """
    f, Pxx = welch(signal_iq, fs=fs, nperseg=nperseg,
                    window='hann', return_onesided=False)
    # FFT shift pour centrer sur 0
    f = np.fft.fftshift(f)
    Pxx = np.fft.fftshift(Pxx)
    Pxx_dB = 10 * np.log10(np.abs(Pxx) + 1e-10)
    return f, Pxx_dB

# Mesures :
# Bruit de fond (noise floor) = median(Pxx_dB[bande_sans_signal])
# SNR = P_signal - P_bruit
# SFDR = P_porteuse - P_spurious_max
# Bande passante occupée = -3dB en dessous du pic
```

### 3.2 Waterfall (spectrogramme SDR)

```python
def waterfall_sdr(signal_iq, fs, nperseg=2048, noverlap=1536):
    """
    Génère un waterfall (spectrogramme) pour visualisation SDR.
    Retourne (f, t, Sxx_dB) où Sxx_dB[i][j] est la puissance
    à la fréquence f[i] au temps t[j].
    """
    from scipy.signal import spectrogram
    f, t, Sxx = spectrogram(signal_iq, fs=fs,
                            nperseg=nperseg, noverlap=noverlap,
                            window='hann', mode='magnitude',
                            return_onesided=False)
    # Centrer
    f = np.fft.fftshift(f)
    Sxx = np.fft.fftshift(Sxx, axes=0)
    Sxx_dB = 20 * np.log10(np.abs(Sxx) + 1e-10)
    return f, t, Sxx_dB
```

---

## 4. Reverse Engineering RF

### 4.1 Protocol Reverse Engineering Workflow

```
1. Capture large bande → Identifier la fréquence et la bande passante
2. Analyse temps-fréquence → Déterminer le type de modulation
3. Démodulation → Récupérer le flux binaire brut
4. Décodage de symbole → Bits, symboles, trames
5. Analyse de protocole → Structure des paquets
6. Rejeu → Vérification
7. Exploitation → Attaque (replay, injection, fuzzing)
```

### 4.2 Détection et catégorisation automatique de signaux

```python
def identifier_modulation(signal_iq, fs):
    """
    Classification basique de modulation par features.

    Features : variance de l'amplitude, variance de la phase,
               symétrie spectrale, cyclic prefix correlation...
    """
    amplitude = np.abs(signal_iq)
    phase = np.unwrap(np.angle(signal_iq))

    features = {
        'var_amplitude': np.var(amplitude),
        'var_phase': np.var(np.diff(phase)),
        'snr_estime': 20 * np.log10(np.mean(amplitude) / np.std(amplitude)),
        'symetrie_spectrale': np.corrcoef(
            signal_iq[:len(signal_iq)//2],
            signal_iq[len(signal_iq)//2:])[0, 1],
    }

    # Règles de décision simples
    if features['var_amplitude'] < 0.1 and features['var_phase'] > 1:
        # Phase qui varie, amplitude constante → FM, PSK, FSK
        # Distinguer FM (phase continue) de PSK (sauts de phase)
        sauts = np.sum(np.abs(np.diff(phase)) > np.pi / 4)
        if sauts > len(signal_iq) * 0.01:
            return "FSK/PSK"
        else:
            return "FM"
    elif features['var_amplitude'] > 0.1 and features['var_phase'] < 1:
        return "AM"
    else:
        return "QAM/APSK"

    return features
```

### 4.3 Analyse de protocoles IoT

| Protocole | Fréquence | Modulation | Débit | Portée |
|:---|---|---:|---:|
| **LoRa** | 433/868/915 MHz | CSS | 0.3-50 kbps | 2-15 km |
| **Zigbee** | 2.4 GHz | OQPSK | 250 kbps | 10-100 m |
| **BLE** | 2.4 GHz | GFSK | 1-2 Mbps | 10-50 m |
| **Z-Wave** | 868/908 MHz | GFSK | 100 kbps | 30 m |
| **SIGFOX** | 868 MHz | DBPSK/GMSK | 100 bps | 10-50 km |
| **NB-IoT** | Bande LTE | QPSK | ~200 kbps | 1-10 km |
| **EnOcean** | 868 MHz | ASK | 125 kbps | 30 m |
| **Wireless M-Bus** | 868 MHz | T曼 | 4.8-100 kbps | 100 m |

### 4.4 Rejeu et injection (Replay Attack)

```python
# Avec HackRF :
# 1. Capture
# hackrf_transfer -r capture.iq -f 433920000 -s 8000000

# 2. Identifier la modulation (URH : Universal Radio Hacker)
# urh

# 3. Rejeu (préambule + payload)
# hackrf_transfer -t payload.iq -f 433920000 -s 8000000 -x 40 -a 1

# Avec GNU Radio :
# Utiliser un bloc Vector Source + Osmocom Sink
```

---

## 5. Radionavigation et Géolocalisation

### 5.1 TDOA (Time Difference of Arrival)

```python
def tdoa(signal_antenne1, signal_antenne2, fs):
    """
    Estimation du TDOA entre deux antennes synchronisées.

    Retourne : délai en échantillons, angle d'arrivée (AoA)
    """
    from scipy.signal import correlate
    corr = correlate(signal_antenne1, signal_antenne2)
    lag = np.argmax(np.abs(corr)) - len(corr) // 2
    delay = lag / fs  # Secondes

    # Angle d'arrivée si distance entre antennes connue (d)
    d = 0.5  # Mètres
    c = 3e8
    theta = np.arcsin(delay * c / d)  # Radians
    return delay, np.degrees(theta)
```

### 5.2 Doppler et localisation par dérive

```python
def estimer_doppler(signal, freq_porteuse, fs):
    """
    Estime le décalage Doppler pour la localisation de mobiles.
    """
    # PLL pour suivre la dérive de fréquence
    # Démodulation FM de la différence de phase
    phase = np.unwrap(np.angle(signal))
    freq_instant = np.diff(phase) * fs / (2 * np.pi)
    doppler_shift = np.mean(freq_instant)
    vitesse = doppler_shift * 3e8 / freq_porteuse  # m/s
    return doppler_shift, vitesse
```

---

## 6. Matériel SDR Avancé

### 6.1 Comparatif plateformes

| Plateforme | $f_s$ max | Bande | Bits ADC | Prix | Full-duplex |
|:---:|---:|---:|---:|---:|---:|
| RTL-SDR | 3.2 MHz | 24-1700 MHz | 8 | ~25€ | Non |
| HackRF | 20 MHz | 1-6000 MHz | 8 | ~300€ | Semi |
| LimeSDR Mini | 30.72 MHz | 10-3500 MHz | 12 | ~200€ | Oui |
| PlutoSDR | 61.44 MHz | 325-3800 MHz | 12 | ~200€ | Oui |
| BladeRF 2.0 | 61.44 MHz | 47-6000 MHz | 12 | ~400€ | Oui |
| USRP B210 | 61.44 MHz | 70-6000 MHz | 12 | ~1100€ | Oui |
| ADALM Pluto | 61.44 MHz | 325-3800 MHz | 12 | ~150€ | Oui |
| KerberosSDR | 3.2 MHz × 4 | 24-1700 MHz | 8 | ~150€ | Non (4x RX) |

### 6.2 Calibration

```python
def calibrer_sdr(sdr_device, freq_test):
    """
    Calibration d'un SDR : compenser les erreurs de fréquence.

    La dérive du TCXO peut atteindre ±50 ppm.
    Un signal de référence (GPS, station FM connue) corrige l'offset.
    """
    # Erreur relative
    erreur_ppm = (freq_mesuree - freq_test) / freq_test * 1e6
    freq_corrigee = freq_souhaitee * (1 - erreur_ppm / 1e6)
    return freq_corrigee
```

---

## 7. Radioamateur et Modes Numériques

### 7.1 FT8 (Franke-Taylor 8-FSK)

- Modulation : 8-FSK, 50 bauds, 15 Hz d'espacement
- Décodeur : `wsprd` / `jtdx`
- SNR minimum : -20 dB (décodable sous le bruit de fond)
- Durée d'un message : 12.6 secondes

### 7.2 WSPR (Weak Signal Propagation Reporter)

- Modulation : 4-FSK, 1.46 bauds
- Bande passante : 6 Hz
- SNR minimum : -28 dB
- Utilisé pour le sondage ionosphérique

### 7.3 APRS (Automatic Packet Reporting System)

- Modulation : AFSK 1200 bauds (Bell 202) sur 144.800 MHz (Europe)
- Protocole : AX.25
- Position, météo, messages

```bash
# Réception APRS
rtl_fm -f 144.800M -s 22050 | multimon-ng -a AFSK1200 -t raw -
```

### 7.4 Satellite et ISS

```python
# Réception SSTV depuis l'ISS (145.800 MHz FM)
# 1. Suivre le passage avec gpredict ou orbitron
# 2. Capturer avec rtl_fm et décoder avec MMSSTV / RX-SSTV
# rtl_fm -f 145.800M -s 22050 -g 40 | sox -t raw -r 22050 -e signed -b 16 -c 1 - sstv.wav

# NOAA APT (images météo)
# rtl_fm -f 137.100M -s 38000 -g 40 | sox -t raw -r 38000 -esigned -b 16 -c 1 - noaa.wav
# wxtoimg noaa.wav image.png
```

---

## Pièges Courants

1. **Saturation du LNA :** Trop de gain → intermodulation et saturation. Commencer par un gain faible.
2. **Offset IQ non corrigé :** Une image fantôme apparaît à $-f_{signal}$ dans le spectre, divisant le SNR par 2.
3. **Bruit de l'horloge USB :** L'alimentation USB des RTL-SDR est brutée. Utiliser un câble avec ferrite ou une alimentation externe.
4. **Échantillonnage insuffisant pour la bande passante :** Pour analyser un signal de 200 kHz de large, $f_s$ doit être ≥ 200 kHz (signal IQ).
5. **Dépassement du buffer USB (overflow) :** Baisser $f_s$ ou le gain si des échantillons sont perdus.

---

## Ressources

- **Signal Identification Wiki** : https://www.sigidwiki.com
- **RadioReference DB** : https://www.radioreference.com
- **Universal Radio Hacker (URH)** : https://github.com/jopohl/urh
- **Inspectrum** : Analyse de signaux IQ : https://github.com/miek/inspectrum
- **SDR++** : Récepteur SDR moderne : https://www.sdrpp.org
- **GNURadio** : https://wiki.gnuradio.org

---

## Liste de vérification (Checklist)

- [ ] Gain LNA configuré (éviter saturation, pas d'intermodulation).
- [ ] Correction IQ appliquée (offset DC, gain imbalance, phase).
- [ ] Bande passante adaptée au signal cible.
- [ ] $f_s$ conforme au théorème de Nyquist pour la bande étudiée.
- [ ] PLL verrouillée pour la démodulation cohérente.
- [ ] Buffer USB sans overflow (vérifier `rtl_test`).
- [ ] Calibration en fréquence (TCXO dérive, référence externe si besoin).