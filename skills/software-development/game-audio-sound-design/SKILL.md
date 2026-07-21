---
name: game-audio-sound-design
description: Guide complet de conception audio pour jeux vidéo — synthèse Wwise/FMOD, spatialisation 3D, procédural audio, middleware, mixing, optimisation mémoire, et implémentation dans Unity/Unreal/Godot.
---

# Game Audio & Sound Design — Guide Complet

Ce skill couvre la conception et l'implémentation audio pour jeux vidéo. À charger pour toute tâche impliquant Wwise, FMOD, spatialisation 3D, synthèse audio procédurale, ou intégration sonore dans Unity/Unreal/Godot.

---

## 1. Architecture Audio dans un Jeu

### Pipeline audio

```
Assets Bruts (.wav, .ogg, .flac)
        ↓
    Middleware (Wwise / FMOD)
        ↓
    SoundBanks / AudioClips
        ↓
    Moteur Audio (Unity/Unreal/Godot)
        ↓
    Spatialisation 3D → Mixer → Output
```

### Hiérarchie des sons

```
Master Mixer
├── Music          (Musique, ambiances)
├── SFX            (Effets sonores)
│   ├── Weapons    (Armes, impacts)
│   ├── Footsteps  (Pas, déplacements)
│   ├── UI         (Menus, clics)
│   └── Environment (Vent, pluie, feu)
├── Voice          (Dialogues, voix-off)
└── UI             (HUD, notifications)
```

---

## 2. Middleware Audio

### Wwise — Architecture

```
Project
├── SoundBanks          # Fichiers .bnk embarqués
│   ├── Init.bnk        # Bus, effets, RTPC
│   └── MonJeu.bnk      # Événements, sons
├── Events              # Déclencheurs audio
│   ├── Play_Footstep
│   ├── Play_Shoot
│   └── Stop_Music
├── RTPC (Real-Time Parameter Control)
│   ├── PlayerSpeed → Footstep Rate
│   └── Health → Heartbeat Intensity
├── States              # États globaux
│   ├── Combat / Exploration
│   └── Day / Night
└── Switches            # Alternatives
    └── TerrainType → Grass / Stone / Wood
```

### FMOD — Architecture

```
FMOD Project
├── Events
│   ├── 2D (Music, UI)
│   └── 3D (Footsteps, Explosions, Environments)
├── Banks
│   ├── Master Bank
│   └── Streaming Bank (musiques longues)
├── Parameters
│   ├── Continuous (speed, health)
│   └── Discrete (state, weapon_type)
└── Snapshots
    └── Underwater, LowHealth, SlowMotion
```

---

## 3. Intégration Unity

### Audio Mixer Unity natif

```csharp
using UnityEngine.Audio;

public class AudioManager : MonoBehaviour
{
    public static AudioManager Instance { get; private set; }
    
    [SerializeField] private AudioMixer _mixer;
    [SerializeField] private AudioSource _sfxSource;
    [SerializeField] private AudioSource _musicSource;
    [SerializeField] private AudioSource _ambienceSource;
    
    public AudioMixerGroup sfxGroup;
    public AudioMixerGroup musicGroup;
    
    public float masterVolume = 1f;
    public float sfxVolume = 1f;
    public float musicVolume = 1f;
    
    void Awake()
    {
        if (Instance == null) Instance = this;
        _sfxSource.outputAudioMixerGroup = sfxGroup;
        _musicSource.outputAudioMixerGroup = musicGroup;
    }
    
    public void PlaySFX(AudioClip clip, Vector3 position = default, float volume = 1f)
    {
        if (position == default)
        {
            _sfxSource.PlayOneShot(clip, volume * sfxVolume);
        }
        else
        {
            AudioSource.PlayClipAtPoint(clip, position, volume * sfxVolume);
        }
    }
    
    public void PlayMusic(AudioClip clip, bool loop = true, float fadeDuration = 1f)
    {
        StartCoroutine(FadeMusic(clip, loop, fadeDuration));
    }
    
    private System.Collections.IEnumerator FadeMusic(AudioClip clip, bool loop, float duration)
    {
        float startVolume = _musicSource.volume;
        for (float t = 0; t < duration; t += Time.deltaTime)
        {
            _musicSource.volume = Mathf.Lerp(startVolume, 0, t / duration);
            yield return null;
        }
        _musicSource.volume = 0;
        
        _musicSource.clip = clip;
        _musicSource.loop = loop;
        _musicSource.Play();
        
        for (float t = 0; t < duration; t += Time.deltaTime)
        {
            _musicSource.volume = Mathf.Lerp(0, 1, t / duration);
            yield return null;
        }
        _musicSource.volume = 1;
    }
    
    public void SetMixerVolume(string parameter, float value)
    {
        // Convertir 0-1 en dB (-80 à 0)
        float dB = value > 0 ? Mathf.Log10(value) * 20 : -80f;
        _mixer.SetFloat(parameter, dB);
    }
}
```

### Audio spatial 3D (Unity)

```csharp
// Source audio 3D
AudioSource source = gameObject.AddComponent<AudioSource>();
source.spatialBlend = 1.0f;      // 0 = 2D, 1 = 3D
source.minDistance = 1f;          // Volume max à 1m
source.maxDistance = 50f;         // Inaudible à 50m
source.rolloffMode = AudioRolloffMode.Logarithmic; // Décroissance réaliste
source.dopplerLevel = 0.1f;       // Effet Doppler (légèrement)
source.spread = 0f;               // Angle du cône (0 = omnidirectionnel)
source.reverbZoneMix = 1f;        // Réverbération dans les zones
```

---

## 4. Intégration Unreal Engine (MetaSounds)

### MetaSounds — Audio procédural UE5

```cpp
// C++: Jouer un son avec MetaSound
#include "MetasoundSource.h"
#include "MetasoundGeneratorHandle.h"

void UMonJeuFunction::JouerSonProcedural()
{
    UMetaSoundSource* MetaSound = LoadObject<UMetaSoundSource>(nullptr, TEXT("/Game/Audio/MS_Explosion"));
    
    UAudioComponent* AudioComp = NewObject<UAudioComponent>(this);
    AudioComp->SetSound(MetaSound);
    AudioComp->SetParameterFloat("Intensity", 0.8f);
    AudioComp->SetParameterFloat("Pitch", 1.0f + FMath::FRandRange(-0.1f, 0.1f));
    AudioComp->Play();
}
```

### Blueprint Audio (UE5)

```
Event → Play Sound 2D/3D → SoundCue/Wave
   └→ Set Sound Mix Class (SFX, Music, Voice)
   └→ Set Attenuation (distance, falloff)
   └→ Set Concurrency (max instances, priority)
```

### Unreal — Attenuation Settings

```cpp
// Paramètres d'atténuation
USoundAttenuation* Att = NewObject<USoundAttenuation>();
Att->Attenuation.FalloffDistance = 3000.0f;   // cm
Att->Attenuation.bEnableListenerFocus = true;  // Focus sur le joueur
Att->Attenuation.FocusAzimuth = 30.0f;         // Angle de focus
Att->Attenuation.bEnableOcclusion = true;      // Occlusion par murs
Att->Attenuation.OcclusionLowPassFilterFrequency = 500.0f; // Son étouffé
```

---

## 5. Intégration Godot

```gdscript
# Godot — AudioManager
extends Node

@onready var master_bus := AudioServer.get_bus_index("Master")
@onready var sfx_bus := AudioServer.get_bus_index("SFX")
@onready var music_bus := AudioServer.get_bus_index("Music")

func play_sfx(path: String, position: Vector2 = Vector2.ZERO) -> void:
    var stream := load(path) as AudioStream
    var player := AudioStreamPlayer2D.new() if position != ZERO else AudioStreamPlayer.new()
    player.stream = stream
    player.bus = "SFX"
    player.volume_db = 0.0
    
    if player is AudioStreamPlayer2D:
        player.position = position
        player.max_distance = 1000.0
        player.attenuation = 1.0
    
    add_child(player)
    player.play()
    await player.finished
    player.queue_free()

func set_volume(bus_name: String, volume: float) -> void:
    var bus_idx := AudioServer.get_bus_index(bus_name)
    var db := linear_to_db(volume)
    AudioServer.set_bus_volume_db(bus_idx, db)

func play_random_footstep() -> void:
    var footsteps := [
        preload("res://audio/footstep_01.ogg"),
        preload("res://audio/footstep_02.ogg"),
        preload("res://audio/footstep_03.ogg"),
    ]
    play_sfx(footsteps[randi() % footsteps.size()].resource_path)
```

### Audio Bus Layout Godot
```
Master
├── Music          ← Reverb
├── SFX            ← Limiter, EQ
│   ├── Weapons    ← Distortion
│   ├── Footsteps  ← Compression
│   └── UI         ← Pas d'effets
└── Voice          ← Compression, EQ
```

---

## 6. Audio Procédurale (Synthèse en Temps Réel)

### Synthèse basique (Python → prototype)

```python
import numpy as np
import soundfile as sf

def generate_laser_beam(duration: float = 0.5, sample_rate: int = 44100) -> np.ndarray:
    """Génère un son de laser sci-fi"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Fréquence qui descend (sweep)
    freq_start = 800
    freq_end = 200
    freq = np.linspace(freq_start, freq_end, len(t))
    
    # Onde sinusoïdale + harmoniques
    signal = np.sin(2 * np.pi * freq * t)
    signal += 0.5 * np.sin(2 * np.pi * freq * 2 * t)  # harmonique
    signal += 0.3 * np.sin(2 * np.pi * freq * 3 * t)  # harmonique
    
    # Enveloppe ADSR simplifiée
    attack = 0.01
    decay = 0.05
    sustain = 0.7
    release = 0.1
    
    envelope = np.ones_like(t)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples)
    envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)
    
    signal *= envelope
    return signal

# Usage
laser = generate_laser_beam()
sf.write("laser_beam.wav", laser, 44100)
```

### Synthèse dans Godot

```gdscript
# Godot — AudioEffect custom
extends AudioEffect

func _process(buffer: AudioSampleBuffer) -> void:
    var data = buffer.get_buffer()
    for i in range(data.size()):
        # Ajouter de la distorsion
        data[i] = clamp(data[i] * 2.0, -1.0, 1.0)
    buffer.set_buffer(data)
```

---

## 7. Audio Dynamique et Adaptation

### Système de zones (Reverb Zones)

```csharp
// Unity — Zone de réverbération
public class ReverbZone : MonoBehaviour
{
    public AudioReverbPreset preset = AudioReverbPreset.Cave;
    public float transitionTime = 1f;
    
    private AudioReverbZone _zone;
    
    void Start()
    {
        _zone = gameObject.AddComponent<AudioReverbZone>();
        _zone.reverbPreset = preset;
        _zone.minDistance = 5f;
        _zone.maxDistance = 20f;
    }
}
```

### Musique adaptative (Horizontal/Vertical Re-Orchestration)

```python
# Concept: couches musicales qui s'activent selon l'état du jeu
# Couche 1: Percussion (toujours)
# Couche 2: Basse (quand le joueur approche d'un ennemi)
# Couche 3: Cordes (en combat)
# Couche 4: Cuivres (boss, climax)

class AdaptiveMusic:
    layers = {
        "percussion": {"active": True,  "volume": 0.8},
        "bass":       {"active": False, "volume": 0.6},
        "strings":    {"active": False, "volume": 0.4},
        "brass":      {"active": False, "volume": 0.5},
    }
    
    def update(self, game_state: dict):
        if game_state["combat"]:
            self.layers["bass"]["active"] = True
            self.layers["strings"]["active"] = True
        if game_state["boss"]:
            self.layers["brass"]["active"] = True
```

---

## 8. Optimisation Mémoire et Streaming

### Formats audio pour jeux

| Format | Usage | Taux | Qualité |
|--------|-------|------|---------|
| **.wav (PCM)** | UI, petits SFX | 1411 kbps | Parfaite |
| **.ogg (Vorbis)** | Musique, ambiances | ~128 kbps | Bonne |
| **.mp3** | Dialogues | ~96 kbps | Correcte |
| **ADPCM** | Footsteps (mobile) | 352 kbps | Acceptable |
| **Vorbis (Wwise)** | Streaming | 64-192 kbps | Configurable |

### Streaming audio

```csharp
// Unity — Chargement en streaming pour les longues musiques
public class StreamingMusic : MonoBehaviour
{
    public string musicPath;
    private AudioClip _clip;
    private Coroutine _loadRoutine;
    
    public void LoadMusicAsync()
    {
        _loadRoutine = StartCoroutine(LoadMusic());
    }
    
    private System.Collections.IEnumerator LoadMusic()
    {
        var request = Resources.LoadAsync<AudioClip>(musicPath);
        yield return request;
        
        _clip = request.asset as AudioClip;
        GetComponent<AudioSource>().clip = _clip;
        GetComponent<AudioSource>().Play();
    }
}
```

### Pool Audio (éviter les allocations)

```csharp
public class AudioPool : MonoBehaviour
{
    [System.Serializable]
    public class PoolEntry
    {
        public string tag;
        public AudioSource prefab;
        public int poolSize = 5;
    }
    
    public List<PoolEntry> entries;
    private Dictionary<string, Queue<AudioSource>> _pools = new();
    
    void Start()
    {
        foreach (var entry in entries)
        {
            var queue = new Queue<AudioSource>();
            for (int i = 0; i < entry.poolSize; i++)
            {
                var source = Instantiate(entry.prefab, transform);
                source.gameObject.SetActive(false);
                queue.Enqueue(source);
            }
            _pools[entry.tag] = queue;
        }
    }
    
    public AudioSource Play(string tag, Vector3 position)
    {
        if (!_pools.ContainsKey(tag) || _pools[tag].Count == 0)
            return null;
        
        var source = _pools[tag].Dequeue();
        source.transform.position = position;
        source.gameObject.SetActive(true);
        source.Play();
        
        StartCoroutine(ReturnToPool(tag, source, source.clip.length));
        return source;
    }
    
    private System.Collections.IEnumerator ReturnToPool(string tag, AudioSource source, float delay)
    {
        yield return new WaitForSeconds(delay + 0.1f);
        source.Stop();
        source.gameObject.SetActive(false);
        _pools[tag].Enqueue(source);
    }
}
```

---

## 9. Outils et Ressources

| Outil | Usage | Prix |
|-------|-------|------|
| **Wwise** | Middleware audio professionnel | Gratuit (indie) |
| **FMOD** | Middleware audio alternatif | Gratuit (indie) |
| **Audacity** | Édition et mastering audio | Gratuit |
| **sfxr / jsfxr** | Synthèse de sons 8-bit/rétro | Gratuit |
| **BFXR** | Synthèse SFX pour jeux | Gratuit |
| **ChipTone** | Synthèse chiptune | Gratuit |
| **Sononym** | Recherche et classification de samples | Payant |
| **Boscaceoil** | Synthèse chiptune | Gratuit |

---

## 10. Pièges Courants

- **Latence audio** : buffer trop grand → délai de 100ms+ → réduire à 256-512 samples
- **Compression trop agressive** : .ogg à 64kbps → artefacts audibles → 128kbps minimum
- **Pas de streaming pour la musique** : musique chargée en RAM → 50MB+ pour une OST
- **Spatialisation 2D pour des sons 3D** : `spatialBlend = 0` → son toujours au centre
- **Pas de pooling audio** : `PlayClipAtPoint()` en boucle → GC spikes → pool obligatoire
- **Volume master qui clippe** : plusieurs sons forts → distorsion → limiter sur le master bus
- **Footsteps trop répétitifs** : 3 samples → 10-15 samples minimum + random pitch
- **Oubli des options accessibilité** : sous-titres, réduction de la dynamique, mono forcé