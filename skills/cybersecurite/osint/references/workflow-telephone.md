# Workflow téléphone OSINT approfondi

Le scan superficiel d'un numéro de téléphone (juste Google) ne suffit pas.
Checklist complète à exécuter systématiquement.

## 1. PhoneInfoga — Google Dorks spécialisés

```bash
phoneinfoga scan -n "+336XXXXXXXX" > phoneinfoga.txt
```

Génère 30+ Google Dorks ciblant des annuaires, sites anti-spam, et
plateformes de lookup téléphonique.

## 2. HudsonRock — Infostealer via le numéro

```bash
curl -s "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-username?username=336XXXXXXXX"
```

Le numéro en format international sans le "+" peut être recherché comme
username dans la base HudsonRock.

## 3. tellows.fr — Score et réputation

```bash
curl -sL "https://www.tellows.fr/num/06XXXXXXXX"
```

Interprétation des scores (échelle 1-9) :
- 1-3 : Fiable
- 4-6 : Suspect (démarchage possible)
- 7-9 : Arnaque confirmée

Le titre de la page tellows mentionne souvent l'opérateur (SFR, Orange,
Bouygues, Free).

## 4. Annuaires inversés (plusieurs formats à tester)

| Site | Format URL |
|------|-----------|
| telephoneannuaire.fr | `/directory/listing/NOM` |
| lannuaire.fr | `/annuaire-inverse-0600000000/` |
| aquiestcenumero.com | `/numero/0600000000` |
| aquiappartientcenumero.com | recherche par numéro |

Tester tous les formats : `0600000000`, `06 00 00 00 00`, `+33600000000`,
`0033600000000`.

## 5. Résultat type (numéro exposé)

```
Opérateur : SFR (tellows)
Score : 5/9 — "Arnaque" (communauté)
Annuaires : COLOMES AMANDINE, 63360 Gerzat (telephoneannuaire.fr)
HudsonRock : Aucune infection
```

## 6. Résultat type (numéro propre)

```
Opérateur : Non confirmé (06 XX = ancien Orange)
Annuaires : Aucune trace
tellows : Pas de page
HudsonRock : Aucune infection
→ Numéro fantôme, hygiène parfaite
```

## 7. Pièges

- Un numéro peut avoir été **réattribué** (portabilité) : l'ancien
  titulaire apparaît encore dans les annuaires
- **Ne jamais appeler** le numéro pour vérifier
- Les annuaires gratuits sont souvent obsolètes
