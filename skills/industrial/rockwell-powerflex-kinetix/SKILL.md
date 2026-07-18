---
name: rockwell-powerflex-kinetix
description: "Configurer les variateurs PowerFlex et servo Kinetix dans les architectures motion Rockwell."
version: 1.1.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [rockwell, powerflex, kinetix, motion, drive, cip-motion, servo]
    related_skills: [drive-motion-control, rockwell-studio5000, rockwell-guardlogix]
---

# Rockwell PowerFlex & Kinetix

## Vue d'ensemble

Cette compétence couvre les architectures motion Rockwell basées sur PowerFlex et Kinetix. Elle aide à structurer drives, axes, diagnostics, profils de mouvement et interactions avec la logique Logix, le réseau EtherNet/IP et la safety GuardLogix.

## Quand l'utiliser

À utiliser pour :
- distinguer correctement drive standard et servo positionné ;
- structurer un contrat motion CIP Motion ;
- définir homing, défauts, permissifs et reprise défaut ;
- formaliser le lien motion ↔ safety ↔ séquence machine.

Ne pas utiliser pour :
- un simple besoin Studio 5000 sans dimension drive/servo ;
- une architecture purement sécurité sans pilotage d'axes ;
- un réglage ponctuel ne nécessitant pas de standardisation.

## Axes de structuration

1. Séparer clairement PowerFlex, Kinetix et logique machine.
2. Définir les états drive/axe : inhibited, ready, moving, stopped, fault.
3. Normaliser les défauts, acquittements et conditions de réarmement.
4. Identifier le comportement après coupure, E-stop, reset et retour en auto.
5. Rendre le diagnostic lisible pour production et maintenance.

## Livrables attendus

- matrice drives/axes/réseau ;
- modèle de signaux motion et défauts ;
- stratégie de homing et de safe restart ;
- règles de couplage avec GuardLogix ;
- scénarios FAT/SAT motion.

## Support files

- `templates/drive-axis-template.md` : gabarit de description axe/drive.
- `references/expert-pack.md` : points d'attention détaillés PowerFlex/Kinetix.
- `references/version-validation-matrix.md` : matrice de validation rapide.

## Pièges Courants (Common Pitfalls)

1. Mélanger pilotage vitesse simple et positionnement servo dans la même logique.
2. Définir une reprise défaut ambiguë ou non testée.
3. Masquer les diagnostics drive derrière des états machine trop synthétiques.
4. Ne pas documenter l'effet safety sur le profil de redémarrage.

## Liste de vérification (Checklist)

- [ ] Drives et axes sont séparés logiquement.
- [ ] Les diagnostics motion sont centralisés et lisibles.
- [ ] Le comportement après défaut ou arrêt sécurité est défini.
- [ ] Les dépendances réseau EtherNet/IP sont prises en compte.
- [ ] L'intégration GuardLogix est documentée.
