---
name: probabilistic-modeling-ai
description: "Appliquer la modélisation probabiliste dans des systèmes IA pour des modèles statistiques avancés, incluant l'inférence bayésienne, les processus gaussiens et l'optimisation de l'incertitude."
version: 2.0.0
author: EVA Agent
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
tags: [probabiliste, bayésien, incertitude, inférence, processus-gaussiens, MCMC]
keywords: [Bayesian inference, MCMC, Gaussian processes, uncertainty quantification, PyMC, probabilistic programming]
---

# Modélisation Probabiliste pour l'IA

## Vue d'ensemble

La modélisation probabiliste fournit un cadre mathématique rigoureux pour représenter et raisonner sur l'incertitude dans les systèmes d'intelligence artificielle. Contrairement aux approches déterministes qui produisent une prédiction unique, les modèles probabilistes quantifient explicitement leur incertitude et mettent à jour leurs croyances à mesure que de nouvelles données sont observées.

Cette compétence couvre les domaines suivants :

1. **Inférence bayésienne** : mise à jour des croyances via le théorème de Bayes.
2. **Processus gaussiens** : modélisation non-paramétrique pour la régression et l'optimisation.
3. **Chaînes de Markov Monte Carlo (MCMC)** : échantillonnage de distributions complexes.
4. **Quantification de l'incertitude** : séparation entre incertitude aléatoire (aléatoire) et épistémique (manque de connaissance).

---

## Quand utiliser cette compétence

| Scénario | Pertinence |
|---|---|
| Données parcellaires ou manquantes (ex. rares pannes industrielles) | Élevée |
| Décision critique nécessitant une quantification de l'incertitude (ex. diagnostic médical) | Élevée |
| Optimisation d'hyperparamètres avec budget d'évaluation limité | Élevée |
| Modélisation de phénomènes physiques avec bruit de mesure | Moyenne |
| Problème de classification standard avec grandes données étiquetées | Faible (préférer les méthodes déterministes) |

---

## 1. Inférence bayésienne

### 1.1 Formalisme mathématique

Le théorème de Bayes constitue le socle de la modélisation probabiliste :

$$
P(\theta \mid \mathcal{D}) = \frac{P(\mathcal{D} \mid \theta) \, P(\theta)}{P(\mathcal{D})}
$$

| Symbole | Signification |
|---|---|
| $ P(\theta) $ | Distribution a priori (prior) — croyance avant les données |
| $ P(\mathcal{D} \mid \theta) $ | Vraisemblance (likelihood) — probabilité des données sachant le paramètre |
| $ P(\theta \mid \mathcal{D}) $ | Distribution a posteriori (posterior) — croyance mise à jour |
| $ P(\mathcal{D}) $ | Évidence (marginal likelihood) — constante de normalisation |

### 1.2 Exemple complet : estimation d'une probabilité de succès

```python
import numpy as np
import pymc as pm
import arviz as az

def inferer_probabilite_succes(donnees: np.ndarray,
                               alpha_prior: float = 2.0,
                               beta_prior: float = 2.0,
                               echantillons: int = 2000) -> dict:
    """Infère la probabilité de succès d'un processus binaire via MCMC.

    Args:
        donnees: Tableau de 0/1 représentant les observations.
        alpha_prior: Paramètre alpha de la distribution Beta a priori.
        beta_prior: Paramètre beta de la distribution Beta a priori.
        echantillons: Nombre d'échantillons MCMC après burn-in.

    Returns:
        Dictionnaire contenant la moyenne, l'intervalle de crédibilité à 94 %
        et la distribution complète a posteriori.

    Raises:
        ValueError: Si les données sont vides.
    """
    if len(donnees) == 0:
        raise ValueError("Les données ne peuvent pas être vides.")

    with pm.Model() as modele_bayesien:
        # Prior : Beta(alpha, beta)
        p = pm.Beta("p", alpha=alpha_prior, beta=beta_prior)

        # Vraisemblance : Bernoulli(p)
        observations = pm.Bernoulli("observations", p=p, observed=donnees)

        # Échantillonnage MCMC (NUTS)
        trace = pm.sample(echantillons, tune=1000, chains=4,
                          return_inferencedata=True, progressbar=False)

    # Résumé des résultats
    resume = az.summary(trace, hdi_prob=0.94)
    posterior_samples = trace.posterior["p"].values.flatten()

    return {
        "moyenne": float(np.mean(posterior_samples)),
        "ecart_type": float(np.std(posterior_samples)),
        "ic_94_inf": float(resume["hdi_2.5%"].iloc[0]) if "hdi_2.5%" in resume else None,
        "ic_94_sup": float(resume["hdi_97.5%"].iloc[0]) if "hdi_97.5%" in resume else None,
        "echantillons": posterior_samples.tolist(),
    }


# Exemple d'utilisation
np.random.seed(42)
donnees_simulees = np.random.binomial(n=1, p=0.7, size=100)
resultat = inferer_probabilite_succes(donnees_simulees)
print(f"Probabilité estimée : {resultat['moyenne']:.3f} "
      f"(IC 94 % : [{resultat['ic_94_inf']:.3f}, {resultat['ic_94_sup']:.3f}])")
```

### 1.3 Comparaison fréquentiste vs. bayésienne

| Aspect | Fréquentiste | Bayésien |
|---|---|---|
| Interprétation probabilité | Fréquence à long terme | Degré de croyance |
| Paramètres | Fixes (inconnus) | Variables aléatoires |
| A priori (prior) | Non utilisé | Obligatoire (subjectif ou non-informatif) |
| Résultat | Estimation ponctuelle + intervalle de confiance | Distribution a posteriori complète |
| Mise à jour incrémentale | Difficile | Naturelle (posterior → prior futur) |

---

## 2. Processus gaussiens (Gaussian Processes)

### 2.1 Modélisation non-paramétrique

Les processus gaussiens sont particulièrement adaptés à la régression avec quantification d'incertitude :

```python
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
import numpy as np

class RegressionGP:
    """Régression par processus gaussien avec quantification d'incertitude."""

    def __init__(self, longueur_echelle: float = 1.0,
                 bruit: float = 0.1, n_restarts: int = 5):
        """Initialise le régresseur GP avec un noyau RBF.

        Args:
            longueur_echelle: Échelle de longueur du noyau RBF.
            bruit: Niveau de bruit estimé dans les observations.
            n_restarts: Nombre de redémarrages pour l'optimisation des hyperparamètres.
        """
        noyau = ConstantKernel(1.0) * RBF(length_scale=longueur_echelle) \
                + WhiteKernel(noise_level=bruit)

        self.gp = GaussianProcessRegressor(
            kernel=noyau,
            n_restarts_optimizer=n_restarts,
            alpha=0.0,  # Bruit déjà géré par WhiteKernel
            normalize_y=True,
            random_state=42,
        )
        self.entraine = False

    def entrainer(self, X: np.ndarray, y: np.ndarray) -> None:
        """Entraîne le processus gaussien sur les données.

        Args:
            X: Caractéristiques d'entrée (n_echantillons, n_dimensions).
            y: Cibles (n_echantillons,).
        """
        self.gp.fit(X, y)
        self.entraine = True

    def predire(self, X_test: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prédit avec quantification d'incertitude.

        Args:
            X_test: Points de test (n_test, n_dimensions).

        Returns:
            Tuple (moyenne, écart_type, borne_inf_ic95, borne_sup_ic95).

        Raises:
            RuntimeError: Si le modèle n'a pas été entraîné.
        """
        if not self.entraine:
            raise RuntimeError("Le modèle doit être entraîné avant la prédiction.")

        moyenne, ecart_type = self.gp.predict(X_test, return_std=True)
        ic_inf = moyenne - 1.96 * ecart_type
        ic_sup = moyenne + 1.96 * ecart_type

        return moyenne, ecart_type, ic_inf, ic_sup


# Exemple d'utilisation
X = np.linspace(0, 10, 20).reshape(-1, 1)
y = np.sin(X).ravel() + np.random.normal(0, 0.1, X.shape[0])
gp = RegressionGP(longueur_echelle=1.5, bruit=0.05)
gp.entrainer(X, y)

X_test = np.linspace(0, 10, 100).reshape(-1, 1)
moy, std, ic_inf, ic_sup = gp.predire(X_test)
```

---

## 3. Quantification de l'incertitude (Uncertainty Quantification)

### 3.1 Types d'incertitude

| Type | Source | Réduction possible |
|---|---|---|
| **Aléatoire (Aleatoric)** | Bruit inhérent aux données, stochasticité | Non (augmenter les données n'aide pas) |
| **Épistémique** | Manque de connaissance, données insuffisantes | Oui (plus de données réduit l'incertitude) |
| **Modélisation** | Mauvais choix de structure du modèle | Oui (meilleur modèle) |

### 3.2 Détection d'out-of-distribution (OOD)

Les modèles probabilistes détectent naturellement les entrées hors distribution :

```python
class DetecteurOOD:
    """Détecte les entrées hors distribution via la vraisemblance du modèle."""

    def __init__(self, modele_gp: GaussianProcessRegressor, seuil: float = 0.05):
        self.modele = modele_gp
        self.seuil = seuil
        # Distribution de référence calculée sur les données d'entraînement
        self.vraisemblance_reference: float | None = None

    def calibrer(self, X_train: np.ndarray) -> None:
        """Calcule la vraisemblance de référence sur les données d'entraînement.

        Args:
            X_train: Données d'entraînement.
        """
        log_vraisemblances = self.modele.score_samples(X_train)
        self.vraisemblance_reference = np.percentile(log_vraisemblances, 5)

    def est_ood(self, X_test: np.ndarray) -> np.ndarray:
        """Vérifie si les points de test sont hors distribution.

        Args:
            X_test: Points à tester (n_test, n_dimensions).

        Returns:
            Tableau booléen : True si le point est OOD.

        Raises:
            RuntimeError: Si le modèle n'a pas été calibré.
        """
        if self.vraisemblance_reference is None:
            raise RuntimeError("Calibrez d'abord le détecteur avec calibrer().")

        log_vraisemblances = self.modele.score_samples(X_test)
        return log_vraisemblances < self.vraisemblance_reference
```

---

## 4. Exemple avancé : optimisation bayésienne

L'optimisation bayésienne utilise un processus gaussien pour modéliser une fonction coûteuse à évaluer :

```python
from scipy.stats import norm

def acquisition_ei(mean: np.ndarray, std: np.ndarray,
                   meilleur_connu: float, xi: float = 0.01) -> np.ndarray:
    """Fonction d'acquisition Expected Improvement (EI).

    Args:
        mean: Moyenne prédite par le GP.
        std: Écart-type prédit par le GP.
        meilleur_connu: Meilleure valeur observée à ce jour.
        xi: Paramètre d'exploration (plus xi est grand, plus on explore).

    Returns:
        Valeur d'Expected Improvement pour chaque point.
    """
    with np.errstate(divide='ignore'):
        diff = mean - meilleur_connu - xi
        z = diff / std
        ei = diff * norm.cdf(z) + std * norm.pdf(z)
        ei[std == 0.0] = 0.0
    return ei


def optimiser_bayesien(X_initial: np.ndarray, y_initial: np.ndarray,
                       limites: tuple, iterations: int = 20) -> list[dict]:
    """Optimisation bayésienne itérative avec Expected Improvement.

    Args:
        X_initial: Points initiaux déjà évalués.
        y_initial: Valeurs correspondantes.
        limites: (borne_inf, borne_sup) pour chaque dimension.
        iterations: Nombre d'itérations d'optimisation.

    Returns:
        Historique des itérations (itération, X, y, EI).
    """
    X = X_initial.copy()
    y = y_initial.copy()
    historique = []

    for i in range(iterations):
        gp = GaussianProcessRegressor(
            kernel=ConstantKernel(1.0) * RBF(length_scale_bounds=(1e-2, 1e2)),
            alpha=1e-6,
            normalize_y=True,
        )
        gp.fit(X, y)

        # Grille d'évaluation pour l'acquisition
        X_grid = np.linspace(limites[0], limites[1], 1000).reshape(-1, 1)
        mean, std = gp.predict(X_grid, return_std=True)
        ei = acquisition_ei(mean, std, y.max())

        # Sélection du prochain point (EI maximal)
        idx_optimal = np.argmax(ei)
        X_suivant = X_grid[idx_optimal]

        historique.append({
            "iteration": i + 1,
            "X_suivant": X_suivant[0],
            "EI_max": float(ei[idx_optimal]),
            "meilleur_y": float(y.max()),
        })

        # Simulation d'évaluation (remplacer par la vraie fonction)
        y_suivant = np.sin(X_suivant[0]) + np.random.normal(0, 0.01)
        X = np.vstack([X, X_suivant])
        y = np.append(y, y_suivant)

    return historique
```

---

## 5. Pièges courants (Pitfalls)

### 5.1 Mauvais choix de prior

> **Problème** : Un prior trop fort (ex. Beta(100, 1) pour une probabilité de succès) écrase les données, rendant l'inférence résistante aux observations.

**Solution** : Utilisez des priors faiblement informatifs. Visualisez toujours le prior seul avant d'ajouter les données. Préférez Beta(1, 1) [uniforme] ou Beta(2, 2) [faiblement informatif] par défaut.

### 5.2 Non-convergence des chaînes MCMC

> **Problème** : Les chaînes MCMC n'ont pas convergé, donnant des estimations a posteriori invalides.

**Solution** : Vérifiez systématiquement :
- **$\hat{R} < 1.01$** (potentiel de réduction d'échelle)
- **ESS (taille effective d'échantillon) > 400**
- Inspection visuelle des traces (arviz.plot_trace)

```python
def verifier_convergence(trace) -> bool:
    """Vérifie la convergence des chaînes MCMC."""
    resume = az.summary(trace)
    r_hat_max = resume["r_hat"].max()
    ess_min = resume["ess_bulk"].min()
    return r_hat_max < 1.01 and ess_min > 400
```

### 5.3 Oubli du coût computationnel

> **Problème** : Les méthodes MCMC et GP passent mal à l'échelle (MCMC : O(n²) par itération ; GP : O(n³) pour l'inversion de matrice).

**Solution** : Pour les grands jeux de données (> 10 000 points) :
- Utilisez des approximations variationnelles (ADVI, Pathfinder) au lieu de MCMC.
- Utilisez des GP approximatifs (Sparse GP, KISS-GP).

### 5.4 Mauvaise spécification du modèle (Model Misspecification)

> **Problème** : Le modèle probabiliste ne capture pas la structure réelle des données (ex. hypothèse de normalité violée).

**Solution** : Validez le modèle via **Posterior Predictive Checks** (PPC) :

```python
def ppc_check(trace, modele, donnees_observées: np.ndarray) -> float:
    """Posterior Predictive Check : compare les données simulées aux observées."""
    with modele:
        predictions = pm.sample_posterior_predictive(trace, progressbar=False)
    moyenne_simulee = predictions["observations"].mean()
    return abs(moyenne_simulee - donnees_observées.mean()) / donnees_observées.std()
```

---

## 6. Checklist de validation

- [ ] Le prior est-il justifié et documenté (informatif / faiblement informatif) ?
- [ ] La convergence des chaînes MCMC a-t-elle été vérifiée ($\hat{R} < 1.01$, ESS > 400) ?
- [ ] Un Posterior Predictive Check a-t-il été réalisé ?
- [ ] L'incertitude est-elle correctement séparée (aléatoire vs. épistémique) ?
- [ ] Le coût computationnel est-il compatible avec les ressources disponibles ?
- [ ] Les dépendances logicielles sont-elles installées (PyMC, ArviZ, scikit-learn) ?
- [ ] Les résultats sont-ils reproductibles (seed aléatoire fixée) ?
- [ ] Les intervalles de crédibilité sont-ils correctement interprétés (94 % HDI) ?
- [ ] La sensibilité au choix du prior a-t-elle été testée (analyse de robustesse) ?
- [ ] Le pipeline d'inférence est-il automatisé (script unique) ?

---

## 7. Extensions et intégrations

### 7.1 Modèles probabilistes profonds (Deep Probabilistic Programming)

Pour combiner réseaux de neurones et modélisation probabiliste :

| Bibliothèque | Usage | Particularité |
|---|---|---|
| [PyMC](https://www.pymc.io/) | Inférence bayésienne générale | MCMC, ADVI, interface Python native |
| [Pyro](https://pyro.ai/) | Deep probabilistic programming | Basé sur PyTorch, GPU natif |
| [TensorFlow Probability](https://www.tensorflow.org/probability) | Probabilistic ML | Intégration TF, distributions abondantes |
| [GPyTorch](https://gpytorch.ai/) | Processus gaussiens | Scalable GPU, Sparse GP |

### 7.2 Compétences complémentaires

- **`memory-management-ai`** : utiliser l'incertitude pour décider quelles informations conserver.
- **`ai-optimization-techniques`** : l'optimisation bayésienne comme méthode de tuning des hyperparamètres.
- **`creative-problem-solving-ai`** : utiliser les priors pour guider l'exploration créative.

---

## 8. Références

- `references/bayesian_workflow.md` : protocole complet de workflow bayésien (du prior au déploiement).
- `scripts/bayesian_ab_testing.py` : script d'analyse bayésienne pour tests A/B.
- `templates/bayesian_report_template.md` : template de rapport d'inférence bayésienne.

---

*Documentation maintenue par EVA Agent — Dernière mise à jour : 2025*
