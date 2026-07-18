---
name: matlab-simulink-industrial
description: "Concevoir et réguler des systèmes sous MATLAB et Simulink."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, windows]
metadata:
  tags: [matlab, simulink, control-theory, pid, mpc, physical-modeling, plc-coder, code-generation]
  related_skills: [iec61131-3-programming-standards, c-cpp-industrial-embedded]
---

# Modélisation MATLAB / Simulink et Génération de Code pour la Régulation Industrielle

Cette compétence encadre l'utilisation de MATLAB et Simulink pour modéliser des systèmes physiques industriels, calculer et régler des régulateurs (PID, MPC), simuler des asservissements et générer automatiquement du code automate (Structured Text / C++) via *Simulink PLC Coder*.

---

## 1. Discrétisation de Modèles Physiques Continus

Un modèle physique continu modélisé dans MATLAB par sa fonction de transfert $G(s)$ ou son espace d'état doit être discrétisé en $G(z)$ pour être implanté dans un processeur d'automate exécuté à pas de temps fixe $T_s$.

### Méthodes de Discrétisation principales
* **ZOH (Zero-Order Hold)** : Bloqueur d'ordre zéro. Méthode par défaut pour la modélisation d'entrées physiques de cartes analogiques.
* **Tustin (Bilinéaire)** : Préserve la réponse en fréquence et cartographie de manière stable le demi-plan gauche du plan $s$ dans le cercle unité du plan $z$. La relation est définie par :
  $$s \approx \frac{2}{T_s} \frac{z - 1}{z + 1}$$
* **Euler (Différences finies arrière)** : Très utilisée en programmation directe sur PLC en raison de sa simplicité de formulation :
  $$s \approx \frac{z - 1}{z \cdot T_s}$$

### Script MATLAB de Discrétisation et de calcul de marge
```matlab
% Parametres du systeme continu (Premier Ordre avec Retard)
K = 2.0;       % Gain statique
tau = 8.5;     % Constante de temps (secondes)
theta = 2.0;   % Retard pur (secondes)

s = tf('s');
G_continu = (K / (tau * s + 1)) * exp(-theta * s);

% Pas d'execution automate = 50ms (0.05 seconde)
Ts = 0.05;

% Discretisation par methode Tustin avec pre-distorsion de frequence
G_discret = c2d(G_continu, Ts, 'tustin');

% Affichage de l'equation de recurrence discrete dans la console
disp('Fonction de transfert discrete G(z) :');
tf(G_discret)
```

---

## 2. Synthèse et Calcul d'un Régulateur PI dans le Domaine Fréquentiel

Pour garantir la stabilité d'une régulation en boucle fermée face aux perturbations de charge, la marge de phase (Phase Margin - $P_m$) doit être typiquement supérieure à 45° (cible idéale à 60°).

### Script MATLAB de calcul analytique d'un correcteur PI
```matlab
% Parametres de performance cibles
omega_c = 0.4; % Frequence de coupure desiree en boucle ouverte (rad/s)
Pm_cible = 60; % Marge de phase visee (degres)

% Calcul de la reponse en frequence du procede G_continu a la frequence omega_c
[mag, phase] = bode(G_continu, omega_c);
phase_deg = squeeze(phase);
mag_val = squeeze(mag);

% Calcul de la phase requise pour le correcteur PI :
% Pm = 180 + phase_systeme + phase_correcteur
% phase_correcteur = Pm - 180 - phase_systeme
phase_C = Pm_cible - 180 - phase_deg;

% L'equation du correcteur PI est C(s) = Kp * (1 + 1 / (Ti * s))
% A la frequence de coupure, la phase de C(s) est atan(1 / (Ti * omega_c)) - 90 (si exprimee sous forme non standard)
% En representation standard : phase_C = atan(-1 / (Ti * omega_c))
Ti = -1 / (omega_c * tan(degtorad(phase_C)));

% Calcul du gain proportionnel Kp pour forcer le gain de boucle a 0 dB (1.0) a omega_c
% |C(jw) * G(jw)| = 1 ==> Kp * sqrt(1 + 1/(Ti*omega_c)^2) * mag_val = 1
Kp = 1 / (mag_val * sqrt(1 + (1 / (Ti * omega_c)^2)));

disp(['Kp calcule : ', num2str(Kp)]);
disp(['Ti calcule (secondes) : ', num2str(Ti)]);
```

---

## 3. Implémentation ST Robuste d'un Régulateur PID Discret avec Anti-Windup Clamping

Lors de la saturation de la commande physique (ex: vanne ouverte à 100%), l'intégrateur continue d'accumuler l'erreur, ce qui provoque un dépassement massif lors du retour à la normale (phénomène de *windup*). L'algorithme ST ci-dessous intègre un anti-windup par **clamping** (blocage de l'intégration si la commande sature et que l'erreur aggrave la saturation).

```pascal
FUNCTION_BLOCK FB_EVA_PID_Precision
VAR_INPUT
    SetPoint : REAL;   (* Consigne physique *)
    ProcessVal : REAL; (* Mesure capteur *)
    ManualMode : BOOL; (* Mode manuel force *)
    ManualCmd : REAL;  (* Commande manuelle forcee *)
    Reset : BOOL;      (* Reinitialisation complete *)
END_VAR
VAR_OUTPUT
    OutputCmd : REAL;  (* Commande de sortie 0-100% *)
    Saturated : BOOL;  (* Indicateur de saturation active *)
END_VAR
VAR
    (* Parametres de reglage *)
    Kp : REAL := 2.5;
    Ki : REAL := 0.15;
    Kd : REAL := 0.45;
    Ts : REAL := 0.05;  (* Periode d'echantillonnage 50ms *)
    N_Filter : REAL := 10.0; (* Coefficient de filtrage de la derivee (D-action filter) *)
    
    (* Variables d'etat internes *)
    I_State : REAL := 0.0;  (* Etat de l'integrateur *)
    D_State : REAL := 0.0;  (* Etat du filtre de derivee *)
    Prev_Error : REAL := 0.0;
END_VAR
VAR_TEMP
    Err : REAL;
    P_Term : REAL;
    D_Term : REAL;
    RawCmd : REAL;
    Clamp_Int : BOOL;
END_VAR

    IF Reset THEN
        I_State := 0.0;
        D_State := 0.0;
        OutputCmd := 0.0;
        Prev_Error := 0.0;
        Saturated := FALSE;
        RETURN;
    END_IF;

    IF ManualMode THEN
        OutputCmd := ManualCmd;
        I_State := ManualCmd - (Kp * (SetPoint - ProcessVal)); (* Pre-chargement de l'integrateur pour transition douce *)
        Saturated := FALSE;
        RETURN;
    END_IF;

    Err := SetPoint - ProcessVal;
    
    (* 1. Calcul du terme Proportionnel *)
    P_Term := Kp * Err;
    
    (* 2. Calcul du terme Derive avec filtre passe-bas passe-haut combine *)
    (* Formule discrete : D_State(k) = (D_State(k-1)*Td + Kd*N*(Err - Prev_Err)) / (Td + N*Ts) *)
    D_Term := (Kd * N_Filter * (Err - Prev_Error) + D_State) / (1.0 + N_Filter * Ts);
    D_State := D_Term;

    (* 3. Sommation temporaire de la commande *)
    RawCmd := P_Term + I_State + D_Term;
    
    (* 4. Detection de la saturation physique *)
    IF (RawCmd > 100.0) OR (RawCmd < 0.0) THEN
        Saturated := TRUE;
        IF RawCmd > 100.0 THEN
            OutputCmd := 100.0;
        ELSE
            OutputCmd := 0.0;
        END_IF;
    ELSE
        Saturated := FALSE;
        OutputCmd := RawCmd;
    END_IF;

    (* 5. Anti-Windup Clamping Logic *)
    (* On bloque l'integration uniquement si :
       a. La commande est saturee.
       b. Le signe de l'erreur est identique au signe de la saturation (l'erreur aggrave la saturation). *)
    Clamp_Int := FALSE;
    IF Saturated THEN
        IF (Err > 0.0 AND RawCmd > 100.0) OR (Err < 0.0 AND RawCmd < 0.0) THEN
            Clamp_Int := TRUE;
        END_IF;
    END_IF;

    (* 6. Mise a jour de l'integrateur si non bloque *)
    IF NOT Clamp_Int THEN
        I_State := I_State + (Ki * Err * Ts);
    END_IF;

    Prev_Error := Err;
END_FUNCTION_BLOCK
```
