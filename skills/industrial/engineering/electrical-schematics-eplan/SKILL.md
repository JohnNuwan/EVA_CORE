---
name: electrical-schematics-eplan
description: "Concevoir, analyser et vérifier des schémas électriques industriels (puissance, commande, distribution) sous EPLAN Electric P8 ou AutoCAD Electrical selon les normes IEC 60204-1."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [electrical, engineering, schematics, eplan, eplan-electric-p8, autocad-electrical, cad, iec-60204, iec-81346, wiring, control-panel, bom]
    related_skills: [electrical-cabinet-3d, cad-bom-automation, pid-instrumentation]
---

# Génie Électrique et Conception de Schémas (EPLAN)

## Vue d'ensemble

Cette compétence encadre la conception, l'analyse et la vérification des schémas électriques pour les armoires industrielles de puissance et de commande, de la distribution MT/BT jusqu'aux circuits de commande. La conception électrique s'appuie sur des outils de CAO dédiés comme **EPLAN Electric P8**, **AutoCAD Electrical** ou **SEE Electrical**, qui permettent de produire des dossiers d'exécution complets incluant les schémas, la nomenclature, les plans de borniers, les plans de câblage et les étiquettes de repérage.

La conformité réglementaire est assurée par le respect des normes internationales suivantes :

- **CEI (IEC) 60204-1** : Sécurité des machines — Équipement électrique des machines. Norme fondamentale couvrant la protection contre les contacts directs/indirects, la coupure d'urgence, les sections de conducteurs et les couleurs de fils.
- **CEI (IEC) 81346** : Systèmes industriels — Principes de structuration et désignation de référence. Définit le système de repérage des équipements (fonction, emplacement, produit).
- **CEI (IEC) 61439-1/2** : Ensembles d'appareillage à basse tension (GBT). Homologation des armoires de distribution.

La CAO électrique ne se limite pas au dessin : chaque composant est une entrée de base de données avec des attributs (référence constructeur, catalogue, symbole graphique, bornes associées, puissance dissipée). L'exploitation de cette base est ce qui différencie un simple dessinateur d'un ingénieur électricien concepteur.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Concevoir un schéma de câblage de puissance et de commande pour une armoire de commande de machine-outil, convoyeur, pompe ou compresseur.
- Sélectionner et dimensionner des composants électriques : disjoncteurs magnéto-thermiques, contacteurs, relais de protection thermique, sectionneurs, câbles, borniers.
- Vérifier la conformité d'un schéma par rapport aux normes industrielles (protection contre les surcharges et les courts-circuits, coupure d'urgence conformément à IEC 60204-1 §9.2).
- Structurer un projet de CAO électrique : nomenclature complète (BOM), repérage d'équipements selon IEC 81346, plans de borniers, plans de câblage, étiquetage.
- Analyser un schéma existant pour identifier un défaut de câblage, une protection manquante ou un non-respect des distances de sécurité.

## Exemple de Conception : Départ-Moteur Triphasé Standard

Voici la structure de principe d'un circuit de puissance pour un départ-moteur triphasé avec démarrage direct (le circuit de commande n'est pas représenté ici) :

```text
        L1      L2      L3      PE
        │       │       │       │
    ┌───┴───────┴───────┴───────┼─────┐
    │            Q1             │     │   Sectionneur à fusible
    │     Sectionneur de        │     │   ou disjoncteur de tête
    │     sécurité              │     │   (IEC 60204-1 §5.3)
    └─────────┬───────┬─────────┼─────┘
              │       │         │
    ┌─────────┴───────┴─────────┼─────┐
    │           QM1            │     │   Disjoncteur magnéto-thermique
    │   Protection moteur       │     │   moteur (IEC 60947-2)
    │   I_th = In_moteur        │     │
    └─────────┬───────┬─────────┼─────┘
              │       │         │
    ┌─────────┴───────┴─────────┼─────┐
    │           KM1            │     │   Contacteur tripolaire
    │   Bobine de commande      │     │   (IEC 60947-4-1)
    │   A1-A2 = 24Vdc           │     │
    └─────────┬───────┬─────────┼─────┘
              │       │         │
    ┌─────────┴───────┴─────────┼─────┐
    │           F1             │     │   Relais thermique
    │   Protection surcharge    │     │   (IEC 60947-4-1)
    │   I_r = In_moteur         │     │   Contacts 95-96 NC, 97-98 NO
    └─────────┬───────┬─────────┼─────┘
              │       │         │
              ▼       ▼         ▼
           [ Moteur M1 ]      [ PE ]
           Pompe / Convoyeur
           P = 5.5 kW
           I_n = 11.5 A (400V)
```

### Dimensionnement du Départ-Moteur

1. **Disjoncteur moteur (QM1)** : Régler le déclencheur magnétique à $10 \times I_n$ (pointe de démarrage) et le thermique à $I_n$ nominal.
2. **Section des conducteurs** : Pour $I_n = 11.5\;A$, utiliser une section minimale de $1.5 mm^2$ en cuivre (PVC, pose en goulotte). Si la chute de tension sur $50\;m$ doit rester $< 3\%$, porter à $2.5 mm^2$.
3. **Pouvoir de coupure ($I_{cu}$)** : Le disjoncteur QM1 doit avoir un pouvoir de coupure $I_{cu} \ge I_{cc}$ au point d'installation. Pour une armoire située à $50\;m$ du transformateur $630\;kVA$, $I_{cc}$ est typiquement de $15\;kA$, donc choisir $I_{cu} \ge 25\;kA$.
4. **Relais thermique (F1)** : Classe 10A (déclenchement entre 4 et 10 secondes à $7.2 \times I_r$) pour protéger le moteur sans déclencher sur le démarrage.

## Règles de Dimensionnement Avancées

### Sections de conducteurs (IEC 60204-1 Tableau 6)

Extrait des sections minimales pour conducteurs en cuivre PVC (température ambiante $40°C$, pose en goulotte, 3 conducteurs chargés) :

| Section ($mm^2$) | Courant admissible ($A$) | Usage typique |
|:---:|:---:|:---|
| $0.75$ | $9$ | Commande (24 Vdc) |
| $1.0$ | $11$ | Commande (24 Vdc, 230 Vac) |
| $1.5$ | $16$ | Puissance petite machine |
| $2.5$ | $22$ | Puissance / prises |
| $4.0$ | $30$ | Distribution |
| $6.0$ | $38$ | Distribution / alimentation |
| $10$ | $52$ | Arrivée puissance |

### Chute de tension

$$\Delta U(\%) = \frac{\sqrt{3} \times I \times L \times (R \cdot \cos\phi + X \cdot \sin\phi)}{U_n} \le 3\%$$

Pour une ligne triphasée en cuivre à $400\;V$, en négligeant la réactance :

$$\Delta U(\%) \approx \frac{0.06 \times I \times L}{S}$$

Où $I$ est le courant ($A$), $L$ la longueur ($m$), $S$ la section ($mm^2$).

### Pouvoir de coupure

Le pouvoir de coupure ($I_{cu}$ ou $I_{cs}$) d'un disjoncteur doit être au moins égal au courant de court-circuit présumé ($I_{cc}$) au point d'installation. $I_{cc}$ se calcule par :

$$I_{cc} = \frac{U_n}{\sqrt{3} \times Z_{boucle}}$$

Où $Z_{boucle}$ est l'impédance de la boucle de défaut vue du point considéré. En l'absence de calcul précis, une valeur $I_{cc} \ge 25\;kA$ est typique pour une armoire secondaire BT.

## Système de Repérage IEC 81346

La norme IEC 81346 remplace l'ancienne notation européenne. Elle structure l'identification des équipements selon trois aspects :

| Aspect | Préfixe | Exemple | Signification |
|:---|:---:|:---|:---|
| Fonction | `=` | `=L1=F1` | Fonction « Protection générale » du lot 1 |
| Emplacement | `+` | `+CAB1` | Emplacement « Coffret 1 » |
| Produit (composant) | `-` | `-KM2` | Composant « Contacteur KM2 » |

Un repérage complet combine les trois : `=L1+CAB1-KM2` se lit « le contacteur KM2 situé dans le coffret CAB1 de la fonction L1 ». La borne A1 de ce contacteur se note `=L1+CAB1-KM2:A1`.

### Codes de désignation des produits (extrait de la norme)

| Code | Composant |
|:---:|:---|
| `-F` | Dispositif de protection (fusible, disjoncteur, relais thermique) |
| `-K` | Contacteur, relais, temporisateur |
| `-M` | Moteur, machine tournante |
| `-Q` | Sectionneur, interrupteur |
| `-S` | Capteur, interrupteur de position, bouton-poussoir |
| `-T` | Transformateur, alimentation |
| `-X` | Bornier, connecteur |
| `-Y` | Électrovanne, actionneur électromagnétique |

## Pièges Courants (Common Pitfalls)

1. **Repérage incohérent des borniers (mauvaise structuration IEC 81346) :**
   - *Erreur :* Assigner arbitrairement des numéros de fil sans respecter la structure d'emplacement (`+Emplacement`). À la fabrication, l'électricien de câblage se retrouve avec des fils étiquetés « 1 », « 2 », « 3 » qui ne veulent rien dire seuls.
   - *Correction :* Appliquer strictement la norme IEC 81346. Un repérage de borne typique dans EPLAN suit la syntaxe : `=Lot+Emplacement-Composant:Borne`. Exemple : `=L1+CAB1-KM2:A1`. La numérotation des borniers doit être séquentielle et unique par emplacement (`-X1:01`, `-X1:02`, etc.).

2. **Oubli de la protection différentielle et de la mise à la terre :**
   - *Erreur :* Omettre de relier les masses métalliques (portes d'armoire, châssis) au collecteur de terre (PE), ou utiliser un mauvais type de disjoncteur différentiel (ex : Type AC au lieu de Type B pour des variateurs de vitesse).
   - *Correction :* Relier systématiquement toutes les portes métalliques au collecteur PE via des tresses en cuivre (section minimale $6 mm^2$). Choisir le type de protection différentielle selon la norme IEC 60755 : **Type AC** pour charges résistives (éclairage) ; **Type A** pour charges électroniques monophasées ; **Type B** pour variateurs de vitesse, onduleurs et chargeurs de batteries.

3. **Mauvaise coordination des protections (sélectivité non assurée) :**
   - *Erreur :* En cas de défaut sur un départ aval ($I_{cc} = 3\;kA$), c'est le disjoncteur général en tête (calibre $630\;A$) qui saute au lieu du disjoncteur aval ($20\;A$), privant toute l'armoire de tension.
   - *Correction :* Vérifier la sélectivité ampèremétrique (les seuils magnétiques du disjoncteur aval doivent être inférieurs au seuil du disjoncteur amont) et chronométrique (les courbes de déclenchement ne doivent pas se chevaucher). Utiliser des disjoncteurs avec sélectivité totale (catégorie B selon IEC 60947-2).

4. **Absence de séparation fonctionnelle entre circuits ELV et LV :**
   - *Erreur :* Acheminer des fils 24 Vdc (ELV) dans la même goulotte que des fils 230 Vac (LV) sans séparation physique. En cas de défaut d'isolement, le 230 Vac se retrouve sur le bus 24 Vdc et détruit les cartes électroniques (PLC, variateurs).
   - *Correction :* Séparer physiquement les circuits ELV (Extra Low Voltage, $< 50\;V$) et LV (Low Voltage, $> 50\;V$) par des goulottes distinctes ou une cloison de séparation. Utiliser des couleurs d'isolant différentes : rouge/orange pour le 230 Vac commande, bleu clair pour le 24 Vdc, jaune/vert pour la terre.

5. **Nomenclature BOM (Bill of Materials) incomplète ou imprécise :**
   - *Erreur :* Exporter la nomenclature sans références fabricant complètes (ex : « Contacteur 9A 24Vdc » sans marque ni référence). L'approvisionnement ne peut pas acheter le bon composant.
   - *Correction :* Maintenir une base de données de composants à jour dans la CAO, avec pour chaque article : référence constructeur, fabricant, prix, délai, puissance dissipée, poids, dimensions (empreinte 3D si EPLAN Pro Panel est utilisé).

## Liste de vérification (Checklist)

- [ ] Tous les conducteurs ont leur section définie selon le courant nominal (IEC 60204-1 Tableau 6) et leur couleur selon la fonction (rouge pour AC commande, bleu clair pour DC commande, vert/jaune pour PE, noir pour puissance).
- [ ] Le pouvoir de coupure des disjoncteurs est supérieur ou égal au courant de court-circuit présumé au point d'installation ($I_{cu} \ge I_{cc}$).
- [ ] Les protections thermiques et magnétiques sont réglées selon la plaque signalétique des moteurs ($I_r = I_n$).
- [ ] La sélectivité des protections est assurée entre le disjoncteur général et les départs (sélectivité ampèremétrique et/ou chronométrique).
- [ ] La nomenclature (BOM) exportée contient les références fabricant exactes, les quantités et les désignations normalisées (IEC 81346).
- [ ] Les circuits ELV (24 Vdc) et LV (230/400 Vac) sont physiquement séparés dans des goulottes distinctes.
- [ ] Toutes les masses métalliques (portes, panneaux, châssis) sont reliées au collecteur PE avec une section $\ge 6 mm^2$.
- [ ] Les protections différentielles sont du type adapté aux charges connectées (Type A, B ou AC selon IEC 60755).
- [ ] La chute de tension maximale entre l'arrivée et le récepteur le plus éloigné est inférieure à $3\%$.
- [ ] Les plans de borniers (terminal diagrams) et les plans de câblage (wiring diagrams) sont générés et vérifiés.

