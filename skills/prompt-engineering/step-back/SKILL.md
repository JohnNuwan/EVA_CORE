---
name: prompt-method-step-back
description: "Prendre du recul en formulant une question plus abstraite pour identifier les principes généraux avant de répondre."
version: 2.0.0
author: John Nuwan Moncel (adapté par Actemium)
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [prompt-engineering, step-back, biblio-ia, methods, abstraction, reasoning]
    related_skills: [python-pep8, simplify-code, plan, analogical, generated-knowledge]
---

# La méthode Step-Back Prompting

## Guide de référence pour l'abstraction préalable et le raisonnement par principes généraux

---

## 1. Vue d'ensemble

La méthode **Step-Back Prompting** (ou « prise de recul ») consiste à demander à un LLM de **formuler une question plus abstraite et générale** avant de répondre à la question spécifique posée. En « prenant du recul », le modèle identifie les principes fondamentaux, les lois générales ou les catégories conceptuelles qui sous-tendent le problème particulier.

### Principe fondateur

Le cœur de la méthode repose sur le principe **« Zoom Out Before Zoom In »** (Élargir avant de préciser) :

- **Abstraction comme point d'entrée** : remonter du cas particulier au principe général
- **Raisonnement descendant** : appliquer des lois générales à des cas spécifiques
- **Réduction des biais** : éviter le sur-apprentissage sur les détails superficiels du problème
- **Transférabilité** : une fois le principe compris, il s'applique à une classe entière de problèmes

### Architecture conceptuelle

```
                    ┌──────────────────────────────────┐
                    │   Question spécifique initiale   │
                    │   « Pourquoi mon code est lent ?»│
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Phase 1 : STEP-BACK             │
                    │  Formuler une question abstraite │
                    │  « Quels sont les principes      │
                    │  d'optimisation de performance ? │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Phase 2 : IDENTIFICATION        │
                    │  des principes généraux          │
                    │  1. Complexité algorithmique     │
                    │  2. Structures de données        │
                    │  3. Gestion mémoire et I/O       │
                    │  4. Profiling avant optimisation  │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Phase 3 : APPLICATION           │
                    │  au cas spécifique               │
                    │  Relier chaque principe          │
                    │  au problème original            │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  ✅ Réponse informée par les     │
                    │     principes fondamentaux        │
                    └──────────────────────────────────┘
```

---

## 2. Quand l'utiliser ?

### Cas d'usage recommandés

| Contexte | Description | Priorité |
|----------|-------------|----------|
| Questions techniques complexes | Problème qui semble spécifique mais relève d'un principe général | Élevée |
| Difficulté de compréhension | L'utilisateur demande une solution sans comprendre le fondement | Élevée |
| Enseignement et mentorat | Expliquer le « pourquoi » avant le « comment » | Élevée |
| Résolution de bugs récurrents | Un bug qui semble nouveau mais appartient à une classe déjà connue | Moyenne |
| Prise de décision stratégique | Évaluer une décision spécifique à la lumière de principes généraux | Moyenne |
| Architecture et design | Choisir un pattern spécifique en comprenant d'abord les principes architecturaux | Moyenne |

### Situations à éviter

- **Questions factuelles simples** : « Quelle est la capitale du Japon ? » — pas besoin de principes généraux
- **Situations d'urgence** : quand une action immédiate est nécessaire, le temps de recul n'est pas disponible
- **Sujets très spécialisés sans principes généraux** : certains problèmes sont purement procéduraux
- **Quand l'abstraction ajoute de la confusion** : si l'utilisateur n'a pas les bases pour comprendre les principes généraux

---

## 3. Procédure pas à pas

### Étape 1 : Recevoir la question spécifique

Identifiez le problème concret posé et notez sa formulation exacte.

```
Question originale : « Pourquoi mon API Flask est-elle si lente
quand je fais 100 requêtes simultanées ? »
```

### Étape 2 : Formuler la question step-back (plus abstraite)

Remontez du cas particulier à la catégorie générale.

**Techniques pour générer une question step-back :**

| Technique | Exemple |
|-----------|---------|
| Généralisation | « Quels sont les principes de... » |
| Catégorisation | « Dans quelle catégorie de problèmes cela s'inscrit ? » |
| Analogie conceptuelle | « Quels sont les lois physiques/mathématiques qui régissent cela ? » |
| Remontée de cause | « Quelle est la cause fondamentale de ce type de problème ? » |

**Prompt de step-back :**

```
Question spécifique : « Pourquoi mon API Flask est-elle si lente
quand je fais 100 requêtes simultanées ? »

Avant de répondre, formule une question plus abstraite et
générale dont cette question est un cas particulier.

Exemples de questions step-back possibles :
- « Quels sont les facteurs qui limitent la concurrence (concurrency)
  dans les applications web Python ? »
- « Quels sont les principes fondamentaux de la gestion des
  connexions simultanées dans un serveur web ? »
```

**Question step-back retenue :**

```
🔭 STEP-BACK :
« Quels sont les principes fondamentaux de la gestion de
la concurrence (concurrency) dans les applications web Python ? »
```

### Étape 3 : Identifier les principes généraux

Répondez à la question step-back en listant les principes fondamentaux.

```
📚 PRINCIPES GÉNÉRAUX IDENTIFIÉS :

1. GIL (Global Interpreter Lock) : Python ne peut exécuter
   qu'un seul thread à la fois pour le code Python pur.
   → Conséquence : le threading ne donne pas de parallélisme
     réel pour le calcul, seulement pour l'I/O.

2. Modèles de concurrence disponibles :
   - Threading : bon pour I/O, limité par GIL pour CPU
   - Multiprocessing : parallélisme réel mais overhead mémoire
   - Async (asyncio) : coopératif, idéal pour I/O réseau
   - Gevent/Eventlet : monkey-patching pour I/O concurrent

3. Goulots d'étranglement typiques :
   - Base de données : connexions limitées, requêtes lentes
   - I/O réseau : latence, bande passante
   - Calcul CPU : boucles, sérialisation/désérialisation
   - Mémoire : fuites, GC overhead

4. Scaling horizontal vs vertical :
   - Vertical : plus de ressources sur une machine
   - Horizontal : plusieurs instances (workers Gunicorn/uWSGI)

5. Profiling : Ne pas optimiser sans mesurer.
   Utiliser : cProfile, py-spy, locust, APM tools
```

### Étape 4 : Appliquer les principes au cas spécifique

Pour chaque principe, montrez comment il s'applique au problème concret.

```
🎯 APPLICATION AU CAS SPÉCIFIQUE :

Question originale : « Pourquoi mon API Flask est-elle si lente
quand je fais 100 requêtes simultanées ? »

Application des principes :

| Principe | Application à mon cas |
|----------|----------------------|
| GIL + Threading | Flask utilise threading par défaut. Le GIL fait que 100 threads ne sont pas réellement parallèles. L'I/O (DB, HTTP) est concurrent, mais pas le traitement. |
| Modèles de concurrence | Avec Flask pur, un worker ne traite qu'une requête à la fois. Pour 100 requêtes simultanées, il faut plusieurs workers. |
| Goulot DB | Vérifier si le goulot est la base de données (connexions, requêtes N+1) |
| Scaling horizontal | Solution : passer à Gunicorn avec plusieurs workers, ou utiliser asyncio avec Quart/FastAPI |
| Profiling | Avant toute optimisation, mesurer avec locust pour identifier le vrai goulot |
```

### Étape 5 : Synthétiser la réponse finale

Produisez une réponse qui lie explicitement les principes généraux à la solution spécifique.

```
📤 RÉPONSE INFORMÉE :

Votre API Flask est lente à 100 requêtes simultanées pour une
raison fondamentale : Flask (Werkzeug) utilise un thread par
défaut, et le GIL de Python limite l'exécution réelle.

Solutions par ordre de recommandation :

1. Passer à Gunicorn avec plusieurs workers (recommandé) :
   ```
   gunicorn -w 4 -k gthread app:app
   ```
   → 4 workers = 4 processus = 4x parallélisme réel

2. Utiliser un serveur asynchrone :
   ```python
   # Migrer vers FastAPI ou Quart
   from fastapi import FastAPI
   app = FastAPI()
   ```
   → Async = concurrence coopérative, idéal pour I/O

3. Optimiser les accès DB :
   - Vérifier les requêtes N+1
   - Ajouter un cache (Redis, Memcached)
   - Utiliser des connexions pool

Principe clé retenu : La concurrence en Python dépend du
modèle choisi (threading vs async vs multiprocessing).
Flask synchrone + Gunicorn workers = solution éprouvée.
```

---

## 4. Workflow complet

```
                    ┌──────────────────────────────────┐
                    │   Question spécifique (S)        │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Reformulation S → question      │
                    │  abstraite (Step-Back)            │
                    │  « Quel est le principe général   │
                    │  derrière ce problème ? »         │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Identification des N principes   │
                    │  fondamentaux                     │
                    │  (lois, règles, patterns, théories)│
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Pour chaque principe :           │
                    │  Vérifier sa pertinence par       │
                    │  rapport à la question originale  │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Application au cas spécifique    │
                    │  Tableau : Principe → Application │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Synthèse : réponse finale        │
                    │  qui montre le lien entre les     │
                    │  principes et la solution         │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  ✅ Réponse = principes +        │
                    │     application concrète          │
                    └──────────────────────────────────┘
```

---

## 5. Exemples concrets de code et prompts

### Exemple 1 : Sécurisation d'une API REST

**Prompt step-back :**

```
Question : « Comment sécuriser mon API REST Express.js ? »

Étape 1 : Formule une question step-back (plus abstraite)
Étape 2 : Identifie les principes généraux de sécurité
Étape 3 : Applique-les à Express.js
```

**Réponse :**

```
🔭 STEP-BACK :
« Quels sont les principes fondamentaux de la sécurité
des applications web, indépendamment du framework ? »

📚 PRINCIPES GÉNÉRAUX DE SÉCURITÉ WEB :

1. Authentification (AuthN) → « Qui es-tu ? »
   - Vérifier l'identité de l'utilisateur
   - Mécanismes : JWT, OAuth2, Session cookies

2. Autorisation (AuthZ) → « Que peux-tu faire ? »
   - Contrôler les accès après identification
   - Modèles : RBAC (rôles), ABAC (attributs)

3. Confidentialité → « Protéger les données »
   - Chiffrement en transit (HTTPS/TLS)
   - Chiffrement au repos (données stockées)

4. Intégrité → « Données non altérées »
   - Signatures, checksums
   - Validation des entrées côté serveur

5. Disponibilité → « Service accessible »
   - Rate limiting, DDoS protection
   - Load balancing, redondance

6. Audit → « Tout est tracé »
   - Logs de connexion, d'action
   - Horodatage, IP, utilisateur

🎯 APPLICATION À EXPRESS.JS :

| Principe | Implémentation Express.js |
|----------|--------------------------|
| AuthN    | passport.js, jsonwebtoken |
| AuthZ    | middleware rbac : `requireRole('admin')` |
| Confidentialité | helmet.js, cors configuré |
| Intégrité | express-validator, Joi |
| Disponibilité | express-rate-limit |
| Audit    | morgan + winston (logs structurés) |

📤 SOLUTION :

```javascript
const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { authenticate } = require('./middleware/auth');
const { requireRole } = require('./middleware/rbac');

const app = express();

// 1. Confidentialité
app.use(helmet());
app.use(cors({ origin: process.env.ALLOWED_ORIGINS }));

// 2. Disponibilité
app.use(rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
}));

// 3. AuthN
app.post('/api/login', loginHandler);
app.use('/api', authenticate);

// 4. AuthZ
app.get('/api/admin', requireRole('admin'), adminHandler);

// 5. Intégrité
app.post('/api/users', validateUserSchema, createUser);
```

### Exemple 2 : Débogage de performance CSS

**Prompt :**

```
Question : « Mon site web a un Cumulative Layout Shift (CLS)
élevé, comment le réduire ? »

Step-back : Quels sont les principes fondamentaux de stabilité
visuelle et de rendu dans le navigateur ?
```

**Réponse :**

```
🔭 STEP-BACK :
« Quels sont les principes de rendu du navigateur qui
affectent la stabilité visuelle ? »

📚 PRINCIPES :
1. Le navigateur rend le HTML progressivement (pas d'attente)
2. Sans dimensions explicites, les éléments resize après
   chargement des ressources (images, polices)
3. Les polices web causent un flash (FOUT/FOIT)
4. Les insertions DOM tardives (JS, publicités) décalent
   le contenu

🎯 APPLICATION :
- Ajouter width/height sur toutes les images et vidéos
- Utiliser font-display: swap pour les polices
- Réserver l'espace pour les emplacements pub/embeds
- Éviter les insertions DOM au-dessus du fold
```

---

## 6. Pièges courants (Pitfalls)

### ⚠️ Piège n°1 : Question step-back trop abstraite ou mal formulée

**Erreur :** La question step-back est si générale qu'elle perd tout lien avec le problème original.

```
❌ Question originale : « Pourquoi mon déploiement Kubernetes échoue ? »
   Step-back : « Quels sont les principes de l'informatique ? »
   → Trop général, inutile pour résoudre le problème
```

**✅ Correction :** La question step-back doit être à un niveau d'abstraction juste au-dessus :

```
✅ Step-back correct : « Quels sont les principes fondamentaux
   du déploiement d'applications conteneurisées sur Kubernetes ? »
✅ Step-back alternatif : « Quelles sont les causes typiques
   d'échec de déploiement dans les orchestrateurs de conteneurs ? »
```

Règle empirique : la question step-back doit rester spécifique au **domaine** du problème tout en étant générale par rapport au **cas particulier**.

### ⚠️ Piège n°2 : Sauter l'étape d'application (principes sans retour au concret)

**Erreur :** Le LLM liste des principes généraux mais ne les relie jamais explicitement au problème spécifique.

```
❌ Principes généraux listés → réponse vague :
   « Appliquez les bons principes de performance »
   → L'utilisateur ne sait pas quoi faire concrètement
```

**✅ Correction :** Structurez la réponse pour que le lien soit explicite :

```
Pour chaque principe :
   [Principe] → Dans VOTRE cas : [Application spécifique]

Ou utilisez un tableau :
| Principe | Application à mon problème |
|----------|---------------------------|
| ...      | ...                       |
```

### ⚠️ Piège n°3 : Mauvais diagnostic — le vrai problème n'est pas celui qui semble évident

**Erreur :** Le step-back est appliqué au mauvais niveau, traitant un symptôme au lieu de la cause profonde.

```
❌ Question : « Comment rendre mon site plus rapide ? »
   Step-back : « Quels sont les principes d'optimisation CSS ? »
   → Mais le vrai problème est : serveur lent, pas CSS
```

**✅ Correction :** Avant le step-back, vérifiez que vous avez bien identifié la nature du problème :

```
1. Demander : « De quel TYPE de problème s'agit-il ? »
   (Performance ? Sécurité ? Architecture ? Bug ? Design ?)

2. Faire un premier diagnostic rapide
   (Est-ce que la lenteur est réseau, serveur, ou frontend ?)

3. Appliquer le step-back sur la BONNE catégorie
```

### ⚠️ Piège n°4 : Confondre Step-Back avec Chain-of-Thought (CoT)

**Erreur :** Step-back n'est pas une simple décomposition en étapes (CoT), c'est un changement de niveau d'abstraction.

```
❌ CoT : « D'abord, analysons le code, puis trouvons les
   goulots, puis optimisons. » (décomposition séquentielle)
✅ Step-back : « Quels sont les principes de performance
   qui s'appliquent ? » (montée en abstraction)
```

Step-back change le QUOI (principe général), pas le COMMENT (procédure).

---

## 7. Checklist d'utilisation

### Avant le step-back

- [ ] La question spécifique est-elle bien formulée et comprise ?
- [ ] Le problème appartient-il à une catégorie qui a des principes généraux identifiables ?
- [ ] La question step-back est-elle au bon niveau d'abstraction (ni trop haut, ni trop bas) ?
- [ ] Avez-vous vérifié que le vrai problème est bien celui qui est énoncé ?

### Pendant l'identification des principes

- [ ] Les principes identifiés sont-ils réellement généraux (pas spécifiques au cas particulier) ?
- [ ] Les principes sont-ils complets (pas de lacune évidente) ?
- [ ] Chaque principe est-il justifié ou démontré ?
- [ ] Les principes sont-ils classés par pertinence pour le problème spécifique ?

### Pendant l'application au cas spécifique

- [ ] Chaque principe est-il explicitement relié au problème original ?
- [ ] L'application est-elle concrète (code, commande, configuration) ?
- [ ] Les contraintes spécifiques du contexte (version, environnement, budget) sont-elles prises en compte ?
- [ ] La réponse finale montre-t-elle clairement le chemin : principe → application → solution ?

### Après la réponse

- [ ] La compréhension du problème est-elle meilleure qu'avec une réponse directe ?
- [ ] L'utilisateur pourrait-il appliquer les mêmes principes à un problème similaire ?
- [ ] La réponse est-elle pédagogique (explique le « pourquoi ») ?
- [ ] La réponse est-elle actionnable (donne le « comment ») ?

---

## 8. Variantes avancées

| Variante | Description | Quand l'utiliser |
|----------|-------------|-----------------|
| Step-Back multi-niveaux | Plusieurs niveaux d'abstraction successifs | Problèmes très complexes |
| Step-Back + Génération de connaissances | Combiner abstraction et faits générés | Maximiser la couverture |
| Step-Back inversé | Partir du principe général et trouver des cas spécifiques d'application | Enseignement |
| Step-Back collaboratif | Plusieurs agents proposent des questions step-back différentes, puis synthèse | Éviter les angles morts |
| Step-Back + Analogie | Après l'abstraction, chercher une analogie qui illustre le principe | Pédagogie renforcée |

---

> **Note importante :** Le Step-Back Prompting est particulièrement utile dans des contextes d'apprentissage, de débogage et d'architecture où la compréhension des principes fondamentaux est plus précieuse que l'obtention rapide d'une réponse. Sa force est aussi sa faiblesse : il prend plus de temps et de tokens qu'une réponse directe. Utilisez-le quand la valeur de la compréhension dépasse le coût de l'abstraction.

