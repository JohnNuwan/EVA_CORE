---
name: midi-sequencing
description: "MIDI — protocole, fichiers Standard MIDI (.mid), séquenceurs logiciels, piano roll, génération algorithmique, mapping contrôleurs, MIDI 2.0, integration hardware/software."
tags: [audio, midi, sequencing, music, synthesis, daw, standards, controllers]
platforms: [linux, macos, windows]
related_skills: [music-generation, webaudio-api, audio-processing]
---

# MIDI & Sequencing — Protocole, Fichiers et Production Musicale

Guide complet du MIDI (Musical Instrument Digital Interface) : protocole, fichiers SMF, séquenceurs, génération algorithmique, MIDI 2.0, intégration matérielle/logicielle.

## 1. Protocole MIDI 1.0

### 1.1 Messages MIDI

```
Message MIDI = Status Byte + Data Bytes (1-2)
Status byte : 0x80-0xFF
  - High nibble = type de message
  - Low nibble = canal MIDI (0-15)
Data bytes : 0x00-0x7F
```

| Message | Status (hex) | Data 1 | Data 2 | Description |
|---------|-------------|--------|--------|-------------|
| **Note Off** | `0x80`+canal | Note (0-127) | Velocity (0-127) | Relâchement de note |
| **Note On** | `0x90`+canal | Note (0-127) | Velocity (0-127) | Début de note |
| **Poly Key Pressure** | `0xA0`+canal | Note | Pressure | Aftertouch polyphonique |
| **Control Change** | `0xB0`+canal | CC# (0-119) | Value (0-127) | Changement de contrôle |
| **Program Change** | `0xC0`+canal | Program# (0-127) | - | Changement d'instrument |
| **Channel Pressure** | `0xD0`+canal | Pressure | - | Aftertouch monophonique |
| **Pitch Bend** | `0xE0`+canal | LSByte (0-127) | MSByte (0-127) | Pitch bend (14-bit) |

### 1.2 Contrôleurs MIDI (CC) — Les plus importants

```c
// Contrôleurs standards (Control Change)
CC 0  = Bank Select (MSB)
CC 1  = Modulation Wheel
CC 2  = Breath Controller
CC 4  = Foot Controller
CC 5  = Portamento Time
CC 7  = Volume (Main)
CC 8  = Balance
CC 10 = Pan (stéréo)
CC 11 = Expression
CC 12 = Effect Control 1
CC 13 = Effect Control 2
CC 64 = Sustain Pedal (Damper)
CC 65 = Portamento On/Off
CC 66 = Sostenuto
CC 67 = Soft Pedal
CC 71 = Resonance (Filter Q)
CC 72 = Release Time
CC 73 = Attack Time
CC 74 = Brightness (Filter Cutoff)
CC 75 = Decay Time
CC 91 = Reverb Send Level
CC 92 = Tremolo Level
CC 93 = Chorus Send Level
CC 94 = Celeste/Detune
CC 95 = Phaser Level
CC 120 = All Sound Off
CC 121 = Reset All Controllers
CC 123 = All Notes Off

// NRPN (Non-Registered Parameter Numbers)
CC 99  = NRPN MSB
CC 98  = NRPN LSB
CC 6   = Data Entry MSB
CC 38  = Data Entry LSB
CC 101 = RPN MSB
CC 100 = RPN LSB
```

### 1.3 MIDI Notes — Mapping

```python
# MIDI Note Number → Fréquence
def midi_to_freq(note):
    """Convertit un numéro MIDI (0-127) en fréquence (Hz)."""
    return 440.0 * (2.0 ** ((note - 69) / 12.0))

# Fréquence → MIDI Note Number
def freq_to_midi(freq):
    """Convertit une fréquence (Hz) en numéro MIDI."""
    return 69 + 12 * np.log2(freq / 440.0)

# Note names
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
def midi_to_name(note):
    """Convertit MIDI note (0-127) en nom (ex: C4, F#5)."""
    octave = (note // 12) - 1
    name = NOTE_NAMES[note % 12]
    return f"{name}{octave}"

# Table rapide
# C4 = 60, C#4 = 61, D4 = 62, D#4 = 63, E4 = 64, F4 = 65
# F#4 = 66, G4 = 67, G#4 = 68, A4 = 69 (440Hz), A#4 = 70, B4 = 71
```

## 2. Standard MIDI File (SMF) Format

### 2.1 Structure du fichier

```
Fichier .mid = Header Chunk + Track Chunks

Header Chunk:
  "MThd" (4 bytes)
  length = 6 (4 bytes, big-endian)
  format (2 bytes) : 0=single track, 1=multi-track synchro, 2=multi-track asynchrone
  n_tracks (2 bytes)
  division (2 bytes) : ticks per quarter note (tick/pulse)

Track Chunk:
  "MTrk" (4 bytes)
  length (4 bytes)
  events (variable length) :
    - Delta-time (Variable-Length Quantity)
    - Event (MIDI event, Sysex, Meta)
```

### 2.2 Meta Events

```python
# Meta Events (0xFF + type + length + data)
META_EVENTS = {
    0x00: "Sequence Number",
    0x01: "Text",
    0x02: "Copyright",
    0x03: "Track Name",
    0x04: "Instrument Name",
    0x05: "Lyric",
    0x06: "Marker",
    0x07: "Cue Point",
    0x20: "MIDI Channel Prefix",
    0x2F: "End of Track",
    0x51: "Set Tempo (microsecondes/crotchet)",
    0x54: "SMPTE Offset",
    0x58: "Time Signature (num, denom_pow2, clocks_per_tick, 32nd_per_quarter)",
    0x59: "Key Signature (sharps/flats, minor/major)",
    0x7F: "Sequencer Specific"
}

# Variable-Length Quantity (VLQ) - décodage
def decode_vlq(data, offset):
    """Décode un nombre en VLQ MIDI."""
    value = 0
    for i in range(4):
        byte = data[offset + i]
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            return value, offset + i + 1
    return 0, offset + 4

# VLQ - encodage
def encode_vlq(value):
    """Encode un nombre en VLQ MIDI."""
    bytes_list = []
    while True:
        bytes_list.insert(0, value & 0x7F)
        value >>= 7
        if value == 0:
            break
    for i in range(len(bytes_list) - 1):
        bytes_list[i] |= 0x80  # MSB = 1 sauf le dernier
    return bytes(bytes_list)
```

### 2.3 Lecture et écriture avec Python

```python
# Avec mido (bibliothèque Python)
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage

# Lecture
mid = MidiFile('song.mid')
print(f"Format: {mid.type}, Tracks: {len(mid.tracks)}, Ticks/beat: {mid.ticks_per_beat}")

for i, track in enumerate(mid.tracks):
    print(f"\nTrack {i}: {track.name}")
    for msg in track:
        print(f"  {msg}")

# Création
def create_midi_file(output_path, bpm=120):
    """Crée un fichier MIDI simple."""
    mid = MidiFile()
    mid.ticks_per_beat = 480  # Résolution standard

    track = MidiTrack()
    mid.tracks.append(track)

    # Tempo
    tempo_us = mido.bpm2tempo(bpm)
    track.append(MetaMessage('set_tempo', tempo=tempo_us))

    # Time signature (4/4)
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))

    # Track name
    track.append(MetaMessage('track_name', name='Piano'))

    # Notes (C major scale)
    notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C4-B5
    for i, note in enumerate(notes):
        # Note On
        track.append(Message(
            'note_on',
            note=note,
            velocity=100,
            time=0 if i == 0 else 480  # 1 beat
        ))
        # Note Off
        track.append(Message(
            'note_off',
            note=note,
            velocity=64,
            time=480  # Durée d'1 beat
        ))

    # End of Track
    track.append(MetaMessage('end_of_track'))

    mid.save(output_path)
    return mid

# Export et conversion temps
def ticks_to_seconds(ticks, ticks_per_beat, tempo_us):
    """Convertit les ticks MIDI en secondes."""
    return ticks * tempo_us / (ticks_per_beat * 1_000_000)
```

## 3. Production avec Python-MIDI

### 3.1 Génération algorithmique

```python
import mido
import random

class MidiGenerator:
    """Générateur de musique MIDI algorithmique."""

    SCALES = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'pentatonic_major': [0, 2, 4, 7, 9],
        'pentatonic_minor': [0, 3, 5, 7, 10],
        'blues': [0, 3, 5, 6, 7, 10],
        'chromatic': list(range(12)),
        'dorian': [0, 2, 3, 5, 7, 9, 10],
        'phrygian': [0, 1, 3, 5, 7, 8, 10],
        'lydian': [0, 2, 4, 6, 7, 9, 11],
        'mixolydian': [0, 2, 4, 5, 7, 9, 10],
        'locrian': [0, 1, 3, 5, 6, 8, 10],
    }

    def __init__(self, bpm=120, ticks_per_beat=480):
        self.bpm = bpm
        self.tpb = ticks_per_beat

    def generate_melody(self, root=60, scale='major', length=16, note_length=480):
        """Génère une mélodie aléatoire dans une gamme."""
        scale_notes = self.SCALES[scale]
        melody = []

        last_note = root
        for _ in range(length):
            # Choix de la note (préfère les pas proches)
            note = random.choice(scale_notes) + root
            if abs(note - last_note) > 12:
                note = last_note + random.choice([-12, 12]) if random.random() > 0.5 else note
            last_note = note

            # Durée (noire par défaut, croche ou blanche parfois)
            duration = note_length
            roll = random.random()
            if roll < 0.15:
                duration = note_length // 2  # Croche
            elif roll > 0.85:
                duration = note_length * 2   # Blanche

            # Vélocité (variation)
            velocity = random.randint(60, 110)

            melody.append((note, duration, velocity))

        return melody

    def generate_chord_progression(self, root=60, scale='major', n_chords=4):
        """Génère une progression d'accords."""
        scale_notes = self.SCALES[scale]
        chords = [
            [0, 2, 4],      # Majeur
            [0, 2, 3],      # Mineur
            [0, 2, 4, 6],   # 7e
            [0, 2, 3, 5],   # min7
            [0, 4],         # 5 (power chord)
            [0, 2, 4, 6, 8], # Maj9
        ]

        progression = []
        for _ in range(n_chords):
            root_offset = random.choice(scale_notes)
            chord_intervals = random.choice(chords)
            chord = [(root + root_offset + interval) for interval in chord_intervals]
            progression.append(chord)

        return progression

    def to_midi(self, melody, output_path='output.mid'):
        """Convertit une mélodie en fichier MIDI."""
        mid = MidiFile()
        mid.ticks_per_beat = self.tpb

        track = MidiTrack()
        mid.tracks.append(track)

        track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.bpm)))
        track.append(MetaMessage('time_signature', numerator=4, denominator=4))
        track.append(MetaMessage('track_name', name='Generated'))

        for note, duration, velocity in melody:
            track.append(Message('note_on', note=note, velocity=velocity, time=0))
            track.append(Message('note_off', note=note, velocity=64, time=duration))

        track.append(MetaMessage('end_of_track'))
        mid.save(output_path)
        return mid

# Utilisation
gen = MidiGenerator(bpm=140)
melody = gen.generate_melody(root=60, scale='blues', length=32)
gen.to_midi(melody, 'blues_melody.mid')
```

### 3.2 Arpégiateur

```python
class Arpeggiator:
    """Génère des arpèges à partir d'accords."""

    PATTERNS = {
        'up': lambda notes, octaves: [n + o * 12 for o in range(octaves) for n in notes],
        'down': lambda notes, octaves: [n + o * 12 for o in reversed(range(octaves)) for n in reversed(notes)],
        'updown': lambda notes, octaves: [n + o * 12 for o in range(octaves) for n in notes] +
                                          [n + o * 12 for o in reversed(range(octaves - 1)) for n in reversed(notes)],
        'random': lambda notes, octaves: [random.choice(notes) + random.choice([0, 12]) for _ in range(len(notes) * octaves)],
        'chord': lambda notes, octaves: notes * octaves,
    }

    def __init__(self, chord, pattern='up', octaves=2, note_value=240, velocity=80):
        self.notes = self.PATTERNS[pattern](chord, octaves)
        self.note_value = note_value
        self.velocity = velocity

    def generate(self, beats=8):
        """Génère l'arpège pour N temps."""
        mid = MidiFile()
        mid.ticks_per_beat = 480
        track = MidiTrack()
        mid.tracks.append(track)

        track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
        track.append(MetaMessage('track_name', name='Arpeggio'))

        total_notes = (beats * 480) // self.note_value
        for i in range(total_notes):
            note = self.notes[i % len(self.notes)]
            track.append(Message('note_on', note=note, velocity=self.velocity, time=0))
            track.append(Message('note_off', note=note, velocity=64, time=self.note_value))

        track.append(MetaMessage('end_of_track'))
        return mid

arp = Arpeggiator(chord=[60, 64, 67], pattern='updown', octaves=2)
mid = arp.generate(beats=8)
mid.save('arpeggio.mid')
```

## 4. MIDI 2.0 — Principales évolutions

| Fonctionnalité | MIDI 1.0 | MIDI 2.0 |
|---------------|----------|----------|
| **Résolution** | 7-bit (0-127) | 32-bit (flottant ou entier) |
| **Précision note** | 128 vélocités | 65536 vélocités |
| **Contrôle** | 128 CC × 128 valeurs | Per-note control |
| **Articulation** | Program Change | Per-note articulation |
| **Communication** | Unidirectionnelle | Bidirectionnelle (UMP) |
| **Découverte** | Aucune | Property Exchange (profile, config) |
| **Transport** | DIN 5 broches | USB, Ethernet, réseau |

```python
# MIDI 2.0 UMP (Universal MIDI Packet) — concept
# 64-bit packet structure
# UMP Message Types :
# 0x0 = Utility (NOF, JR Clock, Delta Clock)
# 0x1 = System (Real-time, SysEx)
# 0x2 = Channel Voice 64-bit
# 0x3 = Channel Voice 96-bit
# 0x4 = Channel Voice 128-bit
# 0x5 = Data (128-bit, 256-bit)
# 0xD = Future
# 0xE = Future
# 0xF = Reserved

# Per-Note Pitch Bend (MIDI 2.0)
# Permet un pitch bend INDÉPENDANT par note
# Chaque note peut avoir son propre pitch bend au lieu d'un seul global
```

## 5. Contrôleurs MIDI et Mapping

### 5.1 Mapping hardware (Ableton Push, Launchpad, etc.)

```python
# Exemple de mapping pour contrôleur MIDI avec python-rtmidi
import rtmidi
from rtmidi.midiutil import open_midiinput, open_midioutput

class MidiControllerMapper:
    """Mapping et filtrage de contrôleur MIDI."""

    def __init__(self):
        self.mappings = {
            # Contrôle de synthétiseur
            (0xB0, 1): ('modulation', lambda v: v / 127),
            (0xB0, 7): ('volume', lambda v: v / 127 * 100),
            (0xB0, 10): ('pan', lambda v: (v - 64) / 64),
            (0xB0, 74): ('filter_cutoff', lambda v: 20 + v * 30),  # 20Hz-3.8kHz
            (0xB0, 71): ('filter_resonance', lambda v: v / 127),
            (0xB0, 64): ('sustain', lambda v: v >= 64),

            # Pistes DAW
            (0xB0, 43): ('volume_track_1', lambda v: v / 127 * -40 + 40),  # dB scale
            (0xB0, 44): ('mute_track_1', lambda v: v >= 64),
            (0xB0, 45): ('solo_track_1', lambda v: v >= 64),
        }

    def process_message(self, message):
        """Traite un message MIDI entrant."""
        status = message[0] if len(message) > 0 else None
        if status is None:
            return

        key = None
        if len(message) >= 2:
            key = (status, message[1])

        if key in self.mappings:
            name, transform = self.mappings[key]
            value = transform(message[2] if len(message) > 2 else 0)
            return name, value

        return None
```

### 5.2 Virtual MIDI ports (OSC / DAW)

```python
# Création d'un port MIDI virtuel (Linux)
# sudo modprobe snd-virmidi midi_devs=2

# Communication avec FluidSynth
# fluidsynth -a alsa /usr/share/sounds/sf2/FluidR3_GM.sf2

# Ou en Python avec rtmidi
midi_out = rtmidi.MidiOut()
ports = midi_out.get_ports()
print(f"Ports MIDI: {ports}")

# Envoyer un message
note_on = [0x90, 60, 100]  # Canal 0, Note C4, Velocity 100
midi_out.send_message(note_on)
```

## 6. Intégration FluidSynth (Lecture audio)

```python
import subprocess
import mido

def play_midi_via_fluidsynth(midi_path, soundfont_path, output_wav=None):
    """Joue ou exporte un fichier MIDI avec FluidSynth."""
    if output_wav:
        # Export audio
        subprocess.run([
            'fluidsynth',
            '-F', output_wav,      # Render to file
            '-g', '0.8',           # Gain
            '-r', '44100',          # Sample rate
            soundfont_path,
            midi_path
        ])
    else:
        # Jouer en direct
        subprocess.Popen([
            'fluidsynth',
            '-a', 'alsa',           # Audio driver
            '-g', '0.8',
            '-r', '44100',
            soundfont_path,
            midi_path
        ])
```

## 7. Analyse de fichiers MIDI

### 7.1 Statistiques et caractéristiques

```python
def analyze_midi(midi_path):
    """Analyse un fichier MIDI pour en extraire des métriques."""
    mid = mido.MidiFile(midi_path)

    total_notes = 0
    note_range = (127, 0)
    unique_notes = set()
    velocities = []
    durations = []
    pitch_bends = []
    cc_changes = {}

    for track in mid.tracks:
        current_time = 0
        last_notes = {}

        for msg in track:
            current_time += msg.time

            if msg.type == 'note_on' and msg.velocity > 0:
                total_notes += 1
                note_range = (min(note_range[0], msg.note), max(note_range[1], msg.note))
                unique_notes.add(msg.note)
                velocities.append(msg.velocity)
                last_notes[msg.note] = current_time

            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in last_notes:
                    duration = current_time - last_notes[msg.note]
                    durations.append(duration)
                    del last_notes[msg.note]

            elif msg.type == 'pitchwheel':
                pitch_bends.append(msg.pitch)

            elif msg.type == 'control_change':
                if msg.control not in cc_changes:
                    cc_changes[msg.control] = []
                cc_changes[msg.control].append(msg.value)

    result = {
        'format': mid.type,
        'tracks': len(mid.tracks),
        'ticks_per_beat': mid.ticks_per_beat,
        'total_notes': total_notes,
        'note_range': f"{midi_to_name(note_range[0])} to {midi_to_name(note_range[1])}",
        'unique_notes': len(unique_notes),
        'avg_velocity': sum(velocities) / len(velocities) if velocities else 0,
        'avg_duration_ticks': sum(durations) / len(durations) if durations else 0,
        'pitch_bend_count': len(pitch_bends),
        'cc_usage': {k: len(v) for k, v in cc_changes.items()}
    }

    return result
```

### 7.2 Outils CLI

```bash
# Midicsv (MIDI ↔ CSV)
midicsv song.mid song.csv
csvmidi song.csv song_modified.mid

# Mido (Python)
python3 -m mido song.mid --verbose

# Display MIDI file info
python3 -c "
import mido
m = mido.MidiFile('song.mid')
print(f'Format: {m.type}, Tracks: {len(m.tracks)}, TPB: {m.ticks_per_beat}')
for t in m.tracks:
    print(f'Track: {t.name} ({len(t)} events)')
"
```

## 8. Pitfalls et solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| Notes qui restent bloquées | Note Off manquant | Envoyer All Notes Off (CC 123) |
| Timing imprécis | Mauvaise gestion delta-time | Utiliser `ticks_per_beat` cohérent |
| Instruments incorrects | Bank Select non défini | Utiliser CC 0 + CC 32 + Program Change |
| MIDI saturé | Trop d'événements | Filtrer CC redondants, réduire résolution |
| Latence audio | Buffer trop grand | 256 ou 128 samples |
| Notes hors gamme | Génération non contrainte | Vérifier note_range 0-127 |

## 9. Ressources matérielles

| Appareil | Type | Usage |
|----------|------|-------|
| KORG nanoKONTROL2 | Control surface | Mixage, effets |
| Novation Launchpad | Grid controller | Performance, clips |
| Akai APC40 | Ableton controller | DAW control |
| Arturia KeyLab | Keyboard controller | Notes + contrôles |
| Behringer BCF2000 | Motor faders | Mixage automatisé |
| Roland A-49 | Compact keyboard | Portable |
| Keith McMillen QuNexus | Pressure sensitive | Expression |

## Références

- **MIDI Spec** : https://www.midi.org/specifications
- **mido** : https://github.com/mido/midi
- **python-rtmidi** : https://github.com/SpotlightKid/python-rtmidi
- **FluidSynth** : https://www.fluidsynth.org/
- **MIDI 2.0** : https://www.midi.org/midi-2-0
- **Standard MIDI Files** : http://www.music.mcgill.ca/~ich/classes/mumt306/midiformat.pdf
- **General MIDI (GM)** : https://www.midi.org/specifications/item/gm-level-1-sound-set