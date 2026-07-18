---
name: hvac-industrial-ventilation
description: "Concevoir des systèmes de Génie Climatique (CVC/HVAC) industriels, dimensionner les réseaux aérauliques et centrales de traitement d'air (CTA), et concevoir des salles propres (salles blanches ISO 14644)."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [hvac, cvc, ventilation, cleanroom, air-handling-unit, psychrometric, filtration, iso-14644, aeraulic]
  EVA:
    related_skills: [cfd-fluid-dynamics, process-pharma, pid-instrumentation]
---

# Génie Climatique & Ventilation Industrielle (HVAC)

## Vue d'ensemble

Cette compétence guide la conception, le calcul et l'optimisation des systèmes de chauffage, ventilation et climatisation (**CVC / HVAC**) industriels. Elle couvre l'intégralité de la chaîne aéraulique, depuis le dimensionnement des réseaux de gaines de ventilation jusqu'à la configuration des centrales de traitement d'air (**CTA / AHU**), en passant par les calculs de charges thermiques, la psychrométrie de l'air humide et la conception avancée de zones de confinement à empoussièrement contrôlé (**salles blanches / salles propres**) régies par la norme internationale **ISO 14644**.

Les systèmes HVAC industriels diffèrent fondamentalement du génie climatique tertiaire par la puissance installée, la complexité des traitements d'air (filtration multi-étages, contrôle d'humidité, cascade de pression), et les exigences réglementaires spécifiques à chaque secteur : pharmacie (BPF), microélectronique (contamination particulaire), agroalimentaire (maîtrise des atmosphères), chimie (captation de polluants dangereux).

Cette compétence est conçue pour être actionnée par l'agent EVA lorsque l'utilisateur exprime un besoin lié à la conception, au dimensionnement, à l'optimisation ou au diagnostic de systèmes HVAC industriels ou de salles propres.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de façon explicite ou implicite de :

- Dimensionner un réseau de gaines de ventilation (calcul de débit d'air, vitesse, pertes de charge, sélection du ventilateur).
- Configurer les étages de filtration et les batteries de traitement thermique d'une Centrale de Traitement d'Air (CTA).
- Réaliser des calculs sur l'air humide à l'aide du diagramme psychrométrique de Mollier ou de Carrier (humidification, déshumidification, point de rosée).
- Définir les classes d'empoussièrement, les cascades de pression et les taux de renouvellement d'air pour une salle blanche ISO 5 à ISO 8.
- Concevoir des systèmes de captage de polluants à la source (poussières, vapeurs nocives, solvants, fumées de soudage).
- Auditer une installation existante pour améliorer son efficacité énergétique ou sa conformité réglementaire.

---

## Psychrométrie de l'air humide

La psychrométrie est la science du mélange air sec / vapeur d'eau. Elle est indispensable pour dimensionner les batteries de chauffe, de refroidissement, d'humidification et les tours de refroidissement.

### Grandeurs fondamentales

| Grandeur | Symbole | Unité | Définition |
|:---------|:--------|:------|:-----------|
| Température sèche | $T_s$ | °C | Température mesurée par un thermomètre standard |
| Température humide | $T_h$ | °C | Température mesurée par un thermomètre dont le bulbe est maintenu humide |
| Température de rosée | $T_r$ | °C | Température à laquelle la vapeur d'eau commence à condenser |
| Humidité absolue | $x$ | $\mathrm{g_{eau}/kg_{air \, sec}}$ | Masse de vapeur d'eau par masse d'air sec |
| Humidité relative | $HR$ | % | Rapport entre la pression partielle de vapeur et la pression de vapeur saturante |
| Enthalpie | $h$ | $\mathrm{kJ/kg_{air \, sec}}$ | Contenu énergétique total de l'air humide |

### Équations fondamentales

$$h = 1.006 \cdot T_s + x \cdot (2501 + 1.86 \cdot T_s)$$

$$HR = \frac{p_v}{p_{vs}(T)} \times 100$$

$$x = 0.622 \cdot \frac{p_v}{p_{atm} - p_v}$$

### Lecture du diagramme psychrométrique (Mollier)

Le diagramme psychrométrique représente les transformations de l'air humide. Les transformations types d'une CTA sont :

1. **Réchauffement sensible** : Trajectoire horizontale vers la droite ($x$ constant, $T_s$ augmente).
2. **Refroidissement sensible** : Trajectoire horizontale vers la gauche ($x$ constant, $T_s$ diminue).
3. **Refroidissement avec déshumidification** : Trajectoire descendante puis horizontale (passage sous le point de rosée, condensation).
4. **Humidification adiabatique** : Trajectoire le long d'une enthalpie constante ($h$ constant, $T_s$ diminue, $x$ augmente).

---

## Dimensionnement des réseaux de gaines

### Calcul des pertes de charge

La perte de charge totale $\Delta P_T$ dans un réseau de gaines est la somme des pertes de charge linéaires et singulières :

$$\Delta P_T = \Delta P_{lin} + \Delta P_{sing}$$

$$\Delta P_{lin} = \lambda \cdot \frac{L}{D_h} \cdot \frac{\rho \cdot v^2}{2}$$

$$\Delta P_{sing} = \xi \cdot \frac{\rho \cdot v^2}{2}$$

Où :
- $\lambda$ : Coefficient de frottement (fonction du nombre de Reynolds et de la rugosité)
- $L$ : Longueur de la gaine ($\mathrm{m}$)
- $D_h$ : Diamètre hydraulique ($\mathrm{m}$) : $D_h = \frac{2ab}{a+b}$ pour gaine rectangulaire
- $\rho$ : Masse volumique de l'air ($1.2 \, \mathrm{kg/m^3}$ à 20 °C)
- $v$ : Vitesse de l'air ($\mathrm{m/s}$)
- $\xi$ : Coefficient de perte de charge singulière (coudes, dérivations, registres)

### Vitesses recommandées dans les gaines

| Type de réseau | Vitesse recommandée | Perte de charge unitaire cible |
|:---------------|:-------------------|:------------------------------|
| Gaine principale (collecteur) | 6 – 8 m/s | 0.8 – 1.2 Pa/m |
| Gaine de distribution secondaire | 4 – 6 m/s | 0.5 – 0.8 Pa/m |
| Gaine de raccordement aux bouches | 2 – 4 m/s | 0.3 – 0.5 Pa/m |
| Soufflage flux laminaire (salle blanche) | 0.45 ± 0.05 m/s | N/A (vitesse de face) |
| Captage de polluants à la source | 10 – 20 m/s | Selon nature du polluant |

### Méthode de dimensionnement par perte de charge constante (Static Regain Method)

1. **Définir le débit total** $Q_{total}$ ($\mathrm{m^3/h}$) à partir des besoins de ventilation ($\text{nombre de renouvellements/h} \times \text{volume}$).
2. **Choisir une perte de charge unitaire cible** dans le tableau ci-dessus.
3. **Calculer le diamètre hydraulique équivalent** à l'aide d'abaques ou de la formule de Colebrook.
4. **Dimensionner chaque tronçon** en descendant l'arbre de distribution, en maintenant une perte de charge cumulée homogène entre les branches.
5. **Équilibrer le réseau** avec des registres de réglage.

---

## Centrales de Traitement d'Air (CTA)

### Configuration typique d'une CTA

```text
Air neuf (OA) ──► [Registre] ──► [Filtre G4] ──► [Filtre F7] ──► [Batterie froide] ──► [Batterie chaude]
                     │                                                                    │
                     └── (By-pass possible) ◄──────────────────────────────────────────────┘
                                                                                           │
                                                                                           ▼
    Reprise (RA) ──► [Filtre G4] ──► [Registre] ──► [CA / Mélange] ◄──────────────────────┘
                                                          │
                                                          ▼
                                             ┌──────────────────────┐
                                             │  Ventilateur de       │
                                             │  soufflage (Supply)   │
                                             └──────────┬───────────┘
                                                        │
                                                        ▼
Air soufflé (SA) ──► [Gaines] ──► [Filtre terminal] ──► [Locaux]
```

### Séquence de régulation typique d'une CTA

1. **Mesure** : Sonde de température et d'humidité en soufflage ($T_{SA}$, $HR_{SA}$) et en reprise ($T_{RA}$, $HR_{RA}$).
2. **Régulation de température** : Vanne 3 voies modulante sur batterie chaude/froide.
3. **Régulation d'humidité** : Humidificateur à vapeur (rampe d'injection) piloté par hygrostat.
4. **Régulation de pression** : Variateur de fréquence sur le moteur du ventilateur (CAV ou VAV).
5. **Économie d'énergie** : Registre de by-pass d'air neuf (free cooling) si $T_{ext}$ favorable.

---

## Conception de salles propres (ISO 14644)

Les salles propres sont des espaces où la concentration de particules en suspension dans l'air est maintenue en dessous de seuils définis. La norme **ISO 14644-1** définit les classes d'empoussièrement par la concentration maximale admissible de particules par $\mathrm{m^3}$ d'air.

### Classes ISO 14644-1

| Classe ISO | $\ge 0.1\,\mathrm{\mu m}$ | $\ge 0.3\,\mathrm{\mu m}$ | $\ge 0.5\,\mathrm{\mu m}$ | $\ge 1.0\,\mathrm{\mu m}$ | $\ge 5.0\,\mathrm{\mu m}$ |
|:----------|:--------------------------|:--------------------------|:--------------------------|:--------------------------|:--------------------------|
| **ISO 3** | 1 000 | 102 | 35 | 8 | — |
| **ISO 4** | 10 000 | 1 020 | 352 | 83 | — |
| **ISO 5** | 100 000 | 10 200 | 3 520 | 832 | 29 |
| **ISO 6** | 1 000 000 | 102 000 | 35 200 | 8 320 | 293 |
| **ISO 7** | — | — | 352 000 | 83 200 | 2 930 |
| **ISO 8** | — | — | 3 520 000 | 832 000 | 29 300 |

### Cascade de pression

La maîtrise de la contamination croisée entre zones de classes différentes s'effectue par des différences de pression statique :

- **Surpression ($+15$ à $+30\,\mathrm{Pa}$)** : Protège le produit contre l'intrusion de contaminants extérieurs. L'air s'écoule de la zone la plus propre vers la zone moins propre via les sas et les interstices.
- **Dépression ($-15$ à $-30\,\mathrm{Pa}$)** : Confine des substances dangereuses (poudres actives, agents pathogènes, toxiques). L'air est aspiré de l'extérieur vers la zone confinée, empêchant toute fuite.
- **Sas de transfert** : Sas à 2 portes verrouillées (interlock électronique), surpression/dépression réglée par registre de fuite calibré.

### Calcul du taux de renouvellement d'air

Le débit d'air soufflé $Q_{air}$ ($\mathrm{m^3/h}$) nécessaire pour maintenir la classe ISO est déterminé par le taux de renouvellement $R_{air}$ :

$$R_{air} = \frac{Q_{air}}{V_{local}}$$

| Classe ISO | Configuration | Taux de renouvellement ($\mathrm{h^{-1}}$) | Vitesse de l'air |
|:----------|:-------------|:-----------------------------------------|:----------------|
| ISO 5 | Flux laminaire unidirectionnel | 300 – 500 | 0.36 – 0.54 m/s |
| ISO 6 | Flux non-unidirectionnel | 60 – 100 | — |
| ISO 7 | Flux non-unidirectionnel | 30 – 60 | — |
| ISO 8 | Flux non-unidirectionnel | 15 – 30 | — |

### Filtration terminale

| Type de filtre | Norme EN 1822 | Efficacité MPPS | Application |
|:-------------|:-------------|:----------------|:------------|
| Préfiltration | G4 (grossier) | — | Protection des batteries, première barrière |
| Filtration fine | F7 – F9 | — | Air de confort, protection CTA |
| HEPA | H13 – H14 | $\ge 99.95\%$ (H13), $\ge 99.995\%$ (H14) | Salles blanches ISO 7/8 |
| ULPA | U15 – U17 | $\ge 99.9995\%$ (U15) | Salles blanches ISO 5, microélectronique |

**Règle de conception** : Les filtres HEPA/ULPA doivent être installés en position terminale, directement au plafond de la salle propre, au plus près des diffuseurs de soufflage, pour éviter la recontamination de l'air dans les gaines.

---

## Captage de polluants à la source

Les systèmes de ventilation industrielle doivent capter et évacuer les polluants émis par les procédés de fabrication (fumées de soudage, poussières de meulage, vapeurs de solvants, brouillards d'huile).

### Principes de conception

- **Captage au plus proche** : La hotte ou la bouche d'aspiration doit être placée au plus près de la source d'émission.
- **Vitesse de captage** : $v_{capt} \ge 0.5\,\mathrm{m/s}$ pour les vapeurs légères, $\ge 1.0\,\mathrm{m/s}$ pour les poussières, $\ge 2.0\,\mathrm{m/s}$ pour les fumées chaudes.
- **Débit d'extraction** : $Q_{ext} = A_{hotte} \times v_{capt}$.
- **Traitement de l'air extrait** : Filtration à manches, cyclones, scrubbers, adsorption sur charbon actif selon la nature du polluant.

---

## Pièges Courants (Common Pitfalls)

### 1. Vitesse d'air trop élevée dans les réseaux de gaines

**Erreur :** Dimensionner des conduits de ventilation trop étroits pour économiser la hauteur sous plafond ou le coût de la tôle, provoquant des vitesses d'air supérieures à 12 m/s dans les gaines principales desservant des locaux occupés. Conséquences : nuisances sonores (sifflements à large bande), pertes de charge décuplées, surconsommation énergétique du ventilateur (loi du carré pour $\Delta P$, puissance cubique).

**Correction :** Respecter les vitesses limites du tableau ci-dessus. Pour les réseaux traversant des zones de travail (bureaux, laboratoires), limiter à 4 m/s dans les branches terminales. Utiliser la méthode *Static Regain* pour équilibrer les pertes de charge entre branches.

### 2. Mauvais positionnement des filtres absolus HEPA

**Erreur :** Placer les filtres haute efficacité (HEPA H14) au niveau de la CTA (en local technique), puis distribuer l'air filtré via de longues gaines en tôle galvanisée. Les gaines, même propres, re-sédimentent des particules et polluent l'air stérile avant qu'il n'atteigne la salle blanche. La classe ISO visée devient impossible à atteindre.

**Correction :** Installer les caissons de filtration HEPA terminaux directement au plafond de la salle propre, en aval des gaines de distribution. Les gaines seront en dessous de la classe attendue, mais non critiques puisque le dernier étage de filtration se situe à la frontière de la zone contrôlée.

### 3. Absence de gestion des condensats dans la CTA

**Erreur :** Dimensionner la batterie froide de la CTA sans prévoir d'évacuation des condensats correctement dimensionnée et siphonnée. En été, l'air chaud et humide arrivant sur la batterie froide se condense abondamment ; l'eau stagne dans le bac, favorise le développement de légionelles et de moisissures, et peut déborder sur les gaines isothermes.

**Correction :** Prévoir un bac à condensats en inox (ou acier galvanisé avec revêtement anticorrosion), une évacuation avec siphon de hauteur suffisante ($H \ge \Delta P_{ventilateur} / (\rho g)$), des pentes $\ge 2\%$, et un traitement biocide régulier (UV ou chimique).

### 4. Oublier les contraintes de maintenance (accès aux filtres)

**Erreur :** Concevoir des caissons de filtration HEPA encastrés dans des faux plafonds sans trappe d'accès dimensionnée pour le changement des filtres. Lorsque les filtres arrivent en fin de vie (un à deux ans), l'exploitant doit démonter des dalles de plafond, voire des cloisons, pour accéder aux filtres, générant des coûts de maintenance disproportionnés et une contamination de la zone blanche.

**Correction :** Prévoir des trappes d'accès de dimensions suffisantes (minimum $600 \times 600\,\mathrm{mm}$) avec une hauteur libre au-dessus du plafond d'au moins $500\,\mathrm{mm}$ pour permettre le changement des filtres. Intégrer ces contraintes dès la phase de conception architecturale.

---

## Liste de vérification (Checklist)

- [ ] La cascade de pression entre les locaux et leurs sas est définie, mesurable par des manomètres et surveillée par des alarmes.
- [ ] Le taux de renouvellement d'air nominal est suffisant pour garantir la classe ISO de la salle blanche selon l'ISO 14644-1.
- [ ] Les étages de filtration de la CTA respectent la logique progressive : Préfiltration (G4) → Filtration fine (F7/F9) → Filtration absolue terminale (H13/H14).
- [ ] Le calcul du point de rosée sur le diagramme psychrométrique valide l'absence de condensation sur les parois froides ou dans les gaines de soufflage.
- [ ] La vitesse d'air au niveau des postes de travail à flux laminaire respecte 0.45 m/s ± 20 %.
- [ ] Les gaines de soufflage sont calorifugées pour éviter la condensation et les pertes thermiques.
- [ ] Un plan de maintenance des filtres (périodicité de changement, pression différentielle de référence) est établi.
- [ ] Les registres de coupure coupe-feu sont conformes à la réglementation incendie et testés périodiquement.
- [ ] Les extracteurs de polluants sont équipés d'une filtration adaptée à la nature des effluents (charbon actif, filtres à manches, cyclones).
- [ ] Le réseau de gaines est équilibré (mesures de débit aux bouches terminales et ajustement des registres).

