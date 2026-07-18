# Remediation checklist for industrial skill-library passes

Priorité de traitement :
1. MCPs manquants
2. Plugins/outils de validation ou d'audit
3. Skills les plus faibles par cluster métier
4. Support files manquants
5. Vérification de sortie de classement faible

Heuristiques utiles :
- skill très courte (<50 lignes) => forte candidate à enrichissement
- skill sans `references/` ni `templates/` => faible réutilisabilité
- plusieurs skills proches dans un même cluster => enrichir l'umbrella ou harmoniser le vocabulaire

Règle pratique issue de session :
- si une politique d'autorisation bloque les suppressions ou certaines écritures groupées, continuer la remédiation non destructive et documenter le blocage au lieu d'arrêter la passe.
