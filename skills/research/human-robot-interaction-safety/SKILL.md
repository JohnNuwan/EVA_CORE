---
name: human-robot-interaction-safety
description: "Compétence en recherche en interaction homme-robot et sécurité robotique suivie sur arXiv sous cs.RO, cs.HC et domaines connexes. Couvre la sécurité des robots, la collaboration homme-robot, la cobotique, l'éthique robotique, la navigation sociale, la perception sociale, la confiance homme-robot, et les normes de sécurité."
category: research
arxiv_categories:
  - cs.RO
  - cs.HC
  - cs.AI
  - cs.MA
  - cs.CY
---

# Compétence : Interaction Homme-Robot et Sécurité Robotique

## Présentation

Cette compétence couvre la recherche en interaction homme-robot (HRI) et sécurité robotique : sécurité fonctionnelle, collaboration homme-robot (cobotique), éthique robotique, navigation sociale, perception sociale, confiance homme-robot, et normes de sécurité. Suivi principal sur arXiv sous **cs.RO** (Robotics) et **cs.HC** (Human-Computer Interaction).

---

## 1. Sécurité et Fiabilité Robotique

### Sécurité fonctionnelle
- Normes ISO : ISO 10218 (robots industriels), ISO/TS 15066 (cobots)
- **IEC 61508** : sécurité fonctionnelle des systèmes électriques/électroniques
- SIL (Safety Integrity Level) et PL (Performance Level)
- Analyse des risques : FMEA, FTA, HAZOP

### Détection de collisions
- Détection par couple (torque sensing)
- Détection par vision/caméras
- Peaux tactiles et capteurs de proximité
- **Arrêt d'urgence sécurisé** et monitoring de la vitesse
- Réduction de la puissance et de la force (PFMD)

### Fiabilité et tolérance aux pannes
- Diagnostic et détection de défaillances
- Redondance matérielle et logicielle
- Vérification formelle de comportements sécuritaires
- Run-time monitoring et systèmes de contrôle distribué

---

## 2. Collaboration Homme-Robot (Cobotique)

### Types de collaboration
- Partage d'espace sans collaboration directe
- Collaboration séquentielle (tâches alternées)
- Collaboration simultanée (co-manipulation)
- Collaboration main dans la main (close interaction)

### Planification conjointe
- Planification de tâches collaboratives
- Ordonnancement homme-robot (HRC scheduling)
- Partage d'objectifs et intentions mutuelles
- Adaptation dynamique au comportement humain

### Interaction physique
- Co-manipulation et transport d'objets
- Assistance physique et amplification de force
- Asservissement et compliance (impedance control)
- Interfaces haptiques pour la téléopération

### Évaluation de la collaboration
- Fluidité de l'interaction (HR fluency)
- Charge de travail (NASA-TLX)
- Performance de la dyade homme-robot
- Satisfaction et confort humain

---

## 3. Navigation Sociale

### Évitement de personnes
- Évitement basé sur la prédiction de trajectoire
- Modèles de foule et flux piétonniers (social force model)
- Anticipation des mouvements humains
- ORCA (Optimal Reciprocal Collision Avoidance) adapté

### Proxémie
- **Proxémie sociale** : distances intime, personnelle, sociale, publique
- Zones de confort et orientation du corps
- Variations culturelles de la proxémie
- Violation de l'espace personnel : détection et récupération

### Règles sociales
- Priorité et droit de passage
- Regroupements, files d'attente et passages étroits
- Comportements socialement acceptables (queuing, giving way)
- Navigation en environnement partagé avec des humains

### Cartographie sociale
- Social cost maps
- Modèles d'interaction sociale spatiale
- Reconnaissance de situations sociales (conversation, regroupement)
- Navigation contextuelle et sensible à la situation

---

## 4. Confiance et Acceptabilité

### Confiance homme-robot
- Modèles de confiance (Muir, Lee & See, Hancock)
- Calibration de la confiance : sur-confiance vs sous-confiance
- Mesure de la confiance : questionnaires, comportementaux, physiologiques
- Dynamique de la confiance : évolution dans le temps, réparation après erreur

### Transparence et explicabilité
- **XAI pour la robotique** : expliquer les décisions du robot
- Transparence des intentions : signaux non-verbaux, écran, langage
- Prédictibilité du comportement robotique
- Niveaux de transparence selon la situation

### Acceptabilité sociale
- TAM (Technology Acceptance Model) appliqué à la robotique
- Robotique de service et acceptation dans l'espace public
- Facteurs culturels, démographiques, contextuels
- Design centré sur l'humain pour l'acceptation

---

## 5. Éthique Robotique

### Principes fondamentaux
- **3 lois d'Asimov** : critique et limitations
- Extensions : éthique de la robotique (Floridi, Wallach, Anderson)
- Dilemmes éthiques : trolley problem version robotique
- Robotique de combat et robots autonomes létaux (LAWS)

### Responsabilité
- Responsabilité légale en cas d'accident
- Qui est responsable : fabricant, programmeur, utilisateur ?
- Enregistrement des décisions (black box robotique)
- Certification et régulation

### Biais et équité
- Biais dans les données d'entraînement des robots sociaux
- Équité dans l'interaction : traitement égalitaire des utilisateurs
- Discrimination algorithmique dans la robotique de service
- Design inclusif et accessibilité

### Vie privée
- Capteurs robotiques et collecte de données personnelles
- Vie privée dans les environnements domestiques et de soin
- Consentement et transparence des données
- Sécurité des données robotiques

---

## 6. Perception Sociale et Interaction

### Reconnaissance de gestes
- Gestes de la main, du bras, du corps
- Pointage, salutation, arrêt
- Reconnaissance d'actions et d'activités
- Apprentissage par démonstration (LfD) sociale

### Interaction vocale
- Reconnaissance vocale pour la robotique
- Synthèse vocale et prosodie sociale
- Dialogue homme-robot : tour de parole, grounding, réparation
- Commande vocale dans environnements bruyants

### Expressions faciales et contact visuel
- Reconnaissance des expressions faciales (émotions)
- Suivi du regard et attention conjointe
- Contact visuel social dans l'interaction
- Expressions faciales robotiques (animatronique, LEDs)

### Interaction multimodale
- Fusion des modalités : parole, geste, regard, toucher
- Architecture de dialogue multi-modal
- Désambiguïsation multimodale
- Adaptation à l'utilisateur (personnalisation)

---

## Catégories arXiv

- **cs.RO** — Robotics (robotique : planification, contrôle, navigation)
- **cs.HC** — Human-Computer Interaction (interaction, facteurs humains)
- **cs.AI** — Artificial Intelligence (IA pour la perception, décision sociale)
- **cs.MA** — Multiagent Systems (systèmes multi-agents, coordination)
- **cs.CY** — Computers and Society (éthique, normes, société)

## Articles Notables

- **"Embodied HRI via Acoustics: AcoustoBots"** — Interaction homme-robot par ondes acoustiques
- **"Delay-Aware MARL for Counter-UAS"** (IROS 2026) — Apprentissage multi-agent avec prise en compte des délais pour la contre-défense anti-drone

## Stratégies de veille

1. Surveiller les nouvelles soumissions sur **cs.RO** (quotidien)
2. Suivre **cs.HC** pour les études utilisateur et les facteurs humains
3. Conférences clés : HRI (ACM/IEEE Human-Robot Interaction), IROS, ICRA, RO-MAN, RSS
4. Journaux : IEEE Transactions on Robotics (T-RO), ACM Transactions on Human-Robot Interaction (THRI), International Journal of Social Robotics
5. Mots-clés : human-robot interaction, cobot, safety, social navigation, trust, robot ethics, proxemics, social robotics