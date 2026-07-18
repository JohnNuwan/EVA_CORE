---
name: mes-integration
description: "Interfacer les automates avec un système MES."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [mes, isa-95, isa-88, scada, erp, industrial-automation, traceability, recipe-management, production-tracking, handshake-protocol]
    related_skills: [isa95-modelling, industrial-protocols, industrial-databases, sparkplug-b, plc-diagnostic]
---

# Intégration MES (Manufacturing Execution System)

## Vue d'ensemble

Un **MES (Manufacturing Execution System)** est le système logiciel central qui fait le pont entre le système de gestion de l'entreprise **(ERP)** et le pilotage direct de l'usine **(SCADA/PLC)**. Conformément à la norme **ISA-95** (CEI 62264), le MES opère au **niveau 3** du modèle hiérarchique de l'entreprise industrielle (Purdue/CIM).

### Les 4 piliers de l'intégration MES-Automates

1. **Descente d'ordres de fabrication (OF)** : Envoi de paramètres de consigne, recettes et nomenclatures directement aux automates. Exemple : changement de format de production sur une ligne de conditionnement.

2. **Remontée de production (Tracking)** : Collecte automatisée des indicateurs de production — nombre de pièces produites, rebutées, temps de cycle, cadence. Alimentation des tableaux de bord TRS/OEE.

3. **Traçabilité et généalogie** : Association des lots de matières premières (via scans codes-barres ou RFID) à chaque produit fini. Garantit la conformité réglementaire (FDA, ISO 22000, IATF 16949).

4. **Contrôle qualité intégré** : Déclenchement de prélèvements d'échantillons en fonction du volume produit, arrêt automatique en cas de dérive de paramètres qualité.

### Normes et standards

| Norme | Rôle | Application |
|-------|------|-------------|
| **ISA-95 (CEI 62264)** | Modèle d'intégration entreprise-contrôle | Structuration des échanges ERP ↔ MES ↔ SCADA |
| **ISA-88 (CEI 61512)** | Modèle de recettes et procédés batch | Gestion des recettes, phases, unités |
| **OPC UA** | Protocole de transport OT | Échange structuré de données entre MES et automates |
| **B2MML (Business To Manufacturing Markup Language)** | XML ISA-95 standardisé | Format d'échange entre ERP et MES |

---

## Quand l'utiliser

### Cas d'usage

À utiliser lorsque l'utilisateur demande :

- D'interfacer une supervision (ex: Ignition, Wonderware, WinCC) avec un MES (ex: Siemens Opcenter, Rockwell FTPC, Aveva MES, Apriso).
- De concevoir des **bases de données de recettes** ou d'ordres de fabrication transférables aux automates.
- D'intégrer des scanners de **traçabilité** (lecteurs codes-barres, RFID) dans des automates.
- D'implémenter des **transactions transactionnelles robustes (handshakes)** pour le transfert d'informations critiques entre PLC et MES.
- De modéliser un **échange ISA-95** entre un ERP SAP, un MES et des automates Siemens/Rockwell.

### Ne pas utiliser pour

- La simple programmation de logique d'automate sans échange de données ERP/MES.
- La configuration de serveurs OPC UA sans lien avec un MES.

---

## 1. Protocole d'Échange Transactionnel (Handshake) PLC-MES

Lors du transfert d'informations critiques (par ex. « Début d'ordre de fabrication », « Changement de recette »), il ne faut **jamais** utiliser une simple écriture directe non sécurisée. On implémente une **poignée de main (handshake)** basée sur des registres d'état mutuellement contrôlés.

### 1.1 Diagramme de séquence du handshake

```
PLC                                 MES
 │                                   │
 │  PLC_Status_Ready = TRUE          │
 │◄──────────────────────────────────│
 │  MES_Trigger_Load = TRUE          │  1. MES demande le chargement
 │  MES_Recipe_ID = 42               │
 │──────────────────────────────────►│
 │                                   │
 │  PLC_Status_Busy = TRUE           │  2. PLC accuse réception, commence
 │  PLC_Status_Ready = FALSE         │
 │◄──────────────────────────────────│
 │                                   │
 │  (Validation interne)             │  3. Traitement côté PLC
 │                                   │
 │  PLC_Status_Done = TRUE           │  4. PLC signale la fin (ou Error)
 │  PLC_Status_Busy = FALSE          │
 │◄──────────────────────────────────│
 │                                   │
 │  MES_Trigger_Load = FALSE         │  5. MES acquitte en remettant à zéro
 │──────────────────────────────────►│
 │                                   │
 │  PLC_Status_Ready = TRUE          │  6. PLC prêt pour prochain échange
 │◄──────────────────────────────────│
```

### 1.2 Implémentation en Structured Text (ST)

```pascal
// --- SÉQUENCE DE CHARGEMENT DE RECETTE DEPUIS LE MES ---
// Interface IO :
//   MES_Trigger_Load   : BOOL ; Écrit par le MES, front montant = requête
//   MES_Recipe_ID      : DINT ; Écrit par le MES, identifiant recette
//   PLC_Status_Ready   : BOOL ; PLC prêt à recevoir une commande
//   PLC_Status_Busy    : BOOL ; PLC en cours de traitement
//   PLC_Status_Done    : BOOL ; Chargement terminé avec succès
//   PLC_Status_Error   : BOOL ; Erreur de paramètres

// Détection du front montant de MES_Trigger_Load
MES_Trigger_Load_R_TRIG(CLK := MES_Trigger_Load);
IF MES_Trigger_Load_R_TRIG.Q AND PLC_Status_Ready AND NOT PLC_Status_Busy THEN
    // Phase 1 : Acquittement de la requête
    PLC_Status_Ready := FALSE;
    PLC_Status_Busy  := TRUE;
    PLC_Status_Done  := FALSE;
    PLC_Status_Error := FALSE;

    // Phase 2 : Validation des données recette
    IF MES_Recipe_ID > 0 AND MES_Recipe_ID <= MAX_RECIPES THEN
        // Charger la recette en mémoire active
        Active_Recipe := Recipe_Database[MES_Recipe_ID];
        Recipe_Load_OK := TRUE;
    ELSE
        Recipe_Load_OK := FALSE;
    END_IF;

    // Phase 3 : Signal de fin
    PLC_Status_Busy := FALSE;
    IF Recipe_Load_OK THEN
        PLC_Status_Done := TRUE;   // Signal de succès
    ELSE
        PLC_Status_Error := TRUE;  // Signal d'erreur
    END_IF;
END_IF;

// Phase 4 : Réinitialisation par le MES (front descendant)
MES_Trigger_Load_F_TRIG(CLK := MES_Trigger_Load);
IF MES_Trigger_Load_F_TRIG.Q AND (PLC_Status_Done OR PLC_Status_Error) THEN
    PLC_Status_Done  := FALSE;
    PLC_Status_Error := FALSE;
    PLC_Status_Ready := TRUE;
END_IF;
```

---

## 2. Conception des Bases de Données d'Interface

### 2.1 Table de staging pour les consommations matières

Une base de données intermédiaire (staging/interface) est utilisée pour découpler le MES des automates :

```sql
-- Table de staging pour les consommations matières
CREATE TABLE mes_material_consumption (
    log_id              INT AUTO_INCREMENT PRIMARY KEY,
    production_order_id VARCHAR(50)  NOT NULL,    -- Identifiant OF ERP
    equipment_path      VARCHAR(255) NOT NULL,    -- Chemin équipement (ex: Ligne01/Poste02)
    material_lot_number VARCHAR(100) NOT NULL,    -- Numéro de lot matière première
    quantity_consumed   DECIMAL(10,3) NOT NULL,   -- Quantité consommée
    unit_of_measure     VARCHAR(10)  NOT NULL,    -- Unité (kg, L, pcs)
    operator_id         VARCHAR(50),              -- ID opérateur (si scan manuel)
    timestamp           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status              VARCHAR(20) DEFAULT 'PENDING',
    -- Contrainte : un statut valide
    CONSTRAINT chk_status CHECK (status IN ('PENDING', 'PROCESSED', 'ERROR')),
    INDEX idx_order (production_order_id),
    INDEX idx_status (status)
);
```

### 2.2 Table de gestion des recettes

```sql
CREATE TABLE mes_recipes (
    recipe_id       INT PRIMARY KEY,
    recipe_name     VARCHAR(100) NOT NULL,
    recipe_version  INT DEFAULT 1,
    valid_from      DATETIME,
    valid_to        DATETIME,
    parameters      JSON,             -- Paramètres de la recette (flexible)
    is_active       BOOLEAN DEFAULT TRUE,
    created_by      VARCHAR(50),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des paramètres de recette par équipement
CREATE TABLE mes_recipe_parameters (
    param_id        INT AUTO_INCREMENT PRIMARY KEY,
    recipe_id       INT NOT NULL REFERENCES mes_recipes(recipe_id),
    equipment_id    VARCHAR(50) NOT NULL,
    parameter_name  VARCHAR(100) NOT NULL,
    parameter_value VARCHAR(255) NOT NULL,
    data_type       VARCHAR(20) DEFAULT 'STRING',
    UNIQUE KEY uq_param (recipe_id, equipment_id, parameter_name)
);
```

### 2.3 Procédure de synchronisation (Stored Procedure)

```sql
DELIMITER //
CREATE PROCEDURE sp_sync_pending_consumptions()
BEGIN
    -- Traiter les consommations en attente vers le MES
    UPDATE mes_material_consumption
    SET status = 'PROCESSED'
    WHERE status = 'PENDING'
      AND timestamp < NOW() - INTERVAL 5 SECOND;  -- Délai de sécurité

    -- Signaler les anomalies (données en attente depuis > 1h)
    UPDATE mes_material_consumption
    SET status = 'ERROR'
    WHERE status = 'PENDING'
      AND timestamp < NOW() - INTERVAL 1 HOUR;
END //
DELIMITER ;
```

---

## 3. Architecture de Buffer Local (Edge Computing)

En cas de perte réseau entre l'usine et le serveur MES, l'automate (ou la passerelle Edge) doit **continuer à produire et bufferiser les données**.

### 3.1 Buffer FIFO en logique automate

```pascal
// Tampon circulaire FIFO pour les logs de production
// Configuration
CONSTANT
    FIFO_SIZE : INT := 100;    // Taille max du buffer (100 entrées)
END_VAR

VAR
    // Données du buffer
    Buffer_Orders      : ARRAY[0..FIFO_SIZE-1] OF STRING[50];
    Buffer_Timestamps  : ARRAY[0..FIFO_SIZE-1] OF DT;
    Buffer_Quantities  : ARRAY[0..FIFO_SIZE-1] OF REAL;

    // Pointeurs
    Head_Ptr : INT := 0;       // Prochaine écriture
    Tail_Ptr : INT := 0;       // Prochaine lecture
    Count    : INT := 0;       // Éléments dans le buffer

    MES_Online : BOOL;         // TRUE si MES accessible
END_VAR

// Ajout d'une entrée (appelé à chaque fin de cycle produit)
IF Count < FIFO_SIZE THEN
    Buffer_Orders[Head_Ptr]     := Current_Order_ID;
    Buffer_Timestamps[Head_Ptr] := NOW();
    Buffer_Quantities[Head_Ptr] := Current_Product_Count;

    Head_Ptr := (Head_Ptr + 1) MOD FIFO_SIZE;
    Count    := Count + 1;
END_IF;

// Vidage vers MES (appelé périodiquement)
IF MES_Online AND Count > 0 THEN
    // Envoyer Buffer_Orders[Tail_Ptr] au MES via protocole configuré
    // ...
    Tail_Ptr := (Tail_Ptr + 1) MOD FIFO_SIZE;
    Count    := Count - 1;
END_IF;
```

### 3.2 Indicateurs d'état du buffer

| Taux de remplissage | État | Action |
|---------------------|------|--------|
| 0–30 % | Normal | Aucune |
| 30–70 % | Surveillance | Vérifier réseau MES |
| 70–90 % | Alarme | Diagnostic MES urgent |
| > 90 % | Critique | Risque de perte de données |

---

## Pièges Courants (Common Pitfalls)

1. **Absence de buffer local en cas de perte réseau :**
   * *Erreur :* Envoyer des données de traçabilité directement au MES sans stockage local (FIFO côté automate). Si le serveur MES ou le réseau tombe, la production s'arrête ou les données de traçabilité sont perdues.
   * *Correction :* Implémenter un buffer FIFO (circulaire) dans l'automate ou la passerelle locale (Edge) pour stocker les logs de production hors ligne et les synchroniser lors du retour au réseau.

2. **Écritures concurrentes sans verrouillage d'état :**
   * *Erreur :* Laisser le MES écrire des valeurs de consigne dans l'automate pendant que la machine est en cours de cycle automatique, provoquant des changements de paramètres intempestifs.
   * *Correction :* Verrouiller les variables d'écriture de recettes côté automate. N'autoriser les modifications de consignes que lorsque la machine est à l'état « Idle » (Arrêtée/Prête). Utiliser l'état machine ISA-88.

3. **Absence d'horodatage unifié :**
   * *Erreur :* L'automate utilise son horloge locale, le MES utilise l'heure du serveur SQL. Les timestamps des événements de production diffèrent, rendant la traçabilité incohérente.
   * *Correction :* Synchroniser l'horloge de tous les automates via NTP (Network Time Protocol) sur le même serveur de temps que le MES. Configurer dans TIA Portal / Studio 5000 le NTP primaire.

4. **Pas de gestion d'erreur dans le protocole handshake :**
   * *Erreur :* Si le MES écrit `MES_Trigger_Load = TRUE` mais le PLC est déjà en Busy, le message est ignoré silencieusement.
   * *Correction :* Toujours lire l'état `PLC_Status_Ready` avant d'écrire `MES_Trigger_Load`. Utiliser des timeouts pour détecter les handshakes bloqués.

5. **Ignorer les contraintes de temps réel :**
   * *Erreur :* Configurer une tâche cyclique critique (ex: régulation PID) avec des blocs de communication MES qui peuvent prendre plusieurs secondes, faisant dépasser le temps de cycle.
   * *Correction :* Déporter tous les échanges MES dans une tâche asynchrone ou un bloc FB dédié, exécuté à basse priorité.

---

## Liste de vérification (Checklist)

- [ ] Un protocole de handshake robuste (Trigger → Busy → Done/Error → Reset) est utilisé pour tous les transferts de données critiques.
- [ ] Le diagramme de séquence du handshake est documenté et validé avec l'équipe MES.
- [ ] L'automate dispose d'un buffer FIFO de secours pour continuer à produire en cas de panne réseau MES.
- [ ] Les variables de consignes (recettes) ne sont modifiables que lorsque l'équipement est dans un état sûr (Idle).
- [ ] La traçabilité associe de manière unique l'identifiant OF (Ordre de Fabrication) avec les lots de matière consommés.
- [ ] Tous les automates sont synchronisés via NTP sur le même serveur de temps que le MES.
- [ ] Les temps de cycle automate incluent une marge pour les blocs de communication MES.
- [ ] La base de données de staging utilise des index et des contraintes CHECK pour garantir l'intégrité.
- [ ] Un mécanisme de purge (archivage) des données de staging est prévu (max 7 jours de buffer).

