---
name: industrial-safety-sistema
description: "Utiliser quand l'utilisateur demande d'évaluer la sécurité des machines (conforme à l'ISO 13849-1), de calculer le niveau de performance (PL) ou d'utiliser le logiciel SISTEMA pour valider des boucles de sécurité."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [sistema, safety-integrity, iso-13849, safety-loops, industrial-standards]
  related_skills: [iso-safety, ot-security]
---

# Évaluation de la Sécurité des Machines & SISTEMA (ISO 13849-1)

## Vue d'ensemble

L'évaluation de la sécurité des machines selon la norme **ISO 13849-1** requiert le calcul du **Niveau de Performance (PL - Performance Level)** pour chaque fonction de sécurité (SRP/CS - Parties des systèmes de commande relatives à la sécurité). 

Pour modéliser et valider la conformité d'une machine, on utilise généralement le logiciel gratuit **SISTEMA** (Safety Integrity Software Tool for Evaluation of Machine Applications) édité par l'IFA.

SISTEMA évalue la fonction de sécurité à partir de 4 critères fondamentaux :
1.  **La Catégorie (Structure) :** Architecture de la boucle (Cat B, 1, 2, 3 ou 4). La catégorie 3/4 représente des structures double canal (redondantes).
2.  **Le $MTTF_d$ (Mean Time to Dangerous Failure) :** Temps moyen avant une défaillance dangereuse de chaque composant (exprimé en années). Pour les composants pneumatiques ou mécaniques, il est calculé à partir du $B_{10d}$ (nombre de cycles moyen avant défaillance) et du taux d'utilisation annuelle ($n_{op}$).
3.  **Le DC (Diagnostic Coverage) :** Taux de couverture du diagnostic (capacité du système à détecter ses propres pannes, ex: surveillance de la discordance temporelle ou contacts miroirs forcés sur les contacteurs).
4.  **Le CCF (Common Cause Failure) :** Mesures prises contre les défaillances de cause commune (séparation des câbles, diversité des technologies).

$$\text{PL Requis (PLr)} \geq \text{PL Calculé}$$

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De calculer le taux de sollicitation annuelle $n_{op}$ d'un capteur de sécurité.
- De modéliser une fonction de sécurité dans SISTEMA (saisie des blocs : Capteur, Logique, Actionneur).
- De convertir des valeurs de cycles $B_{10d}$ en valeurs temporelles $MTTF_d$.
- D'analyser le diagnostic de couverture (DC) d'une boucle double canal (contacts de retour d'état).

**Ne pas utiliser pour :**
- La programmation de la logique de sécurité de l'automate (utiliser `iso-safety` ou `rockwell-studio5000`).

---

## 1. Calcul du $MTTF_d$ pour un composant électromécanique

Contrairement aux composants électroniques, les composants mécaniques (ex: bouton d'arrêt d'urgence, capteur de porte d'accès mécanique, contacteurs de puissance) s'usent en fonction du nombre de cycles de manœuvres.

### Formule de calcul du nombre de cycles annuel ($n_{op}$) :

$$n_{op} = \frac{d_{op} \times h_{op} \times 3600}{t_{cycle}}$$

*   $d_{op}$ : jours de fonctionnement par an (ex: 220 jours).
*   $h_{op}$ : heures de fonctionnement par jour (ex: 16 heures).
*   $t_{cycle}$ : temps moyen entre le début de deux manœuvres successives du composant en secondes (ex: une ouverture de porte toutes les 10 minutes = 600 secondes).

### Formule de calcul du $MTTF_d$ :

$$MTTF_d = \frac{B_{10d}}{0.1 \times n_{op}}$$

### Exemple de script de calcul en Python :

```python
def calculate_mttfd(b10d, days_per_year, hours_per_day, cycle_time_sec):
    """
    Calcule le MTTFd d'un composant mécanique.
    b10d : cycles avant défaillance dangereuse de 10% des composants (donnée constructeur).
    """
    # Calcul du nombre de manoeuvres annuelles nop
    nop = (days_per_year * hours_per_day * 3600.0) / cycle_time_sec
    
    if nop <= 0:
        return {"success": False, "error": "Le nombre de manoeuvres annuelles doit être supérieur à 0."}
        
    # Calcul du MTTFd en années
    mttf_d = b10d / (0.1 * nop)
    
    # Classification réglementaire selon l'ISO 13849-1
    # Limites : Low (3-10 ans), Medium (10-30 ans), High (30-100 ans)
    if mttf_d < 3:
        status = "INSUFFISANT (inférieur à 3 ans)"
    elif mttf_d < 10:
        status = "LOW (Faible)"
    elif mttf_d < 30:
        status = "MEDIUM (Moyen)"
    else:
        status = "HIGH (Élevé)"
        
    return {
        "success": True,
        "n_op_cycles_per_year": round(nop, 1),
        "mttf_d_years": round(mttf_d, 1),
        "classification": status
    }

# Exemple d'appel :
# Bouton Arrêt d'urgence avec B10d = 100 000 cycles.
# Usine ouverte 300 jours/an, 24h/24. Le bouton est testé (sollicité) une fois par poste (toutes les 8 heures = 28800s).
result = calculate_mttfd(b10d=100000, days_per_year=300, hours_per_day=24, cycle_time_sec=28800)
print(result)
# Sortie : {'success': True, 'n_op_cycles_per_year': 900.0, 'mttf_d_years': 1111.1, 'classification': 'HIGH (Élevé)'}
# Note : L'ISO 13849-1 plafonne le MTTFd de chaque composant individuel à 100 ans max dans les calculs finaux de boucle.
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Mauvaise classification du DC (Diagnostic Coverage) :**
    *   *Erreur :* Déclarer une boucle en Catégorie 3 ou 4 (double canal) mais ne pas câbler de retour d'état (contacts miroirs forcés sur les contacteurs de puissance) vers l'automate de sécurité. Le DC calculé sera alors de 0% (ou "Aucun"), ce qui disqualifie le système pour obtenir un PL d ou PL e.
    *   *Correction :* Toujours connecter le retour d'état des actionneurs en série sur les entrées de diagnostic de l'automate de sécurité, et configurer le DC à "Low/Medium/High" dans SISTEMA selon le niveau de surveillance logicielle mis en place.
2.  **Ignorer les Common Cause Failures (CCF) :**
    *   *Erreur :* Câbler les deux canaux de sécurité (Voie A et Voie B) dans le même câble blindé multibrins. Si le câble est écrasé, les deux canaux peuvent court-circuiter ensemble, annulant la redondance.
    *   *Correction :* Assurer une séparation physique des câbles, ou utiliser des filtres d'impulsions (Test Pulses) de l'automate de sécurité pour détecter les courts-circuits croisés.

---

## Liste de vérification (Checklist)

- [ ] La structure de la fonction de sécurité (SISTEMA : Capteur ➔ Logique ➔ Actionneur) est modélisée conformément au schéma de câblage réel.
- [ ] Les données constructeurs ($B_{10d}$ ou $MTTF_d$ en années) des composants de sécurité sont issues des fiches techniques fabricants.
- [ ] La fréquence d'utilisation réelle ($n_{op}$) a été validée avec les cadences opérationnelles réelles de l'usine.
- [ ] Le calcul de l'indice CCF atteint un score réglementaire de 65 points ou plus dans SISTEMA.

