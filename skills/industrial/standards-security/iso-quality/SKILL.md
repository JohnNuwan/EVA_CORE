---
name: iso-quality
description: "Appliquer les processus de gestion de versions du code automate, de gestion du changement en environnement OT (OT Change Management), et documenter les essais qualité (FAT/SAT) conformes à l'ISO 9001 pour les projets d'automatisation industrielle."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [quality, iso-9001, change-management, versioning, octoplant, fat, sat, testing, industrial-automation, plc-versioning, git-lfs, cmms]
    related_skills: [simplify-code, plan, industrial-maintenance-reliability]
    difficulty: intermediate
    industry_sectors: [manufacturing, automotive, chemical, pharmaceutical, energy, aerospace, process-industries]
---

# Gestion du Changement & Qualité OT (ISO 9001 & FAT/SAT)

## Vue d'ensemble

Le développement de logiciels d'automatisation (PLC, IHM, SCADA, variateurs) pour l'industrie s'inscrit dans des exigences de management de la qualité régies par la norme **ISO 9001** (version actuelle : ISO 9001:2015). Contrairement aux projets informatiques classiques (IT) disposant d'outils de versionnement natifs (Git, SVN), le monde de l'informatique industrielle (OT) manipule beaucoup de fichiers binaires propriétaires compilés et des interventions directes en ligne sur les installations en production.

### Contexte : La Qualité Logicielle dans l'Industrie

Un défaut dans un logiciel d'automatisme peut avoir des conséquences bien plus graves qu'un bug informatique classique :
- **Sécurité des personnes** : Mouvement inattendu d'un robot, arrêt de sécurité défaillant.
- **Sûreté de fonctionnement** : Emballement thermique d'un réacteur chimique.
- **Production** : Arrêt de ligne non planifié coûtant des milliers d'euros par heure.
- **Qualité produit** : Lot de fabrication non conforme (rebut de matière première).

La qualité logicielle en OT repose sur trois exigences fondamentales :

1. **La gestion de versions stricte** : Savoir exactement qui a modifié quoi, quand, pourquoi, et conserver des sauvegardes fonctionnelles historiques de toutes les versions.
2. **Le cycle de test formel** : Réaliser des essais en plateforme de simulation (**FAT** — Factory Acceptance Test) puis des essais de mise en service sur site (**SAT** — Site Acceptance Test ou **CAT** — Commissioning Acceptance Test).
3. **Le suivi du changement (OT Change Management)** : Documenter chaque modification post-mise en service pour éviter les dérives et garantir que les modifications sont validées, testées, approuvées et documentées.

Cette compétence guide l'agent Helios pour structurer, documenter et tester ses développements industriels conformément à ces exigences qualité.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :

- De formaliser une **procédure ou un tableau de suivi de tests FAT ou SAT** (modèle de protocole d'essais).
- De rédiger un **document de suivi de modifications (Change Log)** pour un programme automate, une IHM ou un SCADA.
- De définir une **stratégie de structuration Git ou de versionnement** de projets d'automatisation (ex : TIA Portal, Studio 5000, EcoStruxure Control Expert, Codesys).
- De documenter des **non-conformités** ou des **fiches de réserves** de fin de chantier.
- De mettre en place une **procédure d'intervention en ligne** sur automate en production.
- De structurer un **plan qualité projet (PQP)** pour un projet d'automatisme.

**Ne pas utiliser pour :**
- Réaliser du test unitaire de code logiciel pur hors process industriel (utiliser `test-driven-development`).
- Les aspects spécifiques de la cybersécurité des programmes (utiliser `cybersecurity-iec62443`).

## 1. Stratégie de Versionnement du Code Automate (OT)

### Défis du Versionnement en Automatisme

| Défi | Explication | Solution |
|:---|---|:---|
| **Fichiers binaires** | Les IDE industriels stockent les projets sous forme de fichiers binaires volumineux (ex : `.ap16` pour TIA Portal, `.acd` pour Studio 5000, `.smc` pour EcoStruxure). | Git LFS (Large File Storage) ou outil spécialisé (Octoplant, Versiondog) |
| **Pas de diff textuel natif** | Impossible de faire un `git diff` sur un fichier binaire pour voir les modifications. | Exporter le code textuel (SCL, ST, LADDER XML) pour les fichiers modifiés |
| **Multi-IDE** | Le même projet peut utiliser TIA Portal, Step 7, WinCC, Codesys, etc. | Standardiser par ligne de produits |
| **Interventions en ligne** | Les techniciens modifient directement le programme sur l'automate sans repasser par l'IDE. | Règle : "Toute modification en ligne doit être suivie d'un upload et d'un commit" |

### Structure d'Archivage Recommandée

```
projet_automate/
├── 01_CDC/                   # Cahier des charges / Spécifications fonctionnelles
│   ├── CDC_LIGNE1_v1.2.pdf
│   └── IOMapping_LIGNE1.xlsx
├── 02_SOURCES/               # Projets natifs des IDE
│   ├── TIA_Portal_V17/       # Projet TIA Portal complet
│   ├── WinCC_Unified/        # Projet IHM
│   └── SCL_Exports/          # Export textuel des blocs SCL
├── 03_CONFIGURE/             # Fichiers de configuration matérielle
│   ├── Switches_config/
│   └── Drive_config/
├── 04_BACKUPS/               # Sauvegardes (upload) des automates en production
│   ├── 2026-01-15_Avant_modif_S100/
│   └── 2026-03-20_Apres_modif_S100/
├── 05_TESTS/                 # Protocoles et résultats de tests
│   ├── FAT_Protocol_v1.0.pdf
│   ├── FAT_Results_v1.0.xlsx
│   └── SAT_Protocol_v1.0.pdf
└── 06_DOCS/                  # Documentation technique
    ├── Schémas_electriques/
    ├── Plan_cablage/
    └── Manuel_operateur.pdf
```

### Formatage des Messages de Commit

```text
[PROJET] [EQUIPEMENT] [ACTION] Description claire

Exemples :
[A1-L1] [FB_ControlMotor] [MODIF] Ajout sécurité surchauffe sur i_FaultTemp (DM #104)
[USINE-B] [SCADA_Supervision] [CORR] Correction affichage température réacteur R-201 (Bug #87)
[PHARMA-3] [S7300-L3] [INIT] Version initiale du programme automates
```

Où :
- `[PROJET]` : Identifiant du projet ou de l'affaire.
- `[EQUIPEMENT]` : Nom du module, FB, écran, équipement modifié.
- `[ACTION]` : Type de changement (MODIF, CORR, INIT, AJOUT, SUPPR).
- `DM #xxx` : Référence à la Demande de Modification associée.

## 2. Structure d'un Protocole de Validation d'Essais (FAT / SAT)

### Définition FAT vs SAT

| Type | Nom | Lieu | Objectif | Participants |
|:---|:---|:---|:---|---|
| **FAT** | Factory Acceptance Test | Chez l'intégrateur / bureau d'études | Valider le fonctionnement du programme sur simulateur ou platine test | Ingénieur automaticien + client |
| **SAT** | Site Acceptance Test | Sur site, à l'usine du client | Valider le fonctionnement sur l'équipement réel, en conditions réelles | Client + automaticien |
| **CAT** | Commissioning Acceptance Test | Sur site, en production | Valider le fonctionnement en production réelle (matière, cadence) | Client + équipe projet |

### Modèle de Protocole d'Essais

```markdown
### Protocole d'Essais : Commande et Sécurité Moteur 1 (M_01)

Projet : [NOM PROJET]
Équipement : [NOM ÉQUIPEMENT]
Réf document : FAT-001
Version : 1.0
Date : JJ/MM/AAAA

| Réf. Test | Description de l'Action | Résultat Attendu (Spécification) | Résultat Observé | Statut (OK / KO / NA) | Validé par |
|:---|:---|:---|:---|:---:|:---:|
| **TEST-01** | Appui sur bouton physique `i_Start` | Le moteur `q_Run` démarre, l'indicateur IHM passe au vert. | Conforme. | **OK** | J. Dupont |
| **TEST-02** | Déclenchement du défaut thermique `i_Fault` | Le moteur `q_Run` s'arrête immédiatement. Alarme "Défaut Thermique M_01" active sur IHM. | Conforme. | **OK** | J. Dupont |
| **TEST-03** | Appui sur `i_Start` alors que `i_Fault` est actif | Le moteur ne démarre pas. | Conforme. | **OK** | J. Dupont |
| **TEST-04** | Appui sur bouton `i_Stop` pendant que le moteur tourne | Le moteur s'arrête. | Conforme. | **OK** | J. Dupont |
| **TEST-05** | Simulation : perte de communication automate/IHM | Alarme "Perte Communication IHM" sur superviseur SCADA. Conservatisme : Moteur reste dans son dernier état. | Alarme OK, moteur reste en état. | **OK** | J. Dupont |
| **TEST-06** | Test de temps de cycle maximum | Le temps de cycle automate ne dépasse pas 50 ms. | Max mesuré : 42 ms. | **OK** | J. Dupont |
```

### Règles d'Or du Test FAT/SAT

1. **Tester TOUT** : Chaque entrée, chaque sortie, chaque fonction, chaque alarme. Si ce n'est pas testé, c'est potentiellement défaillant.
2. **Tester le normal ET l'anormal** : Tester le fonctionnement normal (démarrage, arrêt) ET les scénarios de défaillance (perte de signal, panne capteur, perte communication).
3. **Tester les limites** : Tester les seuils bas et hauts (température minimale, pression maximale, temps de cycle maximum).
4. **Documenter les réserves** : Si un test échoue, documenter la réserve (non-conformité) avec un plan d'action de correction. Aucun test KO ne doit être oublié.

## 3. Gestion du Changement en Production (OT Change Management)

### Procédure Standard de Modification en Production

```text
1. IDENTIFICATION DU BESOIN :
   → Émetteur (maintenance, production, qualité) remplit une Demande de Modification (DM).
   → La DM documente : quoi, pourquoi, urgence, équipement concerné.

2. ÉVALUATION D'IMPACT :
   → Analyse des risques de la modification (impact sur la sécurité, la production, la qualité).
   → Évaluation du besoin d'arrêt machine.

3. APPROBATION PRÉALABLE :
   → Signature obligatoire : responsable maintenance + responsable production.
   → DM approuvée → autorisation d'intervention.

4. SAUVEGARDE PRÉ-INTERVENTION :
   → Upload complet de l'état actuel de l'automate (sauvegarde horodatée).
   → Copie (snapshot) du projet source en l'état.

5. RÉALISATION DE LA MODIFICATION :
   → Intervention programmée (fenêtre de maintenance planifiée).
   → Suivi de la modification en direct (enregistrement écran ou log des changements).

6. TEST ET VALIDATION :
   → Exécution des tests de non-régression (minimum les tests essentiels).
   → Validation fonctionnelle par le demandeur.

7. SAUVEGARDE POST-INTERVENTION :
   → Upload final de l'automate modifié.
   → Mise à jour du projet source (download → upload → commit).

8. MISE À JOUR DE LA DOCUMENTATION :
   → Mise à jour des schémas électriques (borniers I/O modifiés).
   → Mise à jour du manuel opérateur (si écran IHM modifié).
```

## Pièges Courants (Common Pitfalls)

1. **Interventions directes en ligne sans sauvegarde locale préalable :**
   - *Erreur :* Se connecter en ligne sur l'automate physique en production, faire des modifications de logique "à chaud" (online edit) sans enregistrer de copie locale du code stable actuel. En cas de dysfonctionnement, aucun retour en arrière facile n'est possible (sauf si la fonctionnalité "undo" de l'IDE est encore disponible, ce qui n'est pas garanti).
   - *Correction :* Toujours réaliser une sauvegarde ("Upload") de l'état actuel de l'automate en fonctionnement avant toute modification en ligne. Horodater et archiver cette sauvegarde.

2. **Absence de mise à jour des plans électriques après modification :**
   - *Erreur :* Modifier des affectations de borniers d'entrées/sorties (I/O) dans le programme automate suite à un problème matériel (ex : carte E/S défaillante, on reconnecte sur une autre carte), sans mettre à jour les documents de schéma électrique de l'armoire. Les générations futures d'intervenants ne retrouveront pas le câblage.
   - *Correction :* Inclure dans la procédure de changement une étape obligatoire : "Mise à jour des schémas électriques". Générer une Demande de Modification (DM) spécifique pour le bureau d'études si nécessaire.

3. **Protocoles FAT/SAT rédigés en aval du développement :**
   - *Erreur :* Rédiger les protocoles de tests FAT après avoir développé le programme, en adaptant les tests à ce qui a été réellement implémenté plutôt qu'au cahier des charges initial. Les oublis fonctionnels ne sont pas détectés.
   - *Correction :* Rédiger les protocoles de tests **avant** le développement, sur la base du cahier des charges fonctionnel. Le FAT valide que le programme répond au CDC, pas l'inverse.

4. **Absence de versionning pour les binaires :**
   - *Erreur :* Stocker les projets TIA Portal / Studio 5000 sur un partage réseau Windows sans système de versionnement. Impossible de savoir qui a modifié quoi, ni de revenir à une version antérieure stable après une modification problématique.
   - *Correction :* Mettre en place un système de gestion de versions adapté aux binaires : Octoplant / Versiondog (recommandé pour les environnements multi-fournisseurs) ou Git LFS pour les équipes techniques.

## Références

- **ISO 9001:2015** : Systèmes de management de la qualité — Exigences.
- **ISO 10007** : Management de la configuration — Lignes directrices.
- **IATF 16949** : Standard qualité pour l'industrie automobile (basé sur ISO 9001).
- **GAMP 5** (ISPE) : Guide de validation des systèmes automatisés pour l'industrie pharmaceutique.
- **IEC 61131-3** : Norme de programmation des automates (définit les langages SCL, ST, LADDER, FBD, SFC).
- **IEC 61508** : Sécurité fonctionnelle des systèmes électriques/électroniques/électroniques programmables.

## Liste de vérification (Checklist)

- [ ] Un **archivage de sauvegarde ("Backup" / Upload)** de l'automate a été réalisé et horodaté avant le début des modifications en ligne.
- [ ] Les **messages de commit** ou lignes d'historique de modifications référencent le numéro de Demande de Modification (DM) et décrivent la modification fonctionnelle.
- [ ] Les **protocoles de tests FAT/SAT** définissent clairement l'action de test, la réaction attendue, le critère de validation et l'espace pour le résultat observé.
- [ ] Les **changements d'adresses d'entrées/sorties** (I/O) automates sont consignés et transmis au bureau d'études pour mise à jour des schémas de câblage armoire.
- [ ] Une **procédure d'intervention en ligne** écrite est disponible et connue des techniciens (upload → modification → test → upload → documentation).
- [ ] Les **non-conformités et réserves** issues des FAT/SAT font l'objet d'un plan d'action écrit avec responsable, échéance et suivi.
- [ ] Le **projet source** (IDE) et la **sauvegarde automate** (fichier uploadé) sont systématiquement synchronisés après chaque modification.
- [ ] La **documentation technique** (schémas électriques, plan de câblage, I/O mapping) est mise à jour après chaque modification.
- [ ] Les **comptes rendus de tests** sont signés par les parties prenantes (intégrateur, client, qualité) et archivés.
- [ ] Le **plan qualité projet (PQP)** inclut les jalons de validation (FAT, SAT, CAT) avec les critères de passage.

