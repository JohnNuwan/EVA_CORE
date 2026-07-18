# Checklist architecture SCADA/HMI scripting

## Frontière de responsabilité
- logique critique PLC gardée côté contrôle
- logique UI séparée du reporting
- requêtes SQL centralisées
- scripts longs hors thread IHM

## Maintenabilité
- conventions nommage
- journalisation
- gestion erreurs
- revue de dépendances legacy
