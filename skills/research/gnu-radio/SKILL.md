---
name: gnu-radio
description: "GNU Radio — framework de développement SDR : flowgraphs, OOT modules, blocs Python/C++, gr-osmosdr, traitement temps réel, scheduler, optimisation de débit, gr-satellites, gr-ieee802-11, gr-adsb."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [gnu-radio, grc, flowgraph, sdr, oot-module, python-block, cpp-block, gr-osmosdr, scheduler, polyphase, channelizer, tag-stream, message-passing, gr-satellites, gr-ieee802-11, gr-adsb, gnuradio-companion, volk]
    related_skills: [dsp-fundamentals, fft-algorithms, fir-iir-filters, modulation-demodulation, sdr-advanced, signal-processing-digital, radio-sdr]
---

# GNU Radio — Framework DSP pour SDR

## Vue d'ensemble

GNU Radio est un framework open source pour le développement de radios logicielles. Il fournit une bibliothèque de blocs de traitement du signal et un **scheduler** temps réel qui connecte ces blocs en **flowgraphs** (graphes de traitement).

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Flowgraph GNU Radio                  │
│                                                       │
│  Source → [Filtre] → [Démodulateur] → [Décodeur] → Sink │
│     ↑                                                    │
│  Matériel SDR (via gr-osmosdr / UHD / SoapySDR)         │
└─────────────────────────────────────────────────────┘
```

### Composants clés

| Composant | Rôle |
|:---|---|
| **GNU Radio Companion (GRC)** | Interface graphique pour créer des flowgraphs |
| **Scheduler** | Ordonnanceur temps réel (threads, buffers, tags) |
| **VOLK** (Vector-Optimized Library of Kernels) | SIMD vectorisé (SSE, AVX, NEON) |
| **gr-osmosdr** | Interface unifiée pour RTL-SDR, HackRF, LimeSDR, etc. |
| **UHD** | Pilote pour USRP (Ettus Research) |
| **SoapySDR** | Abstraction multi-plateforme SDR |
| **PMT** (Polymorphic Types) | Système de messages et de tags |

---

## 1. Installation et Configuration

```bash
# Installation complète
sudo apt install gnuradio gnuradio-dev gr-osmosdr gr-osmosdr-dev
# Ou via PyBOMBS (gestionnaire de paquets GNU Radio)
sudo pip install pybombs
pybombs recipes add gr-recipes git+https://github.com/gnuradio/gr-recipes.git
pybombs init
pybombs install gnuradio

# Vérification
gnuradio-config-info --version
gnuradio-config-info --prefix
volk_profile  # Calibration VOLK pour votre CPU
```

### Installation d'OOT (Out-of-Tree) modules

```bash
# gr-satellites (démodulation de satellites)
git clone https://github.com/daniestevez/gr-satellites
cd gr-satellites
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
sudo ldconfig

# gr-ieee802-11 (WiFi)
git clone https://github.com/bastibl/gr-ieee802-11
# Même procédure cmake/make/make install

# Autres OOT utiles :
# gr-adsb        : ADS-B aviation
# gr-lora        : LoRa
# gr-gsm         : GSM
# gr-acars       : ACARS aviation
# gr-pager       : POCSAG/FLEX pagers
# gr-iridium     : Iridium satellite
# gr-inspector   : Analyse spectrale avancée
```

---

## 2. GNU Radio Companion (GRC)

### 2.1 Structure d'un flowgraph GRC

Un flowgraph est composé de :
- **Sources** : entrée de données (SDR, fichier, signal généré)
- **Traitements** : filtres, démodulateurs, décodeurs
- **Sinks** : sortie (audio, fichier, visualisation, socket UDP)

### 2.2 Flowgraph FM récepteur minimal

```
Osmocom Source → Low Pass Filter → WBFM Receive → Audio Sink
                   ↓
               QT GUI Frequency Sink
                   ↓
               QT GUI Waterfall Sink
```

**Configuration clé des blocs :**

```
Osmocom Source :
  - Sample Rate : 2.4 MHz
  - Ch0 Frequency : 103.5 MHz (fréquence FM)
  - Ch0 Gain : 20 dB
  - Ch0 Antenna : RX

Low Pass Filter :
  - Decimation : 10 → output rate = 240 kHz
  - Cutoff Freq : 100 kHz
  - Transition Width : 10 kHz
  - Window : Hamming

WBFM Receive :
  - Audio Rate : 48 kHz
  - Quadrature Rate : 240 kHz

Audio Sink :
  - Sample Rate : 48 kHz
```

### 2.3 Flowgraph NBFM (radioamateur, PMR)

```
Osmocom Source (fs=1MHz)
  → Rational Resampler (decim=10 → 100k)
    → NBFM Receive (100k in, 48k audio out)
      → Audio Sink
        → QT GUI Frequency Sink (options)
```

### 2.4 Flowgraph AM (aéronautique, broadcast)

```
Osmocom Source (fs=2.4MHz)
  → Low Pass Filter (decim=8 → 300k)
    → AM Demod (300k in, 48k audio out)
      → Audio Sink
```

---

## 3. Blocs Python Personnalisés (OOT)

### 3.1 Bloc Python synchronisé (entrée = sortie)

```python
from gnuradio import gr
import numpy as np

class blk(gr.sync_block):
    """
    Bloc Python synchronisé : N échantillons in → N échantillons out.
    Exemple : multiplicateur par constante.
    """
    def __init__(self, facteur=1.0):
        gr.sync_block.__init__(
            self,
            name='Multiplicateur',
            in_sig=[np.float32],
            out_sig=[np.float32]
        )
        self.facteur = facteur

    def work(self, input_items, output_items):
        output_items[0][:] = input_items[0] * self.facteur
        return len(output_items[0])
```

### 3.2 Bloc Python avec plusieurs ports et types

```python
from gnuradio import gr
import numpy as np

class blk(gr.sync_block):
    """
    Bloc avec entrée complexe (gr_complex), sortie flottante.
    Exemple : extraction de la magnitude.
    """
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name='Magnitude',
            in_sig=[np.complex64],
            out_sig=[np.float32]
        )

    def work(self, input_items, output_items):
        output_items[0][:] = np.abs(input_items[0])
        return len(output_items[0])
```

### 3.3 Bloc Python asynchrone (tags + messages)

```python
from gnuradio import gr
import pmt

class blk(gr.sync_block):
    """
    Bloc qui lit les tags et publie des messages.
    Exemple : détection de seuil avec alerte.
    """
    def __init__(self, seuil=0.5):
        gr.sync_block.__init__(
            self,
            name='Détecteur Seuil',
            in_sig=[np.float32],
            out_sig=None  # Pas de sortie stream, que des messages
        )
        self.seuil = seuil
        self.message_port_register_out(pmt.intern('alert'))

    def work(self, input_items, output_items):
        signal = input_items[0]
        if np.max(signal) > self.seuil:
            # Envoyer un message
            msg = pmt.cons(pmt.intern('seuil_depasse'),
                          pmt.from_double(np.max(signal)))
            self.message_port_pub(pmt.intern('alert'), msg)
        return len(signal)
```

### 3.4 Bloc Python avec paramètres et callback (GRC)

```python
# Nécessite un fichier .block.yml pour l'intégration GRC
module: mono
id: bloc_delay
label: Délai Variable
category: '[Mono] Utilitaires'
templates:
  imports: import gnuradio.mono as mono
  make: mono.bloc_delay(${delay})
parameters:
  - id: delay
    label: Délai (échantillons)
    dtype: int
    default: 0
    settable: true
```

---

## 4. Blocs C++ Haute Performance

### 4.1 Bloc C++ synchronisé

```cpp
#include <gnuradio/sync_block.h>

class mon_bloc : public gr::sync_block {
private:
    float d_facteur;

public:
    mon_bloc(float facteur)
        : gr::sync_block("mon_bloc",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(1, 1, sizeof(float))),
          d_facteur(facteur) {}

    int work(int noutput_items,
             gr_vector_const_void_star &input_items,
             gr_vector_void_star &output_items) override {
        const float *in = (const float *)input_items[0];
        float *out = (float *)output_items[0];

        // Utiliser VOLK pour la vectorisation SIMD
        volk_32f_s32f_multiply_32f(out, in, d_facteur, noutput_items);

        return noutput_items;
    }
};
```

### 4.2 VOLK (Vector-Optimized Library of Kernels)

```bash
# Lister les noyaux VOLK disponibles
volk_profile  # Calibration automatique

# Exemples de noyaux VOLK :
# volk_32fc_x2_multiply_32fc    : multiplication complexe
# volk_32f_s32f_multiply_32f    : multiplication scalaire
# volk_32fc_magnitude_32f       : magnitude complexe
# volk_32f_s32f_power_32f       : puissance
# volk_32f_x2_dot_prod_32f      : produit scalaire
# volk_32f_x2_divide_32f        : division
# volk_32fc_s32fc_multiply_32fc : multiplication complexe*scalaire
```

```cpp
// Utiliser VOLK dans un bloc C++
#include <volk/volk.h>

float *output, *input;
int n = 1000;

// Allouer des buffers alignés (16 ou 32 octets pour SIMD)
output = (float*) volk_malloc(n * sizeof(float), volk_get_alignment());
input = (float*) volk_malloc(n * sizeof(float), volk_get_alignment());

// Opération vectorisée
volk_32f_x2_multiply_32f(output, input, input, n);  // output = input * input

volk_free(output);
volk_free(input);
```

---

## 5. Scheduler et Performance

### 5.1 Types de blocs et threading

| Bloc | Type | Entrée/Sortie | Usage |
|:---|:---|:---:|---|
| `gr::sync_block` | Synchronisé | Même nombre d'IO | Filtres, gains |
| `gr::decim_block` | Décimateur | N_in = N_out × decim | DDC |
| `gr::interp_block` | Interpolateur | N_out = N_in × interp | DUC |
| `gr::block` | Général | Variable | Démodulation, FEC |
| `gr::tagged_stream_block` | Trames taggées | Par paquets | Décodeurs |

### 5.2 Configuration du buffer

```python
# Taille du buffer entre deux blocs (échantillons)
# Défaut : 8192 × sizeof(type)
self.set_output_multiple(1024)  # Minimum d'échantillons par appel

# Historique (pour FIR)
self.set_history(64)  # Les appels work() reçoivent 64 échantillons de contexte
```

### 5.3 Optimisation du débit

```bash
# Augmenter la taille des buffers système
sudo sysctl -w net.core.rmem_max=50000000
sudo sysctl -w net.core.wmem_max=1048576

# Ajuster les priorités des threads GNU Radio
# Utiliser le bloc "Throttle" pour limiter le débit en simulation

# Vérifier les buffers perdus (overrun)
# Dans GRC, connecter "Message Debug" aux ports "msg" des sources SDR
```

### 5.4 Débogage de performance

```bash
# Profiler les blocs
# Ajouter "Performance Counters" dans les propriétés du bloc
# Activer : perf_counter_enabled = True

# Vérifier le CPU
htop  # Utilisation par thread GNU Radio

# Vérifier les buffers USB
cat /proc/asound/card*/stream0  # Audio USB
watch -n 1 cat /proc/net/dev     # Réseau (UDP sinks)
```

---

## 6. Blocs Essentiels

### 6.1 Sources matérielles

| Bloc | Commande | Usage |
|:---|---:|---|
| `osmocom Source` | `gr-osmosdr` | RTL-SDR, HackRF, LimeSDR, BladeRF |
| `UHD: USRP Source` | `uhd` | USRP B200/B210/N300/X300 |
| `Soapy SDR Source` | `soapysdr` | Multi-plateforme |

### 6.2 Filtres

| Bloc | Usage |
|:---|---|
| `Low Pass Filter` | FIR, décimation, fenêtre configurable |
| `Rational Resampler` | Changement de taux arbitraire (polyphase) |
| `FFT Filter` | Filtrage par FFT (efficace pour longs FIR) |
| `Frequency Xlating FIR Filter` | DDC complet (décalage + filtrage + décimation) |
| `Interpolating FIR Filter` | Interpolation polyphase |
| `Root Raised Cosine Filter` | Mise en forme d'impulsion (comms) |
| `Band Pass Filter` | Sélection de bande |

### 6.3 Démodulateurs

| Bloc | Modulation |
|:---|---|
| `WBFM Receive` | FM broadcast (stéréo) |
| `NBFM Receive` | FM bande étroite (radioamateur) |
| `AM Demod` | AM double bande |
| `Quadrature Demod` | FM générique (différent de phase) |
| `Constellation Decoder` | PSK, QAM, DPSK |
| `Differential PSK Demod` | DBPSK, DQPSK, D8PSK |
| `Costas Loop` | PLL pour PSK/QAM |
| `Symbol Sync` | Récupération de rythme (Early-Late, Mueller&Muller) |
| `Clock Recovery MM` | Récupération d'horloge (Mueller&Muller) |

### 6.4 Sinks (sorties)

| Bloc | Usage |
|:---|---|
| `Audio Sink` | Sortie audio (ALSA/PulseAudio/Jack) |
| `File Sink` | Sauvegarde dans fichier |
| `UDP Sink` | Streaming réseau |
| `QT GUI Time Sink` | Visualisation temporelle |
| `QT GUI Frequency Sink` | Visualisation spectrale |
| `QT GUI Waterfall Sink` | Waterfall temps-fréquence |
| `QT GUI Constellation Sink` | Diagramme de constellation |
| `QT GUI Eye Sink` | Diagramme de l'œil |
| `Null Sink` | Jette les données (debug) |
| `Socket PDU` | Envoi/réception de trames via TCP/UDP |

### 6.5 Traitement de trames (Tags, PDU, Messages)

```python
# Tags : métadonnées attachées aux échantillons
# (fréquence, timestamp, SNR, CRC, etc.)

# PDU : Protocol Data Unit — messages discrets
from gnuradio import gr, digital, blocks, pdu
# pdu.to_tagged_stream, pdu.tagged_stream_to_pdu

# Message Passing Architecture
# Pour remplacer le streaming par des messages asynchrones
self.message_port_register_in(pmt.intern('cmd'))
self.message_port_register_out(pmt.intern('status'))
```

---

## 7. Flowgraphs Avancés

### 7.1 Récepteur ADS-B (aviation)

```
Osmocom Source (1090 MHz, fs=20 MHz)
  → Band Pass Filter (1088-1092 MHz)
    → Rational Resampler (fs=20M → 10M)
      → Pulse Shaping
        → Correlate Access Code (préambule ADS-B: 8 µs)
          → Parse PDU → UDP Sink → decode1090
```

```bash
# Alternative : gr-adsb
git clone https://github.com/bistromath/gr-adsb
```

### 7.2 Récepteur APT NOAA (images météo)

```
Osmocom Source (137.1 MHz, fs=2.4 MHz)
  → Frequency Xlating FIR Filter (centre 0 Hz, BW=40 kHz)
    → Rational Resampler (240k → 38.4k)
      → FM Demod (Quadrature Demod)
        → Low Pass Filter (2.4 kHz)
          → File Sink (fichier .wav)
            → WXtoIMG / aptdec
```

### 7.3 Analyse spectrale large bande

```
Osmocom Source (fs=20 MHz)
  → Stream to Vector (N=8192)
    → FFT (N=8192)
      → Complex to Mag
        → Vector to Stream
          → QT GUI Time Sink → Waterfall
```

### 7.4 Channelizer polyphase (PFB)

```python
# Polyphase Filter Bank : décompose la bande SDR en N canaux
# par un seul banc de filtres polyphase + FFT
# Beaucoup plus efficace que N DDC séparés

# Bloc : "Polyphase Channelizer" (pfb_channelizer_ccf)
# Paramètres : N canaux, filtre prototype, atténuation
```

---

## 8. Outils de Débogage

### 8.1 gr-inspector

```bash
# Analyse automatique de signaux : type, débit, modulation
git clone https://github.com/gnuradio/gr-inspector
cd gr-inspector && mkdir build && cd build
cmake .. && make && sudo make install
```

### 8.2 gr-qtgui extras

```python
# Visualisation avancée
# QT GUI Chooser : sélection de paramètres runtime
# QT GUI Entry : saisie utilisateur
# QT GUI Range : slider pour réglage en temps réel
# QT GUI Tab Widget : onglets multiples
# QT GUI Compass : affichage de direction (AoA, Doppler)
```

---

## Pièges Courants

1. **Bufs d'overrun/dépassement :** Trop de blocs ou fs trop élevée pour le CPU. Réduire la bande passante, augmenter la décimation.
2. **Fréquence d'horloge non alignée :** La source et le sink doivent avoir des horloges cohérentes. Utiliser Rational Resampler pour adapter les taux.
3. **Tags perdus :** Les tags ne survivent pas à certains blocs (FFT, repack). Vérifier avec Message Debug.
4. **Bloc Throttle manquant en simulation :** Sans Throttle, le flowgraph tourne à 100% CPU en l'absence de source matérielle (SDR).
5. **VOLK non calibré :** Sans `volk_profile`, VOLK utilise l'implémentation générique la plus lente.

---

## Liste de vérification (Checklist)

- [ ] `volk_profile` exécuté après installation.
- [ ] Source SDR correctement configurée (fréquence, gain, fs, antenne).
- [ ] Décimalité adaptée à la bande passante du signal utile.
- [ ] Bloc Throttle présent pour les flowgraphs sans source matérielle.
- [ ] Tags et messages : vérification du routage avec Message Debug.
- [ ] Performance : overruns (F) et underruns (U) dans la console.
- [ ] OOT modules compilés et installés (cmake/make/sudo make install).
- [ ] Scheduler configuré : taille de buffer, priorité des threads.
- [ ] Test unitaire de chaque bloc Python avant intégration au flowgraph.