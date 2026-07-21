---
name: sqlite
description: "Guide complet SQLite — base de données embarquée, CLI, optimisation, WAL mode, FTS5, extensions, et intégration Python/Go/Rust."
version: 1.0.0
author: EVA & communauté EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [sqlite, base-de-donnees, embarqué, sql, fts5, wal, performance]
    homepage: https://www.sqlite.org/
    related_skills: [postgresql, mysql, optimisation-performance, sauvegarde-restauration]
prerequisites:
  commands: [sqlite3]
---

# Compétence SQLite — Base de Données Embarquée, Full-Text Search et Optimisation

## Vue d'ensemble

SQLite est le moteur de base de données le plus déployé au monde (chaque smartphone, navigateur, et des milliards d'appareils l'embarquen). Ce n'est pas un client-serveur, mais une bibliothèque C qui lit/écrit directement un fichier `.db` ou `.sqlite`. Il supporte les transactions ACID, les index, les CTE, les window functions, FTS5 (full-text search), et les extensions.

Sa force : zéro configuration, zéro administration, portable, extrêmement fiable (tests > 100x ceux de PostgreSQL).

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :
- A besoin d'une base embarquée (sans serveur) pour une application desktop ou mobile
- Veut un entrepôt local pour des logs, des données de capteurs, ou du cache
- Demande la recherche plein texte avec FTS5
- Veut utiliser le WAL mode pour le multi-lecteur
- A besoin d'optimiser une base SQLite (PRAGMA, VACUUM, indexes)
- Migre des données entre SQLite et PostgreSQL/MySQL

---

## 1. Fondamentaux

### 1.1 Création et connexion

```bash
# Créer/ouvrir une base
sqlite3 eva_data.db

# Mode colonnes (lisible)
sqlite3 -column -header eva_data.db "SELECT * FROM mesures LIMIT 5;"

# Exécuter un fichier SQL
sqlite3 eva_data.db < schema.sql
```

### 1.2 Types de données (affinités)

SQLite n'a pas de types stricts comme PostgreSQL. Il utilise des **affinités** :

| Type Déclaré | Affinité | Stockage |
|---|---|---|
| INT, INTEGER, BIGINT | INTEGER | 1-8 bytes |
| TEXT, CHAR, VARCHAR | TEXT | UTF-8 |
| REAL, FLOAT, DOUBLE | REAL | 8 bytes IEEE |
| BLOB | BLOB | tel quel |
| NUMERIC, DECIMAL | NUMERIC | INTEGER ou REAL |

### 1.3 Contraintes de type (STRICT — SQLite 3.37+)

```sql
-- Mode strict : rejette les types incorrects
CREATE TABLE mesures (
    id INTEGER PRIMARY KEY,
    temperature REAL NOT NULL,
    horodatage TEXT NOT NULL
) STRICT;
```

---

## 2. Optimisation avec PRAGMA

### 2.1 PRAGMA essentiels

```bash
# Connexion
sqlite3 eva_data.db

# Activer les foreign keys (désactivé par défaut !)
PRAGMA foreign_keys = ON;

# Mode WAL (Write-Ahead Logging) — lecture sans blocage
PRAGMA journal_mode = WAL;

# Cache taille (nombre de pages, 1 page = 4KB)
PRAGMA cache_size = -64000;  # 64 MB (négatif = kilo-octets)

# Synchronisation (sécurité vs performance)
PRAGMA synchronous = NORMAL;  # NORMAL (bon compromis), FULL (sûr), OFF (risqué)

# Temp store
PRAGMA temp_store = MEMORY;  # stocker les temp en RAM

# Cache partagé (multi-connexion)
PRAGMA mmap_size = 268435456;  # 256 MB de memory-mapped I/O

# Optimisation du query planner
PRAGMA automatic_index = ON;
PRAGMA optimize;  # optimise les statistiques (appeler périodiquement)
```

### 2.2 Fichier de configuration réutilisable

```bash
# ~/.sqliterc
.headers on
.mode column
.nullvalue NULL
.timer on
```

---

## 3. WAL Mode (Write-Ahead Logging)

### 3.1 Pourquoi WAL ?

Le mode **WAL** (Write-Ahead Logging) est le mode recommandé pour presque tous les usages modernes :

- **Lectures non-bloquantes** : plusieurs lecteurs simultanés pendant qu'un writer écrit
- **Écritures plus rapides** : l'écriture va dans le WAL, pas dans le fichier principal
- **Moins de fsync** : un seul fsync par transaction au lieu de deux

```bash
sqlite3 eva_data.db
PRAGMA journal_mode = WAL;
-- Retourne : wal
```

### 3.2 Checkpoint WAL

```sql
-- Forcer l'écriture du WAL dans le fichier principal
PRAGMA wal_checkpoint;

-- Checkpoint bloquant (sûr, mais bloque les lectures)
PRAGMA wal_checkpoint(PASSIVE);
PRAGMA wal_checkpoint(FULL);
PRAGMA wal_checkpoint(RESTART);  -- verrou exclusif, compacte complètement
```

### 3.3 WAL auto-checkpoint

```sql
-- Taille du WAL avant auto-checkpoint (défaut: 1000 pages = ~4MB)
PRAGMA wal_autocheckpoint = 500;  -- toutes les 500 pages (~2MB)
```

---

## 4. Full-Text Search (FTS5)

### 4.1 Créer une table FTS5

```sql
-- Table virtuelle FTS5
CREATE VIRTUAL TABLE articles_fts USING fts5(
    titre,
    contenu,
    categorie UNINDEXED,  -- pas indexée dans le FTS
    tokenize='porter unicode61',  -- stemmer anglais + Unicode
    content='articles',  -- synchronisé avec la table réelle
    content_rowid='id'
);

-- Table réelle associée
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    titre TEXT NOT NULL,
    contenu TEXT NOT NULL,
    categorie TEXT,
    date_publication TEXT
);

-- Synchroniser les données
INSERT INTO articles_fts(rowid, titre, contenu)
SELECT id, titre, contenu FROM articles;

-- Trigger pour maintien de la synchronisation
CREATE TRIGGER articles_ai AFTER INSERT ON articles BEGIN
    INSERT INTO articles_fts(rowid, titre, contenu)
    VALUES (new.id, new.titre, new.contenu);
END;

CREATE TRIGGER articles_ad AFTER DELETE ON articles BEGIN
    INSERT INTO articles_fts(articles_fts, rowid, titre, contenu)
    VALUES ('delete', old.id, old.titre, old.contenu);
END;

CREATE TRIGGER articles_au AFTER UPDATE ON articles BEGIN
    INSERT INTO articles_fts(articles_fts, rowid, titre, contenu)
    VALUES ('delete', old.id, old.titre, old.contenu);
    INSERT INTO articles_fts(rowid, titre, contenu)
    VALUES (new.id, new.titre, new.contenu);
END;
```

### 4.2 Recherche FTS5

```sql
-- Recherche basique (AND implicite)
SELECT * FROM articles_fts WHERE articles_fts MATCH 'machine learning';

-- Opérateurs booléens
SELECT * FROM articles_fts WHERE articles_fts MATCH 'temperature AND (pression OR vibration)';
SELECT * FROM articles_fts WHERE articles_fts MATCH 'capteur NOT obsolete';

-- Phrase exacte
SELECT * FROM articles_fts WHERE articles_fts MATCH '"deep reinforcement learning"';

-- Préfixe
SELECT * FROM articles_fts WHERE articles_fts MATCH 'optim*';

-- Near (proximité)
SELECT * FROM articles_fts WHERE articles_fts MATCH 'NEAR(erreur, capteur, 5)';

-- Classement par pertinence (bm25)
SELECT *, bm25(articles_fts) AS score
FROM articles_fts
WHERE articles_fts MATCH 'machine learning'
ORDER BY score;

-- Rang avec highlight
SELECT *, highlight(articles_fts, 1, '<b>', '</b>') AS extrait
FROM articles_fts
WHERE articles_fts MATCH 'machine learning'
ORDER BY rank;
```

### 4.3 Tokenizers personnalisés

```sql
-- Unicode (support accents mieux que simple)
CREATE VIRTUAL TABLE text_unicode USING fts5(
    content, tokenize='unicode61'
);

-- Trigram (recherche approximative et sous-chaîne)
CREATE VIRTUAL TABLE text_trigram USING fts5(
    content, tokenize='trigram'
);

-- Personnalisé avec paramètres
CREATE VIRTUAL TABLE text_custom USING fts5(
    content,
    tokenize='porter unicode61 remove_diacritics 2 tokenchars ''-_'''
);
```

---

## 5. Indexation Avancée

### 5.1 Index partiels (SQLite 3.30+)

```sql
-- Index seulement sur les capteurs actifs
CREATE INDEX idx_capteurs_actifs ON capteurs(valeur)
WHERE statut = 'ACTIF';
```

### 5.2 Index EXCLUDE NULL

```sql
-- Index qui ignore les NULL (économise espace)
CREATE INDEX idx_mesures_temperature ON mesures(temperature)
WHERE temperature IS NOT NULL;
```

### 5.3 Index DESC

```sql
-- Pour ORDER BY DESC
CREATE INDEX idx_mesures_ts_desc ON mesures(horodatage DESC);
```

---

## 6. Intégration en Python

### 6.1 Connexion et optimisation

```python
import sqlite3

conn = sqlite3.connect('eva_data.db')
conn.execute('PRAGMA journal_mode = WAL')
conn.execute('PRAGMA foreign_keys = ON')
conn.execute('PRAGMA cache_size = -64000')
conn.execute('PRAGMA synchronous = NORMAL')

# Row factory (accès par nom de colonne)
conn.row_factory = sqlite3.Row

# Execution multiple
conn.executemany(
    'INSERT INTO mesures (capteur_id, temperature, horodatage) VALUES (?, ?, ?)',
    [(42, 23.5, '2025-06-15T10:00:00'), (42, 23.7, '2025-06-15T10:01:00')]
)
conn.commit()
```

### 6.2 Batch efficace (transaction explicite)

```python
# 100x plus rapide que des INSERT individuels
def bulk_insert(data):
    conn.execute('BEGIN TRANSACTION')
    for row in data:
        conn.execute('INSERT INTO mesures VALUES (?, ?, ?)', row)
    conn.commit()
```

---

## 7. Import/Export de Données

### 7.1 CSV

```bash
# Import CSV vers SQLite
sqlite3 eva_data.db ".mode csv" ".import /data/mesures.csv mesures"

# Export SQLite vers CSV
sqlite3 -header -csv eva_data.db "SELECT * FROM mesures WHERE temperature > 100" > alertes.csv
```

### 7.2 JSON

```bash
# Export JSON
sqlite3 -json eva_data.db "SELECT * FROM mesures LIMIT 10" > mesures.json

# Import JSON (SQLite 3.45+)
sqlite3 eva_data.db "INSERT INTO mesures SELECT * FROM json_each(readfile('mesures.json'));"
```

### 7.3 Backup

```bash
# Backup en ligne (sûr même avec WAL)
sqlite3 eva_data.db ".backup /backup/eva_data_$(date +%Y%m%d).db"

# Via la commande .backup
sqlite3 eva_data.db "VACUUM INTO '/backup/eva_data_clean.db'"

# Restauration
sqlite3 eva_data_restored.db ".restore /backup/eva_data_20250601.db"
```

---

## 8. Optimisation et Diagnostic

### 8.1 EXPLAIN QUERY PLAN

```sql
-- Vérifier l'utilisation des index
EXPLAIN QUERY PLAN
SELECT * FROM mesures
WHERE capteur_id = 42
  AND horodatage >= '2025-06-01'
ORDER BY horodatage DESC;

-- Résultats :
-- |--SEARCH mesures USING INDEX idx_mesures_lookup (capteur_id=? AND horodatage>?)
-- |--USE TEMP B-TREE FOR ORDER BY  (si pas couvert par l'index)
```

### 8.2 Analyse de fragmentation

```sql
-- Espace inutilisé dans la base
PRAGMA freelist_count;

-- Compactage
VACUUM;

-- Analyse des statistiques (pour l'optimiseur)
ANALYZE;
```

### 8.3 Profiling

```bash
# Timer sur chaque requête
sqlite3 -timer eva_data.db "SELECT COUNT(*) FROM mesures;"

# .stats on
sqlite3 eva_data.db ".stats on" "SELECT COUNT(*) FROM mesures;"
```

---

## Pièges Courants

1. **Foreign keys désactivées par défaut.** Toujours exécuter `PRAGMA foreign_keys = ON;` après chaque connexion. SQLite ne les active pas automatiquement.

2. **Écritures concurrentes bloquées.** Sans WAL, un writer bloque tous les lecteurs. Toujours utiliser `PRAGMA journal_mode = WAL;`.

3. **Pas de transactions explicites pour les batchs.** 1000 INSERT individuels = 1000 fsync = très lent. Toujours envelopper dans `BEGIN...COMMIT`.

4. **VACUUM sans espace disque.** VACUUM double temporairement la taille du fichier. Vérifier l'espace disque disponible avant.

5. **Index inutiles sur des petites tables.** SQLite charge une table entière rapidement si < 1000 lignes. L'index ajoute juste de la lenteur en écriture.

6. **LIKE avec % en début.** `LIKE '%vibration'` ne peut pas utiliser d'index. Utiliser FTS5 pour la recherche plein texte.

---

## Checklist

- [ ] `PRAGMA journal_mode = WAL` activé
- [ ] `PRAGMA foreign_keys = ON` après chaque connexion
- [ ] `PRAGMA cache_size = -64000` (64MB minimum)
- [ ] `PRAGMA synchronous = NORMAL`
- [ ] Transactions explicites pour les batchs (> 10 INSERT)
- [ ] Index créés sur les colonnes de WHERE, JOIN, ORDER BY
- [ ] FTS5 utilisé pour la recherche plein texte (pas de LIKE '%...%')
- [ ] `VACUUM` et `ANALYZE` périodiques
- [ ] Backup régulier avec `.backup` (sûr même en ligne)
- [ ] `EXPLAIN QUERY PLAN` vérifié pour les requêtes lentes