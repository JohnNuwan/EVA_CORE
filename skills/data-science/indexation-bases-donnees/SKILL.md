---
name: indexation-bases-donnees
description: "Guide complet des index dans les bases de données — B-tree, Hash, GiST, GIN, BRIN, bitmap, index composites, partiels, couvrants, clustering, et optimisation des plans d'exécution."
version: 1.0.0
author: EVA & communauté EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [index, b-tree, hash, gist, gin, brin, optimisation, performance, base-de-donnees]
    homepage: https://use-the-index-luke.com/
    related_skills: [postgresql, mysql, mongodb, optimisation-performance, sharding-partitionnement]
prerequisites:
  commands: [psql, mysql, sqlite3, mongosh]
---

# Compétence Indexation Avancée des Bases de Données

## Vue d'ensemble

Un index est une structure de données redondante qui accélère la recherche, le tri, et les jointures au prix d'un espace de stockage supplémentaire et d'un ralentissement des écritures. Maîtriser les index est le levier le plus puissant pour les performances des bases de données.

Cette compétence couvre tous les types d'index (B-tree, Hash, GiST, GIN, BRIN, bitmap, trie, covering), leur sélection selon le type de requête, l'optimisation des plans d'exécution, et les pièges à éviter.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :
- Demande d'optimiser des requêtes SQL lentes
- Veut choisir le bon type d'index pour un cas d'usage
- A besoin de comprendre un plan d'exécution (EXPLAIN)
- Doit équilibrer performance en lecture vs écriture
- Veut configurer l'indexation automatique (PostgreSQL, MySQL)
- A besoin de covering indexes, partial indexes, ou functional indexes

---

## 1. Arbre B (B-tree) — L'index Universel

### 1.1 Principe

Le B-tree est l'index par défaut de tous les SGBD relationnels (PostgreSQL, MySQL InnoDB, SQLite). Il organise les données dans un arbre équilibré de hauteur logarithmique (O(log n)). Pour 1 million de lignes, une recherche B-tree demande ~3-4 niveaux d'arbre.

### 1.2 Quand l'utiliser

| Opération | Efficacité B-tree |
|-----------|------------------|
| `WHERE col = valeur` | Excellent (O(log n)) |
| `WHERE col > valeur` | Excellent (range scan) |
| `ORDER BY col` | Excellent (pas de tri supplémentaire) |
| `LIKE 'prefix%'` | Bon (scan de plage) |
| `LIKE '%suffix'` | Impossibilité (pas d'index utilisable) |
| `col IN (1,2,3)` | Bon (multiples recherches) |
| `col IS NULL` | Variable selon SGBD |

### 1.3 Index Composite (Multi-colonnes)

```sql
-- Règle fondamentale : colonnes d'égalité → colonnes de plage → colonnes de tri
-- WHERE machine_id = 42 AND statut = 'OK' ORDER BY ts DESC
CREATE INDEX idx_perf ON mesures (machine_id, statut, ts DESC);

-- Condition : les colonnes de gauche à droite doivent être contraintes
-- BON : WHERE machine_id = 42 AND statut = 'OK'      → utilise 3 colonnes
-- BON : WHERE machine_id = 42                         → utilise 1 colonne
-- MAUVAIS : WHERE statut = 'OK'                       → n'utilise PAS l'index
-- MAUVAIS : WHERE machine_id = 42 AND temperature > 100 → utilise 2 colonnes (machine_id, température)
--          mais la 3e colonne (statut) sautée par le range scan
```

### 1.4 Index Couvrant (Covering Index)

```sql
-- L'index contient TOUTES les colonnes de la requête
-- Évite de lire la table (Index-Only Scan)

CREATE INDEX idx_covering ON mesures (machine_id, statut, ts, temperature, pression);

-- Cette requête ne lit QUE l'index (pas de FETCH)
SELECT machine_id, statut, ts, temperature
FROM mesures
WHERE machine_id = 42 AND statut = 'OK' AND ts > '2025-06-01';
```

---

## 2. Index Hash

### 2.1 Principe

Table de hachage : O(1) pour les égalités, impossible pour les plages ou les tris.

### 2.2 PostgreSQL

```sql
-- PostgreSQL : CREATE INDEX ... USING HASH
CREATE INDEX idx_capteur_hash ON mesures USING HASH (capteur_id);

-- Limitations : n'accepte QUE les opérateurs =
-- Pas de : <, >, <=, >=, BETWEEN, ORDER BY
-- Utile pour : clés étrangères, lookup exacts, colonnes de jointure
```

### 2.3 MySQL / InnoDB

```sql
-- MySQL InnoDB ne supporte pas HASH index (sauf MEMORY engine)
-- L'index B-tree d'InnoDB est déjà très efficace pour les égalités
-- Les HASH index sont automatiquement créés par l'Adaptive Hash Index (AHI)
```

---

## 3. Index GiST (Generalized Search Tree)

### 3.1 Principe

Arbre équilibré généralisé qui supporte les opérateurs de distance, d'intersection, et de voisinage. Utilisé pour les données géométriques, géospatiales, full-text, et ranges.

### 3.2 Usages

```sql
-- PostgreSQL : GiST pour géospatial (PostGIS)
CREATE INDEX idx_localisation ON sites USING GIST (geom);

-- Requête des 10 plus proches voisins
SELECT nom, ST_Distance(geom, ST_MakePoint(4.387, 45.441)) AS dist
FROM sites
ORDER BY geom <-> ST_MakePoint(4.387, 45.441)
LIMIT 10;

-- GiST pour les ranges (daterange, int4range)
CREATE INDEX idx_periode ON contrats USING GIST (periode);
SELECT * FROM contrats WHERE periode @> CURRENT_DATE;  -- contient
SELECT * FROM contrats WHERE periode && '[2025-01-01, 2025-06-30]'::daterange;  -- overlap
```

### 3.3 Opérateurs GiST

| Opérateur | Signification | Exemple |
|-----------|--------------|---------|
| `<<` | strictement à gauche | `point << box` |
| `&<` | ne s'étend pas à droite | `box &< box` |
| `&&` | overlap | `box && box` |
| `<->` | distance | `point <-> point` |
| `@>` | contient | `polygon @> point` |
| `<@` | contenu dans | `point <@ polygon` |

---

## 4. Index GIN (Generalized Inverted Index)

### 4.1 Principe

Index inversé : stocke une liste de documents pour chaque mot-clé. Parfait pour les tableaux, JSONB, et full-text search.

### 4.2 Usages

```sql
-- PostgreSQL GIN pour JSONB
CREATE INDEX idx_tags ON articles USING GIN (tags);
CREATE INDEX idx_donnees_json ON mesures USING GIN (donnees jsonb_path_ops);

-- Recherche dans JSONB
SELECT * FROM mesures WHERE donnees @> '{"temperature": 23.5}';
SELECT * FROM articles WHERE tags ? 'machine-learning';  -- contient la clé
SELECT * FROM articles WHERE tags ?| ARRAY['python', 'ml'];  -- au moins une
SELECT * FROM articles WHERE tags ?& ARRAY['python', 'ml'];  -- toutes

-- GIN pour full-text
CREATE INDEX idx_texte ON documents USING GIN (to_tsvector('french', contenu));
SELECT * FROM documents
WHERE to_tsvector('french', contenu) @@ to_tsquery('french', 'machine & apprentissage');
```

### 4.3 GIN vs GiST

| Critère | GIN | GiST |
|---------|-----|------|
| Vitesse de recherche | Très rapide | Rapide |
| Vitesse d'écriture | Lente (reconstruit l'index) | Rapide |
| Taille | 2-3x plus gros | 1.5x plus gros |
| Use case | JSONB, full-text statique | Full-text dynamique, géospatial |

---

## 5. Index BRIN (Block Range Index)

### 5.1 Principe

Index qui stocke les valeurs min/max par plage de blocs physiques. Extrêmement compact (100-1000x plus petit qu'un B-tree), mais efficace seulement si les données sont naturellement ordonnées physiquement.

### 5.2 Usages

```sql
-- PostgreSQL BRIN (parfait pour les séries temporelles)
CREATE INDEX idx_ts_brin ON mesures USING BRIN (timestamp) WITH (pages_per_range = 32);

-- Taille : 8 Ko pour 1 milliard de lignes
-- vs 25 Go pour un B-tree sur la même colonne

-- BRIN avec multi-minmax (PostgreSQL 14+)
CREATE INDEX idx_brin_multicol ON mesures USING BRIN (timestamp, machine_id)
WITH (pages_per_range = 16) INCLUDE (temperature);
```

### 5.3 Quand BRIN plutôt que B-tree

| Situation | Recommandation |
|-----------|---------------|
| Séries temporelles (timestamp ordonné) | BRIN (100x plus petit) |
| Données physiquement corrélées (ID auto-incrémenté) | BRIN (excellent) |
| Haute cardinalité aléatoire | B-tree (échec BRIN) |
| Beaucoup d'écritures, peu de lectures | BRIN (écritures rapides) |
| RAM limitée | BRIN (index minuscule) |

---

## 6. Index Partiels (Partial Index)

### 6.1 Principe

Index qui ne contient qu'un sous-ensemble de lignes, économisant espace et écritures.

```sql
-- Index seulement sur les valeurs critiques
CREATE INDEX idx_alertes_critiques ON mesures (capteur_id, ts DESC)
WHERE niveau = 'CRITIQUE';

-- Index seulement sur les données du mois courant
CREATE INDEX idx_mois_courant ON mesures (machine_id, ts)
WHERE ts >= date_trunc('month', CURRENT_DATE);

-- Requête qui utilise l'index partiel
SELECT * FROM mesures
WHERE niveau = 'CRITIQUE' AND capteur_id = 42;
```

---

## 7. Index Fonctionnels (Expression Index)

### 7.1 Principe

Index sur le résultat d'une expression ou d'une fonction.

```sql
-- PostgreSQL : index sur l'expression
CREATE INDEX idx_lower_email ON utilisateurs (LOWER(email));
SELECT * FROM utilisateurs WHERE LOWER(email) = 'user@example.com';

-- MySQL 8.0+ : index fonctionnel
ALTER TABLE utilisateurs ADD INDEX idx_lower_email ((LOWER(email)));

-- Index sur extraction JSON
CREATE INDEX idx_json_temp ON mesures ((donnees->>'temperature'));
SELECT * FROM mesures WHERE (donnees->>'temperature')::numeric > 100;
```

---

## 8. Index Cluster (Clustering)

### 8.1 Principe

Réorganise physiquement les lignes dans l'ordre de l'index. Une table ne peut avoir qu'un seul cluster.

```sql
-- PostgreSQL CLUSTER
CLUSTER mesures USING idx_mesures_ts;
-- Attention : verrouille la table, peut prendre du temps
-- Recluster périodiquement : CLUSTER VERBOSE mesures;

-- MySQL InnoDB
-- La table est toujours organisée par la PRIMARY KEY (index cluster)
-- Les index secondaires contiennent la PK, pas l'adresse physique
```

### 8.2 Impact du clustering

```sql
-- Avant clustering : lecture aléatoire (slow)
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM mesures WHERE ts BETWEEN 'A' AND 'B';
-- Buffers: shared hit=5000, read=20000  ← lectures disque

-- Après clustering : lectures séquentielles (fast)
-- Buffers: shared hit=25000, read=0  ← tout en cache
```

---

## 9. Analyse et Maintenance des Index

### 9.1 Index inutilisés

```sql
-- PostgreSQL : index jamais scannés
SELECT
    schemaname, tablename, indexname,
    idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname NOT IN ('pg_catalog', 'information_schema');
```

### 9.2 Fragmentation des index

```sql
-- PostgreSQL : taille réelle vs estimée
SELECT
    indexrelid::regclass AS index_name,
    pg_size_pretty(pg_relation_size(indexrelid::regclass)) AS size,
    pg_size_pretty(pg_relation_size(indexrelid::regclass) * (1 - avg_leaf_density / 100)) AS waste
FROM pg_stat_user_indexes, LATERAL (
    SELECT (avg_leaf_density)::int
    FROM pgstatindex(indexrelid::regclass::text)
) stats
WHERE avg_leaf_density < 80;

-- Rebuild : REINDEX INDEX CONCURRENTLY idx_name;
```

### 9.3 Index et EXPLAIN

```sql
-- PostgreSQL : vérifier le type de scan
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM mesures WHERE machine_id = 42;

-- Plans possibles :
-- Seq Scan (mauvais) : scan complet de la table
-- Index Scan (bon) : cherche dans l'index, puis FETCH sur la table
-- Index Only Scan (excellent) : tout dans l'index, pas de FETCH
-- Bitmap Index Scan (moyen) : construction d'un bitmap avant FETCH
-- Bitmap Heap Scan : associé à Bitmap Index Scan
```

---

## 10. Index par SGBD — Tableau Comparatif

| Type d'Index | PostgreSQL | MySQL (InnoDB) | SQLite | MongoDB |
|---|---|---|---|---|
| B-tree | Par défaut | Par défaut (cluster PK) | Par défaut | Par défaut |
| Hash | `USING HASH` | Mémoire seulement | Non | `{ hashed: true }` |
| GiST | `USING GIST` | Non | Non | 2dsphere |
| GIN | `USING GIN` | Non | Non | Non |
| BRIN | `USING BRIN` | Non | Non | Non |
| Partiel | `WHERE ...` | `WHERE ...` (MySQL 8.0+) | `WHERE ...` | `partialFilterExpression` |
| Fonctionnel | `INDEX (expr)` | `INDEX ((expr))` | Non | Non |
| Text | `to_tsvector` | `FULLTEXT` | FTS5 | `text` |
| Géospatial | PostGIS | `SPATIAL` | Non | `2dsphere` |
| TTL | Non | Non | Non | `expireAfterSeconds` |
| Invisible | Oui | Oui (8.0+) | Non | Non |

---

## Pièges Courants

1. **Indexer toutes les colonnes individuellement.** MySQL/PostgreSQL n'utilise qu'un seul index par table par requête (sauf Bitmap Scan). Un index composite est souvent meilleur que 3 index simples.

2. **Index sur des colonnes de faible cardinalité.** Un index sur `sexe` (M/F) ou `booléen` n'aide pas — 50% des lignes sont retournées. Préférer un index partiel.

3. **Pas de covering index pour les requêtes fréquentes.** Si une requête très fréquente lit 5 colonnes, créer un index qui les contient toutes = Index-Only Scan.

4. **Index B-tree sur JSONB.** Utiliser GIN, pas B-tree, pour les opérateurs `@>`, `?`, `?|`.

5. **Oublier les index sur les clés étrangères.** Chaque `JOIN` sur une FK doit avoir un index coté référencé. InnoDB le fait automatiquement, PostgreSQL non.

6. **REINDEX sans CONCURRENTLY.** En production, `REINDEX` verrouille la table. Toujours utiliser `REINDEX INDEX CONCURRENTLY` (PostgreSQL 12+).

---

## Checklist

- [ ] Les index composites suivent l'ordre : égalité → plage → tri
- [ ] Les requêtes fréquentes ont un covering index (Index-Only Scan)
- [ ] Les index inutilisés sont identifiés (`idx_scan = 0`) et supprimés
- [ ] Les index sur JSONB utilisent GIN (pas B-tree)
- [ ] Les index partiels sont utilisés pour les sous-ensembles de données
- [ ] Les clés étrangères sont indexées
- [ ] `EXPLAIN (ANALYZE, BUFFERS)` vérifié pour les requêtes lentes
- [ ] BRIN envisagé pour les séries temporelles volumineuses
- [ ] REINDEX CONCURRENTLY planifié périodiquement
- [ ] L'index cluster est réappliqué périodiquement si nécessaire