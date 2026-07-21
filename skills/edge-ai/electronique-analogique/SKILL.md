---
name: electronique-analogique
description: "Concevoir et analyser des circuits analogiques — amplificateurs opérationnels, transistors (BJT, MOSFET), filtres passifs/actifs, alimentations linéaires/DC-DC, oscillateurs, boucles PLL et mise en forme de signaux."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [electronique-analogique, amplificateur-operationnel, aop, transistor, bjt, mosfet, filtre, passe-bas, passe-haut, passe-bande, alimentation, regulateur, dc-dc, buck, boost, flyback, oscillateur, pll, phase-locked-loop, mise-en-forme, comparateur, redresseur, multiplieur]
    related_skills: [prototypage-electronique, signal-processing-digital, pcb-design-electronique, embedded-systems-firmware]
---

# Électronique Analogique

## Vue d'ensemble

L'électronique analogique traite des signaux continus (tension, courant) qui varient dans le temps. Contrairement au numérique, les valeurs ne sont pas discrétisées en bits. Cette compétence couvre la conception et l'analyse des circuits fondamentaux : amplificateurs opérationnels, transistors, filtres, alimentations, oscillateurs, boucles à verrouillage de phase (PLL), et conditionnement de signaux de capteurs.

### Domaines d'application

| Domaine | Circuits analogiques |
|:---|---|
| **Instrumentation** | Amplificateur d'instrumentation, pont de Wheatstone, conditionneur de jauge de contrainte |
| **Audio** | Préamplificateur, égaliseur, filtre actif, ampli de puissance classe AB/D |
| **Alimentation** | Régulateur linéaire (LDO), convertisseur DC-DC (buck, boost, flyback), PFC |
| **RF** | Amplificateur faible bruit (LNA), mélangeur, oscillateur local, filtre SAW |
| **Capteurs** | Interface photodiode, conditionneur PT100/RTD, amplificateur de charge (piézo) |
| **Commande de puissance** | Driver MOSFET/IGBT, pont en H, circuit de snubber, détection de zéro |

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Concevoir un circuit avec amplificateur opérationnel (AOP) : amplificateur non-inverseur, inverseur, sommateur, intégrateur, dérivateur, comparateur.
- Dimensionner un filtre passif (RC, RL, RLC) ou actif (Sallen-Key, MFB, Butterworth, Chebyshev).
- Calculer un étage à transistor (BJT ou MOSFET) : polarisation, gain, impédance d'entrée/sortie.
- Concevoir une alimentation linéaire (régulateur 78xx, LDO) ou découpage (buck, boost, flyback).
- Mettre en forme un signal analogique (redresseur, écrêteur, détecteur de crête, échantillonneur-bloqueur).
- Conditionner un signal de capteur (PT100, thermocouple, photodiode, accéléromètre piézoélectrique).
- Analyser un circuit : gain en tension, bande passante, impédance d'entrée, CMRR, PSRR, bruit, distorsion.

Ne pas utiliser pour : la logique numérique (utiliser `fpga-verilog-vhdl`), la conception de PCB (utiliser `pcb-design-electronique`), le traitement du signal numérique post-ADC (utiliser `signal-processing-digital`).

---

## 1. Amplificateurs Opérationnels (AOP)

### 1.1 Montages fondamentaux

```python
import math

# Modèle d'AOP idéal : gain infini, impédance d'entrée infinie,
# impédance de sortie nulle, bande passante infinie.

def non_inverting(gain_db: float) -> dict:
    """
    Amplificateur non-inverseur.
    Gain = 1 + R2 / R1
    """
    gain_v = 10 ** (gain_db / 20)
    # Choisir R1 = 1 kΩ, calculer R2
    r1 = 1000  # Ω
    r2 = r1 * (gain_v - 1)
    return {"gain_v": gain_v, "gain_db": gain_db, "R1": r1, "R2": r2}

def inverting(gain_db: float) -> dict:
    """
    Amplificateur inverseur.
    Gain = - R2 / R1
    Impédance d'entrée = R1
    """
    gain_v_mag = 10 ** (gain_db / 20)
    r1 = 1000  # Ω, impédance d'entrée
    r2 = r1 * gain_v_mag
    return {"gain_v": -gain_v_mag, "gain_db": gain_db, "R1": r1, "R2": r2}

def difference_gain(r1: float, r2: float, r3: float, r4: float) -> dict:
    """
    Amplificateur différentiel (soustracteur).
    Vout = (R2/R1) × (V2 - V1)  si R1=R3 et R2=R4
    CMRR limité par la tolérance des résistances.
    """
    gain_diff = r2 / r1
    cmrr_ideal = 20 * math.log10((r2/r1 + 1) / (4 * 0.01))  # 1% tolérance
    return {"gain_differentiel": gain_diff, "cmrr_db_estime": cmrr_ideal}

# Exemples
amp = non_inverting(20)  # Gain 20 dB = ×10
print(f"Non-inverseur : R1={amp['R1']} Ω, R2={amp['R2']:.0f} Ω")

amp2 = inverting(6)      # Gain 6 dB = ×2
print(f"Inverseur : R1={amp2['R1']} Ω, R2={amp2['R2']:.0f} Ω")
```

### 1.2 Filtre actif Sallen-Key (passe-bas, 2e ordre)

```python
def sallen_key_lowpass(fc_hz: float, q: float = 0.707,
                       c_value: float = 10e-9) -> dict:
    """
    Filtre passe-bas Sallen-Key (2e ordre).

    Paramètres :
        fc_hz   : fréquence de coupure (Hz)
        q       : facteur de qualité
                  - 0.707 : Butterworth (maximally flat)
                  - 0.5   : Bessel (bonne réponse impulsionnelle)
                  - 1.0   : Chebyshev 0.5 dB (transition raide)
        c_value : capacité (F), typique 10 nF

    Retourne :
        R, valeurs des composants
    """
    # Pour R1 = R2 = R, C1 = C, C2 = C × 2Q
    r = 1 / (2 * math.pi * fc_hz * c_value)
    c2 = c_value * 2 * q

    return {
        "type": "Sallen-Key passe-bas 2e ordre",
        "fc_hz": fc_hz,
        "Q": q,
        "R1": r,
        "R2": r,
        "C1": c_value,
        "C2": c2,
        "gain_dc_db": 0,  # Unity gain
    }

# Exemple : filtre anti-aliasing, fc = 1 kHz, Butterworth
filtre = sallen_key_lowpass(1000, 0.707, 10e-9)
print(f"R1=R2={filtre['R1']:.0f} Ω, C1={filtre['C1']:.1e} F, C2={filtre['C2']:.1e} F")
# R ≈ 15.9 kΩ, C1 = 10 nF, C2 = 14.1 nF
```

### 1.3 Comparateur à hystérésis (Trigger de Schmitt)

```python
def schmitt_trigger(r1: float, r2: float, vref: float, vcc: float) -> dict:
    """
    Comparateur non-inverseur à hystérésis.

    Vout passe à HIGH quand Vin dépasse Vth_high,
    Vout passe à LOW quand Vin descend sous Vth_low.

    Paramètres :
        r1, r2 : résistances de réaction positive
        vref   : tension de référence (V)
        vcc    : tension d'alimentation (V)

    Retourne :
        seuils haut et bas
    """
    beta = r1 / (r1 + r2)  # Taux de réaction

    vth_high = vref * (1 + beta)  # Seuil haut (V → HIGH)
    vth_low = vref * (1 - beta)   # Seuil bas (HIGH → LOW)

    hysteresis = vth_high - vth_low

    return {
        "Vth_high": vth_high,
        "Vth_low": vth_low,
        "hysteresis_V": hysteresis,
        "beta": beta,
        "R1": r1,
        "R2": r2,
        "Vref": vref,
    }

# Exemple : détection de passage à zéro avec hystérésis 0,5 V
schmitt = schmitt_trigger(10e3, 100e3, 2.5, 5.0)
print(f"Seuils : {schmitt['Vth_low']:.2f} V → {schmitt['Vth_high']:.2f} V")
print(f"Hystérésis : {schmitt['hysteresis_V']:.2f} V")
```

---

## 2. Transistors (BJT et MOSFET)

### 2.1 Polarisation d'un transistor BJT (émetteur commun)

```python
def bjt_common_emitter(vcc: float, ic_mA: float, vce: float,
                       beta: float = 200, vbe: float = 0.7) -> dict:
    """
    Conception d'un étage amplificateur à émetteur commun.

    Paramètres :
        vcc   : tension d'alimentation (V)
        ic_mA : courant de collecteur (mA)
        vce   : tension collecteur-émetteur au point de repos (V)
        beta  : gain en courant du transistor
        vbe   : tension base-émetteur (V)

    Retourne :
        valeurs des résistances
    """
    ic = ic_mA / 1000  # A
    rc = (vcc - vce) / ic          # Résistance de collecteur
    re = vce / (4 * ic)            # Règle : V_RE ≈ VCC/4
    ib = ic / beta
    r2 = vcc / (10 * ib)           # Pont diviseur : I_R2 ≈ 10 × I_B
    vb = vbe + ic * re
    r1 = (vcc - vb) / (vb / r2)

    return {
        "RC": rc,
        "RE": re,
        "R1": r1,
        "R2": r2,
        "gain_tension_approx": -rc / re,  # Gain négatif (inverseur)
        "impedance_entree": r1 * r2 / (r1 + r2),
        "ic_mA": ic_mA,
        "vce_V": vce,
    }

bjt = bjt_common_emitter(12, 2, 6)
print(f"RC={bjt['RC']:.0f} Ω, RE={bjt['RE']:.0f} Ω")
print(f"Gain approximatif : {bjt['gain_tension_approx']:.1f}")
```

### 2.2 MOSFET en commutation (driver de charge)

```python
def mosfet_switch(vgs: float, vth: float, rds_on: float,
                  load_a: float, vdd: float) -> dict:
    """
    Dimensionnement d'un MOSFET en commutation (N-channel).

    Paramètres :
        vgs    : tension gate-source appliquée (V)
        vth    : tension de seuil (V) — typique 2-4 V pour power MOSFET
        rds_on : résistance drain-source à l'état passant (Ω)
        load_a : courant de charge (A)
        vdd    : tension d'alimentation de la charge (V)

    Retourne :
        puissance dissipée, température, gate resistor
    """
    if vgs <= vth:
        return {"error": "VGS insuffisant pour saturer le MOSFET"}

    # Puissance dissipée par effet Joule dans Rds(on)
    p_diss = rds_on * load_a ** 2

    # Résistance de gate (limite le courant de pic de charge de la gate)
    # Courant de pic typique : 1-2 A, durée ~100 ns
    qg = 100e-9  # Charge de gate typique (C), dépend du MOSFET
    r_gate = vgs / 2  # ~12 Ω pour VGS = 5 V (limitant le pic à ~400 mA)

    return {
        "Vgs-Vth": vgs - vth,
        "puissance_dissipee_W": p_diss,
        "resistance_gate_Ohm": r_gate,
        "temps_montee_ns_estime": 2.2 * r_gate * qg / (vgs - vth) * 1e9,
        "type": "N-channel, low-side switch",
    }

# Exemple : commutation d'une charge 5 A avec IRLZ44N (Rds(on)=0.022 Ω)
mos = mosfet_switch(vgs=5.0, vth=2.0, rds_on=0.022, load_a=5, vdd=12)
print(f"Puissance dissipée : {mos['puissance_dissipee_W']:.3f} W")
print(f"Temps de montée : {mos['temps_montee_ns_estime']:.1f} ns")
```

---

## 3. Alimentations

### 3.1 Régulateur linéaire LDO

```python
def ldo_design(vin: float, vout: float, iout_a: float) -> dict:
    """
    Dimensionnement d'un régulateur linéaire (LDO).

    Paramètres :
        vin    : tension d'entrée (V)
        vout   : tension de sortie régulée (V)
        iout_a : courant de sortie max (A)

    Retourne :
        puissance dissipée, rendement, radiateur nécessaire
    """
    # Dropout voltage typique pour LDO : 0,1-0,5 V
    v_drop = vin - vout
    p_diss = v_drop * iout_a
    efficiency = vout / vin * 100

    # Estimation de la température du boîtier
    # TO-220 : RthJC ≈ 3 °C/W, RthJA ≈ 50 °C/W (sans dissipateur)
    rth_ja = 50  # °C/W (sans dissipateur)
    temp_junction = 25 + p_diss * rth_ja  # Ta = 25 °C

    return {
        "vin": vin,
        "vout": vout,
        "dropout_V": v_drop,
        "puissance_dissipee_W": p_diss,
        "rendement_pct": efficiency,
        "temp_junction_C": temp_junction,
        "necessite_dissipateur": temp_junction > 85,
        "condensateur_sortie_uF": 10,   # Minimum recommandé
    }

ldo = ldo_design(5.0, 3.3, 0.5)
print(f"Puissance : {ldo['puissance_dissipee_W']:.2f} W")
print(f"Rendement : {ldo['rendement_pct']:.1f} %")
print(f"Température jonction : {ldo['temp_junction_C']:.0f} °C")
```

### 3.2 Convertisseur Buck (abaisseur DC-DC)

```python
def buck_converter(vin: float, vout: float, iout_a: float,
                   f_sw_hz: float = 500e3) -> dict:
    """
    Dimensionnement d'un convertisseur Buck (abaisseur).

    Paramètres :
        vin      : tension d'entrée (V)
        vout     : tension de sortie (V)
        iout_a   : courant de sortie max (A)
        f_sw_hz  : fréquence de découpage (Hz)

    Retourne :
        valeurs des composants : inductance, capacité, etc.
    """
    # Duty cycle
    d = vout / vin

    # Ripple de courant dans l'inductance : 30 % de Iout
    di_l = 0.3 * iout_a

    # Inductance
    l = (vin - vout) * d / (f_sw_hz * di_l)

    # Capacité de sortie (ripple de tension < 1 %)
    v_ripple_max = vout * 0.01
    c_out = di_l / (8 * f_sw_hz * v_ripple_max)

    # Condensateur d'entrée (RMS current)
    i_cin_rms = iout_a * math.sqrt(d * (1 - d))

    return {
        "type": "Buck (abaisseur)",
        "duty_cycle": d,
        "inductance_uH": l * 1e6,
        "capacite_sortie_uF": c_out * 1e6,
        "ripple_courant_A": di_l,
        "ripple_tension_mV": v_ripple_max * 1000,
        "i_cin_rms_A": i_cin_rms,
        "frequence_decoupage_kHz": f_sw_hz / 1000,
    }

# Exemple : 12 V → 3,3 V, 2 A
buck = buck_converter(12, 3.3, 2.0)
print(f"Inductance : {buck['inductance_uH']:.1f} µH")
print(f"Capacité sortie : {buck['capacite_sortie_uF']:.1f} µF")
```

---

## 4. Oscillateurs et PLL

### 4.1 Oscillateur à pont de Wien

```python
def wien_bridge_oscillator(freq_hz: float) -> dict:
    """
    Oscillateur sinusoïdal à pont de Wien.

    Condition d'oscillation :
    - Gain de l'amplificateur = 3 (AOP non-inverseur : R2 = 2 × R1)
    - Fréquence : f = 1 / (2π × R × C)
    """
    # Choisir C = 10 nF, calculer R
    c = 10e-9
    r = 1 / (2 * math.pi * freq_hz * c)

    # Résistances pour le gain de 3
    r1 = 10000  # Ω
    r2 = 2 * r1  # Gain = 1 + R2/R1 = 3

    return {
        "type": "Pont de Wien",
        "freq_hz": freq_hz,
        "R": r,
        "C": c,
        "R1": r1,
        "R2": r2,
        "gain_necesaire": 3,
    }

osc = wien_bridge_oscillator(1000)
print(f"R = {osc['R']:.0f} Ω, C = {osc['C']:.1e} F")
```

### 4.2 Boucle PLL (Phase-Locked Loop)

```python
def pll_parameters(f_vco_min: float, f_vco_max: float,
                   f_ref: float, n_divider: int) -> dict:
    """
    Paramètres de base d'une PLL.

    f_out = N × f_ref (où N = diviseur de retour)

    Paramètres :
        f_vco_min : fréquence min du VCO (Hz)
        f_vco_max : fréquence max du VCO (Hz)
        f_ref     : fréquence de référence (Hz)
        n_divider : rapport de division

    Retourne :
        fréquences, bande passante de la boucle
    """
    f_out = f_ref * n_divider
    f_loop_bw = f_ref / 10  # Règle empirique : BW ≈ f_ref / 10

    return {
        "f_reference_Hz": f_ref,
        "f_sortie_Hz": f_out,
        "rapport_division_N": n_divider,
        "bande_passante_boucle_Hz": f_loop_bw,
        "temps_accrochage_approx_s": 3 / f_loop_bw,
        "vco_dans_plage": f_vco_min <= f_out <= f_vco_max,
    }

# Exemple : synthétiseur de fréquence, référence 10 MHz, N=100 → 1 GHz
pll = pll_parameters(100e6, 2e9, 10e6, 100)
print(f"Fréquence sortie PLL : {pll['f_sortie_Hz']/1e6:.0f} MHz")
print(f"Bande passante boucle : {pll['bande_passante_boucle_Hz']/1e3:.0f} kHz")
```

---

## Pièges Courants

1. **Réaction positive au lieu de négative dans un AOP :** Inverser les entrées (+) et (-) transforme un amplificateur en comparateur (ou oscillateur). Vérifier la boucle de contre-réaction : elle doit toujours relier la sortie à l'entrée (-).

2. **Découplage insuffisant des AOP haute vitesse :** Un AOP avec un gain de 100 MHz peut osciller si l'alimentation n'est pas découplée par 100 nF placé à moins de 5 mm de chaque pin d'alimentation.

3. **Saturation des amplificateurs différentiels :** Le mode commun dépasse la plage d'entrée de l'AOP. Vérifier la plage de tension d'entrée en mode commun (input common-mode range, ICMR) qui varie selon l'AOP (rail-to-rail ou non).

4. **Transistor MOSFET non saturé :** Un MOSFET de puissance commandé avec VGS insuffisant (< 10 V pour les MOSFET standard) fonctionne en zone linéaire et dissipe des puissances excessives. Utiliser un gate driver ou un MOSFET logic-level (Vth < 2,5 V).

5. **Capacité parasite Miller dans les étages BJT :** La capacité Cbc du transistor crée un effet Miller qui réduit la bande passante à gain élevé. Un étage commun avec gain ×50 peut voir sa bande passante divisée par 50.

6. **Inductance parasite des fils dans les alimentations DC-DC :** Les pics de courant rapides (di/dt > 1 A/µs) dans les boucles de commutation créent des surtensions destructrices. Minimiser la surface de la boucle de puissance (layout critique).

7. **Instabilité des régulateurs LDO avec certains condensateurs :** Certains LDO sont instables avec des condensateurs à faible ESR (MLCC céramique). Utiliser un condensateur avec ESR dans la plage spécifiée par la datasheet (souvent 0,1-1 Ω).

---

## Liste de vérification (Checklist)

- [ ] Les AOP ont une contre-réaction négative (sortie → entrée inverseuse).
- [ ] Les alimentations des AOP sont découplées (100 nF MLCC par chip + 10 µF par carte).
- [ ] Les transistors BJT sont polarisés dans la zone linéaire (VCE ≈ VCC/2).
- [ ] Les MOSFET de puissance ont un VGS suffisant pour la saturation complète.
- [ ] Les filtres actifs ont le bon facteur de qualité Q (Butterworth, Bessel, Chebyshev).
- [ ] Les convertisseurs DC-DC ont une inductance correctement dimensionnée (courant saturation > Ipeak).
- [ ] Les boucles de commutation DC-DC sont minimisées (layout critique).
- [ ] Les oscillateurs ont une condition de démarrage vérifiée (gain > 1 en petit signal).
- [ ] Les PLL ont un filtre de boucle dimensionné (fréquence de coupure = f_ref / 10).
- [ ] La puissance dissipée des composants est < 80 % de la valeur nominale.
- [ ] Les tensions maximales (VCE, VDS, VGS) ne sont pas dépassées.
- [ ] Les résistances de rappel (pull-up/pull-down) sont présentes sur les entrées des comparateurs.