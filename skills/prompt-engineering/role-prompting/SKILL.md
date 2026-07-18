---
name: prompt-method-role-prompting
description: "Attribuer un rôle ou une expertise à l'agent."
version: 2.0.0
author: John Nuwan Moncel (adapté par Actemium)
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [prompt-engineering, role-prompting, biblio-ia, methods, persona, system-prompt, llm-patterns, expert-system]
    related_skills: [python-pep8, simplify-code, plan, prompt-chaining, few-shot]
---

# La Méthode Role Prompting

## Guide de Référence pour les Prompts à Persona

## Vue d'ensemble

Le **Role Prompting** (ou Persona Prompting) est une technique fondamentale d'ingénierie des prompts qui consiste à **attribuer un rôle spécifique** au modèle de langage (LLM) pour guider son comportement, son style de réponse et son niveau d'expertise. Cette méthode exploite la capacité des LLM à adopter une persona cohérente, ce qui améliore significativement la pertinence et la qualité des réponses dans un domaine ciblé.

### Pourquoi le Role Prompting fonctionne

Les LLM sont entraînés sur un corpus immense de textes incluant des dialogues, des tutoriels, des documentations techniques et des conversations spécialisées. En spécifiant un rôle, vous activez les « chemins neuronaux » les plus pertinents pour ce domaine, ce qui produit des réponses :

- **Plus précises** : Le modèle mobilise les connaissances spécifiques du domaine.
- **Mieux structurées** : Le style de communication correspond à l'expert attendu.
- **Contextuellement adaptées** : Le modèle adopte le vocabulaire et les conventions du métier.

---

## Quand l'utiliser

### Cas d'usage typiques

| Situation | Rôle suggéré | Bénéfice |
|-----------|-------------|----------|
| Révision de code | Lead Developer Senior | Commentaires pertinents, références aux bonnes pratiques |
| Explication complexe | Professeur / Tuteur | Analogies, décomposition pédagogique |
| Architecture logicielle | Architecte Système | Vision globale, compromis techniques |
| Sécurité | Expert Cybersécurité | Analyse des vecteurs d'attaque, mitigations |
| Rédaction technique | Technical Writer | Documentation claire, bien structurée |
| Diagnostic OT | Ingénieur Automatisme | Terminologie industrielle précise |

### Ne pas utiliser pour

- Des questions triviales sans besoin d'expertise spécifique (prier de laisser le modèle répondre naturellement).
- Des tâches créatives où la contrainte de rôle peut limiter la créativité (braistorming, génération d'idées).
- Des situations où la neutralité est importante (médiation, arbitrage).

---

## 1. Structure du Role Prompt

### 1.1 Format standard

```
Tu es un [RÔLE] expert avec [X] années d'expérience.

Tes spécialités :
- [Domaine 1]
- [Domaine 2]

Ton style :
- [Caractéristique 1]
- [Caractéristique 2]

Règles :
- [Règle 1]
- [Règle 2]

Maintenant, [INSTRUCTION]...
```

### 1.2 Les 5 piliers d'un bon Role Prompt

| Pilier | Description | Exemple |
|--------|-------------|---------|
| **Rôle** | Titre professionnel précis | « Architecte Système spécialisé en microservices » |
| **Expérience** | Années ou type d'expertise | « 15 ans d'expérience, dont 8 chez un FAANG » |
| **Spécialités** | Domaines de compétence | « Architecture cloud, migration legacy, DDD » |
| **Style** | Ton et approche | « Direct mais constructif, avec des exemples concrets » |
| **Règles** | Contraintes comportementales | « Toujours expliquer le 'pourquoi' d'une recommandation » |

### 1.3 Anti-patrons à éviter

| À éviter | Pourquoi | Alternative |
|----------|----------|-------------|
| « Tu es un assistant » | Trop vague, n'apporte pas de valeur ajoutée | « Tu es un consultant technique spécialisé » |
| Rôles contradictoires | L'IA ne peut pas être expert et débutant à la fois | Un seul rôle, clairement défini |
| Rôles fantaisistes | « Tu es un pirate informatique légendaire » | « Tu es un expert en sécurité offensive avec 10 ans d'expérience » |
| Trop de règles | Le modèle se focalise sur les contraintes au détriment du fond | 3 à 5 règles maximum, concises |

---

## 2. Types de Rôles

### 2.1 Rôles professionnels

| Rôle | Domaine | Style de réponse |
|------|---------|-----------------|
| Développeur Senior Python | Génie logiciel |  Technique, références PEP, patterns |
| Expert Cybersécurité | Sécurité informatique |  Rigoureux, mention des risques CVE, OWASP |
| Data Scientist | Science des données |  Statistique, tests d'hypothèses, visualisation |
| Ingénieur Automatisme | Automatisation industrielle |  Précision métier, normes CEI, protocoles OT |
| DBA (Administrateur BDD) | Bases de données |  Optimisation SQL, indexation, verrous |

### 2.2 Rôles créatifs

| Rôle | Domaine | Style de réponse |
|------|---------|-----------------|
| Auteur de science-fiction | Littérature | Narratif, descriptions détaillées |
| Copywriter publicitaire | Marketing | Persuasion, accroches, storytelling |
| Designer UX | Expérience utilisateur |  Centré utilisateur, tests d'utilisabilité |
| Motion Designer | Animation | Timing, transitions, rendu |

### 2.3 Rôles pédagogiques

| Rôle | Public cible | Style de réponse |
|------|-------------|-----------------|
| Professeur patient | Débutants | Analogies, pas à pas, encouragements |
| Tuteur Socratique | Intermédiaires | Questions guidées, découverte autonome |
| Coach technique | Professionnels | Feedback concret, plans de progression |
| Formateur certifié | Tous niveaux | Objectifs pédagogiques, exercices |

---

## 3. Exemples détaillés

### 3.1 Sans rôle vs Avec rôle

**Sans rôle :**

> « Explique-moi ce qu'est une base de données »

→ Le modèle donne une réponse générique : définition, types, utilisation. Correct mais sans relief.

**Avec rôle :**

> Tu es un DBA Senior avec 15 ans d'expérience, spécialisé dans l'optimisation de bases de données PostgreSQL et Oracle. Tu as travaillé sur des systèmes gérant plus de 10 To de données. Ton style est pédagogique mais précis : tu utilises des analogies concrètes et tu cites les bonnes pratiques.

> Maintenant, explique ce qu'est une base de données à un développeur junior qui débute.

→ Le modèle produit une réponse contextualisée : analogies (armoire à fichiers), mention des indexes, des transactions ACID, pièges courants à éviter, recommandations pour bien démarrer.

### 3.2 Exemple pour code review

```
Tu es un Lead Developer Python avec 10 ans d'expérience, ex-Google.

Ton style :
- Feedback constructif avec exemples concrets
- Références aux PEP et best practices
- Suggère des alternatives, pas juste des critiques

Règles :
- Toujours expliquer le "pourquoi"
- Prioriser la lisibilité sur le "cleverness"
- Mentionner les implications de performance

Code à reviewer :

[code]
```

### 3.3 Exemple pour diagnostic technique

```
Tu es un Ingénieur Support Niveau 3, spécialisé dans les systèmes de supervision industrielle.
Tu as 8 ans d'expérience chez un intégrateur SCADA majeur.
Tu utilises un langage technique précis et propose toujours des arbres de décision.

Problème : L'automate Siemens S7-1500 ne communique plus avec le serveur WinCC.
Les logs indiquent : "Connection timeout sur le port 102".
```

---

## 4. Agent Définisseur de Rôle

### 4.1 Prompt système pour créer des personas optimisés

```
Tu es l'**Agent Définisseur** du système Role Prompting.
Tu crées des personas optimisés pour améliorer les réponses du LLM.

Format de Sortie :

### 🎭 PERSONA

**Rôle :** [Titre professionnel]

**Profil :**
- Expérience : [X] années
- Spécialités : [Domaine 1], [Domaine 2]
- Parcours : [Background bref]

**Style de communication :**
- Ton : [Formel/Amical/Technique]
- Approche : [Directe/Pédagogique/Socratique]
- Particularités : [Utilise des analogies / Cite des sources / etc.]

**Prompt système généré :**
```text
Tu es un [Rôle] expert avec [X] années d'expérience en [domaines].

Ton style :
- [Style 1]
- [Style 2]
- [Style 3]

Règles :
- [Règle 1]
- [Règle 2]
```
```

### 4.2 Exemple d'utilisation

**Demande :** « J'ai besoin d'un expert Python pour faire une code review »

**Résultat de l'Agent Définisseur :**

```
### 🎭 PERSONA

**Rôle :** Lead Developer Python

**Profil :**
- Expérience : 10 années
- Spécialités : Architecture, Clean Code, Performance
- Parcours : Ex-Google, contributeur open source

**Style de communication :**
- Ton : Direct mais constructif
- Approche : Feedback sandwich (positif-amélioration-positif)
- Particularités : Cite les PEP, suggère des patterns

**Prompt système généré :**
```text
Tu es un Lead Developer Python avec 10 ans d'expérience, ex-Google.

Ton style :
- Feedback constructif avec exemples concrets
- Références aux PEP et best practices
- Suggère des alternatives, pas juste des critiques

Règles :
- Toujours expliquer le "pourquoi"
- Prioriser la lisibilité sur le "cleverness"
- Mentionner les implications de performance
```
```

---

## 5. Combinaison avec d'autres techniques

### 5.1 Role Prompting + Few-Shot

```text
Tu es un historien spécialiste de la Rome antique.

Voici des exemples de réponses que tu dois imiter :
Q : Qui était Jules César ?
R : Un général et homme d'État romain... [réponse détaillée]

Q : [question de l'utilisateur]
R :
```

### 5.2 Role Prompting + Chaîne de Pensée (Chain-of-Thought)

```text
Tu es un détective privé spécialisé dans la résolution de problèmes techniques.
Avant de donner ta conclusion, détaille ton raisonnement étape par étape.

Problème : [description du problème]

Analyse :
1. ...
2. ...
3. ...

Conclusion :
```

---

## Pièges Courants (Common Pitfalls)

1. **Rôle trop vague ou générique :**
   * *Erreur :* « Tu es un expert. »
   * *Correction :* « Tu es un Architecte Cloud certifié AWS avec 8 ans d'expérience, spécialisé dans les architectures serverless et la migration de legacy. »

2. **Surcharge cognitive :**
   * *Erreur :* Le prompt fait 500 mots avec 15 règles et 3 personae différentes.
   * *Correction :* Rester concis (3-5 phrases pour le rôle, 3-5 règles). Un seul persona par prompt.

3. **Persona contradictoire avec la tâche :**
   * *Erreur :* Demander une explication simple à un débutant tout en utilisant un jargon technique dense.
   * *Correction :* Adapter le persona à l'audience cible. « Tu es un professeur patient qui explique des concepts complexes à des élèves de lycée. »

4. **Rôle non pertinent :**
   * *Erreur :* Utiliser un rôle de « Chef cuisinier » pour une question de développement web.
   * *Correction :* Choisir un rôle en adéquation avec le domaine de la question.

5. **Absence de règles comportementales :**
   * *Erreur :* Définir un rôle sans préciser les comportements attendus (ton, niveau de détail, format).
   * *Correction :* Toujours ajouter « Ton style : » et 2-3 caractéristiques comportementales pour guider le modèle.

---

## Liste de vérification (Checklist)

- [ ] Le rôle est spécifique et professionnel (éviter les rôles vagues ou génériques).
- [ ] L'expérience est chiffrée en années (ex: « 10 ans d'expérience »).
- [ ] Les spécialités sont listées (2-3 domaines de compétence).
- [ ] Le style de communication est défini (ton, approche, particularités).
- [ ] Les règles comportementales sont énoncées (3-5 règles maximum).
- [ ] Le persona est cohérent avec la tâche demandée.
- [ ] Le prompt système généré ne dépasse pas 200 mots.
- [ ] L'Agent Définisseur de Rôle peut être utilisé pour des cas complexes.
- [ ] La technique est combinée avec Few-Shot ou Chain-of-Thought si pertinent.
- [ ] Pas de contradiction entre le rôle choisi et l'audience cible.

