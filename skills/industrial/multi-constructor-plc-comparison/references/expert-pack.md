# Pack Expert Comparatif Multi-Constructeurs

## Objectif

Fournir une méthode de comparaison robuste entre plateformes automates pour éviter les choix basés uniquement sur l'habitude locale. Ce pack sert à sélectionner un constructeur, préparer une migration, ou définir une standardisation groupe.

## 1. Grille d'évaluation recommandée

Évaluer chaque plateforme selon :
- adéquation au type d'application : machine, process, utilités, edge ;
- motion et servo ;
- safety ;
- intégration SCADA/MES/OT-IT ;
- ouverture protocolaire ;
- outillage engineering ;
- maintenabilité locale ;
- disponibilité des compétences ;
- coût de cycle de vie ;
- stratégie de standardisation multi-sites.

## 2. Questions de cadrage avant comparaison

- Le projet est-il machine discrète, process, batch, utilités ou architecture edge ?
- Le motion est-il critique ou secondaire ?
- La safety est-elle basique, intégrée ou très exigeante ?
- Le site doit-il converger vers un standard groupe ?
- Les équipes locales maîtrisent-elles déjà fortement un constructeur ?
- L'ouverture OT/IT est-elle un critère clé ?

## 3. Référentiel de lecture par famille

### Siemens
- excellent pour standardisation site/usine ;
- fort sur TIA, PROFINET, safety intégrée ;
- très bon pour continuité atelier-usine-supervision.

### Rockwell
- très fort en machine discrète et base installée Allen-Bradley ;
- fort sur EtherNet/IP et écosystème nord-américain ;
- très cohérent si la maintenance locale est déjà Logix.

### Beckhoff
- très fort pour motion, PC-based control, EtherCAT, ouverture logicielle ;
- excellent pour architectures techniques modernes et fortes exigences axes.

### Omron
- solide pour machine et motion avec Sysmac ;
- bon compromis logique + réseau + axes.

### Schneider
- adapté aux utilités, infrastructures, process léger et Modicon ;
- bon quand l'intégration énergétique et bâtiment/procédé compte.

### WAGO
- fort pour contrôleurs compacts, edge, CODESYS, passerelles ;
- bon pour télégestion, agrégation et petits/moyens automatismes.

### PLCnext
- très fort en ouverture OT/IT, software-defined et edge ;
- pertinent pour architectures hybrides contrôle + services data.

### B&R
- excellent pour OEM machine, motion, safety et visualisation intégrés ;
- très fort pour plateformes machines rapides et modulaires.

### Mitsubishi
- fort pour machines, assemblage, convoyage et environnement MELSEC ;
- pertinent pour standardisation machine en environnement asiatique/international.

## 4. Matrice de décision rapide

### Choisir en priorité Siemens si
- le site veut homogénéiser l'usine ;
- safety, réseau, HMI et PLC doivent rester intégrés ;
- la gouvernance usine est structurée autour de TIA.

### Choisir en priorité Rockwell si
- l'usine est déjà Logix ;
- EtherNet/IP domine ;
- le besoin principal est machine discrète avec forte base locale.

### Choisir en priorité Beckhoff ou B&R si
- motion et axes sont centraux ;
- l'architecture machine est modulaire et exigeante ;
- la performance machine prime.

### Choisir WAGO ou PLCnext si
- edge, passerelles, OT/IT et ouverture logicielle sont décisifs ;
- l'on cherche une architecture flexible, compacte ou software-defined.

## 5. Scénarios types

### Scénario A — Standard groupe usine automobile
- priorités : homogénéité, safety, maintenance, documentation, réseau.
- candidats forts : Siemens, Rockwell.

### Scénario B — OEM packaging haute cadence
- priorités : motion, synchronisation, modularité.
- candidats forts : B&R, Beckhoff, Omron, Mitsubishi.

### Scénario C — Sous-station énergie / télégestion / utilités
- priorités : robustesse, edge, protocoles, compacité.
- candidats forts : WAGO, Schneider, PLCnext.

### Scénario D — Nouvelle architecture OT/IT ouverte
- priorités : MQTT/OPC UA, edge, software-defined, intégration data.
- candidats forts : PLCnext, WAGO, Beckhoff.

## 6. Pièges de comparaison

1. Comparer des plateformes sans distinguer type d'application.
2. Ignorer l'impact des compétences maintenance déjà présentes.
3. Surpondérer la mode technologique au détriment du support terrain.
4. Oublier la stratégie future d'intégration data/UNS/SCADA/MES.

## 7. Checklist de décision

- [ ] Le type d'application est formalisé.
- [ ] Les besoins motion, safety et SCADA sont pondérés.
- [ ] Les contraintes réseau/protocoles sont connues.
- [ ] Le coût de maintenance et de migration est estimé.
- [ ] Le choix final est défendable techniquement et organisationnellement.
