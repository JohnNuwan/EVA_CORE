---
name: webaudio-api
description: "Web Audio API — AudioContext, oscillateurs, buffers, effets DSP, spatialisation, analyse temps réel, Tone.js, microphone, streaming audio dans le navigateur."
tags: [audio, web, javascript, webaudio, tonejs, dsp, browser, audio-api, realtime]
platforms: [linux, macos, windows]
related_skills: [audio-processing, music-generation, midi-sequencing]
---

# Web Audio API — Traitement Audio dans le Navigateur

Guide complet de l'API Web Audio : synthèse, effets, spatialisation, analyse temps réel, intégration Tone.js, microphone, streaming.

## 1. Architecture de la Web Audio API

### 1.1 Graphe audio

```
AudioContext (graphe orienté acyclique)
├── Source Nodes
│   ├── OscillatorNode       → Synthèse d'onde
│   ├── AudioBufferSourceNode → Buffer audio
│   ├── MediaStreamSourceNode → Microphone / stream
│   └── MediaElementSourceNode → <audio> / <video>
│
├── Processing/Effect Nodes
│   ├── GainNode             → Volume / mix
│   ├── BiquadFilterNode     → Filtre IIR (passe-bas, etc.)
│   ├── ConvolverNode        → Reverb convolution
│   ├── DelayNode            → Ligne à retard
│   ├── WaveShaperNode       → Distorsion
│   ├── DynamicsCompressorNode → Compression
│   ├── StereoPannerNode     → Panning stéréo
│   └── PannerNode           → Spatialisation 3D
│
└── Destination
    └── AudioDestinationNode → Haut-parleurs
```

### 1.2 Création de l'AudioContext

```javascript
// Création (nécessite une interaction utilisateur)
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
console.log(`Sample rate: ${audioCtx.sampleRate}Hz`);

// Reprendre après interaction
if (audioCtx.state === 'suspended') {
  await audioCtx.resume();
}

// Configuration avancée
const audioCtx2 = new AudioContext({
  sampleRate: 48000,
  latencyHint: 'interactive'  // 'balanced', 'playback', 'interactive'
});
```

## 2. Synthèse Sonore de Base

### 2.1 Oscillateurs

```javascript
// Oscillateur simple
const osc = audioCtx.createOscillator();
osc.type = 'sine';       // sine, square, sawtooth, triangle, custom
osc.frequency.value = 440;  // Hz (A4)
osc.detune.value = 0;       // cents

// Gain (volume)
const gain = audioCtx.createGain();
gain.gain.value = 0.5;

// Connexion
osc.connect(gain);
gain.connect(audioCtx.destination);

// Démarrage/arrêt
osc.start();
osc.stop(audioCtx.currentTime + 2);  // Joue 2s
```

### 2.2 Synthèse par modulation

```javascript
// AM Synth (Amplitude Modulation)
const carrier = audioCtx.createOscillator();
carrier.frequency.value = 440;

const modulator = audioCtx.createOscillator();
modulator.frequency.value = 5;  // LFO rate
modulator.type = 'sine';

const modGain = audioCtx.createGain();
modGain.gain.value = 0.5;  // Profondeur de modulation

// Modulation : LFO → Gain du carrier
modulator.connect(modGain);
modGain.connect(carrier.frequency);  // FM : connecter à .frequency
// ou AM : modGain.connect(carrierGain.gain);

const outputGain = audioCtx.createGain();
outputGain.gain.value = 0.3;

carrier.connect(outputGain);
outputGain.connect(audioCtx.destination);

carrier.start();
modulator.start();

// FM Synth (Frequency Modulation)
const fmCarrier = audioCtx.createOscillator();
fmCarrier.frequency.value = 220;

const fmModulator = audioCtx.createOscillator();
fmModulator.frequency.value = 440;
const fmModGain = audioCtx.createGain();
fmModGain.gain.value = 100;  // Modulation index (en Hz)

fmModulator.connect(fmModGain);
fmModGain.connect(fmCarrier.frequency);  // FM directe

fmCarrier.connect(audioCtx.destination);
fmCarrier.start();
fmModulator.start();
```

### 2.3 Enveloppe ADSR

```javascript
class ADSREnvelope {
  constructor(audioCtx, output) {
    this.ctx = audioCtx;
    this.output = output;
  }

  triggerAttack() {
    const now = this.ctx.currentTime;
    this.output.gain.cancelScheduledValues(now);
    this.output.gain.setValueAtTime(0, now);
    this.output.gain.linearRampToValueAtTime(1, now + 0.01);  // Attack
    this.output.gain.linearRampToValueAtTime(0.7, now + 0.1); // Decay
    // Sustain maintenu par défaut
  }

  triggerRelease() {
    const now = this.ctx.currentTime;
    this.output.gain.cancelScheduledValues(now);
    this.output.gain.setValueAtTime(this.output.gain.value, now);
    this.output.gain.linearRampToValueAtTime(0, now + 0.5);  // Release
  }
}

// Utilisation
const envGain = audioCtx.createGain();
envGain.gain.value = 0;

const env = new ADSREnvelope(audioCtx, envGain);
osc.connect(envGain);
envGain.connect(audioCtx.destination);

env.triggerAttack();
setTimeout(() => env.triggerRelease(), 1000);
```

## 3. Effets Audio

### 3.1 Filtres (BiquadFilterNode)

```javascript
const filter = audioCtx.createBiquadFilter();
filter.type = 'lowpass';     // lowpass, highpass, bandpass, lowshelf, highshelf, peaking, notch, allpass
filter.frequency.value = 1000;  // Hz
filter.Q.value = 1;              // Résonance (0.001 - 1000)
filter.gain.value = 0;           // Gain (shelving/peaking seulement)

// Connexion typique : source → filtre → destination
source.connect(filter);
filter.connect(audioCtx.destination);

// Balayage de fréquence (sweep)
filter.frequency.setValueAtTime(200, audioCtx.currentTime);
filter.frequency.exponentialRampToValueAtTime(8000, audioCtx.currentTime + 3);

// Filtre en peigne (comb filter) via delay
const delay = audioCtx.createDelay(0.1);
delay.delayTime.value = 0.005;  // 5ms
const feedback = audioCtx.createGain();
feedback.gain.value = 0.3;

source.connect(delay);
delay.connect(feedback);
feedback.connect(delay);  // Boucle de feedback
delay.connect(audioCtx.destination);
```

### 3.2 Reverb (ConvolverNode)

```javascript
async function createReverb(audioCtx, irUrl, mix = 0.5) {
  // Chargement de la réponse impulsionnelle
  const response = await fetch(irUrl);
  const arrayBuffer = await response.arrayBuffer();
  const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);

  // Convolveur
  const convolver = audioCtx.createConvolver();
  convolver.buffer = audioBuffer;
  convolver.normalize = true;

  // Mix dry/wet
  const dry = audioCtx.createGain();
  const wet = audioCtx.createGain();
  dry.gain.value = 1 - mix;
  wet.gain.value = mix;

  return { convolver, dry, wet, connect(source) {
    source.connect(dry);
    source.connect(convolver);
    convolver.connect(wet);
    dry.connect(audioCtx.destination);
    wet.connect(audioCtx.destination);
  }};
}

// Utilisation
const reverb = await createReverb(audioCtx, 'ir/church.wav', 0.7);
reverb.connect(source);
```

### 3.3 Delay / Echo

```javascript
const delayNode = audioCtx.createDelay(1.0);  // Max 1s
delayNode.delayTime.value = 0.3;  // 300ms

const feedbackGain = audioCtx.createGain();
feedbackGain.gain.value = 0.4;  // Feedback amount

const wetGain = audioCtx.createGain();
wetGain.gain.value = 0.5;  // Mix niveau

source.connect(delayNode);
delayNode.connect(feedbackGain);
feedbackGain.connect(delayNode);  // Feedback loop
delayNode.connect(wetGain);
wetGain.connect(audioCtx.destination);

// Ping-pong delay (stéréo)
const delayL = audioCtx.createDelay(1.0);
const delayR = audioCtx.createDelay(1.0);
delayL.delayTime.value = 0.25;
delayR.delayTime.value = 0.5;

const feedbackL = audioCtx.createGain();
const feedbackR = audioCtx.createGain();
feedbackL.gain.value = 0.3;
feedbackR.gain.value = 0.3;

source.connect(delayL);
source.connect(delayR);
delayL.connect(feedbackL);
feedbackL.connect(delayR);  // Ping-pong: L → R
delayR.connect(feedbackR);
feedbackR.connect(delayL);  // R → L
delayL.connect(audioCtx.destination);
delayR.connect(audioCtx.destination);
```

### 3.4 Distorsion (WaveShaperNode)

```javascript
function createDistortionCurve(amount = 50) {
  const samples = 44100;
  const curve = new Float32Array(samples);
  for (let i = 0; i < samples; i++) {
    const x = (i * 2) / samples - 1;
    curve[i] = ((3 + amount) * x * 20 * Math.PI / 180) /
               (Math.PI + amount * Math.abs(x));
  }
  return curve;
}

const distortion = audioCtx.createWaveShaper();
distortion.curve = createDistortionCurve(100);
distortion.oversample = '4x';  // 'none', '2x', '4x'

const gainBefore = audioCtx.createGain();
gainBefore.gain.value = 1.0;  // Drive

const gainAfter = audioCtx.createGain();
gainAfter.gain.value = 0.5;   // Volume

source.connect(gainBefore);
gainBefore.connect(distortion);
distortion.connect(gainAfter);
gainAfter.connect(audioCtx.destination);
```

### 3.5 Compression (DynamicsCompressorNode)

```javascript
const compressor = audioCtx.createDynamicsCompressor();
compressor.threshold.value = -24;   // dB, seuil d'activation
compressor.knee.value = 30;          // dB, transition douce (0-40)
compressor.ratio.value = 4;          // Compression ratio (1-20)
compressor.attack.value = 0.003;     // secondes (0-1)
compressor.release.value = 0.25;     // secondes (0-1)

source.connect(compressor);
compressor.connect(audioCtx.destination);

// Sidechain compression (nécessite un second contexte)
// Le sidechain n'est pas natif dans Web Audio API
// Alternative : utiliser un second AudioContext comme sidechain
// ou un script node/audio worklet
```

## 4. Analyse Temps Réel

### 4.1 Analyseur de spectre (AnalyserNode)

```javascript
const analyser = audioCtx.createAnalyser();
analyser.fftSize = 2048;  // Taille FFT (puissance de 2)
analyser.smoothingTimeConstant = 0.8;  // Lissage temporel
analyser.minDecibels = -90;  // Seuil bas
analyser.maxDecibels = -30;  // Seuil haut

source.connect(analyser);
analyser.connect(audioCtx.destination);

// Données fréquentielles
const bufferLength = analyser.frequencyBinCount;  // fftSize / 2
const frequencyData = new Uint8Array(bufferLength);

function updateSpectrum() {
  analyser.getByteFrequencyData(frequencyData);

  // Exemple : affichage bars
  const canvas = document.getElementById('spectrum');
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#00ff00';

  const barWidth = canvas.width / bufferLength;
  for (let i = 0; i < bufferLength; i++) {
    const barHeight = (frequencyData[i] / 255) * canvas.height;
    ctx.fillRect(i * barWidth, canvas.height - barHeight, barWidth - 1, barHeight);
  }

  requestAnimationFrame(updateSpectrum);
}

// Données temporelles (onde)
const waveform = new Uint8Array(bufferLength);
analyser.getByteTimeDomainData(waveform);
```

### 4.2 Détection de pitch (autocorrélation)

```javascript
function autoCorrelate(buffer, sampleRate) {
  // Autocorrélation pour la détection de hauteur
  const SIZE = buffer.length;
  let maxSamples = Math.floor(SIZE / 2);
  let bestOffset = -1;
  let bestCorrelation = 0;
  let rms = 0;

  for (let i = 0; i < SIZE; i++) {
    const val = buffer[i];
    rms += val * val;
  }
  rms = Math.sqrt(rms / SIZE);
  if (rms < 0.01) return -1;  // Trop silencieux

  let lastCorrelation = 1;
  for (let offset = 0; offset < maxSamples; offset++) {
    let correlation = 0;
    for (let i = 0; i < maxSamples; i++) {
      correlation += Math.abs((buffer[i]) - (buffer[i + offset]));
    }
    correlation = 1 - (correlation / maxSamples);
    if (correlation > 0.9 && correlation > lastCorrelation) {
      bestOffset = offset;
      bestCorrelation = correlation;
    }
    lastCorrelation = correlation;
  }

  if (bestOffset > 0) {
    return sampleRate / bestOffset;  // Fréquence en Hz
  }
  return -1;
}

// Utilisation dans un loop audio
function updatePitch() {
  analyser.getFloatTimeDomainData(timeDomain);
  const pitch = autoCorrelate(timeDomain, audioCtx.sampleRate);
  if (pitch > 0) {
    const note = frequencyToNote(pitch);
    document.getElementById('pitch').textContent = `${pitch.toFixed(1)}Hz (${note})`;
  }
  requestAnimationFrame(updatePitch);
}

function frequencyToNote(freq) {
  const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  const semitone = 12 * Math.log2(freq / 440) + 69;
  const octave = Math.floor(semitone / 12) - 1;
  const noteIndex = Math.round(semitone) % 12;
  return `${notes[noteIndex]}${octave}`;
}
```

## 5. Capture Audio (Microphone)

### 5.1 Entrée microphone

```javascript
async function startMic(audioCtx) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: 48000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: false
      }
    });

    const source = audioCtx.createMediaStreamSource(stream);

    // Analyse temps réel
    const analyser = audioCtx.createAnalyser();
    source.connect(analyser);

    return { stream, source, analyser };
  } catch (err) {
    console.error('Erreur micro:', err);
  }
}

// Visualisation en direct
const mic = await startMic(audioCtx);
```

### 5.2 Enregistrement

```javascript
class AudioRecorder {
  constructor(audioCtx, source) {
    this.ctx = audioCtx;
    this.source = source;
    this.chunks = [];
    this.mediaRecorder = null;
  }

  start() {
    const dest = this.ctx.createMediaStreamDestination();
    this.source.connect(dest);

    this.mediaRecorder = new MediaRecorder(dest.stream, {
      mimeType: 'audio/webm;codecs=opus'
    });

    this.mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) this.chunks.push(e.data);
    };

    this.mediaRecorder.start(100); // Chunks de 100ms
  }

  stop() {
    return new Promise((resolve) => {
      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.chunks, { type: 'audio/webm' });
        this.chunks = [];
        resolve(blob);
      };
      this.mediaRecorder.stop();
    });
  }

  static async blobToAudioBuffer(audioCtx, blob) {
    const arrayBuffer = await blob.arrayBuffer();
    return await audioCtx.decodeAudioData(arrayBuffer);
  }
}
```

## 6. Tone.js (Framework haut niveau)

### 6.1 Installation et base

```javascript
// Installation : npm install tone
import * as Tone from 'tone';

// Démarrage (nécessite interaction utilisateur)
await Tone.start();
console.log(`Tone.js ready, sample rate: ${Tone.context.sampleRate}`);

// Synthétiseur simple
const synth = new Tone.Synth().toDestination();
synth.triggerAttackRelease('C4', '8n');  // Note C4, croche

// PolySynth (polyphonique)
const polySynth = new Tone.PolySynth(Tone.Synth).toDestination();
polySynth.triggerAttackRelease(['C4', 'E4', 'G4'], '4n');  // Accord
```

### 6.2 Synthétiseurs Tone.js

```javascript
// FM Synth
const fmSynth = new Tone.FMSynth({
  harmonicity: 3,  // Ratio harmonique carrier/modulator
  modulationIndex: 10,
  carrier: { oscillator: { type: 'sine' } },
  modulator: { oscillator: { type: 'triangle' } }
}).toDestination();

fmSynth.triggerAttackRelease('A2', '2n');

// AM Synth
const amSynth = new Tone.AMSynth().toDestination();
amSynth.triggerAttackRelease('C4', '4n');

// DuoSynth (deux oscillateurs)
const duoSynth = new Tone.DuoSynth({
  voice0: { oscillator: { type: 'sawtooth' } },
  voice1: { oscillator: { type: 'sine' } }
}).toDestination();

// MonoSynth
const monoSynth = new Tone.MonoSynth({
  oscillator: { type: 'sawtooth' },
  filter: { type: 'lowpass', frequency: 800 },
  envelope: { attack: 0.1, decay: 0.2, sustain: 0.5, release: 0.8 }
}).toDestination();

// MetalSynth (cloches, métal)
const metalSynth = new Tone.MetalSynth({
  frequency: 200,
  envelope: { attack: 0.001, decay: 0.5, release: 0.2 }
}).toDestination();
```

### 6.3 Séquences et patterns

```javascript
// Séquence mélodique
const notes = ['C4', 'E4', 'G4', 'B4', 'D5'];
const seq = new Tone.Sequence((time, note) => {
  synth.triggerAttackRelease(note, '8n', time);
}, notes, '4n');

seq.start('4m');  // Démarre après 4 mesures
Tone.Transport.start();

// Pattern rythmique
const kick = new Tone.MembraneSynth().toDestination();
const hihat = new Tone.NoiseSynth({ volume: -10 }).toDestination();

const beat = new Tone.Pattern((time, note) => {
  if (note === 'kick') kick.triggerAttackRelease('C1', '8n', time);
  if (note === 'hat') hihat.triggerAttackRelease('16n', time);
}, ['kick', 'hat', 'kick', 'hat', 'kick', 'hat', 'kick', 'hat'], '8n');

beat.start(0);

// Partie (plusieurs pistes synchronisées)
const part = new Tone.Part((time, value) => {
  synth.triggerAttackRelease(value.note, value.duration, time, value.velocity);
}, [
  { time: '0:0:0', note: 'C4', duration: '4n', velocity: 0.8 },
  { time: '0:1:0', note: 'E4', duration: '4n', velocity: 0.6 },
  { time: '0:2:0', note: 'G4', duration: '2n', velocity: 0.9 },
]);

Tone.Transport.bpm.value = 120;
Tone.Transport.start();
```

### 6.4 Effets Tone.js (chaînés)

```javascript
// Chaîne d'effets
const signal = new Tone.Synth();

const reverb = new Tone.Reverb({ decay: 3, wet: 0.5 });
const delay = new Tone.FeedbackDelay('8n', 0.3);
const filter = new Tone.AutoFilter({ frequency: '4n', depth: 0.5 });
const chorus = new Tone.Chorus({ frequency: 0.5, depth: 2 });
const distortion = new Tone.Distortion(0.5);
const compressor = new Tone.Compressor({ threshold: -20, ratio: 4 });
const eq = new Tone.EQ3({ low: 0, mid: 2, high: -1 });

// Chaînage
signal.chain(filter, compressor, distortion, eq, chorus, delay, reverb, Tone.Destination);

signal.triggerAttackRelease('C4', '2n');

// Effets modulés
const phaser = new Tone.Phaser({ frequency: 0.5, octaves: 3 });
const tremolo = new Tone.Tremolo({ frequency: 5, depth: 0.5 }).start();
const vibrato = new Tone.Vibrato({ frequency: 5, depth: 0.1 });
```

### 6.5 Échantillonneurs

```javascript
// Sampler (instruments multi-échantillons)
const sampler = new Tone.Sampler({
  urls: {
    'C4': 'C4.mp3',
    'D#4': 'Ds4.mp3',
    'F#4': 'Fs4.mp3',
    'A4': 'A4.mp3'
  },
  baseUrl: 'https://tonejs.github.io/audio/salamander/',
  onload: () => {
    sampler.triggerAttackRelease(['C4', 'E4', 'G4'], '4n');
  }
}).toDestination();

// Players (échantillons uniques)
const players = new Tone.Players({
  kick: 'kick.wav',
  snare: 'snare.wav',
  hat: 'hat.wav',
  bass: 'bass.wav'
}).toDestination();

players.player('kick').start();
```

## 7. Audio Worklet (Traitement personnalisé bas niveau)

### 7.1 Module Worklet

```javascript
// worklet-processor.js
class GainProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.gain = 1.0;
    this.port.onmessage = (event) => {
      this.gain = event.data.gain;
    };
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    const output = outputs[0];

    for (let channel = 0; channel < input.length; channel++) {
      const inputChannel = input[channel];
      const outputChannel = output[channel];

      for (let i = 0; i < inputChannel.length; i++) {
        outputChannel[i] = inputChannel[i] * this.gain;
      }
    }

    return true;  // Garder le processor actif
  }
}

registerProcessor('gain-processor', GainProcessor);
```

### 7.2 Utilisation du Worklet

```javascript
// Chargement et connexion
await audioCtx.audioWorklet.addModule('worklet-processor.js');

const workletNode = new AudioWorkletNode(audioCtx, 'gain-processor');
workletNode.port.postMessage({ gain: 0.5 });

source.connect(workletNode);
workletNode.connect(audioCtx.destination);
```

## 8. Pitfalls et solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| AudioContext suspendu | Interaction requise | Attendre un clic/tauch avant de créer |
| Clics aux notes | Pas de release envelope | Enveloppe ADSR systématique sur chaque note |
| Latence élevée | Tampon trop grand | `latencyHint: 'interactive'`, réduire buffer |
| Distorsion saturée | Somme de signaux > 0dB | Gain master à 0.3, headroom suffisant |
| Feedback Larsen | Boucle micro → HP | Casque, gain micro réduit |
| GC freeze | Nodes non nettoyés | `disconnect()`, `stop()`, `close()` |
| Analyseur trop lent | fftSize trop petit | 2048 minimum, 8192 pour haute résolution |

## Références

- **Web Audio API (MDN)** : https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- **Tone.js** : https://tonejs.github.io/
- **Audio Worklet** : https://developer.chrome.com/blog/audio-worklet
- **Web Audio Demos** : https://webaudiodemos.appspot.com/
- **Web Audio School** : https://mmckegg.github.io/web-audio-school/
- **Tone.js examples** : https://github.com/Tonejs/Tone.js/tree/master/examples