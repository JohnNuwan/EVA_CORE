---
name: pid-instrumentation
description: "Concevoir, interpréter et documenter des schémas de procédé P&ID (Piping & Instrumentation Diagram) et sélectionner l'instrumentation industrielle (capteurs, vannes, transmetteurs) selon la norme ISA-5.1."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [piping, instrumentation, pid, isa-51, isa-20, process, sensors, valves, control-loops, loop-diagram, engineering]
    related_skills: [electrical-schematics-eplan, pid-tuning-control, electrical-cabinet-3d]
---

# Schémas P&ID et Instrumentation Industrielle

## Vue d'ensemble

Cette compétence encadre l'élaboration, la lecture critique et la documentation des schémas de tuyauterie et d'instrumentation (**P&ID — Piping and Instrumentation Diagram**) ainsi que la sélection des instruments de mesure et de contrôle associés pour les procédés industriels continus et discontinus (batch). Les conventions de représentation graphique et d'identification des instruments (le « Tagging ») suivent principalement la norme nord-américaine **ISA-5.1-2022** (*Instrumentation Symbols and Identification*) et son équivalent européen **EN ISO 10628** (*Schémas de procédé pour les installations industrielles*).

Un P&ID n'est pas un simple dessin : c'est un contrat technique entre les disciplines génie des procédés, génie mécanique, instrumentation et contrôle-commande. Il définit :

- La topologie du réseau de tuyauterie (diamètres, matériaux, accessoires).
- La boucle de régulation dans son intégralité (capteur $\rightarrow$ transmetteur $\rightarrow$ contrôleur $\rightarrow$ actionneur $\rightarrow$ procédé).
- Les interfaces avec le système de contrôle (DCS, PLC, SIS).
- Les conditions de sécurité en mode dégradé (fail-safe).

Cette compétence couvre également la spécification technique des instruments principaux (débitmètres, capteurs de pression, température et niveau, vannes de régulation) selon les normes ISA-20 et les bonnes pratiques de l'industrie.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Interpréter un schéma P&ID complexe contenant des boucles de régulation de température, pression, débit ou niveau, y compris les interverrouillages de sécurité (SIS).
- Spécifier un instrument physique : capteur de température PT100 avec émetteur, débitmètre électromagnétique, capteur de pression différentielle, vanne de régulation à cage ou à siège excentré.
- Attribuer des codes d'identification (tags) à des équipements selon la nomenclature ISA-5.1 (ex : FIT-101, TCV-202, PSV-301).
- Définir des boucles de contrôle de procédé avec leurs interconnexions physiques (signaux analogiques 4-20 mA, numériques Modbus/Profibus, logiques TOR).
- Vérifier la cohérence entre le P&ID et le diagramme de boucle (Loop Diagram) pour le câblage et le paramétrage du système de contrôle.
- Établir une nomenclature d'instruments (Instrument Index) pour un projet d'ingénierie complet.

## Convention d'Identification ISA-5.1

Le repérage (tag) d'un instrument est composé de lettres de désignation suivies d'un numéro de boucle, éventuellement complétées par un suffixe :

```text
                     TIC - 102
                      │││   │
                      │││   └── Numéro de boucle (unique par unité)
                      ││└────── Fonction de commande/régulation (Control)
                      │└─────── Fonction de lecture/affichage (Indicate)
                      └──────── Grandeur physique mesurée (Temperature)
```

Un tag complet peut inclure un préfixe d'unité fonctionnelle et un suffixe de zone :

```text
       10 - PIT - 201 - A
        │     │    │    │
        │     │    │    └── Suffixe (A, B : redondance)
        │     │    └─────── Numéro de boucle
        │     └──────────── Code instrument (P=Pressure, I=Indicator, T=Transmitter)
        └────────────────── Numéro d'unité (Zone 10)
```

### Lettres d'identification fréquentes (ISA-5.1)

| 1<sup>ère</sup> lettre (grandeur) | Signification |
|:---|:---|
| **F** | Flow (Débit) |
| **P** | Pressure (Pression) |
| **L** | Level (Niveau) |
| **T** | Temperature (Température) |
| **A** | Analysis (Analyse, pH, conductivité, O₂) |
| **D** | Density (Densité) |
| **V** | Viscosity (Viscosité) |

| Lettres subséquentes (fonction) | Signification |
|:---|:---|
| **I** | Indicator (Affichage local) |
| **R** | Recorder (Enregistreur) |
| **C** | Controller (Régulateur) |
| **T** | Transmitter (Transmetteur) |
| **V** | Valve (Vanne) |
| **S** | Switch (Contact / seuil) |
| **A** | Alarm (Alarme) |
| **H** / **L** | High / Low (Haut / Bas — en suffixe) |

### Exemples de tags

| Tag | Signification |
|:---|:---|
| `FIT-101` | Flow Indicator Transmitter — Transmetteur indicateur de débit (boucle 101) |
| `FCV-102` | Flow Control Valve — Vanne de régulation de débit (boucle 101 / cascade FT) |
| `PIT-201` | Pressure Indicator Transmitter — Transmetteur de pression |
| `PSV-201` | Pressure Safety Valve — Soupape de sécurité |
| `LIT-301` | Level Indicator Transmitter — Transmetteur de niveau |
| `LSH-302` | Level Switch High — Contact de niveau haut |
| `TT-401` | Temperature Transmitter — Transmetteur de température |
| `TE-401` | Temperature Element — Élément de mesure (thermocouple, PT100) |
| `XV-501` | Isolation Valve (On/Off) — Vanne d'arrêt tout-ou-rien |
| `YV-502` | Solenoid Valve — Électrovanne associée à un vérin |

## Typologie des Signaux et Représentation Graphique

Le P&ID utilise des conventions de lignes strictes pour distinguer la nature des liaisons :

| Type de ligne | Signification | Exemple d'utilisation |
|:---|:---|:---|
| **Trait continu épais** | Tuyauterie de procédé | Conduite principale du fluide |
| **Trait fin continu** | Tuyauterie auxiliaire | Purge, vidange, évent, drain |
| **Trait pointillé fin** | Signal électrique analogique (4-20 mA) | Laison transmetteur $\to$ DCS |
| **Trait discontinu (tirets)** | Signal électrique logique (24 Vdc) | Commande TOR d'une vanne |
| **Trait mixte (point-trait)** | Signal pneumatique ou hydraulique | Tube 3-15 psi vers positionneur |
| **Double barre oblique** | Laison réseau numérique | Modbus RTU, Profibus PA, Foundation Fieldbus |
| **Trait ondulé** | Laison capillaire | Tube à distance pour manomètre à membrane |

## Sélection des Instruments de Mesure

### Débitmètres

| Technologie | Fluides typiques | Avantages | Limites |
|:---|:---|:---|:---|
| Électromagnétique | Eau, eaux usées, boues conductrices ($\sigma \ge 5\,\mu S/cm$) | Aucune perte de charge, grande précision ($\pm 0.2\%$) | Ne convient pas aux gaz, ni aux liquides non conducteurs |
| Vortex | Liquides, gaz, vapeur | Robustesse, pas de pièces mobiles | Sensible aux vibrations amont (nécessite $10D$ droit) |
| Massique (Coriolis) | Tous fluides (y compris non-conducteurs) | Mesure directe de masse et densité, très précis ($\pm 0.1\%$) | Coût élevé, perte de charge notable |
| Ultrasonore (TDM) | Liquides propres, eaux chargées | Non intrusif, installation en dérivation ou clamp-on | Précision moindre ($\pm 0.5\%$ à $1.5\%$) |

### Vannes de Régulation

Le choix du corps de vanne dépend du fluide, du $\Delta P$ et du débit :

- **Vanne à siège simple (Globe Valve)** : Standard pour la régulation de débit et de pression. Bonne plage de réglage (Rangeability $50:1$). Étanchéité modérée.
- **Vanne à cage (Cage Valve)** : Dérivée de la vanne globe avec cage de guidage. Idéale pour les hauts $\Delta P$ et la réduction de bruit.
- **Vanne papillon (Butterfly Valve)** : Grands diamètres ($DN \ge 200$), faible coût, faible perte de charge. Utilisable en régulation mais avec une plage réduite ($20:1$).
- **Vanne à bille segmentée (V-Ball Valve)** : Fluides chargés (pâtes, boues). Effet de cisaillement, bon pour les fluides à fibres.
- **Vanne à excentrique (Eccentric Rotary Plug)** : Fluides très chargés ou abrasifs, grande plage de réglage ($100:1$).

## États de Défaillance (Fail-Safe)

Toute vanne automatique doit avoir un état de sécurité défini en cas de perte d'énergie motrice (air, électricité, hydraulique) :

| Code | Signification | Symbole P&ID |
|:---|:---|:---|
| **FC** | Fail Closed (Fermée) | Flèche orientée vers le bas à gauche de la bulle pneumatique |
| **FO** | Fail Open (Ouverte) | Flèche vers le haut à gauche |
| **FL** | Fail Locked (Verrouillée) | Cadenas à gauche |
| **FD** | Fail Last Position (Dernière position maintenue) | Losange à gauche |

## Pièges Courants (Common Pitfalls)

1. **Confusion entre vannes d'arrêt et de régulation :**
   - *Erreur :* Indiquer une vanne papillon Tout-ou-Rien (tagguée **XV**) sur un P&ID lorsque la boucle nécessite un contrôle proportionnel fin du débit. Une vanne TOR n'a pas de positionneur, sa courbe caractéristique n'est pas adaptée à la régulation continue.
   - *Correction :* Utiliser les symboles et tags corrects. Une vanne d'isolement est tagguée **XV** ou **YV** (avec électrovanne associée). Une vanne de contrôle continue est tagguée **FCV**, **PCV**, **LCV** ou **TCV** et possède un positionneur et un convertisseur I/P.

2. **Oubli des conditions de défaillance (Fail-Safe) :**
   - *Erreur :* Ne pas spécifier l'état de sécurité d'une vanne en cas de perte d'air comprimé ou de puissance électrique. En situation d'urgence, l'opérateur ne peut pas savoir si la vanne s'est fermée, ouverte ou maintenue.
   - *Correction :* Indiquer systématiquement sur le P&ID l'état de repli : **FC** (fermée par manque d'air/ressort), **FO** (ouverte par ressort), **FL** (verrouillée). Cette information est également reportée dans la spécification technique de la vanne (Data Sheet).

3. **Boucle de régulation incomplète ou incohérente entre P&ID et Loop Diagram :**
   - *Erreur :* Le P&ID montre un transmetteur FT-101 qui envoie un signal au DCS, mais le Loop Diagram ne précise pas le type de signal, l'alimentation électrique ni le câblage de terre. L'installation est impossible sans ces informations.
   - *Correction :* S'assurer que le Loop Diagram (schéma de boucle) détaille pour chaque instrument : le type de signal (4-20 mA HART, Profibus PA), la référence du câble, le bornier de raccordement, l'alimentation (24 Vdc, 230 Vac) et la mise à la terre.

4. **Absence de considération des conditions de procédé (Pression, Température) :**
   - *Erreur :* Spécifier un débitmètre électromagnétique avec une garniture en PTFE standard pour un fluide à $220°C$. Le PTFE se dégrade au-delà de $180°C$ et la colle du revêtement se décompose.
   - *Correction :* Vérifier la température maximale de service ($T_{max}$), la pression maximale admissible ($P_{max}$) et la compatibilité chimique des matériaux en contact avec le fluide (wetted parts) : PTFE ($-50°C$ à $+180°C$), PFA ($-50°C$ à $+210°C$), PEEK ($-50°C$ à $+260°C$), élastomères EPDM ($-40°C$ à $+150°C$).

5. **Non-respect des distances de débitmètre (partie droite amont/aval) :**
   - *Erreur :* Installer un débitmètre vortex à moins de $5$ diamètres en aval d'un coude brusque. Les turbulences non résorbées faussent la mesure de plus de $10\%$.
   - *Correction :* Respecter les préconisations de l'ISA-20 : pour un débitmètre vortex ou électromagnétique, prévoir $10D$ de conduite droite amont et $5D$ aval. Pour un débitmètre ultrasonore, $15D$ amont et $7D$ aval.

## Liste de vérification (Checklist)

- [ ] Tous les instruments possèdent un tag unique conforme à la norme ISA-5.1, incluant les lettres de grandeur et de fonction appropriées.
- [ ] Les types de lignes du P&ID distinguent clairement les fluides procédés des signaux de contrôle (électriques, pneumatiques, réseau numérique).
- [ ] L'état de sécurité en cas de panne (FC, FO, FL, FD) est renseigné pour toutes les vannes automatiques.
- [ ] Les diamètres nominaux (DN), les classes de pression (PN/Class) et les matériaux de tuyauterie sont indiqués sur les conduites principales.
- [ ] Les instruments sont compatibles avec les conditions de service ($T_{max}$, $P_{max}$, agressivité chimique) et les matériaux en contact sont spécifiés.
- [ ] Les débitmètres sont installés avec les longueurs droites amont/aval suffisantes ($10D$ / $5D$ minimum).
- [ ] Les boucles de régulation sont cohérentes entre le P&ID et le Loop Diagram (type de signal, alimentation, câblage, terre).
- [ ] Les numéros de boucle sont uniques et une nomenclature d'instruments (Instrument Index) est tenue à jour.
- [ ] Les soupapes de sécurité (PSV, RV) sont dimensionnées selon le code ASME VIII ou ISO 4126 avec leur capacité de décharge.
- [ ] Les interverrouillages de sécurité (SIS) sont clairement identifiés et séparés des boucles de régulation standard (BPCS).

