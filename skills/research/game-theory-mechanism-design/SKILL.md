---
name: game-theory-mechanism-design
description: "Compétence en recherche en théorie des jeux et conception de mécanismes suivie sur arXiv sous cs.GT et math.CO. Couvre les jeux algorithmiques, la conception de mécanismes, les enchères, le choix social, la théorie de la décision, les jeux coopératifs, la théorie de la négociation et l'économie algorithmique."
category: research
arxiv_categories:
  - cs.GT
  - cs.MA
  - cs.AI
  - econ.TH
  - math.CO
---

# Compétence : Théorie des Jeux et Conception de Mécanismes

## Présentation

Cette compétence couvre la recherche en théorie des jeux algorithmiques, conception de mécanismes, enchères, choix social computationnel, théorie de la décision, jeux coopératifs, théorie de la négociation et économie algorithmique. Le suivi se fait principalement sur arXiv sous **cs.GT** (Computer Science and Game Theory) et **math.CO** (Combinatorics), avec des extensions vers cs.MA, cs.AI et econ.TH.

---

## 1. Théorie des Jeux Algorithmiques

### Jeux sous forme normale et extensive
- Forme normale : matrices de paiement, stratégies pures/mixtes
- Forme extensive : arbres de jeu, information parfaite/imparfaite
- Équilibre de Nash : existence, unicité, calcul (Lemke-Howson, PPAD-complétude)
- Équilibre de Nash corrélé : concept d'Aumann, algorithmes de calcul
- Raffinements : équilibre parfait en sous-jeu, équilibre séquentiel, tremblant

### Complexité computationnelle
- PPAD, PLS, et classes de complexité pour les jeux
- Calcul d'équilibre dans les jeux à sommets nuls
- Algorithmes d'apprentissage : fictitious play, regret matching, no-regret dynamics

---

## 2. Conception de Mécanismes

### Mécanismes classiques
- **Vickrey-Clarke-Groves (VCG)** : enchères à second prix généralisées
- Compatibilité des incitations (incentive compatibility)
- Rationalité individuelle (individual rationality)
- Efficacité et optimalité sociale

### Enchères
- Enchères combinatoires (CA) : Winner Determination Problem
- Enchères à paquet (package bidding)
- Enchères séquentielles et simultanées
- Enchères en ligne et dynamiques

### Conception de mécanismes algorithmique
- Algorithmic Mechanism Design (Nisan-Ronen)
- Mécanismes sans paiement (payment-free mechanisms)
- Mécanismes véridiques et approximations
- Marchés prédictifs et scoring rules

---

## 3. Choix Social Computationnel

### Agrégation de préférences
- Théorème d'Arrow et impossibilités computationnelles
- Règles de vote (Borda, Condorcet, STV, approbation)
- Manipulation et stratégie : complexité de la manipulation
- Classement et top-k agrégation

### Systèmes de recommandation sociaux
- Classement par pair (ranking)
- Agrégation de classements (rank aggregation)
- Équité et diversité dans les décisions collectives
- Jugement majoritaire (majority judgment)

---

## 4. Jeux Coopératifs

### Concepts de solution
- **Valeur de Shapley** : axiomes, calcul (exact et approximatif)
- **Noyau (core)** : conditions de Bondareva-Shapley, non-vacuité
- Ensemble de négociation (bargaining set)
- Nucléole (nucleolus) et concepts de stabilité

### Applications
- Répartition des coûts et des bénéfices
- Formation de coalitions : Coalition Structure Generation
- Jeux de marché et jeux d'échange
- Jeux de réseau coopératifs

---

## 5. Jeux de Réseau

### Modèles fondamentaux
- Jeux de congestion (congestion games) — potentiel, existence d'équilibre
- Jeux sur graphes (graphical games)
- Jeux de formation de réseaux (network formation games)
- Jeux de trafic et routage (Wardrop, Pigou)

### Équilibre et dynamique
- Price of Anarchy (PoA) et Price of Stability (PoS)
- Jeux de coordination sur réseaux
- Diffusion et adoption sur réseaux sociaux
- Apprentissage distribué dans les jeux de réseau

---

## 6. Théorie de la Négociation et des Contrats

### Modèles de négociation
- Négociation axiomatique (Nash, Kalai-Smorodinsky)
- Négociation stratégique (Rubinstein, offre-alternée)
- Contrats incomplets et théorie de l'agence
- Conception de contrats optimaux

### Économie algorithmique
- Marchés en ligne et dynamic pricing
- Allocation de ressources (fair division, cake cutting)
- Conception de marchés pour l'IA et le ML

---

## 7. Applications ML et IA

- GANs comme jeux minimax : équilibre de Nash dans l'entraînement adversaire
- Jeux pour l'IA : Go, poker, échecs, StarCraft (approches par équilibre)
- Apprentissage par renforcement multi-agent (MARL)
- Théorie des jeux dans les LLM : marchés d'agents, économies de prompts
- Équité algorithmique et théorie des jeux coopératifs

---

## Articles Notables

- **"Axioms for Correlated Equilibrium"** — Fondements axiomatiques de l'équilibre corrélé
- **"Network games"** — Modèles de jeux sur réseaux
- **"Fighting discrimination with reputation"** — Réputation et équité algorithmique
- **"FootsiesGym"** — Environnement RL pour jeux de combat (jeux minimax)
- **"Information Limits in LLM Agent Economies"** — Limites informationnelles dans les économies d'agents LLM

## Stratégies de veille

1. Surveiller les nouvelles soumissions sur **cs.GT** (quotidien)
2. Suivre les articles **econ.TH** pour l'économie théorique computationnelle
3. Suivre **math.CO** pour les aspects combinatoires
4. Conférences clés : EC (ACM Conference on Economics and Computation), WINE, AAAI, NeurIPS (sessions game theory)
5. Mots-clés : Nash equilibrium, mechanism design, social choice, bargaining, auctions, network games, Shapley value