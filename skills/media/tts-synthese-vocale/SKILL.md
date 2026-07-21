---
name: tts-synthese-vocale
description: "Synthèse Vocale (TTS) — Tacotron, FastSpeech, VITS, Bark, Coqui, Piper, XTTS, évaluation MOS, voix personnalisées."
tags: [audio, tts, speech-synthesis, text-to-speech, coqui, piper, bark, vits, fastspeech]
platforms: [linux, macos]
related_skills: [asr-reconnaissance-vocale, voice-cloning, audio-processing]
---

# TTS — Synthèse Vocale

Guide complet des systèmes de Text-to-Speech : architectures modernes, entraînement, inférence, voix personnalisées, évaluation.

## 1. Architectures TTS — Vue d'ensemble

| Architecture | Modèles | Qualité | Latence | Contrôle |
|-------------|---------|---------|---------|----------|
| **Pipeline (2 étages)** | Tacotron2 + WaveGlow | ★★★ | Haute | Faible |
| **End-to-End 1-stage** | VITS, Grad-TTS | ★★★★ | Moyenne | Faible |
| **Neural Codec** | Bark, XTTS, CosyVoice | ★★★★★ | Haute | Élevé |
| **Lightweight edge** | Piper, Coqui | ★★★ | Très faible | Moyen |
| **Autoregressif** | Tacotron2, FastPitch | ★★★ | Variable | Moyen |
| **Non-autoregressif** | FastSpeech2, Glow-TTS | ★★★★ | Faible | Élevé |

## 2. Coqui TTS (la référence open-source)

### 2.1 Installation

```bash
pip install TTS
# ou depuis le dépôt
git clone https://github.com/coqui-ai/TTS
cd TTS
pip install -e .
```

### 2.2 Synthèse de base

```python
from TTS.api import TTS

# Liste des modèles disponibles
print(TTS().list_models())

# Chargement : modèle TTS en français
tts = TTS("tts_models/fr/mai/tacotron2-DDC")

# Synthèse (fichier)
tts.tts_to_file(
    text="Bonjour, je suis une voix synthétique française.",
    file_path="output.wav"
)

# Synthèse en mémoire (numpy array)
wav = tts.tts("Bonjour, je suis une voix synthétique.")
```

### 2.3 Synthèse multilingue avec XTTS

```python
from TTS.api import TTS

# XTTS v2 — voix naturelle, multilingue, clonage vocal
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# Synthèse avec clonage vocal
tts.tts_to_file(
    text="Je parle français avec la voix de cette personne.",
    speaker_wav="reference_speaker.wav",  # Échantillon audio de référence (3-10s)
    language="fr",
    file_path="cloned_output.wav"
)

# Avec split de phrases pour meilleur contraste
tts.tts_to_file(
    text="Première phrase. Deuxième phrase. Troisième phrase.",
    speaker_wav="ref.wav",
    language="fr",
    file_path="xtts_fr.wav",
    split_sentences=True
)
```

### 2.4 Entraînement d'une voix personnalisée

```bash
# 1. Préparation du dataset (format LJSpeech-like)
# metadata.csv : id|text
# wavs/id.wav

# 2. Configuration de l'entraînement
tts --list_models  # Voir les modèles disponibles
# Config YAML : /path/to/TTS/recipes/ljspeech/tacotron2-DDC/run.py

# 3. Lancer l'entraînement
python TTS/bin/train_tts.py \
    --config_path config.json \
    --output_path /output/folder \
    --restore_path /checkpoint.pth

# 4. Synthèse après entraînement
from TTS.utils.manage import ModelManager
from TTS.tts.configs.vits_config import VitsConfig
```

## 3. Piper TTS (Léger, edge)

```bash
# Installation
pip install piper-tts

# Synthèse en ligne de commande
echo "Bonjour le monde" | \
  piper \
    --model ~/voices/fr_FR-mai-medium.onnx \
    --output_file output.wav \
    --length_scale 1.0 \
    --noise_scale 0.667 \
    --noise_w 0.8 \
    --sentence_silence 0.2

# Téléchargement de modèles
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/mai/medium/fr_FR-mai-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/mai/medium/fr_FR-mai-medium.onnx.json
```

### 3.1 API Python Piper

```python
import piper
import sounddevice as sd

# Chargement du modèle
voice = piper.load_voice("fr_FR-mai-medium.onnx")

# Synthèse
audio = piper.synthesize(
    "Bonjour, ceci est un test de synthèse vocale.",
    voice,
    length_scale=1.0,
    noise_scale=0.667,
    noise_w=0.8
)

# Lecture
sd.play(audio, 22050)
sd.wait()
```

## 4. Bark (Suno AI — Voix + émotions + sons)

```bash
pip install git+https://github.com/suno-ai/bark.git
# ou
pip install transformers
```

```python
from transformers import AutoProcessor, BarkModel
import torch
import scipy.io.wavfile as wav

processor = AutoProcessor.from_pretrained("suno/bark-small")
model = BarkModel.from_pretrained("suno/bark-small").to("cuda")

# Synthèse avec histoire dans la voix
voice_preset = "v2/fr_speaker_3"  # Voix française

inputs = processor(
    text="Bonjour, je m'appelle [sadness] et je suis un peu triste aujourd'hui [laughter].",
    voice_preset=voice_preset,
    return_tensors="pt"
).to("cuda")

with torch.no_grad():
    audio_array = model.generate(**inputs, do_sample=True)

audio_array = audio_array[0].cpu().numpy()
sampling_rate = model.generation_config.sample_rate
wav.write("bark_output.wav", sampling_rate, audio_array)
```

### 4.1 Étiquettes d'émotion / style (Bark)

| Tag | Effet | Exemple |
|-----|-------|---------|
| `[laughter]` | Rire | "C'était drôle [laughter]" |
| `[laughs]` | Rire bref | "Il [laughs] a fait une blague" |
| `[sighs]` | Soupir | "[sighs] Je suis fatigué" |
| `[music]` | Musique | "[music] La la la [music]" |
| `[clears throat]` | Raclement | "[clears throat] Bonjour" |
| `[noise]` | Bruit | "[noise]" |

### 4.2 Voix françaises Bark

| Présélection | Description |
|-------------|-------------|
| `v2/fr_speaker_0` | Voix féminine 1 |
| `v2/fr_speaker_1` | Voix féminine 2 |
| `v2/fr_speaker_2` | Voix masculine 1 |
| `v2/fr_speaker_3` | Voix masculine 2 |
| `v2/fr_speaker_4` | Voix féminine 3 |
| `v2/fr_speaker_5` | Voix féminine 4 |
| `v2/fr_speaker_6` | Voix masculine 3 |
| `v2/fr_speaker_7` | Voix féminine 5 |
| `v2/fr_speaker_8` | Voix masculine 4 |
| `v2/fr_speaker_9` | Voix féminine 6 |

## 5. VITS (Variational Inference Text-to-Speech)

```python
from transformers import VitsModel, AutoTokenizer
import torch
import scipy.io.wavfile as wav

# Français
model = VitsModel.from_pretrained("facebook/mms-tts-fra")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-fra")

# Synthèse
inputs = tokenizer(
    "Bonjour, ceci est une voix synthétique française.",
    return_tensors="pt"
)

with torch.no_grad():
    output = model(**inputs)

audio = output.waveform[0].numpy()
wav.write("vits_fr.wav", model.config.sampling_rate, audio)
```

### 5.1 Modèles MMS-TTS (Meta — 1100+ langues)

```python
import torch
from transformers import VitsModel, AutoTokenizer
from huggingface_hub import list_models

# Lister tous les modèles MMS-TTS
mms_tts = [m for m in list_models() if "mms-tts" in m.id]
print(f"Modèles disponibles : {len(mms_tts)}")

# Exemples de langues supportées
# facebook/mms-tts-fra (français)
# facebook/mms-tts-eng (anglais)
# facebook/mms-tts-deu (allemand)
# facebook/mms-tts-spa (espagnol)
# facebook/mms-tts-jpn (japonais)
```

## 6. Évaluation TTS (Métriques subjectives et objectives)

### 6.1 MOS (Mean Opinion Score)

```python
# MOS subjectif : écoute humaine sur échelle 1-5
# 1 = très mauvais, 5 = parfaitement naturel

# MOS prédictif (WVMOS, DNSMOS)
# pip install wvmos
from wvmos import get_wvmos
mos_model = get_wvmos()

score = mos_model.calculate_one("output.wav")
print(f"MOS prédit : {score:.2f}")
```

### 6.2 Métriques objectives

```python
import librosa
import numpy as np
from scipy.spatial.distance import cosine

# MCD (Mel Cepstral Distortion)
def mcd_distance(gen_audio, ref_audio, sr=22050):
    gen_mfcc = librosa.feature.mfcc(y=gen_audio, sr=sr, n_mfcc=13)
    ref_mfcc = librosa.feature.mfcc(y=ref_audio, sr=sr, n_mfcc=13)
    # DTW alignment puis distance euclidienne
    from dtw import dtw
    alignment = dtw(gen_mfcc.T, ref_mfcc.T, keep_internals=True)
    return alignment.distance / gen_mfcc.shape[1]  # MCD

# F0 RMSE (erreur de hauteur tonale)
def f0_rmse(gen_audio, ref_audio, sr=22050):
    gen_f0, _, _ = librosa.pyin(gen_audio, fmin=65, fmax=2093, sr=sr)
    ref_f0, _, _ = librosa.pyin(ref_audio, fmin=65, fmax=2093, sr=sr)
    # Interpolation des NaN
    gen_f0 = np.nan_to_num(gen_f0, nan=np.nanmean(gen_f0))
    ref_f0 = np.nan_to_num(ref_f0, nan=np.nanmean(ref_f0))
    return np.sqrt(np.mean((gen_f0 - ref_f0) ** 2))
```

| Métrique | Signification | Seuil acceptable |
|----------|---------------|------------------|
| **MOS** (subjectif) | Naturalité perçue | > 4.0 (bon), > 4.5 (excellent) |
| **MCD** | Distortion mél-cepstrale | < 7 dB (bon), < 5 dB (excellent) |
| **F0 RMSE** | Erreur de prosodie | < 30 Hz (bon) |
| **CER** (Wav2Vec2) | Intelligibilité | < 5% |

## 7. Synthèse temps réel / streaming

### 7.1 Coqui TTS streaming

```python
from TTS.tts.configs.vits_config import VitsConfig
from TTS.tts.models.vits import Vits
import numpy as np

class StreamingTTS:
    def __init__(self, model_path):
        self.model = Vits.init_from_config(VitsConfig())
        self.model.load_checkpoint(model_path)

    def synthesize_stream(self, text):
        """Génère et retourne l'audio en chunks pour streaming."""
        outputs = self.model.synthesize(text)
        return outputs["wav"]

# Utilisation avec sounddevice pour lecture en temps réel
import sounddevice as sd

def play_tts_stream(text):
    stream_tts = StreamingTTS("model.pth")
    audio = stream_tts.synthesize_stream(text)
    sd.play(audio, samplerate=22050)
    sd.wait()
```

### 7.2 Piper (le plus rapide)

```bash
# Streaming avec Piper (temps réel sur Raspberry Pi)
cat long_text.txt | \
  piper \
    --model fr_FR-mai-medium.onnx \
    --output-raw | \
  aplay -r 22050 -f S16_LE -c 1 -
```

## 8. Entraînement avancé

### 8.1 Préparation du dataset pour VITS/Coqui

```python
import librosa
import soundfile as sf
from pathlib import Path

def prepare_dataset(input_dir, output_dir, target_sr=22050):
    """Prépare un dataset TTS au format LJSpeech."""
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    wavs_dir = output_dir / "wavs"
    wavs_dir.mkdir(parents=True, exist_ok=True)

    metadata = []

    for audio_path in sorted(input_dir.glob("*.wav")):
        # Chargement et normalisation
        audio, sr = librosa.load(str(audio_path), sr=target_sr, mono=True)
        audio = audio / (audio.max() + 1e-8) * 0.95

        # Nom du fichier
        base_name = audio_path.stem
        output_path = wavs_dir / f"{base_name}.wav"

        # Sauvegarde normalisée
        sf.write(str(output_path), audio, target_sr)
        metadata.append(f"{base_name}|{audio_path.stem}")

    # Sauvegarde du metadata.csv
    with open(output_dir / "metadata.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(metadata))

# Structure finale :
# output_dir/
#   ├── metadata.csv
#   └── wavs/
#       ├── file1.wav
#       └── file2.wav
```

### 8.2 Fine-tuning XTTS v2

```bash
# 1. Préparation des données
# Créer un dossier speakers/ avec :
#   - speaker1.wav (3-10s de parole claire)
#   - speaker2.wav
#   - ...

# 2. Fine-tuning
python TTS/bin/train_xtts.py \
    --output_path /models/xtts_finetuned \
    --base_model_path /models/xtts_v2 \
    --dataset_path /data/speakers/ \
    --num_epochs 10 \
    --batch_size 2 \
    --gradient_accumulation_steps 4 \
    --learning_rate 5e-5

# 3. Inférence
tts = TTS(model_path="/models/xtts_finetuned", gpu=True)
tts.tts_to_file(
    text="Voix personnalisée en français.",
    language="fr",
    file_path="finetuned.wav"
)
```

## 9. Pitfalls et solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| Voix robotique | Modèle auto-regressif non maîtrisé | Essayer VITS/Glow-TTS |
| Clics/artefacts | Discontinuités phase vocale | Post-processing : filtrage passe-bande |
| Prosodie plate | Contrôle de durée manquant | Réglage `length_scale` / `noise_scale` |
| Latence streaming | Modèle trop lourd | Piper (ONNX) ou TinyVITS |
| Clonage imparfait | Référence trop courte/bruitée | 5-10s, propre, même voix uniquement |
| Hallucinations phonèmes | Texte mal formaté | Nettoyage texte : normalisation chiffres/abbrév. |

## Références

- **Coqui TTS** : https://github.com/coqui-ai/TTS
- **Piper** : https://github.com/rhasspy/piper
- **Bark** : https://github.com/suno-ai/bark
- **VITS** : https://github.com/jaywalnut310/vits
- **Meta MMS** : https://github.com/facebookresearch/fairseq/tree/main/examples/mms
- **XTTS** : https://github.com/coqui-ai/TTS/tree/dev/TTS/tts/models/xtts
- **WVMOS** : https://github.com/AndreevP/wvmos