# Rapport-type OSINT — Gabarit

Template basé sur l'investigation John Nuwan Moncel (14 juillet 2026).
Utiliser ce canevas pour toute investigation individuelle.

---

# Rapport d'Analyse OSINT — [NOM CIBLE]

**Date de l'analyse** : [DATE]
**Identifiant cible** : [NOM / TÉLÉPHONE / EMAIL / PSEUDO]
**Type d'analyse** : [Auto-OSINT / Investigation légitime / CTF]
**Périmètre** : Sources publiques uniquement

⚠️ **Note éthique** : [Contexte légitime de la recherche]

---

## 1. IDENTITÉ

| Champ | Valeur |
|-------|--------|
| Nom complet | |
| Prénoms | |
| Nom de famille | |
| Pseudos connus | |
| Initiales | |

---

## 2. LOCALISATION GÉOGRAPHIQUE

### Adresse(s)
- 

### Zone d'activité probable
- 

---

## 3. NUMÉRO DE TÉLÉPHONE

### Informations extraites
- **Type** : [Mobile / Fixe / VoIP]
- **Format international** : 
- **Apparaît dans** : [Sources]
- **Association trouvée** : 

### Analyse
- [Réattribution possible / coûts / anciens titulaires]

---

## 4. PRÉSENCE SUR LES RÉSEAUX SOCIAUX

| Plateforme | URL / Handle | Nom affiché | Activité |
|------------|-------------|-------------|----------|
| LinkedIn | | | |
| Instagram | | | |
| Twitter/X | | | |
| Facebook | | | |
| GitHub | | | |
| YouTube | | | |
| SoundCloud | | | |

---

## 5. ACTIVITÉ PROFESSIONNELLE

### Emploi(s)
- **Employeur** : 
- **Poste** : 
- **Secteur** : 

### Entreprise(s) détenue(s)
- **Nom** : 
- **SIRET** : 
- **Création** : 
- **Adresse** : 

---

## 6. PROJETS TECHNIQUES & COMPÉTENCES

### Repositories / Projets

| Nom | Description | Technologie |
|-----|-------------|-------------|
| | | |

### Compétences identifiées
- 

---

## 7. CENTRES D'INTÉRÊT

| Domaine | Preuves |
|---------|---------|
| | |

---

## 8. ANALYSE CHRONOLOGIQUE

| Date | Événement |
|------|-----------|
| | |

---

## 9. NIVEAU D'EXPOSITION OSINT

| Critère | Niveau | Détail |
|---------|--------|--------|
| **Exposition nom complet** | 🔴/🟠/🟢 | |
| **Exposition téléphone** | 🔴/🟠/🟢 | |
| **Exposition adresse** | 🔴/🟠/🟢 | |
| **Exposition professionnelle** | 🔴/🟠/🟢 | |
| **Pseudonymat des comptes** | 🔴/🟠/🟢 | |
| **Surface d'attaque sociale** | 🔴/🟠/🟢 | |

---

## 10. AUDIT DE SÉCURITÉ — BRÈCHES ET FUITES

### Have I Been Pwned
- **Email** : [vérifié / bloqué]
- **Action** : https://haveibeenpwned.com/account/[email]

### HudsonRock (infostealer)
- **API** : `curl -s "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-username?username=<pseudo>"`
- **Résultat** : 
- **⚠️ SI POSITIF** : ne pas conclure immédiatement. Vérifier :
  - IP géolocalisée (ip-api.com) → pays cohérent avec le sujet ?
  - Nom de la machine (computer_name) → machine connue du sujet ?
  - Nom du propriétaire → rechercher dans les sources académiques/web
  - Si divergence géographique → faux positif probable (pseudo partagé)
  - Si cohérence → compromission confirmée, escalader en URGENT 

### Autres vérifications
- BreachDirectory, DeHashed, LeakCheck : bloqués par Cloudflare (vérification manuelle)

---

## 11. RECOMMANDATIONS

### 🔴 URGENT (si infostealer détecté)
1. Changer TOUS les mots de passe utilisés à la date de l'infection
2. Activer le 2FA partout
3. Scanner toutes les machines (Malwarebytes, Bitdefender)

### 🟠 Exposition numérique
1. 
2. 
3. 

---

## 12. SOURCES CONSULTÉES

- 
- 

---

## 12. LIMITES DE L'ANALYSE

- Sources publiques gratuites uniquement
- N'ont PAS été consultés : bases payantes, dark web, API privées, reconnaissance faciale

---

*Rapport généré par Hermes Agent — [DATE]*
*Source unique : informations publiquement accessibles sur Internet*

---

# Notes méthodologiques (pour l'agent)

## Workflow parallèle — le plus efficace

**Phase 1 — PARALLÈLE** : lancer 3-4 recherches simultanées
```
"Prénom Nom" (guillemets)
"Pseudo1" OR "Pseudo2"
"0600000000" (tous les formats)
site:linkedin.com "Nom" OR site:github.com "Nom"
```

**Phase 2 — PIVOT** : chaque résultat ouvre une piste
```
LinkedIn → chercher l'entreprise sur Pappers
GitHub → analyser les repos (langages, centres d'intérêt)
Instagram → extraire les posts publics (lieux, dates)
Numéro dans annuaire → vérifier l'adresse sur geoportail
```

**Phase 3 — CROISEMENT** : valider les découvertes
```
Nom sur GitHub + Twitter avec même bio → même personne
Adresse proche d'un employeur → cohérence géographique
Hobbies cohérents entre plateformes → confirmation
```

**Phase 4 — COMPILATION** : rapport structuré (ce template)

## Pièges à éviter

- **Homonymes** : toujours vérifier le contexte avant d'associer
- **Numéros réattribués** : le titulaire actuel peut différer de l'annuaire
- **Profils abandonnés** : Google+ (fermé 2019), MySpace, etc.
- **Snippets trompeurs** : un résultat de moteur de recherche peut mentionner le bon nom mais concerner une autre personne
- **Pseudos dérivés du nom** : toujours chercher les variantes (Jay pour J., Nuwan fusionné, etc.)
- **HudsonRock faux positifs** : un pseudo partagé avec un inconnu à l'autre bout du monde peut générer une alerte infostealer → toujours géolocaliser l'IP et croiser avec le computer_name
- **Email en bio TikTok/Instagram** : pattern très fréquent chez les créateurs — à signaler comme risque d'exposition
- **Stage name vs civil name** : un artiste peut avoir un nom de scène distinct de son état civil — les deux doivent être investigués séparément

## Sources françaises à consulter systématiquement

| Cible | Source |
|-------|--------|
| Entreprise | pappers.fr, societe.com, infogreffe.fr |
| Téléphone | telephoneannuaire.fr, pagesjaunes.fr |
| Adresse | geoportail.gouv.fr, app.dvf.etalab.gouv.fr |
| Artiste/Intermittent | idspectacle.com |
| Open data | data.gouv.fr, annuaire-entreprises.data.gouv.fr |
| Presse locale | la1ere.franceinfo.fr (outre-mer), francebleu.fr (régions) |
