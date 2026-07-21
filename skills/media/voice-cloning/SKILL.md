---
name: voice-cloning
description: "Clonage vocal et conversion de voix — RVC, So-VITS-SVC, Coqui XTTS, Tortoise-TTS, FreeVC, retrieval-based voice conversion, fine-tuning TTS."
tags: [audio, voice-cloning, voice-conversion, rvc, sovits, xtts, tts, speaker-adaptation]
platforms: [linux, macos]
related_skills: [tts-synthese-vocale, asr-reconnaissance-vocale, audio-processing]
---

# Voice Cloning — Clonage Vocal et Conversion de Voix

Guide complet des techniques de clonage vocal : voice conversion (VC), text-to-speech speaker adaptation, retrieval-based voice cloning, fine-tuning.

## 1. Taxonomie du Clonage Vocal

| Technique | Description | Données nécessaires | Qualité |
|-----------|-------------|---------------------|---------|
| **Voice Conversion (VC)** | Transforme la voix source → voix cible | 10-60s voix cible | ★★★★ |
| **Speaker Adaptation TTS** | Fine-tuning TTS sur voix cible | 5-30min voix cible | ★★★★★ |
| **Few-shot TTS** | Synthèse avec 3-10s de référence | 3-10s voix cible | ★★★ |
| **Zero-shot TTS** | Synthèse sans adaptation | 0s (embedding speaker) | ★★-★★★ |
| **Retrieval-based VC** | VC basé sur banque de timbres | 30-60s voix cible | ★★★★ |

## 2. RVC (Retrieval-based Voice Conversion)

### 2.1 Architecture

```
Audio source → F0 extraction (RMVPE/PARTS) → HuBERT encoder → 
  → Features → RMVPE (prédiction F0) → Index retrieval → 
  → NSF-HiFiGAN → Audio converti
```

### 2.2 Installation

```bash
# Cloner le dépôt
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI

# Installation
pip install -r requirements.txt

# Ou utiliser l'application WebUI intégrée
python infer-web.py
```

### 2.3 Entraînement d'un modèle RVC

```bash
# 1. Préparation : dossier avec fichiers audio de la voix cible
# /data/target_voice/*.wav (10-60s recommandé, 5-30min idéal)

# 2. Prétraitement
python tools/process_data.py \
    --data_dir /data/target_voice \
    --model_name my_voice \
    --sr 40000 \
    --hop_length 320

# 3. Entraînement des hubert features
python train_hubert.py \
    --model_name my_voice \
    --dataset /data/target_voice \
    --epochs 100 \
    --batch_size 8 \
    --learning_rate 1e-4

# 4. Entraînement du modèle principal
python train.py \
    --model_name my_voice \
    --dataset /data/target_voice \
    --epochs 100 \
    --batch_size 4 \
    --learning_rate 1e-4 \
    --save_every_epoch 10
```

### 2.4 Inférence avec RVC

```python
# API Python
from rvc_infer import RVCInference

rvc = RVCInference()
rvc.load_model("models/my_voice.pth", "models/my_voice.index")

# Conversion
output = rvc.infer(
    "source_audio.wav",           # Audio source à convertir
    "output_converted.wav",       # Fichier de sortie
    pitch_shift=0,                # Pitch shift (demi-tons)
    index_rate=0.5,               # Ratio d'index (0 = pure génération, 1 = pur retrieval)
    filter_radius=3,              # Rayon de filtrage médian
    rms_mix_rate=0.25,            # Mix RMS (0 = volume source, 1 = volume cible)
    protect=0.33,                 # Protection des consonnes
    crepe_hop_length=128,         # Résolution F0 (plus petit = plus précis)
    f0_method="rmvpe"             # Méthode F0 : "dio", "harvest", "crepe", "rmvpe"
)
```

### 2.5 Paramètres RVC détaillés

| Paramètre | Plage | Défaut | Effet |
|-----------|-------|--------|-------|
| `pitch_shift` | -12 à +12 | 0 | Transposition en demi-tons |
| `index_rate` | 0.0-1.0 | 0.5 | 0 = génération pure, 1 = retrieval pur |
| `filter_radius` | 0-7 | 3 | Lissage spectral (0 = pas de lissage) |
| `rms_mix_rate` | 0.0-1.0 | 0.25 | 0 = timbre source, 1 = timbre cible |
| `protect` | 0.0-0.5 | 0.33 | Protection des consonnes explosives |
| `f0_method` | dio/harvest/crepe/rmvpe | rmvpe | Qualité de l'extraction F0 (crepe > rmvpe > dio) |

## 3. So-VITS-SVC (SoftVC VITS Singing Voice Conversion)

### 3.1 Installation

```bash
git clone https://github.com/voicepaw/so-vits-svc.git
cd so-vits-svc
pip install -r requirements.txt
```

### 3.2 Entraînement

```bash
# 1. Préparation : dataset voix cible
# Format : /dataset/raw/{speaker_id}/*.wav

# 2. Prétraitement
python preprocess.py \
    --config configs/config.json \
    --input_dir /dataset/raw

# 3. Entraînement
python train.py \
    -c configs/config.json \
    -m logs/my_model \
    --pretrained_g "" \
    --pretrained_s "" \
    --num_epochs 10000 \
    --batch_size 4 \
    --learning_rate 1e-4
```

### 3.3 Inférence

```python
# CLI
python svc_inference.py \
    --model_path logs/my_model/G_10000.pth \
    --config_path configs/config.json \
    --input "source.wav" \
    --output "output.wav" \
    --speaker 0 \
    --tran 0 \          # Transposition (demi-tons)
    --auto_predict_f0 true \
    --cluster_model_path "" \
    --cluster_infer_ratio 0.5
```

## 4. Coqui XTTS v2 (Few-shot + Fine-tuning)

### 4.1 Few-shot (zéro entraînement)

```python
from TTS.api import TTS

# Chargement XTTS v2
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

# Clonage avec 3-10s de référence
tts.tts_to_file(
    text="Bonjour, ceci est ma voix clonée avec XTTS.",
    speaker_wav="reference_voice.wav",  # 3-10s de voix cible
    language="fr",
    file_path="cloned_voice.wav",
    speed=1.0
)

# Options avancées
tts.tts_to_file(
    text="Texte long. Avec plusieurs phrases. Pour tester la prosodie.",
    speaker_wav="ref.wav",
    language="fr",
    file_path="output.wav",
    split_sentences=True,           # Split en phrases pour meilleur timing
    temperature=0.7,                # Variabilité de la génération
    length_scale=1.0,               # 0.5 = plus rapide, 2.0 = plus lent
    noise_scale=0.667,              # Variabilité du timbre
    noise_scale_w=0.8               # Variabilité de la durée
)
```

### 4.2 Fine-tuning XTTS (5-30min audio)

```bash
# 1. Préparation du dataset
# /data/voix_cible/ :
#   - metadata.csv : file|text
#   - wavs/*.wav

# 2. Fine-tuning
python TTS/bin/train_xtts.py \
    --output_path /models/xtts_personnalise \
    --base_model_path /models/xtts_v2 \
    --dataset_path /data/voix_cible \
    --num_epochs 10 \
    --batch_size 2 \
    --gradient_accumulation_steps 4 \
    --learning_rate 5e-5 \
    --save_step 500 \
    --eval_step 500

# 3. Inférence
tts = TTS(model_path="/models/xtts_personnalise", gpu=True)
tts.tts_to_file(
    text="Voix personnalisée en français.",
    language="fr",
    file_path="finetuned.wav"
)
```

## 5. Tortoise-TTS (Haute qualité, lent)

### 5.1 Installation

```bash
pip install tortoise-tts
```

### 5.2 Synthèse avec clonage

```python
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio, load_voice, load_voices

# Chargement
tts = TextToSpeech()

# Clonage avec une voix de référence
voice_samples, conditioning_latents = load_voice("my_voice", ["reference.wav"])

# Génération
gen = tts.tts_with_preset(
    "Bonjour, ceci est un test de clonage vocal avec Tortoise.",
    voice_samples=voice_samples,
    conditioning_latents=conditioning_latents,
    preset="ultra_fast",   # "ultra_fast", "fast", "standard", "high_quality"
    k=1,                   # Nombre de candidats
    cvvp_amount=0.0        # CVVP amount (0 = désactivé)
)

# Sauvegarde
import torchaudio
torchaudio.save("tortoise_output.wav", gen.squeeze(0).cpu(), 24000)
```

### 5.3 Presets Tortoise

| Preset | Vitesse | Qualité |
|--------|---------|---------|
| `ultra_fast` | ★★★★★ | ★★ |
| `fast` | ★★★★ | ★★★ |
| `standard` | ★★★ | ★★★★ |
| `high_quality` | ★ | ★★★★★ |

## 6. FreeVC (Voice Conversion sans entraînement par locuteur)

### 6.1 Installation

```bash
git clone https://github.com/OlaWod/FreeVC.git
cd FreeVC
pip install -r requirements.txt
```

### 6.2 Inférence

```python
# CLI
python inference.py \
    --source "source.wav" \
    --target "target.wav" \
    --output "output.wav" \
    --model_path "checkpoints/freevc.pth" \
    --spk_encoder "dprnn" \
    --use_grl false \
    --use_vc模式 true

# FreeVC ne nécessite aucun entraînement par locuteur !
# La voix cible est extraite à la volée depuis le fichier target
```

## 7. Comparaison des solutions

| Solution | Usage | Données | Temps entraînement | VRAM | Qualité |
|----------|-------|---------|-------------------|------|---------|
| **RVC** | Chant, voix | 10s-30min | 1-4h | 4-6GB | ★★★★ |
| **So-VITS-SVC** | Chant, voix | 5-30min | 4-12h | 6-8GB | ★★★★★ |
| **XTTS few-shot** | Parole | 3-10s | 0 | 6-8GB | ★★★ |
| **XTTS finetune** | Parole | 5-30min | 2-6h | 8-12GB | ★★★★★ |
| **Tortoise** | Parole | 3-60s | 0 | 8-12GB | ★★★★ (lent) |
| **FreeVC** | Parole | 0 | 0 | 2-4GB | ★★★ |
| **OpenVoice** | Parole + style | 0 | 0 | 4-6GB | ★★★ |

## 8. Préparation du dataset

### 8.1 Bonnes pratiques

```python
import librosa
import soundfile as sf
import noisereduce as nr
from pathlib import Path

def prepare_voice_dataset(input_dir, output_dir, target_sr=24000):
    """Nettoie et prépare un dataset vocal pour l'entraînement."""
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for audio_path in sorted(input_dir.glob("*.wav")):
        audio, sr = librosa.load(str(audio_path), sr=target_sr, mono=True)

        # 1. Normalisation du volume
        audio = audio / (np.max(np.abs(audio)) + 1e-8) * 0.95

        # 2. Réduction de bruit
        audio = nr.reduce_noise(y=audio, sr=target_sr, prop_decrease=0.9)

        # 3. Gate (couper les silences)
        from scipy import signal
        envelope = np.abs(audio)
        b = np.ones(int(0.05 * target_sr)) / int(0.05 * target_sr)
        envelope = signal.filtfilt(b, 1, envelope)
        mask = envelope > 0.01  # Seuil de silence
        audio = audio[mask]

        # 4. Découpage en segments de 10s max
        max_len = 10 * target_sr
        if len(audio) > max_len:
            for i, start in enumerate(range(0, len(audio), max_len)):
                segment = audio[start:start + max_len]
                if len(segment) > target_sr:  # Min 1s
                    sf.write(output_dir / f"{audio_path.stem}_part{i}.wav", segment, target_sr)
        else:
            if len(audio) > target_sr:
                sf.write(output_dir / f"{audio_path.stem}.wav", audio, target_sr)

# Critères de qualité :
# - SNR > 20 dB
# - Pas de clipping (max amplitude < 0.95)
# - Pas de bruit de fond audible
# - Pas de distorsion
# - Environnement acoustique stable
```

### 8.2 Critères de sélection des échantillons

| Critère | Minimum | Idéal |
|---------|---------|-------|
| Durée totale | 10s | 5-30min |
| Durée par fichier | 1s | 3-10s |
| SNR | 15 dB | 30 dB |
| Échantillons | 5 | 50-500 |
| Variété phonétique | 20 phonèmes | Couverture complète |
| Plage dynamique | 20 dB | 30 dB |

## 9. Pitfalls et solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| Voix métallique | Artefacts du vocoder | Réduire index_rate, augmenter données |
| Respiration artificielle | Bruit de fond dans dataset | Prétraitement + noise reduction |
| Prononciation instable | Données insuffisantes | +5-10min de données variées |
| Craquements HF | Index rate trop élevé | Réduire à 0.3-0.5 |
| Perte d'émotion | Modèle VC trop fort | Réduire la force de conversion |
| Voix inconsistante | Mélange de locuteurs | Vérifier que toutes les données sont du même locuteur |

## Références

- **RVC** : https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
- **So-VITS-SVC** : https://github.com/voicepaw/so-vits-svc
- **Coqui XTTS** : https://github.com/coqui-ai/TTS
- **Tortoise-TTS** : https://github.com/neonbjb/tortoise-tts
- **FreeVC** : https://github.com/OlaWod/FreeVC
- **OpenVoice** : https://github.com/myshell-ai/OpenVoice
- **RMVPE** : https://github.com/Dream-High/RMVPE