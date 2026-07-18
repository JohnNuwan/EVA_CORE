# Arbre de diagnostic rapide monitoring

## Étape 1 — La donnée existe-t-elle ?
- Oui → passer à l'étape 2
- Non → vérifier connectivité, protocole, endpoint, droits, qualité source

## Étape 2 — L'équipement répond-il ?
- Oui → passer à l'étape 3
- Non → vérifier CPU, port, session protocole, réseau, alimentation équipement

## Étape 3 — Le défaut est-il communication ou métier ?
- communication : qualité mauvaise, timeout, reconnects, timestamps gelés
- métier : états, défauts, analogiques incohérents mais communication stable

## Étape 4 — Où est le premier symptôme ?
- automate / CPU
- sécurité
- robot
- drive / motion
- process / instrumentation
- énergie / utilités

## Étape 5 — La dérive est-elle brutale ou lente ?
- brutale : arrêt, défaut franc, perte com, sécurité
- lente : temps de cycle, température, consommation, resets répétés

## Étape 6 — Quel niveau d'analyse lancer ?
- N1 : état / défaut / communication
- N2 : chronologie + top défauts + comparaison nominale
- N3 : KPI, tendance, énergie, micro-arrêts, prédictif ciblé

## Règle d'or
Ne jamais conclure sur un seul bit de défaut. Toujours reconstruire au minimum :
- état machine ;
- dernier défaut ;
- qualité communication ;
- une ou deux mesures analogiques critiques.
