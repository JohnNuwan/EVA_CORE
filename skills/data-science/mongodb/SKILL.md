---
name: mongodb
description: "Guide complet MongoDB — NoSQL documents, agrégation, indexation, sharding, réplica sets, transactions, Geospatial, et bonnes pratiques de modélisation."
version: 1.0.0
author: EVA & communauté EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [mongodb, nosql, base-de-donnees, documents, agrégation, sharding, réplication, index]
    homepage: https://www.mongodb.com/
    related_skills: [redis, indexation-bases-donnees, sharding-partitionnement, replication-haute-disponibilite, sauvegarde-restauration]
prerequisites:
  commands: [mongosh, mongod, mongos, mongorestore, mongodump]
---

# Compétence MongoDB — Agrégation, Indexation, Sharding et Réplica Sets

## Vue d'ensemble

MongoDB est le leader des bases NoSQL orientées documents. Il stocke les données en BSON (JSON binaire), supporte les transactions ACID multi-documents (depuis 4.0), le sharding natif, les réplica sets, un pipeline d'agrégation extrêmement puissant, et les index de types variés (text, geospatial, TTL, partial, hashed).

Cette compétence couvre la modélisation de documents, le pipeline d'agrégation, l'indexation avancée, les réplica sets, le sharding, les transactions, et les bonnes pratiques de performance.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :
- Veut modéliser des données en documents NoSQL
- A besoin d'écrire un pipeline d'agrégation complexe ($match, $group, $lookup, $unwind)
- Demande de configurer un réplica set ou un cluster shardé
- Veut optimiser des requêtes (index, explain, hint)
- A besoin de géospatial (2dsphere), de recherche textuelle, ou de TTL
- Migre d'un SGBD relationnel vers MongoDB

---

## 1. Modélisation des Documents

### 1.1 Principes fondamentaux

Contrairement au SQL, MongoDB ne normalise pas par défaut. Les choix de modélisation :

| Pattern | Quand l'utiliser |
|---------|-----------------|
| **Embedded (imbriqué)** | Relations 1:1, 1:N avec sous-docs limités (< 100) |
| **Reference (référence)** | Relations N:M, sous-docs volumineux, accès indépendant |
| **Bucket pattern** | Séries temporelles (grouper les mesures par heure) |
| **Polymorphic** | Documents de structure différente dans une même collection |

### 1.2 Exemple — Poste et mesures

```javascript
// EMBEDDED — bon pour les mesures récentes d'un capteur
db.capteurs.insertOne({
  capteur_id: "TEMP-A001",
  nom: "Thermocouple ligne 3",
  localisation: { type: "Point", coordinates: [4.387, 45.441] },
  dernieres_mesures: [
    { ts: ISODate("2025-06-01T10:00:00Z"), valeur: 23.5 },
    { ts: ISODate("2025-06-01T10:01:00Z"), valeur: 23.7 },
    { ts: ISODate("2025-06-01T10:02:00Z"), valeur: 23.4 }
  ]
});

// REFERENCE — pour les historiques longs
db.mesures.insertOne({
  capteur_id: ObjectId("..."),
  ts: ISODate("2025-06-01T10:00:00Z"),
  temperature: 23.5,
  pression: 1.02
});

// BUCKET — mesure groupée par heure (réduit les documents de 60x)
db.mesures_bucket.insertOne({
  capteur_id: "TEMP-A001",
  heure: ISODate("2025-06-01T10:00:00Z"),
  min: 23.0, max: 24.1, avg: 23.5,
  count: 60,
  valeurs: [23.0, 23.2, 23.5, ..., 24.1]
});
```

---

## 2. Pipeline d'Agrégation

### 2.1 Pipeline complet

```javascript
db.mesures.aggregate([
  // Stage 1 — Filtrer les documents (utilise l'index)
  { $match: {
      capteur_id: ObjectId("..."),
      ts: { $gte: ISODate("2025-06-01"), $lt: ISODate("2025-07-01") }
  }},
  // Stage 2 — Grouper par heure et calculer des stats
  { $group: {
      _id: { $dateTrunc: { date: "$ts", unit: "hour" } },
      avg_temp: { $avg: "$temperature" },
      max_temp: { $max: "$temperature" },
      min_temp: { $min: "$temperature" },
      ecart_type: { $stdDevPop: "$temperature" },
      count: { $sum: 1 }
  }},
  // Stage 3 — Trier par heure
  { $sort: { _id: 1 } },
  // Stage 4 — Projection
  { $project: {
      _id: 0,
      heure: "$_id",
      avg_temp: { $round: ["$avg_temp", 2] },
      max_temp: 1,
      min_temp: 1,
      variabilite: { $round: ["$ecart_type", 2] },
      count: 1
  }}
]);
```

### 2.2 $lookup (équivalent de JOIN)

```javascript
db.commandes.aggregate([
  // Jointure avec la collection 'clients'
  { $lookup: {
      from: "clients",
      localField: "client_id",
      foreignField: "client_id",
      as: "client",
      pipeline: [
        { $project: { nom: 1, email: 1, _id: 0 } }
      ]
  }},
  // Dérouler le tableau d'un élément (commande → 1 client max)
  { $unwind: "$client" },
  // Jointure avec les lignes de commande
  { $lookup: {
      from: "lignes_commande",
      localField: "commande_id",
      foreignField: "commande_id",
      as: "articles"
  }},
  // Calculer le total de la commande
  { $addFields: {
      total_ht: { $sum: "$articles.montant_ht" }
  }},
  // Trier par date
  { $sort: { date_commande: -1 } },
  // Limiter
  { $limit: 20 }
]);
```

### 2.3 Fenêtrage ($setWindowFields — MongoDB 5.0+)

```javascript
db.mesures.aggregate([
  { $match: { capteur_id: "TEMP-A001" } },
  { $setWindowFields: {
      partitionBy: "$capteur_id",
      sortBy: { ts: 1 },
      output: {
        moyenne_mobile_7: {
          $avg: "$temperature",
          window: { documents: [-7, 0] }
        },
        rang: { $rank: {} },
        delta_precedent: {
          $derivative: { input: "$temperature", unit: "minute" }
        }
      }
  }}
]);
```

---

## 3. Indexation Avancée

### 3.1 Types d'index

```javascript
// Index simple
db.mesures.createIndex({ capteur_id: 1, ts: -1 });

// Index composé couvrant
db.mesures.createIndex(
  { capteur_id: 1, ts: -1, temperature: 1, pression: 1 },
  { name: "idx_covering" }
);

// Index partiel (économise de l'espace et de l'écriture)
db.mesures.createIndex(
  { temperature: 1 },
  { partialFilterExpression: { temperature: { $gt: 100 } } }
);

// Index TTL (expire automatiquement après 30 jours)
db.logs.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 2592000 }
);

// Index textuel (recherche plein texte)
db.articles.createIndex(
  { titre: "text", contenu: "text" },
  { weights: { titre: 10, contenu: 1 }, name: "idx_fulltext" }
);

// Index géospatial 2dsphere
db.sites.createIndex(
  { localisation: "2dsphere" }
);

// Index hashed (pour le sharding)
db.mesures.createIndex(
  { capteur_id: "hashed" }
);
```

### 3.2 Analyse des requêtes (explain)

```javascript
// Vérifier l'utilisation de l'index
db.mesures.find({
  capteur_id: "TEMP-A001",
  ts: { $gte: ISODate("2025-06-01") }
}).sort({ ts: -1 }).explain("executionStats");

// Indicateurs clés :
// - totalDocsExamined : doit être ≈ totalKeysExamined
// - executionTimeMillis : temps réel
// - IXSCAN (vs COLLSCAN) : utilisation d'index ou scan complet
// - stage FETCH + IXSCAN = bon plan
```

### 3.3 Index inefficaces

```javascript
// Détecter les index non utilisés (MongoDB 4.4+)
db.aggregate([
  { $indexStats: {} },
  { $match: { accesses.ops: 0 } }
]);
```

---

## 4. Réplica Sets

### 4.1 Configuration

```javascript
// Configurer un réplica set à 3 membres (mongod.conf)
// replication:
//   replSetName: "rs_eva"

// Initialiser
rs.initiate({
  _id: "rs_eva",
  members: [
    { _id: 0, host: "192.168.1.10:27017", priority: 2 },
    { _id: 1, host: "192.168.1.11:27017", priority: 1 },
    { _id: 2, host: "192.168.1.12:27017", priority: 0, votes: 0, hidden: true }
  ]
});

// Vérifier l'état
rs.status();
rs.conf();
```

### 4.2 Read Preferences

```javascript
// Lire depuis le secondaire (tolérance à la stale)
db.getMongo().setReadPref("secondaryPreferred");

// Lire depuis le primary (consistance forte, défaut)
db.getMongo().setReadPref("primary");

// Tag-aware read preference
db.getMongo().setReadPref("secondary", [
  { region: "eu-west-1" }
]);
```

### 4.3 Write Concern

```javascript
// Écriture acquittée par le primary seulement
db.mesures.insertOne(doc, { writeConcern: { w: 1 } });

// Écriture acquittée par majorité des membres du réplica set
db.mesures.insertOne(doc, { writeConcern: { w: "majority" } });

// Avec journalisation
db.mesures.insertOne(doc, { writeConcern: { w: "majority", j: true } });
```

---

## 5. Sharding (Distribution)

### 5.1 Architecture

```
mongos → [config server (3)] → shard1, shard2, shard3
```

### 5.2 Activation

```javascript
// Se connecter au mongos
sh.enableSharding("eva_db");

// Configurer une clé de shard
// Range-based (recommandé pour les données avec bonne cardinalité)
sh.shardCollection("eva_db.mesures", { capteur_id: 1, ts: 1 });

// Hashed (distribution uniforme garantie)
sh.shardCollection("eva_db.mesures_hash", { _id: "hashed" });
```

### 5.3 Zone-based sharding

```javascript
// Associer une zone à un shard
sh.addShardTag("shard01", "EUROPE");
sh.addShardTag("shard02", "AMERICA");

// Définir la plage de clés pour la zone
sh.updateZoneKeyRange(
  "eva_db.utilisateurs",
  { region: "EU" },
  { region: "EU\uFFFF" },
  "EUROPE"
);
```

---

## 6. Transactions ACID (MongoDB 4.0+)

```javascript
// Démarrer une session transactionnelle
const session = db.getMongo().startSession();
session.startTransaction({ readConcern: { level: "snapshot" }, writeConcern: { w: "majority" } });

try {
  const collection1 = session.getDatabase("eva_db").getCollection("comptes");
  const collection2 = session.getDatabase("eva_db").getCollection("transactions");

  // Débiter
  collection1.updateOne(
    { _id: "compte_A" },
    { $inc: { solde: -1000 } }
  );

  // Créditer
  collection1.updateOne(
    { _id: "compte_B" },
    { $inc: { solde: 1000 } }
  );

  // Journaliser
  collection2.insertOne({
    from: "compte_A", to: "compte_B",
    montant: 1000, ts: new Date()
  });

  session.commitTransaction();
} catch (e) {
  session.abortTransaction();
  print("Transaction annulée:", e);
} finally {
  session.endSession();
}
```

---

## 7. Sauvegarde et Restauration

```bash
# mongodump (binaire, plus lent, plus fiable)
mongodump --uri="mongodb://localhost:27017/eva_db" --out=/backup/mongo_$(date +%Y%m%d)
mongodump --uri="mongodb://localhost:27017/eva_db" --gzip --archive=/backup/eva_db_$(date +%Y%m%d).gz

# mongorestore
mongorestore --uri="mongodb://localhost:27018/eva_db" --drop /backup/mongo_20250601/eva_db
mongorestore --uri="mongodb://localhost:27018/eva_db" --gzip --archive=/backup/eva_db_20250601.gz

# mongodump avec réplica set (--oplog pour point-in-time)
mongodump --uri="mongodb://192.168.1.10:27017/eva_db" --oplog --out=/backup/mongo_oplog

# mongotools avancé (par collection)
mongodump --uri="mongodb://localhost:27017" --collection=mesures --db=eva_db --out=/backup/mesures
```

---

## Pièges Courants

1. **Documents trop gros.** MongoDB a une limite de 16 Mo par document. Un document embedded qui dépasse casse l'écriture. Solution : utiliser le pattern Bucket ou Reference.

2. **Pas d'index sur les requêtes fréquentes.** Un `COLLSCAN` (collection scan) sur des millions de documents ruine les performances. Vérifier avec `.explain("executionStats")`.

3. **$lookup sans index.** La collection `from` du $lookup doit avoir un index sur le champ de jointure, sinon c'est un Nested Loop sans index.

4. **Write Concern trop laxiste.** `w: 0` ou `w: 1` sans journalisation peut perdre des écritures. Mettre `w: "majority"` pour les données critiques.

5. **Sharding avec une clé de faible cardinalité.** Une clé comme `{ statut: 1 }` ne crée que 2-3 chunks max. Toujours choisir une clé avec haute cardinalité.

6. **Oublier les indexes dans les pipelines.** Chaque `$match` en début de pipeline doit être couvert par un index. Les stages suivants ne peuvent pas en bénéficier.

---

## Checklist

- [ ] Chaque collection a au moins un index sur le champ de filtre le plus fréquent
- [ ] Les requêtes utilisent `explain("executionStats")` pour vérifier `IXSCAN`
- [ ] Les documents ne dépassent pas 1 Mo (sauf cas justifié)
- [ ] Les `$lookup` ont un index sur la collection référencée
- [ ] Réplica set configuré avec au moins 3 membres
- [ ] Write Concern = `majority` pour les données critiques
- [ ] Sharding activé avec une clé à haute cardinalité
- [ ] Index TTL configuré pour les données temporaires (logs, sessions)
- [ ] Backup régulier avec `mongodump --oplog` pour restauration point-in-time
- [ ] Monitoring via `mongostat` et `mongotop` régulier