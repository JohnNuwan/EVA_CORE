# Génération Rockwell Multi-Zone par Sous-Agents Parallèles

## Contexte

Pour les projets industriels de grande envergure (50+ FDS, 7+ zones fonctionnelles), la génération séquentielle de chaque FDS est trop lente. Cette référence documente l'approche par sous-agents parallèles (via `delegate_task`) utilisée sur le projet RGY.

## Workflow

```
1. INGESTION PROJET
   ├── Lire la Cell List / I/O List (XLS) → architecture globale
   ├── Lire les GENERALITIES → UDTs/AOIs standards
   └── Cartographier les zones (dossiers) et skids

2. DÉLÉGATION PARALLÈLE (3 sous-agents max)
   ├── Sous-agent 1 : Zones A, B
   ├── Sous-agent 2 : Zones C, D
   └── Sous-agent 3 : Zones E, F, G

3. CHAQUE SOUS-AGENT
   ├── Liste les fichiers .docx/.pdf (ignore ~$*)
   ├── Lit chaque FDS avec python-docx
   ├── Extrait séquences, états, timers, permissifs
   ├── Génère : xxx.st + xxx_AOI.L5X + xxx_Routine.L5X
   ├── Respecte les conventions Rockwell (:=, ;, TON, CASE, CDATA, ≤40 chars)
   └── Écrit dans output/rockwell_gen/{PROJET}/{ZONE}/

4. CONSOLIDATION
   ├── Compte les fichiers par zone
   ├── Vérifie les fichiers manquants (FDS sans .docx)
   └── Signale les zones incomplètes
```

## Contraintes techniques

- **Limite de parallélisme** : `delegate_task` supporte max 3 sous-agents par lot. Planifier 2-3 lots si le projet a plus de zones.
- **Pas d'accès à async_call_llm** : Les sous-agents ne peuvent pas utiliser le script `generate_rockwell_from_fds.py` (qui dépend de `agent.auxiliary_client`). Ils doivent implémenter leur propre logique LLM ou générer le code directement.
- **Taille des FDS** : Les FDS SUPERPOSITION/SUPERVISION peuvent faire 6 MB+ (Word avec images). Extraire uniquement le texte via python-docx.
- **Timeout** : Chaque sous-agent a un timeout de ~1200 secondes (20 min). Prévoir des lots suffisamment petits pour tenir dans cette limite.

## Pièges spécifiques

### Fichiers temporaires Office (~$)
- **Problème** : Quand un fichier .docx est ouvert dans Word, Office crée un fichier `~$NOM_DU_FICHIER.docx` de 162 octets.
- **Symptôme** : `read_file` échoue avec une erreur XML malformed. Le fichier fait ~160 octets au lieu de plusieurs centaines de KB.
- **Solution** : Filtrer avec `grep -v "~$"` ou `[f for f in files if not f.startswith('~$')]`.

### FDS disponibles uniquement en PDF
- **Problème** : Certains FDS n'existent qu'en PDF, pas de .docX original.
- **Impact** : Le script python-docx ne peut pas les lire. Il faut pypdf pour l'extraction.
- **Solution** : Pour les sous-agents, préférer pypdf (qui fonctionne dans un subprocess) ou lire le PDF via read_file + vision tool si le PDF est scanné.

### FDS manquants (fichiers fantômes)
- **Problème** : Un dossier peut ne contenir QUE des `~$` fichiers (les .docx ont été déplacés ou supprimés après ouverture).
- **Symptôme** : Le sous-agent liste 0 fichiers valides dans le dossier.
- **Solution** : Vérifier aussi les dossiers `Master/` et `SENT/` qui contiennent parfois les originaux.

### Nombre de fichiers par zone
- Un sous-agent qui doit traiter 20+ FDS (comme 02-GRINDING) va saturer son propre contexte.
- **Solution** : Si une zone dépasse 15 FDS, la diviser en sous-zones (ex: GRINDING-DOSAGE, GRINDING-TRANSFERT, GRINDING-MELANGEURS).

### README de projet
- **Obligatoire** : Après consolidation, créer un `README.md` à la racine du projet de sortie (`output/rockwell_gen/{PROJET}/README.md`) documentant :
  - La structure du projet (arborescence zone par zone)
  - La liste des FDS sources
  - Les UDTs standards créés
  - Les instructions d'import dans Studio 5000 (3 options : projet master, programme zone, AOI individuelle)
  - Les cellules et équipements couverts
  - Les statistiques (nb fichiers, lignes, taille)
  - Les points d'attention (FDS manquants, mapping E/S à compléter)
- Le README sert de point d'entrée pour l'automaticien qui réceptionne le livrable

## Exemples vécus

Sur le projet RGY (7 zones, ~45 FDS) :
- Lot 1 : 00-GENERAL + 01-RECEPTION (2 sous-agents, OK)
- Lot 2 : 02-GRINDING + 03-EXTRUSION + 04-PACKAGING/08-INTERFACE/09-UTILITY (3 sous-agents)
- Résultat : 152 fichiers (54 ST + 98 L5X), ~648 KB, 7 dossiers de sortie
- Durée totale : ~40 minutes
- Fichiers absents signalés : 9 FDS dans 03-EXTRUSION/ (docx manquants, seulement ~$)

*Documenté le 2026-07-06 — Session projet RGY.*

### Projet ROH (5 FDS, 1 zone, PDF uniquement)

Projet plus petit mais avec une contrainte spécifique : **tous les FDS sont en PDF** (pas de DOCX).

- 5 FDS extrusion : calibration NAOX, calibration générale, aspiration élévateur, aspiration sécheur, aspiration enrobeur
- Extraction via `pypdf` (23-26 pages par document, ~130K caractères)
- Génération : 5 ST + 10 L5X (5 AOI + 5 Routine)
- Projet master : 1 031 lignes
- **Leçon** : L'extraction PDF est moins fiable que DOCX (tableaux déformés, textes dans des ordres non linéaires). Vérifier la cohérence du code généré.

*Documenté le 2026-07-06 — Session projet ROH.*