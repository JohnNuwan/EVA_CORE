---
name: mitsubishi-gx-works3
description: "Programmer les automates Mitsubishi MELSEC avec MELSOFT GX Works3 et motion intégré."
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [mitsubishi, melsec, gx-works3, iq-r, iq-f, mx-controller, motion, fa]
    related_skills: [drive-motion-control, industrial-protocols, plc-converter, industrial-communication-protocols]
---

# Mitsubishi MELSEC & GX Works3

## Vue d'ensemble

Cette compétence couvre MELSOFT GX Works3 comme environnement moderne pour les automates Mitsubishi MELSEC, en particulier les familles iQ-R et iQ-F. Elle aide à structurer les projets, organiser le cycle design/programming/debug/maintenance, intégrer le motion et rendre les applications compréhensibles pour les équipes de mise en service et de maintenance.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Programmer un automate Mitsubishi sous GX Works3.
- Structurer un projet MELSEC iQ-R ou iQ-F.
- Intégrer de la logique motion dans un projet Mitsubishi.
- Comparer ou migrer entre GX Works2 et GX Works3.
- Préparer une couche d'échange propre avec la supervision.

## Architecture recommandée

- Logique machine par zone/fonction.
- Bibliothèque standard moteurs, vannes, convoyeurs.
- Couche paramètres et recettes.
- Couche alarmes/diagnostic.
- Couche motion si axes présents.
- Couche échange SCADA/Historian.

## Bonnes pratiques

- Garder une structure lisible pour les mainteneurs.
- Séparer logique process, diagnostic et supervision.
- Standardiser les blocs et noms de variables.
- Traiter debug et maintenance dès la conception.

## Cas d'usage typiques

- Machines compactes à moyennes.
- Lignes d'assemblage.
- Convoyage et manutention.
- Séquences avec axes simples à moyens.

## Pièges Courants (Common Pitfalls)

1. Projet compréhensible uniquement par le développeur d'origine.
2. Motion insuffisamment découplé de la séquence machine.
3. Migration GX Works2/GX Works3 non revalidée.
4. Exposition SCADA non maîtrisée.

## Liste de vérification (Checklist)

- [ ] Le projet GX Works3 est structuré par fonctions claires.
- [ ] Les états machine critiques sont visibles pour debug et maintenance.
- [ ] La couche motion est séparée de la logique process globale.
- [ ] Les blocs récurrents sont standardisés.
- [ ] La couche d'échange supervision est stable et documentée.
- [ ] Les aspects debug et maintenance sont pensés dès la conception.
