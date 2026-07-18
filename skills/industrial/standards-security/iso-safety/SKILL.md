---
name: iso-safety
description: "Utiliser quand l'utilisateur demande d'écrire ou d'analyser des logiques de sécurité machine (Safety PLC) conformes aux normes ISO 13849-1 (Performance Level) et CEI 62061 (SIL)."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [safety, failsafe, iso-13849, iec-62061, plc, logic, industrial-automation]
    related_skills: [simplify-code, plan]
---

# Sécurité Fonctionnelle Industrielle (ISO 13849-1 & CEI 62061)

## Vue d'ensemble

La sécurité des personnes travaillant sur ou à proximité de machines industrielles est primordiale. Les normes **ISO 13849-1** (Performance Level : PL a à e) et **CEI 62061** (Safety Integrity Level : SIL 1 à 3) définissent les exigences de sécurité fonctionnelle applicables aux systèmes de commande relatifs à la sécurité.

Dans les automates de sécurité (Safety PLC/Failsafe), l'écriture du code de sécurité impose des structures spécifiques et des blocs fonctions standardisés pour éviter toute défaillance logicielle systématique.

Cette compétence guide l'agent Helios pour concevoir et programmer des logiques de sécurité machine (Safety).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De concevoir ou de programmer une logique d'arrêt d'urgence, de verrouillage de porte ou de radar de zone.
- D'implémenter la détection de discordance (Discrepancy) sur des entrées double canal.
- De programmer des séquences de contournement temporaire sécurisé (*Muting*) pour des barrières photoélectriques.
- De gérer la validation ou l'acquittement de défauts de sécurité.

**Ne pas utiliser pour :**
- Du contrôle-commande de procédé standard non-Safety (ex: régulation de température).

---

## 1. Surveillance de Discordance Temporelle (Double Canal)

Pour atteindre les niveaux de sécurité élevés (PL d/e ou SIL 2/3), les capteurs de sécurité (ex. bouton arrêt d'urgence, interrupteur de porte) sont câblés en double canal (deux contacts séparés). L'automate doit vérifier que les deux contacts changent d'état presque simultanément. Si un seul contact s'ouvre, l'automate doit détecter un défaut de discordance.

### Exemple de logique de surveillance de discordance double canal en SCL standard (simulé) :

```scl
FUNCTION_BLOCK "FB_Actemium_DiscrepancyCheck"
   VAR_INPUT
      i_Channel_A : Bool;       // Contact physique 1 (ex. Normalement Fermé)
      i_Channel_B : Bool;       // Contact physique 2 (ex. Normalement Fermé)
      i_DiscrepancyTime : Time; // Temps max de décalage autorisé (ex: 500ms)
   END_VAR

   VAR_OUTPUT
      q_SafetyOut : Bool;       // Sortie de sécurité validée
      q_DiscrepancyFault : Bool;// Défaut de discordance détecté
   END_VAR

   VAR
      stat_Timer : TON_TIME;
   END_VAR

BEGIN
   // Si les deux canaux sont dans des états différents, on démarre le timer
   #stat_Timer(IN := (#i_Channel_A <> #i_Channel_B),
               PT := #i_DiscrepancyTime);
               
   // Si le temps de discordance est dépassé, on lève un défaut
   IF #stat_Timer.Q THEN
       #q_DiscrepancyFault := TRUE;
   END_IF;
   
   // Réinitialisation du défaut si les canaux redeviennent cohérents à 0 (sécurité)
   IF NOT #i_Channel_A AND NOT #i_Channel_B THEN
       #q_DiscrepancyFault := FALSE;
   END_IF;
   
   // La sortie de sécurité est active uniquement si les deux canaux sont fermés (True) et pas de défaut
   #q_SafetyOut := #i_Channel_A AND #i_Channel_B AND NOT #q_DiscrepancyFault;
END_FUNCTION_BLOCK
```

---

## 2. Logique de Muting de Barrière Immatérielle

Le *Muting* consiste à suspendre temporairement la fonction de sécurité d'une barrière immatérielle (ex. pour laisser passer une palette de produits) tout en empêchant le passage d'un opérateur humain. Cela nécessite des capteurs physiques de détection de palette (Muting Sensors) disposés en amont et en aval de la barrière.

### Règles de programmation du Muting :
* **Séquence temporelle stricte :** Les capteurs de muting (ex. capteurs photoélectriques croisés en X ou parallèles) doivent être activés dans un ordre et un délai précis (généralement moins de 3 à 4 secondes d'intervalle).
* **Limite de temps maximale (Timeout) :** Le muting ne doit jamais rester actif indéfiniment. Une temporisation maximale de sécurité (ex. 60 secondes) doit désactiver le muting et déclencher l'arrêt de sécurité si la palette reste bloquée sous la barrière.

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Acquittement automatique d'un défaut de sécurité :**
   * *Erreur :* Réarmer automatiquement une zone de sécurité (ex. relancer des moteurs) dès qu'une porte de protection est refermée, sans nécessiter d'action volontaire de l'opérateur. C'est extrêmement dangereux en cas de présence humaine dans l'enceinte de la machine.
   * *Correction :* Exiger systématiquement un signal de réarmement manuel (bouton physique d'acquittement) détecté sur front montant, situé en dehors de la zone dangereuse avec visibilité complète sur la machine.

2. **Utilisation de variables standards pour piloter de la sécurité :**
   * *Erreur :* Utiliser une variable provenant d'un écran tactile IHM standard (liaison Ethernet non-Safety) pour forcer ou shunter directement un signal de sécurité automate.
   * *Correction :* Les commandes IHM ne doivent jamais remplacer les sécurités câblées physiques ou les réseaux Failsafe (ProfiSafe, CIP Safety). Elles ne peuvent servir qu'à l'acquittement ou au diagnostic.

---

## Liste de vérification (Checklist)

- [ ] Les entrées double canal sont associées à une détection de discordance temporelle paramétrée (ex: 500ms maximum).
- [ ] Le réarmement de la sécurité s'effectue sur un front montant (`R_TRIG`) d'un bouton physique externe et jamais de manière automatique.
- [ ] Les fonctions de muting incluent un chien de garde (Timeout) pour forcer le retour à l'état de sécurité si l'activation se prolonge.
- [ ] Aucune variable issue d'une communication standard (non-Failsafe) n'est utilisée pour outrepasser directement une logique d'arrêt de sécurité.

