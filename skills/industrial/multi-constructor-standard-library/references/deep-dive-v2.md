# Référence v2 approfondie multi-constructeurs

## Principe d'architecture
Le contrat métier doit être défini une fois, puis décliné par plateforme. Les détails d'E/S, d'alarmes, de permissifs, de timers et d'échanges SCADA/MES restent dans le JSON métier afin de conserver un point de vérité unique.

## Couche de génération recommandée
1. JSON métier enrichi
2. Génération d'artefacts par constructeur
3. Génération de mapping documentaire
4. Compléments projet manuels (safety, hardware, site specifics)

## Cas d'usage cibles
- création rapide de bibliothèques standards multi-marques ;
- génération d'un lot d'équipements homogènes ;
- amorçage d'un standard groupe ;
- préparation de contrats PLC ↔ SCADA ↔ MES cohérents.
