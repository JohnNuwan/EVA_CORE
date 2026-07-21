---
name: music-generation
description: "Génération musicale par IA — modèles autoregressifs, diffusion, symbolique (MIDI), raw audio, MusicGen, Stable Audio, Muzic, Riffusion, Magenta, contrôle mélodique et stylistique."
tags: [audio, music, generation, ai, musicgen, magentam, mubert, symbolic, midi, diffusion, transformers]
platforms: [linux, macos]
related_skills: [audiocraft-audio-generation, heartmula, midi-sequencing, audio-processing]
---

# Music Generation — Génération Musicale par IA

Guide complet des modèles et techniques de génération musicale : audio brut, symbolique (MIDI), modèles de diffusion, transformers, contrôle mélodique et stylistique.

## 1. Approches de Génération Musicale

| Paradigme | Modèles | Avantages | Inconvénients |
|-----------|---------|-----------|---------------|
| **Raw Audio** (token audio) | MusicGen, Stable Audio, AudioLM | Contrôle timbre/production | Coûteux, artefacts possibles |
| **Symbolique** (MIDI/score) | MusicTransformer, MuseNet, Anticopula | Contrôle harmonique, compact | Sonorité dépend du synthétiseur |
| **Latent Diffusion** | Stable Audio, DiffSound | Haute qualité, conditionnement | Lent en inférence |
| **Neural Codec** | AudioLM, EnCodec, DAC | Compression haute fidélité | Besoin de vocoder |
| **Hybride** | Riffusion (spectrogramme → audio) | Simple, visuel | Bande passante limitée |

## 2. MusicGen (Meta — AudioCraft)

```python
from audiocraft.models import MusicGen
import torchaudio
import torch

# Chargement
model = MusicGen.get_pretrained('facebook/musicgen-medium')  # small (300M), medium (1.5B), large (3.3B)
model.to('cuda')

# Paramètres globaux
model.set_generation_params(
    duration=30,           # Durée en secondes (1-120)
    top_k=250,             # Échantillonnage top-k
    top_p=0.0,             # Nucleus sampling (0 = désactivé)
    temperature=1.0,       # Température (0.7 = conservateur, 1.2 = créatif)
    cfg_coef=3.0           # Classifier-free guidance (plus haut = plus fidèle au prompt)
)

# Génération text-to-music
descriptions = [
    "epic orchestral soundtrack with strings and brass, cinematic",
    "lo-fi hip hop beat with jazzy piano and vinyl crackle",
    "deep techno with heavy bass, 128 BPM"
]
wav = model.generate(descriptions)  # Batch

for i, audio in enumerate(wav):
    torchaudio.save(f"music_{i}.wav", audio.cpu(), 32000)
```

### 2.1 Mélodie conditionnée

```python
# Chargement du modèle melody
model = MusicGen.get_pretrained('facebook/musicgen-melody')
model.set_generation_params(duration=30)

# Charger une mélodie de référence
melody, sr = torchaudio.load("hummed_melody.wav")

# Conditionnement chroma + texte
descriptions = ["acoustic folk guitar following the melody"]
wav = model.generate_with_chroma(descriptions, melody, sr)

torchaudio.save("melody_conditioned.wav", wav[0].cpu(), 32000)
```

### 2.2 Style transfert

```python
model = MusicGen.get_pretrained('facebook/musicgen-style')
model.set_generation_params(duration=30, cfg_coef=3.0, cfg_coef_beta=5.0)
model.set_style_conditioner_params(eval_q=3, excerpt_length=3.0)

# Référence de style
style_ref, sr = torchaudio.load("reference_style.wav")

# Génération avec ce style
descriptions = ["upbeat dance track with synths"]
wav = model.generate_with_style(descriptions, style_ref, sr)
```

## 3. MusicGen — Ingénierie de prompts

### 3.1 Structure de prompt

```
[Genre], [ambiance], [instruments], [tempo], [structure], [production]
```

| Élément | Exemples |
|---------|----------|
| **Genre** | electronic, orchestral, jazz, rock, ambient, lo-fi, techno |
| **Ambiance** | dark, uplifting, melancholic, energetic, hypnotic |
| **Instruments** | piano, strings, 808, synth pads, distorted guitar |
| **Tempo** | 140 BPM, slow groove, uptempo, half-time |
| **Structure** | with breakdown, building tension, evolving layers |
| **Production** | vintage warmth, modern crisp, lo-fi, cinematic reverb |

### 3.2 Exemples par genre

```python
prompts = {
    "Cinématique": [
        "epic orchestral soundtrack, dramatic strings and brass, building tension, cinematic percussion, dark minor key, 80 BPM, wide reverb",
        "emotional piano and strings, soft rising melody, hopeful atmosphere, film score, 60 BPM, intimate",
        "action trailer music, aggressive brass stabs, driving percussion, hybrid orchestral, 130 BPM"
    ],
    "Électronique": [
        "minimal techno, deep kick, atmospheric pads, 128 BPM, Berlin style, hypnotic",
        "future garage, 2-step rhythm, atmospheric synths, 140 BPM, emotional chords",
        "ambient drone, evolving textures, field recordings, slow, meditative, no percussion"
    ],
    "Hip-Hop / Lofi": [
        "lo-fi hip hop, jazzy piano sample, vinyl crackle, boom bap drums, 85 BPM, relaxed",
        "trap beat, dark 808s, hi-hat rolls, atmospheric, 140 BPM, modern",
        "old school hip hop, funk sample, heavy kick and snare, 92 BPM, west coast"
    ],
    "Jazz / Acoustique": [
        "smooth jazz, saxophone melody, walking bass, brushed drums, 120 BPM, smoky club",
        "acoustic guitar fingerstyle, warm, intimate, folk, 80 BPM, nature sounds",
        "bossa nova, nylon guitar, soft percussion, romantic, 130 BPM"
    ]
}
```

## 4. Riffusion (Spectrogram → Audio)

```python
# Riffusion : génération via spectrogrammes stables
# Diffusion dans le domaine spectral, puis inversion

from diffusers import StableDiffusionImg2ImgPipeline
import torch
import librosa
import soundfile as sf
import numpy as np

# Riffusion utilise un modèle de diffusion d'images entraîné sur des spectrogrammes
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "riffusion/riffusion-model-v1",
    torch_dtype=torch.float16
).to("cuda")

def generate_music_riffusion(prompt, seed=42, duration_s=5):
    """Génère de la musique via Riffusion."""
    # Prompt pour le spectrogramme
    prompt_spectrogram = f"{prompt}, spectrogram, mel scale, 2048 n_fft"

    # Génération du spectrogramme
    generator = torch.Generator("cuda").manual_seed(seed)
    image = pipe(
        prompt_spectrogram,
        generator=generator,
        num_inference_steps=50,
        guidance_scale=7.5
    ).images[0]

    # Conversion spectrogramme → audio (Griffin-Lim ou vocoder)
    # Riffusion utilise un inverse STFT appris
    audio = riffusion_spectrogram_to_audio(image, duration_s)
    return audio
```

## 5. Symbolique — Music Transformer / Magenta

### 5.1 MusicTransformer (Google Magenta)

```python
# Magenta : génération symbolique (MIDI)
import magenta
from magenta.models.music_vae import TrainedModel
from magenta.models.music_vae.configs import configs
import note_seq

# Chargement du modèle (Melody RNN)
import note_seq

# Génération mélodique
model = note_seq.MelodyRnnModel(
    config_name='attention_rnn',
    checkpoint_dir='~/magenta-models/attention_rnn/'
)

# Amorcer avec une mélodie optionnelle
primer_melody = note_seq.Melody([60, 62, 64, 65, 67])  # Do Ré Mi Fa Sol
generated = model.generate(
    temperature=1.0,
    steps=128,  # Nombre de pas
    primer_melody=primer_melody,
    beam_size=1
)

# Sauvegarde en MIDI
note_seq.sequence_proto_to_midi_file(generated, 'generated.mid')
```

### 5.2 Anticopula (Markov + RNN)

```python
pip install music21
```

```python
import music21
from music21 import stream, note, chord, meter, tempo

# Génération par chaîne de Markov
def generate_markov_melody(seed_notes=['C4', 'D4', 'E4', 'G4'], length=16):
    """Génération simple par chaîne de Markov sur les hauteurs."""
    import random

    transitions = {}
    # Probabilités de transition
    for i in range(len(seed_notes) - 1):
        current = seed_notes[i]
        next_note = seed_notes[i + 1]
        if current not in transitions:
            transitions[current] = []
        transitions[current].append(next_note)
    # Retour au début
    if seed_notes[-1] not in transitions:
        transitions[seed_notes[-1]] = []
    transitions[seed_notes[-1]].append(seed_notes[0])

    # Génération
    melody = stream.Part()
    melody.append(tempo.MetronomeMark(number=120))
    melody.append(meter.TimeSignature('4/4'))

    current = seed_notes[0]
    for _ in range(length):
        n = note.Note(current)
        n.quarterLength = random.choice([0.25, 0.5, 1.0, 2.0])
        melody.append(n)
        current = random.choice(transitions.get(current, seed_notes))

    return melody

# Sauvegarde MIDI
melody = generate_markov_melody()
melody.write('midi', 'generated_melody.mid')
```

### 5.3 Muzic (Microsoft — génération symbolique avancée)

```bash
git clone https://github.com/microsoft/muzic.git
cd muzic

# MusicBERT (représentation musicale)
# SongMASS (génération de chansons)
# PopMAG (génération multi-instrumentale pop)
```

## 6. Génération avec conditionnement audio

### 6.1 Continuation audio

```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import torchaudio

processor = AutoProcessor.from_pretrained("facebook/musicgen-medium")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-medium").to("cuda")

# Charger un audio pour continuation
audio, sr = torchaudio.load("intro.wav")

# Conditionner avec texte + audio
inputs = processor(
    audio=audio.squeeze().numpy(),
    sampling_rate=sr,
    text=["continue this with a full band arrangement"],
    padding=True,
    return_tensors="pt"
).to("cuda")

# Génération
audio_values = model.generate(
    **inputs,
    do_sample=True,
    guidance_scale=3.0,
    max_new_tokens=512
)
```

### 6.2 Loop / Groove generation

```python
# Génération de boucles rythmiques
model.set_generation_params(duration=4)

loop_prompts = [
    "drum and bass break, 170 BPM, amen break style",
    "four on the floor house beat, 128 BPM, kick clap hi-hat",
    "half-time trap beat, 140 BPM, heavy 808, hi-hat rolls"
]

wav = model.generate(loop_prompts)
```

## 7. Évaluation musicale

### 7.1 Métriques qualitatives

| Métrique | Description | Usage |
|----------|-------------|-------|
| **MOS** | Mean Opinion Score (écoute humaine) | Standard |
| **FD** | Fréchet Distance (embeddings audio) | Similarité distribution |
| **KL Div** | KL divergence des chroma features | Harmonie |
| **Pitch Accuracy** | Précision des hauteurs | Génération mélodique |
| **Groove Consistency** | Cohérence rythmique | Percussion |
| **Structure Score** | Cohérence structurelle | Longues durées |

### 7.2 Analyse objective

```python
import librosa
import numpy as np

def analyze_generated_music(audio_path):
    """Analyse objective d'une piste générée."""
    audio, sr = librosa.load(audio_path, sr=22050)

    # Analyse rythmique
    tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
    onset_env = librosa.onset.onset_strength(y=audio, sr=sr)

    # Analyse harmonique
    chroma = librosa.feature.chroma_cqt(y=audio, sr=sr)
    tonal_centroid = np.mean(chroma, axis=1)

    # Analyse spectrale
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
    spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=sr))
    zero_crossings = np.mean(librosa.feature.zero_crossing_rate(audio))

    return {
        "tempo": f"{tempo:.1f} BPM",
        "n_beats": len(beats),
        "spectral_centroid": f"{spectral_centroid[0]:.0f} Hz",
        "spectral_bandwidth": f"{spectral_bandwidth[0]:.0f} Hz",
        "zero_crossings": f"{zero_crossings[0]:.2f}",
        "chroma_variance": f"{np.var(chroma):.4f}",
        "duration": f"{len(audio) / sr:.1f}s"
    }
```

## 8. Contrôle et édition avancés

### 8.1 Inpainting audio (remplacement de section)

```python
# MusicGen ne supporte pas l'inpainting nativement
# Alternative : découpage et collage avec crossfade

from audiocraft.models import MusicGen
import torchaudio

model = MusicGen.get_pretrained('facebook/musicgen-medium')
model.set_generation_params(duration=4)  # Section à générer

# Générer une section alternative
wav_new = model.generate(["jazzy piano solo section"])

# Fusion avec crossfade
def crossfade_merge(original, new_section, insert_at_s, sr=32000, fade_duration=0.5):
    """Fusionne une section générée dans un audio original."""
    insert_at = int(insert_at_s * sr)
    fade_len = int(fade_duration * sr)

    fade_out = np.linspace(1, 0, fade_len)
    fade_in = np.linspace(0, 1, fade_len)

    result = original.copy()
    section_len = len(new_section)

    # Appliquer crossfade
    if insert_at > 0:
        result[insert_at:insert_at+fade_len] = \
            result[insert_at:insert_at+fade_len] * fade_out + \
            new_section[:fade_len] * fade_in

    # Remplacer le reste
    result[insert_at+fade_len:insert_at+section_len-fade_len] = \
        new_section[fade_len:section_len-fade_len]

    return result
```

### 8.2 Mixage multi-pistes

```python
# Génération multi-pistes (batches séparés)
model.set_generation_params(duration=30)

tracks = {
    "drums": "drum track, 128 BPM, four on the floor, techno",
    "bass": "deep bassline, 128 BPM, dark techno",
    "synth": "atmospheric synth pad, minor keys, evolving",
    "melody": "lead synth melody, arpeggiated, 16th notes"
}

# Générer chaque piste séparément
generated = {}
for name, prompt in tracks.items():
    wav = model.generate([prompt])
    generated[name] = wav[0].cpu().numpy()

# Mixer avec volumes personnalisés
mix = np.zeros_like(generated["drums"])
levels = {"drums": 1.0, "bass": 0.8, "synth": 0.6, "melody": 0.7}
for name, audio in generated.items():
    mix += audio * levels[name]

# Normalisation
mix = mix / np.max(np.abs(mix)) * 0.95

import soundfile as sf
sf.write("multitrack_mix.wav", mix, 32000)
```

## 9. Pitfalls et solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| Son boueux | Trop d'instruments basses fréquences | Spécifier des instruments dans le prompt |
| Manque de structure | Pas de direction temporelle | Prompts décrivant l'évolution |
| Répétitions | Température trop basse | Augmenter à 1.0-1.2 |
| Bruit HF | Vocoder/artifact | Filtrer passe-bas à 16kHz |
| Timing instable | Modèle raw audio | Spécifier BPM exact dans le prompt |
| Mélodie non suivie | Chroma mal aligné | Meilleure extraction F0, plus de données |

## Références

- **MusicGen** : https://github.com/facebookresearch/audiocraft
- **Stable Audio** : https://www.stability.ai/products/stable-audio
- **Riffusion** : https://www.riffusion.com/
- **Magenta** : https://magenta.tensorflow.org/
- **Muzic** : https://github.com/microsoft/muzic
- **AudioCraft** : https://github.com/facebookresearch/audiocraft
- **music21** : https://web.mit.edu/music21/
- **note-seq** : https://github.com/magenta/note-seq