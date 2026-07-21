---
name: mfcc-spectrogram-analysis
description: "Analyse spectrale audio — MFCC, spectrogramme Mel, chroma, spectral features, STFT, CQT, extraction de caractéristiques pour ML/ASR/classification musicale."
tags: [audio, dsp, mfcc, spectrogram, features, librosa, feature-extraction, signal-analysis]
platforms: [linux, macos, windows]
related_skills: [audio-processing, asr-reconnaissance-vocale, music-generation]
---

# MFCC & Spectrogram Analysis — Analyse Spectrale et Extraction de Caractéristiques

Guide complet des représentations temps-fréquence, extraction de caractéristiques audio pour ML, ASR, classification musicale et analyse acoustique.

## 1. Fondamentaux : Transformations Temps-Fréquence

### 1.1 STFT (Short-Time Fourier Transform)

```python
import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Chargement
audio, sr = librosa.load("audio.wav", sr=22050)

# STFT avec paramètres
D = librosa.stft(
    audio,
    n_fft=2048,        # Taille de la fenêtre FFT (puissance de 2)
    hop_length=512,     # Pas entre fenêtres (généralement n_fft/4)
    win_length=2048,    # Taille de la fenêtre (≤ n_fft)
    window='hann',      # Fenêtre (hann, hamming, blackman, etc.)
    center=True         # Centrer les trames
)

# Magnitude (dB)
magnitude_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

# Phase
phase = np.angle(D)

# Affichage
librosa.display.specshow(magnitude_db, sr=sr, hop_length=512, x_axis='time', y_axis='hz')
plt.colorbar(format='%+2.0f dB')
plt.title('Spectrogramme STFT')
plt.tight_layout()
```

### 1.2 Paramètres de la STFT

| Paramètre | Valeur typique | Effet |
|-----------|---------------|-------|
| `n_fft` | 2048 (93ms @ 22kHz) | Résolution fréquentielle `Δf = sr/n_fft` |
| `hop_length` | 512 (23ms) | Résolution temporelle : `Δt = hop/sr` |
| `window` | hann | Compromis résolution/leakage spectral |
| `center` | True | Trames centrées (pas de décalage) |

**Compromis temps-fréquence** : `n_fft` large → haute résolution fréquentielle, faible résolution temporelle. `n_fft` petit → l'inverse.

### 1.3 CQT (Constant-Q Transform)

```python
# CQT : résolution fréquentielle logarithmique (perceptive)
C = librosa.cqt(
    audio,
    sr=sr,
    fmin=librosa.note_to_hz('C1'),  # 32.7 Hz
    n_bins=84,                       # 7 octaves × 12 demi-tons
    bins_per_octave=12,              # Résolution chromatique
    filter_scale=1                   # Largeur des filtres (1 = default)
)

# Spectrogramme CQT en dB
C_db = librosa.amplitude_to_db(np.abs(C), ref=np.max)

# CQT hybride (plus rapide, même qualité)
C_half = librosa.hybrid_cqt(audio, sr=sr, fmin=32.7, n_bins=84)

# Affichage
librosa.display.specshow(C_db, sr=sr, x_axis='time', y_axis='cqt_note')
plt.title('Spectrogramme CQT (Constant-Q)')
```

## 2. Mel Spectrogramme

### 2.1 Génération

```python
# Mel spectrogramme (échelle perceptuelle)
mel_spec = librosa.feature.melspectrogram(
    y=audio,
    sr=sr,
    n_fft=2048,
    hop_length=512,
    win_length=2048,
    window='hann',
    n_mels=128,           # Nombre de bandes Mel (40-128)
    fmin=0,               # Fréquence minimale (Hz)
    fmax=sr/2,            # Fréquence maximale (Hz)
    htk=False,            # Échelle Mel HTK (vs Slaney)
    power=2.0             # Puissance (2.0 = puissance, 1.0 = magnitude)
)

# Conversion en dB (log)
mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

# Affichage
librosa.display.specshow(mel_spec_db, sr=sr, hop_length=512, x_axis='time', y_axis='mel')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel Spectrogramme (128 bandes)')
```

### 2.2 Échelle Mel — Formule

```
Formule standard :  Mel(f) = 2595 × log10(1 + f/700)
Formule HTK :       Mel(f) = 1127 × ln(1 + f/700)
```

L'échelle Mel est linéaire < 1000 Hz, logarithmique au-dessus, imitant la perception humaine des hauteurs.

### 2.3 Mel spectrogramme inversé

```python
# Reconstruction audio depuis un mel spectrogramme (Griffin-Lim)
# Utilisé dans les modèles vocaux (TTS, vocoders)

# Mel → puissance → phase approximée
S = librosa.db_to_power(mel_spec_db)
y_reconstructed = librosa.feature.inverse.mel_to_audio(
    S,
    sr=sr,
    n_fft=2048,
    hop_length=512,
    win_length=2048,
    window='hann',
    n_iter=32,             # Itérations Griffin-Lim (plus = meilleur)
    length=len(audio)      # Longueur cible
)

# Mel → STFT (avec phase estimée)
stft_reconstructed = librosa.feature.inverse.mel_to_stft(
    S,
    sr=sr,
    n_fft=2048,
    power=2.0
)

# Utilisation avec un vocoder neuronal (HiFi-GAN, WaveGlow)
# L'approche Mel → Vocoder donne une qualité bien supérieure à Griffin-Lim
```

## 3. MFCC (Mel-Frequency Cepstral Coefficients)

### 3.1 Extraction

```python
# MFCC classiques
mfccs = librosa.feature.mfcc(
    y=audio,
    sr=sr,
    n_mfcc=13,          # 13 coefficients (standard ASR)
    n_fft=2048,
    hop_length=512,
    win_length=2048,
    window='hann',
    n_mels=40,          # 40 bandes Mel pour le calcul intermédiaire
    fmin=0,
    fmax=sr/2,
    dct_type=2,         # Type de DCT (2 = standard)
    norm='ortho',       # Normalisation orthogonale
    lifter=0,           # Liftering (0 = pas de lifter)
)

print(f"Forme : {mfccs.shape}")  # (n_mfcc, n_frames)

# MFCC avec delta et delta-delta
mfccs_delta = librosa.feature.delta(mfccs)
mfccs_delta2 = librosa.feature.delta(mfccs, order=2)

# Feature vector complet (39 dimensions : 13 + 13Δ + 13ΔΔ)
mfccs_full = np.vstack([mfccs, mfccs_delta, mfccs_delta2])

# Affichage
librosa.display.specshow(mfccs, sr=sr, hop_length=512, x_axis='time')
plt.ylabel('Coefficient MFCC')
plt.title('MFCC (13 coefficients)')
```

### 3.2 Pipeline de prétraitement pour ASR

```python
class ASRFeatureExtractor:
    """Extraction de caractéristiques pour ASR (type Kaldi)."""
    def __init__(self, sr=16000, n_mfcc=13, n_mels=23, frame_length=25, frame_shift=10):
        self.sr = sr
        self.n_mfcc = n_mfcc
        self.n_mels = n_mels
        self.n_fft = int(sr * frame_length / 1000)  # 400 samples @ 25ms
        self.hop_length = int(sr * frame_shift / 1000)  # 160 samples @ 10ms

    def extract(self, audio):
        # Pré-emphasis
        audio = np.append(audio[0], audio[1:] - 0.97 * audio[:-1])

        # Mel spectrogramme
        mel = librosa.feature.melspectrogram(
            y=audio, sr=self.sr,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            n_mels=self.n_mels,
            fmin=0, fmax=self.sr/2,
            power=2.0
        )

        # Log
        log_mel = np.log(mel + 1e-10)

        # DCT → MFCC
        mfcc = librosa.feature.mfcc(
            S=log_mel, n_mfcc=self.n_mfcc,
            dct_type=2, norm='ortho'
        )

        # Normalisation (CMVN : Cepstral Mean and Variance Normalization)
        mfcc = (mfcc - np.mean(mfcc, axis=1, keepdims=True)) / (np.std(mfcc, axis=1, keepdims=True) + 1e-10)

        # Delta + Delta-Delta
        delta = librosa.feature.delta(mfcc)
        delta2 = librosa.feature.delta(mfcc, order=2)

        return np.vstack([mfcc, delta, delta2])

# Utilisation
extractor = ASRFeatureExtractor()
features = extractor.extract(audio)  # (39, n_frames)
```

### 3.3 MFCC pour classification musicale

```python
def extract_music_features(audio_path):
    """Extrait MFCC + features musicaux pour classification de genre."""
    audio, sr = librosa.load(audio_path, sr=22050, duration=30)

    # MFCC (20 coefficients pour musique)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20, n_mels=128)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)
    mfcc_skew = np.mean(((mfcc - mfcc_mean.reshape(-1, 1)) / (mfcc_std.reshape(-1, 1) + 1e-10)) ** 3, axis=1)

    # Chroma features
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)

    # Spectral features
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
    spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)

    # Zero-crossing rate
    zcr = librosa.feature.zero_crossing_rate(audio)

    # Tempo
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)

    # Feature vector
    feature_vector = np.concatenate([
        mfcc_mean, mfcc_std, mfcc_skew,
        chroma_mean,
        [np.mean(spectral_centroid), np.std(spectral_centroid)],
        [np.mean(spectral_bandwidth), np.std(spectral_bandwidth)],
        [np.mean(spectral_rolloff), np.std(spectral_rolloff)],
        [np.mean(spectral_contrast), np.std(spectral_contrast)],
        [np.mean(zcr), np.std(zcr)],
        [tempo]
    ])

    return feature_vector
```

## 4. Caractéristiques Spectrales Avancées

### 4.1 Spectral features

```python
# Centroid spectral (centre de masse du spectre)
centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
# Valeur basse → sons graves, valeur haute → sons aigus

# Bandwidth spectral (largeur de bande)
bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr, p=2)
# p=2 → puissance 2 (RMS-like), p=3 → skewness

# Rolloff (fréquence en dessous de laquelle X% de l'énergie est concentrée)
rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr, roll_percent=0.85)

# Contrast spectral (différence pic/creux par bande)
contrast = librosa.feature.spectral_contrast(y=audio, sr=sr, n_bands=6, fmin=200.0)

# Flatness (mesure de bruit vs tonal)
flatness = librosa.feature.spectral_flatness(y=audio, sr=sr, amin=1e-10, power=2.0)
# Proche de 0 → tonal, proche de 1 → bruit

# Tonnetz (réseaux tonaux — Tonal Centroid Features)
tonnetz = librosa.feature.tonnetz(y=audio, sr=sr, chroma=None)
# 6 dimensions : [tonic, dominant, subdominant, ...]
```

### 4.2 Chroma Features

```python
# Chroma STFT (pitch class profile : 12 classes)
chroma_stft = librosa.feature.chroma_stft(y=audio, sr=sr, n_chroma=12, norm=2)

# Chroma CQT (meilleure résolution)
chroma_cqt = librosa.feature.chroma_cqt(y=audio, sr=sr, n_chroma=12)

# Chroma CENS (Chroma Energy Normalized, robuste à la dynamique)
chroma_cens = librosa.feature.chroma_cens(y=audio, sr=sr, n_chroma=12)

# Mapping des 12 classes
chroma_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Profil harmonique moyen
chroma_mean = np.mean(chroma_cqt, axis=1)
for note, energy in zip(chroma_notes, chroma_mean):
    print(f"{note:>2} : {'█' * int(energy * 50)}")
```

### 4.3 Rhythmic Features

```python
# Tempo (BPM)
tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
print(f"Tempo : {tempo:.1f} BPM ({len(beats)} beats)")

# Inter-beat intervals
ibi = np.diff(beats) / sr * 1000  # ms
print(f"IBI moyen : {np.mean(ibi):.1f}ms, std : {np.std(ibi):.1f}ms")

# Pulse strength
onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
pulse = librosa.beat.plp(y=audio, sr=sr)
print(f"PLP max : {np.max(pulse):.3f}, min : {np.min(pulse):.3f}")

# Tempogram
tempogram = librosa.feature.tempogram(y=audio, sr=sr, onset_envelope=onset_env)
# Représentation temps-BPM de la périodicité rythmique
```

## 5. Extraction pour Machine Learning

### 5.1 TensorFlow / PyTorch : Spectrogram dataset

```python
import torch
import torch.nn as nn
import torchaudio

# Avec torchaudio
waveform, sr = torchaudio.load("audio.wav")

# Mel spectrogramme (GPU-compatible)
mel_transform = torchaudio.transforms.MelSpectrogram(
    sample_rate=sr,
    n_fft=2048,
    hop_length=512,
    n_mels=128,
    f_min=0,
    f_max=sr/2
)
mel_spec_torch = mel_transform(waveform)  # (1, n_mels, n_frames)
mel_spec_db = torchaudio.transforms.AmplitudeToDB()(mel_spec_torch)

# MFCC (GPU-compatible)
mfcc_transform = torchaudio.transforms.MFCC(
    sample_rate=sr,
    n_mfcc=13,
    melkwargs={
        'n_fft': 2048,
        'hop_length': 512,
        'n_mels': 40,
        'f_min': 0,
        'f_max': sr/2
    }
)
mfcc_torch = mfcc_transform(waveform)  # (1, 13, n_frames)
```

### 5.2 Augmentation de spectrogrammes

```python
class SpecAugment:
    """Augmentation de spectrogrammes pour l'entraînement (SpecAugment paper)."""
    def __init__(self, freq_mask=15, time_mask=30, num_freq_masks=2, num_time_masks=2):
        self.freq_mask = freq_mask
        self.time_mask = time_mask
        self.num_freq_masks = num_freq_masks
        self.num_time_masks = num_time_masks

    def __call__(self, spec):
        """spec: (n_mels, n_frames) ou (batch, n_mels, n_frames)"""
        if spec.ndim == 2:
            spec = spec[np.newaxis, :, :]
        augmented = spec.copy()

        # Frequency masking
        for _ in range(self.num_freq_masks):
            f = np.random.randint(0, self.freq_mask)
            f0 = np.random.randint(0, spec.shape[1] - f)
            augmented[:, f0:f0+f, :] = 0

        # Time masking
        for _ in range(self.num_time_masks):
            t = np.random.randint(0, self.time_mask)
            t0 = np.random.randint(0, spec.shape[2] - t)
            augmented[:, :, t0:t0+t] = 0

        return augmented

# Pour PyTorch
class SpecAugmentTorch(nn.Module):
    def __init__(self, freq_mask=15, time_mask=30, num_freq_masks=2, num_time_masks=2):
        super().__init__()
        self.freq_mask = freq_mask
        self.time_mask = time_mask
        self.num_freq_masks = num_freq_masks
        self.num_time_masks = num_time_masks

    def forward(self, x):
        # x: (batch, freq, time)
        for _ in range(self.num_freq_masks):
            f = torch.randint(0, self.freq_mask, (1,)).item()
            f0 = torch.randint(0, x.size(1) - f, (1,)).item()
            x[:, f0:f0+f, :] = 0

        for _ in range(self.num_time_masks):
            t = torch.randint(0, self.time_mask, (1,)).item()
            t0 = torch.randint(0, x.size(2) - t, (1,)).item()
            x[:, :, t0:t0+t] = 0

        return x
```

### 5.3 Normalisation des features

```python
# CMVN (Cepstral Mean and Variance Normalization)
def cmvn(features, mask=None):
    """Normalisation moyenne-variance cepstrale."""
    # features: (n_features, n_frames) ou (batch, n_features, n_frames)
    if features.ndim == 2:
        mean = np.mean(features, axis=1, keepdims=True)
        std = np.std(features, axis=1, keepdims=True)
        return (features - mean) / (std + 1e-10)
    else:
        mean = np.mean(features, axis=2, keepdims=True)
        std = np.std(features, axis=2, keepdims=True)
        return (features - mean) / (std + 1e-10)

# Per-channel mean subtraction (pour les spectrogrammes)
def pcmn(spec):
    """Soustraction de la moyenne par canal."""
    return spec - np.mean(spec, axis=-1, keepdims=True)

# Global mean-variance normalization
def global_cmvn(features, global_mean, global_std):
    """Normalisation avec statistiques globales (calculées sur tout le dataset)."""
    return (features - global_mean) / (global_std + 1e-10)
```

## 6. Outils CLI

### 6.1 songsee (spectrogrammes)

```bash
# Installation
go install github.com/steipete/songsee/cmd/songsee@latest

# Multi-panel visualization
songsee audio.wav --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux

# Style
songsee audio.wav --viz spectrogram --style magma -o spectro.png
```

### 6.2 audio-processing CLI

```bash
# SoX : spectrogramme
sox audio.wav -n spectrogram -o spectro.png

# FFmpeg : spectrogramme
ffmpeg -i audio.wav -lavfi showspectrumpic=s=1920x1080 spectro.png

# Python : extraction MFCC en batch
python3 -c "
import librosa, json, sys
audio, sr = librosa.load(sys.argv[1], sr=16000)
mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
print(json.dumps({'mean': mfcc.mean(axis=1).tolist(), 'std': mfcc.std(axis=1).tolist()}))
" audio.wav
```

## 7. Pitfalls et solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| MFCC instables | Audio non normalisé | Normalisation du volume avant extraction |
| Bruit dans les hauts MFCC | Bruit HF | Limiter `fmax` à 8000Hz, filtrage |
| Artefacts Griffin-Lim | Phase non naturelle | Utiliser un vocoder neuronal (HiFi-GAN) |
| Spectrogramme flou | Fenêtre trop large | Réduire `n_fft` ou augmenter `hop_length` |
| Chroma non informatif | Timbre dominant | Utiliser CQT ou CENS au lieu de STFT |
| Overfitting ML | Features trop nombreuses | SpecAugment, CMVN, réduction dimensionnelle |

## 8. Références

- **librosa** : https://librosa.org/doc/main/feature.html
- **torchaudio** : https://pytorch.org/audio/stable/
- **SpecAugment** : https://arxiv.org/abs/1904.08779
- **MFCC originaux** : Davis & Mermelstein (1980)
- **CQT** : https://ieeexplore.ieee.org/document/1257396
- **songsee** : https://github.com/steipete/songsee
- **FFmpeg spectrogram** : https://ffmpeg.org/ffmpeg-filters.html#showspectrumpic