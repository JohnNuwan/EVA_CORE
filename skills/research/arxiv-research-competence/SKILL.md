---
name: arxiv-research-competence
description: >-
  Compétence professionnelle pour naviguer, rechercher et extraire des
  publications de recherche sur arXiv dans les domaines de l'informatique,
  des mathématiques, des statistiques et domaines connexes. Couvre la
  taxonomie complète des catégories arXiv, les techniques de recherche
  avancée et les bonnes pratiques de veille scientifique.
category: research
---

# Compétence en Recherche sur arXiv

## Présentation

arXiv est un service gratuit de distribution et une archive en libre accès de près de 2,4 millions d'articles scientifiques dans les domaines de la physique, des mathématiques, de l'informatique, de la biologie quantitative, de la finance quantitative, des statistiques, du génie électrique et des systèmes, et de l'économie. Cette compétence fournit une approche structurée pour naviguer et utiliser arXiv efficacement.

## Règles Générales

### Langue : Français obligatoire
Toute la production liée à la recherche sur arXiv (notes de veille, résumés d'articles, rapports, synthèses, fiches de compétence, documentation, réponses utilisateur) DOIT être rédigée en français. Les seules exceptions sont :
- Les citations littérales (titres d'articles, abstracts en anglais)
- Les noms propres techniques (noms d'algorithmes, de frameworks, de modèles)
- Les identifiants arXiv et URLs

Cette règle s'applique à toutes les sous-compétences de recherche listées dans `references/catalogue-skills.md`.

### Couverture : exhaustive et multi-source
Par défaut, la recherche doit être la plus exhaustive possible. Quand l'utilisateur demande d'explorer un domaine :
1. **Multiplier les angles** — ne pas se limiter à une seule catégorie ou source
2. **Explorer la taxonomie complète** — regarder toutes les catégories arXiv pertinentes
3. **Aller au-delà d'arXiv** — utiliser Semantic Scholar, OpenAlex, PubMed, SSRN selon le domaine
4. **Vérifier les volumes** — noter le nombre d'entrées par catégorie (ex: `/list/cs.AI/recent` → 1283 entrées/semaine)
5. **Capturer les articles récents** — citer les papiers avec leurs identifiants réels
6. **Créer un skill par domaine** — pas de skills génériques, chaque fichier = une compétence

### Création par lots parallèles
Pour créer plusieurs skills simultanément :
1. Utiliser `delegate_task` avec un tableau `tasks` contenant chaque skill
2. Chaque tâche appelle `skill_manage(action='create', name='...', category='research', content='...')`
3. Limiter à 5-12 skills par lot pour éviter les timeouts
4. Vérifier l'arrivée des lots avec `skills_list(category='research')`
5. Relancer les lots qui n'ont pas abouti

### Niveau Contenu
Chaque skill doit être de niveau ingénieur/docteur, incluant :
- Outils concrets (APIs, frameworks, plateformes avec URLs)
- Normes industrielles (ISO, DO, OWASP, IEEE)
- Benchmarks et datasets
- Articles notables récents avec identifiants
- Workflows et pipelines pratiques

## Taxonomie des Catégories arXiv (Domaines Clés)

### Informatique (cs.*)
| ID | Catégorie | Pertinence |
|----|-----------|------------|
| cs.AI | Intelligence Artificielle | Méthodes d'IA, raisonnement, planification, représentation des connaissances |
| cs.LG | Apprentissage Automatique | Apprentissage supervisé/non supervisé, deep learning, réseaux de neurones, transformers |
| cs.MA | Systèmes Multi-Agents | Apprentissage par renforcement multi-agents, coordination, théorie des jeux |
| cs.CL | Langage et Calcul | TALN, LLMs, transformers, agents langagiers, dialogue |
| cs.CV | Vision par Ordinateur | Reconnaissance d'images, génération, compréhension vidéo, vision 3D |
| cs.RO | Robotique | IA incarnée, manipulation, navigation, interaction homme-robot |
| cs.CR | Cryptographie et Sécurité | Cybersécurité, cryptographie, confidentialité différentielle, attaques adverses |
| cs.SE | Génie Logiciel | IA pour le code, tests, program repair, vérification |
| cs.IR | Recherche d'Information | RAG, ranking, moteurs de recherche neuronaux, recommandation |
| cs.HC | Interaction Homme-Machine | UX, visualisation, interfaces intelligentes, AR/VR, accessibilité |
| cs.CY | Informatique et Société | Éthique, équité, impact sociétal, désinformation |
| cs.NE | Calcul Neural et Évolutionnaire | Neuroévolution, architectures neuronales, SNN |
| cs.GT | Théorie des Jeux | Conception de mécanismes, enchères, théorie des jeux pour l'IA |
| cs.DC | Systèmes Distribués | Cloud, edge, apprentissage fédéré, HPC, parallélisme |
| cs.NI | Réseaux | Protocoles, 5G/6G, IoT, MEC, SDN |
| cs.SD | Son et Audio | ASR, TTS, génération musicale, traitement audio |
| cs.PL | Langages de Programmation | Types, compilation, vérification formelle, synthèse |
| cs.DS | Structures de Données | Algorithmes, streaming, hachage, online algorithms |
| cs.CC | Complexité Computationnelle | Classes de complexité, NP, approximation |
| cs.GR | Infographie | Rendu 3D, visualisation, animation, NeRF |
| cs.DB | Bases de Données | SQL, graphes de connaissances, NoSQL, NL2SQL |
| cs.LO | Logique | Vérification de modèles, preuves assistées, logique mathématique |
| cs.CG | Géométrie Computationnelle | Triangulation, TDA, topologie algorithmique |
| cs.SI | Systèmes Sociaux | Réseaux sociaux, dynamique d'opinion, science sociale computationnelle |
| cs.ET | Informatique Émergente | Calcul quantique, neuromorphique |
| cs.CE | Ingénierie Computationnelle | Finance, biologie, chimie computationnelles |

### Mathématiques (math.*) — Sous-catégories Pertinentes pour l'IA
| ID | Catégorie | Pertinence |
|----|-----------|------------|
| math.OC | Optimisation et Contrôle | Optimisation convexe, méthodes de gradient, théorie du contrôle |
| math.PR | Probabilités | Processus stochastiques, inégalités de concentration, matrices aléatoires |
| math.ST | Théorie Statistique | Statistiques mathématiques, théorie de la décision |
| math.NA | Analyse Numérique | Solveurs d'EDP, algèbre linéaire numérique, calcul scientifique |
| math.DS | Systèmes Dynamiques | Théorie du chaos, stabilité, bifurcations |
| math.CO | Combinatoire | Théorie des graphes, mathématiques discrètes pour l'IA |
| math.FA | Analyse Fonctionnelle | Espaces de Banach/Hilbert, théorie des opérateurs |
| math.IT | Théorie de l'Information | Codage source/canal, taux-distorsion |
| math.AT | Topologie Algébrique | TDA, homologie persistante, théorie de l'homotopie |
| math.DG | Géométrie Différentielle | Variétés, géométrie riemannienne, deep learning géométrique |
| math.RT | Théorie de la Représentation | Groupes de Lie, algèbres, invariants |
| math.CA | Analyse Classique | Ondelette, analyse harmonique, EDO |
| math.QA | Algèbre Quantique | Groupes quantiques, physique mathématique |

### Statistiques (stat.*)
| ID | Catégorie | Pertinence |
|----|-----------|------------|
| stat.ML | Apprentissage Automatique | Théorie de l'apprentissage statistique, méthodes à noyau, processus gaussiens |
| stat.ME | Méthodologie | Plans d'expérience, inférence causale, séries temporelles, méthodes bayésiennes |
| stat.TH | Théorie Statistique | Asymptotique, théorie de la décision, statistiques haute dimension |
| stat.CO | Calcul | MCMC, inférence variationnelle, algorithmes d'optimisation |
| stat.AP | Applications | Statistiques appliquées dans des domaines spécifiques |

### Finance Quantitative (q-fin.*)
| ID | Catégorie | Pertinence |
|----|-----------|------------|
| q-fin.CP | Finance Computationnelle | Calcul financier, simulation, pricing |
| q-fin.PR | Tarification des Titres | Option pricing, volatilité, modèles stochastiques |
| q-fin.MF | Mathématiques Financières | Modélisation mathématique, analyse stochastique |
| q-fin.ST | Finance Statistique | Économétrie financière, séries temporelles |
| q-fin.PM | Gestion de Portefeuille | Risk management, allocation, optimisation |
| q-fin.TR | Trading | Microstructure, trading algorithmique, HFT |
| q-fin.RM | Gestion des Risques | Risque de crédit, risque opérationnel |
| q-fin.EC | Finance quantitative générale | Économie financière |
| q-fin.GN | Général | Finance générale |

### Économie (econ.*)
| ID | Catégorie | Pertinence |
|----|-----------|------------|
| econ.EM | Économétrie | ML pour l'économie, inférence causale |
| econ.TH | Théorie Économique | Théorie des jeux, choix social, mécanismes |
| econ.GN | Général | Macroéconomie, économie de la santé, travail |

### Physique (physics.*) pertinente
| ID | Catégorie | Pertinence |
|----|-----------|------------|
| physics.soc-ph | Physique et Société | Science des réseaux, systèmes complexes |
| physics.comp-ph | Physique Computationnelle | Méthodes de Monte Carlo, simulations |
| physics.data-an | Analyse de Données | Méthodes physiques pour l'analyse de données |
| physics.bio-ph | Biophysique | Biophysique computationnelle, protéines |
| physics.med-ph | Physique Médicale | Imagerie médicale, radiothérapie |

### Biologie Quantitative (q-bio.*)
| ID | Catégorie | Pertinence |
|----|-----------|------------|
| q-bio.QM | Méthodes Quantitatives | Modélisation moléculaire, docking, bioinformatique |
| q-bio.GN | Génomique | Génomique computationnelle, DNA/RNA-seq |
| q-bio.BM | Biomolécules | Protéines, acides nucléiques, drug design |
| q-bio.NC | Neurosciences | Modélisation neuronale, BCI, imagerie cérébrale |

### Génie Électrique et Systèmes (eess.*)
| ID | Catégorie | Pertinence |
|----|-----------|------------|
| eess.SY | Systèmes et Contrôle | Théorie du contrôle, smart grids, automatique |
| eess.SP | Traitement du Signal | Filtrage, analyse spectrale, compressed sensing |
| eess.AS | Audio et Parole | ASR, TTS, traitement audio |
| eess.IV | Traitement d'Images | Restauration, super-résolution, compression |

### Informatique Quantique (quant-ph)
| ID | Pertinence |
|----|------------|
| quant-ph | Algorithmes quantiques, correction d'erreurs, QML, circuits variationnels, cryptographie post-quantique |

## Techniques de Recherche

### Recherche par URL (Efficace)
```
# Listes récentes par catégorie
https://arxiv.org/list/cs.AI/recent
https://arxiv.org/list/cs.LG/recent
https://arxiv.org/list/stat.ML/recent
https://arxiv.org/list/cs.MA/recent

# Recherche par mot-clé
https://arxiv.org/search/?searchtype=all&query=<requete>&start=0
```

### Comprendre les IDs arXiv
- Format : `YYMM.NNNNN` (ex : `2607.06546`)
- YY = année, MM = mois, NNNNN = numéro séquentiel
- Les papiers récents (2026+) utilisent 5 chiffres

## Processus de Veille

### Suivi Quotidien/Hebdomadaire
1. Consulter les nouvelles soumissions dans les catégories cibles via `/list/<cat>/recent`
2. Parcourir les soumissions des 5 derniers jours (mer, mar, ven, jeu, mer)
3. Suivre les cross-listings entre catégories

### Critères d'Évaluation d'un Article
- **Champ Subjects** : catégories primaire + secondaires
- **Champ Comments** : contient souvent la conférence de publication (ex : "Accepted at ICML 2026")
- **Résumé (Abstract)** : premier indicateur de contribution et résultats
- **Liste d'auteurs** : nombre et affiliation

### Stratégie de Lecture Approfondie
1. Titre → Subjects → Comments (30 secondes)
2. Résumé + Figures (2 minutes)
3. Introduction + Travaux connexes (5 minutes)
4. Méthode + Expériences (15 minutes)
5. Article complet (approfondi)

## Conseils Pratiques
- **"new" vs "recent"** : `/list/cs.AI/new` montre les changements de la veille ; `/list/cs.AI/recent` montre les 5 derniers jours
- **Cross-listings** : un article dans cs.AI peut aussi apparaître dans cs.LG — vérifier le champ Subjects
- **Lien PDF direct** : `https://arxiv.org/pdf/YYMM.NNNNN`
- **Version HTML** : `https://arxiv.org/html/YYMM.NNNNN`
- **API arXiv** : `https://export.arxiv.org/api/query` pour un accès programmatique
- **Recherche par guillemets** : utiliser des guillemets pour une correspondance exacte

## Compétences Associées

Un catalogue complet des 115+ sous-compétences de recherche est disponible dans le fichier de référence :
- `references/catalogue-skills.md` — liste exhaustive de tous les skills de recherche par domaine (18 groupes, 115+ skills)

Chaque sous-compétence peut être chargée via `skill_view(nom-du-skill)` pour accéder à son contenu détaillé (domaines de recherche, articles notables récents, URLs de veille).