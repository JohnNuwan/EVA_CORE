---
name: asr-reconnaissance-vocale
description: "Reconnaissance Automatique de la Parole (ASR) — Whisper, Wav2Vec2, Kaldi, DeepSpeech, pipelines de transcription, alignement forcé, diarisation."
tags: [audio, asr, speech-recognition, whisper, wav2vec2, kaldi, transcription, diarization]
platforms: [linux, macos]
related_skills: [tts-synthese-vocale, audio-processing, mfcc-spectrogram-analysis]
---

# ASR — Reconnaissance Automatique de la Parole

Guide complet des systèmes ASR (Automatic Speech Recognition) : transcription, alignement forcé, diarisation du locuteur, modèles open-source, pipelines de bout en bout.

## 1. Architectures ASR — Vue d'ensemble

| Paradigme | Modèles | Description | Latence |
|-----------|---------|-------------|---------|
| **End-to-End** | Whisper, Wav2Vec2, HuBERT, USM | Audio → texte direct, pas de lexicon séparé | Faible |
| **Hybride** | Kaldi + DNN-HMM | Acoustic model + language model + lexicon | Moyenne |
| **CTC** | Wav2Vec2-CTC, QuartzNet | Prédiction frame-level, greedy/beam search | Faible |
| **Seq2Seq** | Whisper, SpeechT5 | Encoder-decoder transformer, attention cross | Variable |
| **RNN-T** | RNNT, Conformer-Transducer | Streaming, pas d'attente fin d'échantillon | Très faible |

## 2. OpenAI Whisper

### 2.1 Installation et utilisation de base

```bash
pip install openai-whisper
# ou via huggingface
pip install transformers torch
```

```python
import whisper

# Chargement du modèle
model = whisper.load_model("large-v3")  # tiny, base, small, medium, large, large-v2, large-v3

# Transcription
result = model.transcribe("audio.wav")
print(result["text"])

# Avec langue et tâche
result = model.transcribe(
    "audio.mp3",
    language="fr",
    task="transcribe",  # ou "translate" vers l'anglais
    temperature=0.0,
    beam_size=5,
    word_timestamps=True,
    condition_on_previous_text=False,
    verbose=True
)

# Timestamps par segment
for segment in result["segments"]:
    print(f"{segment['start']:.2f}s - {segment['end']:.2f}s : {segment['text']}")
```

### 2.2 Paramètres critiques

| Paramètre | Valeur conseillée | Effet |
|-----------|-------------------|-------|
| `temperature` | 0.0 (déterministe) | > 0.0 = plus créatif, plus d'hallucinations |
| `compression_ratio_threshold` | 2.4 | Rejette les répétitions excessives |
| `logprob_threshold` | -1.0 | Rejette les segments de confiance trop basse |
| `no_speech_threshold` | 0.6 | Détection silence/seulement musique |
| `beam_size` | 5 | Taille du faisceau de recherche |
| `patience` | 1.0 | Pénalité de longueur |
| `word_timestamps` | True | Active les timestamps par mot (utile pour sous-titres) |

### 2.3 Prétraitement pour Whisper

```python
import librosa
import soundfile as sf

# Rééchantillonnage à 16kHz (obligatoire pour Whisper)
audio, sr = librosa.load("audio_source.wav", sr=16000, mono=True)

# Normalisation du gain
audio = audio / (audio.abs().max() + 1e-8) * 0.95

# Découpage de silence (VAD)
import webrtcvad
vad = webrtcvad.Vad(2)  # agressivité 0-3

# Sauvegarde
sf.write("audio_preprocessed.wav", audio, 16000)
```

### 2.4 Faster-Whisper (CTranslate2, 4× plus rapide)

```bash
pip install faster-whisper
```

```python
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cuda", compute_type="float16")

# Transcription avec VAD intégré
segments, info = model.transcribe(
    "audio.wav",
    beam_size=5,
    vad_filter=True,              # Filtre VAD intégré
    vad_parameters=dict(
        min_silence_duration_ms=500,
        threshold=0.5
    ),
    language="fr",
    condition_on_previous_text=False
)

print(f"Détecté : {info.language} (p={info.language_probability:.2f})")

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
```

## 3. Wav2Vec2 / HuBERT (Meta)

### 3.1 Transcription avec Wav2Vec2

```python
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import soundfile as sf

processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h").to("cuda")

# Chargement audio
audio, sr = sf.read("speech.wav")
if sr != 16000:
    import librosa
    audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)

# Tokenisation
inputs = processor(audio, sampling_rate=16000, return_tensors="pt").input_values.to("cuda")

# Inférence
with torch.no_grad():
    logits = model(inputs).logits

# Décodage CTC (greedy)
predicted_ids = torch.argmax(logits, dim=-1)
transcription = processor.batch_decode(predicted_ids)[0]
print(transcription)

# Décodage avec beam search (nécessite un language model)
from transformers import Wav2Vec2ProcessorWithLM
processor_lm = Wav2Vec2ProcessorWithLM.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")
transcription = processor_lm.batch_decode(predicted_ids.cpu().numpy()).text[0]
```

### 3.2 Modèles pré-entraînés (transformers)

| Modèle | Description | Langues |
|--------|-------------|---------|
| `facebook/wav2vec2-large-960h` | 960h LibriSpeech | EN |
| `facebook/wav2vec2-large-xlsr-53` | 53 langues | Multilingue |
| `facebook/hubert-large-ls960` | HuBERT large | EN |
| `facebook/mms-1b-all` | Massively Multilingual Speech | 1162 langues |
| `facebook/mms-1b-l1107` | MMS 1107 langues | Multilingue |
| `NbAiLab/nb-wav2vec2-1b-bokmaal` | 1B paramètres, Norvégien | NO |

## 4. Kaldi (Framework ASR de référence)

### 4.1 Installation

```bash
git clone https://github.com/kaldi-asr/kaldi.git
cd kaldi/tools
make -j $(nproc)
cd ../src
./configure --shared
make depend -j $(nproc)
make -j $(nproc)
```

### 4.2 Recipe typique (LibriSpeech)

```bash
cd egs/librispeech/s5
./run.sh  # Télécharge, prépare, entraîne GMM-HMM, DNN

# Les étapes :
# 1. Préparation du corpus (data/, lang/, local/)
# 2. Extraction MFCC (steps/make_mfcc.sh)
# 3. Entraînement monophone (steps/train_mono.sh)
# 4. Triphone (steps/train_deltas.sh)
# 5. LDA+MLLT (steps/train_lda_mllt.sh)
# 6. SAT (steps/train_sat.sh)
# 7. DNN (steps/nnet3/train_raw_dnn.sh)
# 8. Décodage avec graphe WFST
```

### 4.3 Concepts clés Kaldi

```
Audio → MFCC → GMM-HMM (alignement) → DNN (priori) → Décodeur WFST → Texte
```

- **WFST** (Weighted Finite State Transducer) : graphe de décodage qui combine l'acoustic model, le lexicon et le language model en un seul automate
- **FST** : `L.fst` (lexique) → `G.fst` (grammaire/LM) → `LG.fst` (composé)
- **Alignment forcé** : `steps/align_si.sh` ou `steps/nnet3/align.sh`

## 5. Diarisation du locuteur

### 5.1 PyAnnote Audio (basé sur SpeechBrain)

```bash
pip install pyannote.audio
```

```python
from pyannote.audio import Pipeline
from pyannote.core import notebook

# Pipeline prêt à l'emploi
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="hf_..."
)

# Diarisation
diarization = pipeline("conversation.wav")

# Résultat
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"[{turn.start:.1f}s - {turn.end:.1f}s] {speaker}")

# Export RTTM
with open("diarization.rttm", "w") as f:
    diarization.write_rttm(f)
```

### 5.2 Whisper + Diarisation (pipeline complet)

```bash
pip install nemo_toolkit['all']
```

```python
# Pipeline whisper + diarisation
# 1. Transcrire avec Whisper (word timestamps)
# 2. Extraire les embeddings de locuteur (speaker embeddings)
# 3. Clustering spectral (Agglomerative Clustering)
# 4. Assigner chaque segment au bon locuteur

from faster_whisper import WhisperModel
from sklearn.cluster import AgglomerativeClustering
import torchaudio
import torch

asr = WhisperModel("large-v3", device="cuda")
segments, _ = asr.transcribe("call.wav", word_timestamps=True, vad_filter=True)

# Chunk l'audio par segment
waveform, sr = torchaudio.load("call.wav")
# ... extraire speaker embeddings (speechbrain, wespeaker) ...
# ... clustering ...
```

### 5.3 Outils de diarisation

| Outil | Langage | Méthode | Performance (DER) |
|-------|---------|---------|-------------------|
| PyAnnote 3.1 | Python | End-to-end + clustering | ~8-12% |
| NVIDIA NeMo | Python | MarbleNet + clustering | ~7-10% |
| SpeechBrain | Python | ECAPA-TDNN + AHC | ~10-15% |
| diarization-3.1 | Python | Transformer + clustering | ~6-9% |

## 6. Alignment forcé (Forced Alignment)

```python
# Montreal Forced Aligner (MFA)
# Installation
pip install montreal-forced-aligner

# Alignement
# mfa align corpus/ dictionary.txt acoustic.zip output/
mfa align ~/audio_corpus/ french_mfa.dict french_mfa.zip ~/aligned/

# Gentle (outil alternatif, Python natif)
git clone https://github.com/lowerquality/gentle.git
cd gentle
./install.sh
python3 gentle.py --nthreads 4 audio.mp3 transcript.txt
```

## 7. Pipelines de transcription optimisés

### 7.1 Traitement par lots

```python
from faster_whisper import WhisperModel
from pathlib import Path
import json

model = WhisperModel("large-v3", device="cuda", compute_type="float16")

def transcribe_batch(input_dir: str, output_dir: str, language: str = "fr"):
    """Transcrit tous les fichiers audio d'un répertoire."""
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for audio_path in sorted(input_dir.glob("*")):
        if audio_path.suffix not in (".wav", ".mp3", ".m4a", ".flac"):
            continue

        segments, info = model.transcribe(
            str(audio_path),
            language=language,
            beam_size=5,
            word_timestamps=True,
            vad_filter=True
        )

        result = {
            "file": audio_path.name,
            "duration": info.duration,
            "language": info.language,
            "segments": [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text.strip(),
                    "words": [
                        {"word": w.word, "start": w.start, "end": w.end}
                        for w in seg.words
                    ] if seg.words else []
                }
                for seg in segments
            ]
        }

        output_path = output_dir / f"{audio_path.stem}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"✓ {audio_path.name} → {output_path.name}")
```

### 7.2 VAD (Voice Activity Detection) avancé

```python
# Silero VAD (excellent, très léger)
import torch
import torchaudio

model_vad, utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad",
    model="silero_vad"
)
(get_speech_timestamps, _, read_audio, _, _) = utils

wav = read_audio("speech.wav", sampling_rate=16000)
speech_timestamps = get_speech_timestamps(
    wav, model_vad,
    threshold=0.5,
    min_speech_duration_ms=250,
    min_silence_duration_ms=100,
    window_size_samples=512
)

# Utiliser les timestamps pour découper l'audio
for ts in speech_timestamps:
    segment = wav[ts['start']:ts['end']]
    print(f"Parole: {ts['start']/16000:.2f}s - {ts['end']/16000:.2f}s")
```

## 8. Évaluation ASR (Métriques)

```python
from jiwer import wer, cer

reference = "je voudrais un café s'il vous plaît"
hypothesis = "je voudrais un café sil vous plait"

w = wer(reference, hypothesis)   # Word Error Rate
c = cer(reference, hypothesis)   # Character Error Rate

print(f"WER: {w:.2%}, CER: {c:.2%}")

# Word Information Loss (WIL)
from jiwer import wil
print(f"WIL: {wil(reference, hypothesis):.2%}")
```

| Métrique | Signification | Seuil acceptable |
|----------|---------------|------------------|
| **WER** | Word Error Rate | < 5% (studio) / < 15% (bruit) |
| **CER** | Character Error Rate | < 2% (studio) / < 8% (bruit) |
| **MER** | Match Error Rate | Complémentaire à WER |
| **WIL** | Word Information Lost | Perte d'information |

## 9. Modèles ASR open-source par cas d'usage

| Cas d'usage | Modèle recommandé | Taille | VRAM |
|-------------|-------------------|--------|------|
| Transcription rapide | `distil-whisper/distil-large-v3` | 756M | ~2GB |
| Haute qualité français | `whisper-large-v3` ou faster-whisper | 1.5B | ~4GB |
| Streaming temps réel | `facebook/wav2vec2-base-960h` | 95M | ~512MB |
| Multilingue 1000+ | `facebook/mms-1b-all` | 1B | ~3GB |
| Embedded / Edge | `openai/whisper-tiny` | 39M | ~256MB |
| Diarisation complète | PyAnnote 3.1 + Whisper | — | ~4GB |

## 10. Pitfalls et solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| Hallucinations Whisper | Audio trop silencieux/musical | VAD filter, `no_speech_threshold` haut |
| Mots répétés en boucle | Température trop haute | `temperature=0.0`, `compression_ratio_threshold=2.4` |
| Timestamps incorrects | Word timestamps mal calibrés | Rééchantillonner exactement à 16kHz mono |
| WER élevé sur français | Accent, bruit de fond | Fine-tuning avec données cibles, augmentation |
| Mémoire GPU OOM | Long fichier audio | Découpage en chunks de 30s |
| Diarisation confuse | Chevauchement de parole | Essayer PyAnnote 3.1 + résolution oracle |

## Références

- **Whisper** : https://github.com/openai/whisper
- **Faster-Whisper** : https://github.com/SYSTRAN/faster-whisper
- **Wav2Vec2** : https://huggingface.co/facebook/wav2vec2-large-960h
- **Kaldi** : https://github.com/kaldi-asr/kaldi
- **PyAnnote** : https://github.com/pyannote/pyannote-audio
- **SpeechBrain** : https://speechbrain.github.io/
- **Montreal Forced Aligner** : https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner
- **Silero VAD** : https://github.com/snakers4/silero-vad
- **WER/CER** : https://github.com/jitsi/jiwer
