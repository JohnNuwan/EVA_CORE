# Agents d'Automatismes Multi-Constructeurs (RAG Context Injection)

Ce document de référence décrit la méthodologie d'intégration basée sur les travaux récents (*Vendor-Aware Industrial Agents*, arXiv 2026) pour l'utilisation sécurisée de LLM locaux couplés à une architecture RAG pour la génération de code PLC.

---

## 1. Problématique des API Constructeurs et Propriétaires

Bien que le standard IEC 61131-3 unifie la syntaxe du Structured Text (ST), chaque constructeur d'automates (Siemens, Rockwell, Beckhoff, Schneider) possède son propre compilateur, ses propres limites de typage et ses propres bibliothèques de fonctions système :

*   **Siemens (TIA Portal)** : Utilise des blocs d'organisation (OB), des fonctions système (SFC/SFB) et des annotations d'optimisation mémoire `{ S7_Optimized_Access := 'TRUE' }`.
*   **Rockwell Automation (Studio 5000)** : S'appuie sur le format d'import XML L5X, les instructions personnalisées Add-On Instructions (AOI) et les types de données utilisateur (UDT) spécifiques.
*   **Beckhoff (TwinCAT)** : Propose des extensions orientées objet (méthodes, interfaces, héritage de blocs fonctionnels) et des bibliothèques d'axes physiques (NC/CNC).

Sans contexte, un LLM standard génère du code hybride invalide sur toutes les cibles.

---

## 2. Architecture du Système RAG Local Industriel

Afin de préserver la confidentialité des savoir-faire industriels, le moteur de génération doit s'exécuter en local ou sur site (on-premise). La base de connaissances vectorielle stocke les manuels techniques et les guides de standardisation de l'entreprise (ex: standard Actemium).

```
   [ Requête utilisateur ]
             │
             ▼
   ┌──────────────────┐      ┌─────────────────────────┐
   │ Moteur RAG Local │ ───> │ Base de données Vecteurs│
   │                  │ <─── │ (Manuels Siemens/L5X)   │
   └────────┬─────────┘      └─────────────────────────┘
            │
            │ (Prompt augmenté avec manuels de référence)
            ▼
   ┌──────────────────┐
   │  LLM Local (ST)  │ ───> [ Code ST/SCL 100% compatible compilateur ]
   └──────────────────┘
```

---

## 3. Directives d'Injection pour Siemens SCL

Pour générer du code SCL Siemens compilable :
*   **En-tête de Bloc** : Injecter systématiquement les attributs d'optimisation mémoire et la version.
*   **Fonctions Système** : Utiliser la syntaxe exacte de TIA Portal (ex: `RD_SYS_T` pour lire l'heure système, `TON_TIME` pour les temporisations).

### Exemple de contexte injecté (Siemens TON)
```pascal
// L'implémentation IEC standard de TON utilise une syntaxe de passage de paramètres :
// MyTimer(IN := Condition, PT := T#5s);
// Chez Siemens, l'utilisation de multi-instances TON requiert une déclaration et un appel explicite.
VAR
    timerDelay : TON; // Déclaré dans les variables locales d'instance
END_VAR

BEGIN
    timerDelay(IN := startCondition, PT := T#5s);
    outputSignal := timerDelay.Q;
END
```
