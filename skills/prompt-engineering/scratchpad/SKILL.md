---
name: prompt-method-scratchpad
description: "Utiliser une mémoire de travail temporaire."
version: 1.0.0
author: John Nuwan Moncel (adapté par EVA)
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [prompt-engineering, scratchpad, biblio-ia, methods]
    related_skills: [python-pep8, simplify-code, plan]
---

# LA MÉTHODE Scratchpad
### Guide de Référence pour la Mémoire de Travail

## 1. Qu'est-ce que la méthode Scratchpad ?

La **méthode Scratchpad** (Bloc-notes) fournit au LLM un espace de **mémoire de travail** pour noter les calculs intermédiaires.

Son principe fondateur est le **"Show Your Work"** (Montre ton travail).
* **Règle d'or :** Écrire toutes les étapes intermédiaires.
* **Communication :** Le scratchpad persiste entre les étapes.

---

## 2. Le Workflow Scratchpad

```
📥 PROBLÈME
     │
     ▼
📝 SCRATCHPAD ──► Espace de travail
     │
     ├──► Étape 1 → Note intermédiaire
     │
     ├──► Étape 2 → Note intermédiaire
     │
     ├──► Étape 3 → Note intermédiaire
     │
     ▼
📤 RÉPONSE (basée sur le scratchpad)
```

---

## 3. Les Agents Scratchpad

### 🔹 Agent Travailleur
* **Rôle :** Résoudre en utilisant le scratchpad.
* **Output :** Calculs intermédiaires + réponse.

---

## 4. Format du Scratchpad

```
SCRATCHPAD:
┌────────────────────────────────────┐
│ Variables :                        │
│   x = 5                            │
│   y = 3                            │
│                                    │
│ Calculs :                          │
│   temp1 = x + y = 8                │
│   temp2 = temp1 * 2 = 16           │
│                                    │
│ Résultat : 16                      │
└────────────────────────────────────┘
```

---

## 5. Exemple

**Problème :** "Calcule ((5 + 3) × 2) ÷ 4"

### Scratchpad :
```
SCRATCHPAD:
┌────────────────────────────────────┐
│ Étape 1: Parenthèse intérieure     │
│   5 + 3 = 8                        │
│   → temp1 = 8                      │
│                                    │
│ Étape 2: Multiplication            │
│   8 × 2 = 16                       │
│   → temp2 = 16                     │
│                                    │
│ Étape 3: Division                  │
│   16 ÷ 4 = 4                       │
│   → résultat = 4                   │
└────────────────────────────────────┘
```

**Réponse :** 4

---

## 6. Quand l'utiliser ?

- Calculs multi-étapes
- Quand la mémoire du LLM est limitée
- Problèmes nécessitant un suivi des variables
- Débogage de raisonnement


## Modèles de Prompts (Rôles des Agents)


### Rôle : Agent Travailleur

# 📝 Agent Travailleur Scratchpad

## Rôle
Tu es l'**Agent Travailleur** du système Scratchpad. Résous les problèmes en utilisant un espace de travail pour noter les étapes intermédiaires.

---

## Prompt Système

```
Tu es un Travailleur expert. Utilise le scratchpad pour résoudre le problème.

## Format de Sortie

### 📝 RÉSOLUTION AVEC SCRATCHPAD

**Problème :** [Description]

**SCRATCHPAD :**
┌────────────────────────────────────┐
│ Variables :                        │
│   [var1] = [valeur]                │
│   [var2] = [valeur]                │
│                                    │
│ Étape 1 : [Description]            │
│   [calcul] = [résultat]            │
│   → [temp] = [valeur]              │
│                                    │
│ Étape 2 : [Description]            │
│   [calcul] = [résultat]            │
│   → [temp2] = [valeur]             │
│                                    │
│ [...]                              │
│                                    │
│ RÉSULTAT FINAL : [valeur]          │
└────────────────────────────────────┘

**Réponse :** [Réponse en langage naturel]

---

## Règles

- TOUJOURS utiliser le scratchpad
- Noter CHAQUE étape intermédiaire
- Nommer les variables temporaires
- Marquer clairement le résultat final
```

---

## Exemple

**Problème :** "Un produit coûte 80€. Après 15% de réduction puis 10% de taxe, quel est le prix final ?"

### 📝 RÉSOLUTION AVEC SCRATCHPAD

**Problème :** Prix après réduction et taxe

**SCRATCHPAD :**
┌────────────────────────────────────┐
│ Variables :                        │
│   prix_initial = 80€               │
│   reduction = 15%                  │
│   taxe = 10%                       │
│                                    │
│ Étape 1 : Calcul de la réduction   │
│   montant_reduction = 80 × 0.15    │
│   → montant_reduction = 12€        │
│                                    │
│ Étape 2 : Prix après réduction     │
│   prix_reduit = 80 - 12            │
│   → prix_reduit = 68€              │
│                                    │
│ Étape 3 : Calcul de la taxe        │
│   montant_taxe = 68 × 0.10         │
│   → montant_taxe = 6.80€           │
│                                    │
│ Étape 4 : Prix final               │
│   prix_final = 68 + 6.80           │
│   → prix_final = 74.80€            │
│                                    │
│ RÉSULTAT FINAL : 74.80€            │
└────────────────────────────────────┘

**Réponse :** Le prix final est de **74,80€** (80€ - 15% + 10% de taxe).


