---
name: audio-processing
description: "Traitement numérique du signal audio — librosa, sox/soxr, ffmpeg, filtrage FIR/IIR, noise reduction, normalisation, resampling, pitch shifting, time stretching."
tags: [audio, dsp, signal-processing, librosa, sox, ffmpeg, filtering, noise-reduction, resampling]
platforms: [linux, macos, windows]
related_skills: [mfcc-spectrogram-analysis, asr-reconnaissance-vocale, tts-synthese-vocale]
---

# Audio Processing — Traitement du Signal Audio

Guide complet du traitement numérique du signal audio : analyse, filtrage, transformation, restauration, effets.

## 1. Fondamentaux du DSP Audio

### 1.1 Concepts clés

```
Signal analogique → Échantillonnage → Quantification → Signal numérique (PCM)
               ADC (Analog-to-Digital Converter)
```

| Concept | Formule | Description |
|---------|---------|-------------|
| **Fréquence d'échantillonnage** | `fs` | Nombre d'échantillons/s (8kHz-192kHz) |
| **Quantification** | `2^n` niveaux | 16-bit = 65536 niveaux, 24-bit = 16M |
| **Théorème de Nyquist** | `f_max ≤ fs/2` | ½ de fs = fréquence max représentable |
| **Résolution temporelle** | `dt = 1/fs` | Intervalle entre échantillons |
| **Rapport signal/bruit** | `SNR = 6.02n + 1.76 dB` | Théorique pour quantification n-bit |

### 1.2 Bibliothèques Python principales

```python
import numpy as np
import librosa          # Analyse musicale
import soundfile as sf  # Lecture/écriture WAV/FLAC/OGG
import sounddevice as sd  # Lecture/écoute temps réel
import scipy.signal as signal  # Filtres avancés
import pydub            # Manipulation haute niveau (ffmpeg backend)
import pyrubberband     # Time stretching / pitch shifting
import noisereduce      # Réduction de bruit
import pyloudnorm       # Normalisation de loudness (EBU R128)
```

## 2. Manipulations fondamentales avec librosa

### 2.1 Chargement et sauvegarde

```python
import librosa
import soundfile as sf

# Chargement
audio, sr = librosa.load("fichier.wav", sr=22050, mono=True, offset=0.0, duration=None)
# sr=None = conserver le taux natif
# sr=22050 = rééchantillonner
# mono=True = convertir en mono

# Sauvegarde
sf.write("output.wav", audio, sr, subtype="PCM_16")

# Durée et autres métadonnées
duration = librosa.get_duration(y=audio, sr=sr)  # secondes
n_samples = len(audio)
```

### 2.2 Rééchantillonnage

```python
# librosa (SoX-like, bonne qualité)
audio_16k = librosa.resample(audio, orig_sr=sr, target_sr=16000)

# Avec scipy (filtre anti-aliasing)
from scipy import signal as sp_signal
audio_16k_scipy = sp_signal.resample_poly(
    audio,
    up=16000, down=sr,
    window=('kaiser', 5.0)  # Bon compromis qualité/performance
)

# Avec pyrubberband (haute qualité audio)
import pyrubberband as pyrb
audio_stretched = pyrb.time_stretch(audio, sr, 1.5)  # 1.5× plus lent
audio_shifted = pyrb.pitch_shift(audio, sr, 4)        # +4 demi-tons
```

### 2.3 Découpage et concaténation

```python
# Découpage temporel
segment = audio[int(5.0 * sr):int(10.0 * sr)]  # 5s à 10s

# Concaténation
audio_concat = np.concatenate([audio_a, audio_b])

# Cross-fade entre deux segments
def crossfade(a, b, duration=0.1, sr=22050):
    """Fondu-croisé entre deux signaux audio."""
    fade_len = int(duration * sr)
    fade_up = np.linspace(0, 1, fade_len)
    fade_down = np.linspace(1, 0, fade_len)

    a_out = a[:-fade_len]
    b_out = b[fade_len:]
    cross = a[-fade_len:] * fade_down + b[:fade_len] * fade_up

    return np.concatenate([a_out, cross, b_out])
```

## 3. Filtrage numérique

### 3.1 Filtres IIR (Infinite Impulse Response)

```python
from scipy import signal

# Filtre passe-bas Butterworth
b, a = signal.butter(4, 1000 / (sr/2), btype='low')  # 4e ordre, coupure 1kHz
audio_filtered = signal.filtfilt(b, a, audio)  # Phase linéaire (bidirectionnel)

# Filtre passe-haut (anti-pop / coupe DC)
b_hp, a_hp = signal.butter(2, 80 / (sr/2), btype='high')  # Coupe < 80 Hz
audio_hp = signal.filtfilt(b_hp, a_hp, audio)

# Filtre passe-bande
b_bp, a_bp = signal.butter(4, [300 / (sr/2), 3400 / (sr/2)], btype='band')  # Téléphone
audio_bp = signal.filtfilt(b_bp, a_bp, audio)

# Filtre réjecteur de bande (notch = 50Hz)
b_notch, a_notch = signal.iirnotch(50, 30, sr)  # Hum électrique
audio_notch = signal.filtfilt(b_notch, a_notch, audio)
```

### 3.2 Filtres FIR (Finite Impulse Response)

```python
# Conception FIR par fenêtrage
from scipy.signal import firwin, lfilter

# Passe-bas FIR avec fenêtre de Kaiser
taps = firwin(
    numtaps=101,         # Ordre du filtre (latence)
    cutoff=1000,          # Fréquence de coupure (Hz)
    fs=sr,
    window=('kaiser', 8.0),  # Fenêtre, beta contrôle l'atténuation
    pass_zero='lowpass'
)

# Application
audio_fir = lfilter(taps, 1.0, audio)  # Phase linéaire

# Comparaison FIR vs IIR
# FIR : phase linéaire, stable, latence élevée (n/2 échantillons)
# IIR : non-linéaire, peut être instable, latence faible
```

### 3.3 Filtres audio classiques

```python
# Filtre pré-emphasis (pour ASR)
def pre_emphasis(signal, coeff=0.97):
    """Souligne les hautes fréquences."""
    return np.append(signal[0], signal[1:] - coeff * signal[:-1])

# Filtre de de-emphasis (inverse)
def de_emphasis(signal, coeff=0.97):
    """Restaure le signal original après pre-emphasis."""
    out = np.zeros_like(signal)
    out[0] = signal[0]
    for i in range(1, len(signal)):
        out[i] = signal[i] + coeff * out[i-1]
    return out

# Filtre A-weighting (pondération perceptuelle)
def a_weighting(frequencies):
    """Pondération A pour mesure de bruit perceptuelle."""
    f = frequencies
    return (12194**2 * f**4) / (
        (f**2 + 20.6**2) * np.sqrt((f**2 + 107.7**2) * (f**2 + 737.9**2)) *
        (f**2 + 12194**2)
    )
```

## 4. Réduction de bruit

### 4.1 Spectral gating (noisereduce)

```python
import noisereduce as nr
import librosa

# Chargement bruité
noisy, sr = librosa.load("noisy_speech.wav", sr=16000)

# Réduction de bruit
# Méthode 1 : profil de bruit d'une section silencieuse
noise_sample = noisy[:int(0.5 * sr)]  # 500ms de bruit seul
reduced = nr.reduce_noise(
    y=noisy,
    sr=sr,
    y_noise=noise_sample,         # Profil de bruit
    prop_decrease=1.0,            # 1.0 = suppression max
    n_fft=2048,
    win_length=2048,
    hop_length=512,
    n_std_thresh_stationary=1.5,  # Seuil pour bruit stationnaire
    stationary=True
)

# Méthode 2 : estimation automatique du bruit
reduced_auto = nr.reduce_noise(
    y=noisy,
    sr=sr,
    prop_decrease=1.0,
    stationary=False,  # Bruit non-stationnaire
    n_jobs=4           # Parallélisation
)
```

### 4.2 Wiener filter adaptatif

```python
from scipy import signal as sp_signal

def wiener_filter(audio, noise_floor_db=-60, sr=16000):
    """Filtre de Wiener adaptatif."""
    n_fft = 2048
    hop_length = 512

    # STFT
    f, t, Zxx = sp_signal.stft(audio, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length)
    mag = np.abs(Zxx)
    phase = np.angle(Zxx)

    # Estimation du bruit (médiane des 10 premières trames)
    noise_est = np.median(mag[:, :10], axis=1, keepdims=True)

    # Rapport signal/bruit a priori (Decision-Directed)
    alpha = 0.98
    snr_prior = 0.01 * np.ones_like(mag)
    for t_idx in range(1, mag.shape[1]):
        snr_post = (mag[:, t_idx] ** 2) / (noise_est[:, 0] ** 2 + 1e-10) - 1
        snr_post = np.maximum(snr_post, 0)
        snr_prior[:, t_idx] = alpha * (mag[:, t_idx-1] ** 2) / (noise_est[:, 0] ** 2 + 1e-10) + (1-alpha) * snr_post

    # Gain Wiener
    gain = snr_prior / (1 + snr_prior)

    # Application
    Zxx_clean = gain * mag * np.exp(1j * phase)
    _, audio_clean = sp_signal.istft(Zxx_clean, fs=sr)

    return audio_clean
```

### 4.3 Réduction bruit avec FFmpeg / SoX (CLI)

```bash
# SoX : réduction de bruit (nécessite un sample de bruit)
sox noisy.wav reduced.wav noisered noise_profile.wav 0.2

# Créer profil de bruit
sox noisy.wav -n trim 0 1 noiseprof noise_profile.wav  # 1s de bruit
sox noisy.wav reduced.wav noisered noise_profile.wav 0.3

# FFmpeg : filtre passe-haut + afir
# Filtre afftdn (neural network based)
ffmpeg -i noisy.wav -af "afftdn=nf=-25" clean.wav
# anlmdn (non-local means denoising)
ffmpeg -i noisy.wav -af "anlmdn=s=1:p=0.5" clean.wav
```

## 5. Normalisation et Loudness

### 5.1 Normalisation du pic

```python
# Normalisation peak (crête)
def normalize_peak(audio, target_db=-1.0):
    """Normalise le pic à target_db."""
    peak = np.max(np.abs(audio))
    if peak == 0:
        return audio
    gain_db = target_db - 20 * np.log10(peak)
    gain_linear = 10 ** (gain_db / 20)
    return audio * gain_linear
```

### 5.2 Normalisation LUFS (EBU R128)

```python
import pyloudnorm as pyln

# Mesure du loudness
meter = pyln.Meter(sr)  # Taux d'échantillonnage du signal
loudness = meter.integrated_loudness(audio)
print(f"Loudness intégré : {loudness:.1f} LUFS")

# Normalisation à -14 LUFS (YouTube/Spotify standard)
loudness_normalized = pyln.normalize.loudness(audio, loudness, -14.0)

# Mesure de la plage dynamique
loudness_range = pyln.LoudnessRange(meter)
lr_value = loudness_range(audio)
print(f"Plage dynamique : {lr_value:.1f} LU")

# True peak
true_peak = np.max(np.abs(audio)) * (20 ** 0.5) / 2  # Approximation
```

### 5.3 Gate et expander

```python
def noise_gate(audio, threshold_db=-40, sr=44100, attack_ms=5, release_ms=50):
    """Noise gate : coupe les sections silencieuses."""
    threshold_linear = 10 ** (threshold_db / 20)
    attack = int(sr * attack_ms / 1000)
    release = int(sr * release_ms / 1000)

    envelope = np.abs(audio)
    # Filtrage de l'enveloppe (lissage)
    b = np.ones(attack) / attack
    envelope = signal.filtfilt(b, 1, envelope)

    # Application du gain
    gain = np.ones_like(audio)
    for i in range(1, len(audio)):
        if envelope[i] < threshold_linear:
            gain[i] = max(0, gain[i-1] - 1/release)  # Release
        else:
            gain[i] = min(1, gain[i-1] + 1/attack)  # Attack

    return audio * gain
```

## 6. Effets audio

### 6.1 Reverb (convolution avec IR)

```python
import scipy.io.wavfile as wav

# Convolution avec réponse impulsionnelle (IR)
def apply_reverb(audio, ir_path, sr=44100, mix=0.5):
    """Applique une reverb par convolution."""
    ir, ir_sr = librosa.load(ir_path, sr=sr, mono=True)
    ir = ir / np.sum(ir)  # Normalisation

    # Convolution
    wet = signal.fftconvolve(audio, ir, mode='full')[:len(audio)]

    # Mix dry/wet
    return (1 - mix) * audio + mix * wet
```

### 6.2 Compression

```python
def compressor(audio, threshold_db=-24, ratio=4.0, attack_ms=2, release_ms=100, sr=44100):
    """Compresseur audio classique."""
    threshold_linear = 10 ** (threshold_db / 20)
    attack = int(sr * attack_ms / 1000)
    release = int(sr * release_ms / 1000)

    # Calcul de l'enveloppe (RMS)
    window = int(sr * 0.01)  # 10ms
    rms = np.sqrt(np.mean(audio.reshape(-1, window) ** 2, axis=1))
    rms = np.repeat(rms, window)

    # Compression
    gain_reduction = np.ones_like(rms)
    for i in range(len(rms)):
        if rms[i] > threshold_linear:
            gain_reduction[i] = (threshold_linear + (rms[i] - threshold_linear) / ratio) / rms[i]

    # Lissage attack/release
    smoothed = np.zeros_like(gain_reduction)
    for i in range(1, len(gain_reduction)):
        tau = attack if gain_reduction[i] < smoothed[i-1] else release
        smoothed[i] = smoothed[i-1] + (gain_reduction[i] - smoothed[i-1]) / tau * window

    return audio * smoothed
```

### 6.3 Égalisation paramétrique

```python
from scipy.signal import iirpeak, iirnotch

class ParametricEQ:
    """Égaliseur paramétrique 3 bandes."""
    def __init__(self, sr):
        self.sr = sr

    def peaking(self, audio, freq, gain_db, q=1.0):
        """Filtre en cloche (peaking)."""
        A = 10 ** (gain_db / 40)
        omega = 2 * np.pi * freq / self.sr
        alpha = np.sin(omega) / (2 * q)

        b0 = 1 + alpha * A
        b1 = -2 * np.cos(omega)
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * np.cos(omega)
        a2 = 1 - alpha / A

        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0

        return signal.filtfilt(b, a, audio)

    def lowshelf(self, audio, freq, gain_db):
        """Filtre shelving basse fréquence."""
        A = 10 ** (gain_db / 40)
        omega = 2 * np.pi * freq / self.sr
        alpha = np.sin(omega) / np.sqrt(2)
        sqrt2A = 2 * np.sqrt(A) * alpha

        b0 = A * ((A + 1) - (A - 1) * np.cos(omega) + sqrt2A)
        b1 = 2 * A * ((A - 1) - (A + 1) * np.cos(omega))
        b2 = A * ((A + 1) - (A - 1) * np.cos(omega) - sqrt2A)
        a0 = (A + 1) + (A - 1) * np.cos(omega) + sqrt2A
        a1 = -2 * ((A - 1) + (A + 1) * np.cos(omega))
        a2 = (A + 1) + (A - 1) * np.cos(omega) - sqrt2A

        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0

        return signal.filtfilt(b, a, audio)
```

## 7. SoX (Swiss Army Knife audio CLI)

```bash
# Informations
sox --i input.wav

# Conversion de format
sox input.wav -r 16000 -b 16 -c 1 output.wav  # 16kHz, 16-bit, mono

# Pitch shifting (sans changer durée)
sox input.wav output.wav pitch 300  # +300 cents (+3 demi-tons)

# Time stretching
sox input.wav output.wav tempo -s 1.5  # 1.5× plus rapide

# Trim et fade
sox input.wav output.wav trim 10 15  # 10s → 25s
sox input.wav output.wav fade 3 30 1  # fade-in 3s, total 30s, fade-out 1s

# Mixer deux fichiers
sox -m input1.wav input2.wav mixed.wav

# Effet chorus
sox input.wav output.wav chorus 0.7 0.9 55 0.4 0.25 2 -t

# Effet flanger
sox input.wav output.wav flanger

# Spectrogramme en image
sox input.wav -n spectrogram -o spectrogram.png
```

## 8. FFmpeg (audio processing avancé)

```bash
# Conversion de conteneur/codec
ffmpeg -i input.mp3 output.wav
ffmpeg -i input.wav -c:a libmp3lame -b:a 192k output.mp3

# Extraction audio de vidéo
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 44100 audio.wav

# Changement de fréquence d'échantillonnage
ffmpeg -i input.wav -ar 16000 output.wav

# Concaténation avec filtre crossfade
ffmpeg -i a.wav -i b.wav -filter_complex "acrossfade=d=0.5" merged.wav

# Volume / Normalisation
# Normalisation EBU R128
ffmpeg -i input.wav -af "loudnorm=I=-14:LRA=1:TP=-1" output.wav
# Volume simple (×2)
ffmpeg -i input.wav -af "volume=2.0" output.wav

# Filtre audio : égaliseur
ffmpeg -i input.wav -af "equalizer=f=1000:t=q:w=1:g=5" output.wav  # +5dB à 1kHz

# Filtre : suppression silence
ffmpeg -i input.wav -af "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.5" output.wav

# Filtre : ré-échantillonnage haute qualité
ffmpeg -i input.wav -af "aresample=resampler=soxr" -ar 44100 output.wav

# Génération tons de test
ffmpeg -f lavfi -i "sine=frequency=440:duration=5" 440hz.wav
ffmpeg -f lavfi -i "anoisesrc=d=5:c=pink:seed=42" pink_noise.wav
```

## 9. Analyse spectrale temps réel

```python
import numpy as np
import sounddevice as sd

class RealtimeSpectrumAnalyzer:
    """Analyseur de spectre temps réel."""
    def __init__(self, sr=44100, block_size=2048):
        self.sr = sr
        self.block_size = block_size
        self.freqs = np.fft.rfftfreq(block_size, 1/sr)

    def callback(self, indata, frames, time, status):
        """Callback audio en temps réel."""
        if status:
            print(f"Erreur: {status}")

        # FFT
        spectrum = np.fft.rfft(indata[:, 0] * np.hanning(len(indata)))
        magnitude = np.abs(spectrum)

        # Bandes de fréquences
        bands = {
            "Sub (20-60Hz)": self._band_energy(magnitude, 20, 60),
            "Bass (60-250Hz)": self._band_energy(magnitude, 60, 250),
            "Low Mid (250-500Hz)": self._band_energy(magnitude, 250, 500),
            "Mid (500-2000Hz)": self._band_energy(magnitude, 500, 2000),
            "Upper Mid (2-4kHz)": self._band_energy(magnitude, 2000, 4000),
            "Presence (4-6kHz)": self._band_energy(magnitude, 4000, 6000),
            "Brilliance (6-20kHz)": self._band_energy(magnitude, 6000, 20000),
        }

        # Affichage barres ASCII
        for name, energy in bands.items():
            bars = int(energy * 50)
            print(f"{name:20} |{'█' * bars}{'░' * (50 - bars)}")

    def _band_energy(self, magnitude, f_min, f_max):
        mask = (self.freqs >= f_min) & (self.freqs <= f_max)
        return np.mean(magnitude[mask]) / (np.max(magnitude) + 1e-10)

    def start(self):
        """Démarre l'analyse en continu."""
        with sd.InputStream(device=0, channels=1, callback=self.callback,
                          blocksize=self.block_size, samplerate=self.sr):
            input("Analyseur en cours... Appuyez sur Entrée pour arrêter")
```

## 10. Pitfalls et solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| Alias (fréquences fantômes) | Échantillonnage < 2*f_max | Filtre anti-aliasing avant downsampling |
| Clics aux jonctions | Discontinuités de phase | Cross-fade aux coupures |
| Distorsion numérique | Écrêtage (clipping) | Normalisation avant effets |
| Réverbération de bruit | Gate trop agressif | Release plus long, threshold adaptatif |
| Phase non-linéaire | Filtres IIR | Utiliser filtfilt ou FIR |
| Artefacts MP3 | Compression avec pertes | Travailler en WAV/FLAC, convertir à la fin |

## Références

- **librosa** : https://librosa.org/
- **SoX** : http://sox.sourceforge.net/
- **FFmpeg** : https://ffmpeg.org/ffmpeg-filters.html
- **pyloudnorm** : https://github.com/csteinmetz1/pyloudnorm
- **noisereduce** : https://github.com/timsainb/noisereduce
- **pyrubberband** : https://github.com/bmcfee/pyrubberband
- **scipy.signal** : https://docs.scipy.org/doc/scipy/reference/signal.html
- **sounddevice** : https://python-sounddevice.readthedocs.io/