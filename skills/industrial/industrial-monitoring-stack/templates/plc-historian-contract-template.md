# Contrat type PLC ↔ Historian

## 1. Portée
- automate / zone couverte :
- protocole :
- collecteur :
- fréquence de collecte :

## 2. Familles de points exposées
- `Sts`
- `Alm`
- `Ana`
- `Cnt`
- `Safe`
- `Meta`

## 3. Règles de données
- timestamps UTC ;
- qualité stockée si disponible ;
- unités stabilisées ;
- points booléens séparés des événements ;
- changements d'états historisés sans ambiguïté.

## 4. Exigences minimales
- état machine ;
- défaut général ;
- mode ;
- temps de cycle ;
- compteurs ;
- analogiques critiques ;
- état CPU ou santé automate si disponible.

## 5. Critères d'acceptation
- cohérence physique ;
- cohérence temporelle ;
- absence de trous silencieux ;
- modèle de nommage stable.
