---
name: robot-plc-standard-interface
description: "Standardiser l'interface robot ↔ PLC pour signaux, états, défauts, sécurité et séquence de cycle."
version: 1.1.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [robotics, plc, interface, handshake, safety, standard]
    related_skills: [robotics-abb, robotics-fanuc, robotics-kuka, robotics-staubli, industrial-protocols]
---

# Interface standard robot ↔ PLC

## Vue d'ensemble

Cette compétence définit un contrat standard entre le robot et l'automate : commandes, états, défauts, sécurité, mode auto/manu, acquittements et séquence de cycle. Le but est d'obtenir une interface multi-marques stable, audit-able et réutilisable sans dépendre de la seule logique constructeur.

## Quand l'utiliser

À utiliser pour :
- standardiser un handshake robot ↔ PLC ;
- concevoir une interface réutilisable pour plusieurs marques robots ;
- formaliser les modes, permissifs, défauts et resets ;
- préparer un contrat pour supervision, maintenance ou intégration MES.

Ne pas utiliser pour :
- une simple cellule mono-robot sans objectif de standardisation ;
- une logique purement sécurité sans handshake process ;
- une description robot interne ne sortant jamais vers le PLC.

## Contrat minimal recommandé

### Commandes PLC vers robot
- Cmd.StartCycle
- Cmd.StopCycle
- Cmd.ResetFault
- Cmd.Home
- Cmd.AutoEnable
- Cmd.ManualEnable

### États robot vers PLC
- Sts.Ready
- Sts.Busy
- Sts.CycleDone
- Sts.AtHome
- Sts.Fault
- Sts.InAuto
- Sts.InManual

### Sécurité
- Safe.RobotSafe
- Safe.FenceClosed
- Safe.EStopOk
- Safe.ResetRequired

## Séquence standard

1. PLC valide sécurité et permissifs.
2. PLC donne autorisation Auto.
3. Robot publie Ready.
4. PLC envoie StartCycle.
5. Robot passe Busy.
6. Robot publie CycleDone en fin de séquence.
7. PLC réinitialise la commande et enregistre le résultat.

## Livrables attendus

- table Cmd / Sts / Safe ;
- séquence nominale et séquences dégradées ;
- matrice défauts / resets / acquittements ;
- règles de mapping multi-marques ;
- check-list FAT/SAT interface robot.

## Support files

- `templates/robot-plc-handshake-template.md` : contrat type.
- `templates/robot-fault-matrix.md` : gestion des défauts.
- `references/expert-pack.md` : points d'attention multi-marques.

## Bonnes pratiques

- Séparer strictement défaut robot, défaut process et défaut sécurité.
- Centraliser l'acquittement défaut.
- Exposer clairement les modes Auto / Manual / Teach.
- Garder un mapping identique quelle que soit la marque robot.
- Conserver les responsabilités temps réel côté automate et le détail cinématique côté robot.

## Pièges Courants (Common Pitfalls)

1. Fusionner Busy et Ready dans un seul bit ambigu.
2. Utiliser des signaux sécurité comme simples états process.
3. Ne pas documenter la transition CycleDone → acquittement PLC.
4. Laisser varier la sémantique des bits entre constructeurs.

## Liste de vérification (Checklist)

- [ ] Les signaux Cmd / Sts / Safe sont séparés.
- [ ] La séquence nominale est documentée.
- [ ] Les défauts et resets sont clairement définis.
- [ ] Les modes Auto / Manual / Teach sont explicités.
- [ ] Le contrat reste maintenable pour plusieurs marques robots.
