---
name: delphi-industrial-programming
description: Expertise en maintenance, analyse et développement Delphi (Object Pascal) en milieu industriel.
version: 1.0.0
author: EVA
license: Privée EVA
platforms: [windows]
metadata:
  EVA:
    tags: [delphi, object-pascal, vcl, industrial, legacy, maintenance]
---

# Expert Delphi (Object Pascal) en milieu industriel

Cette compétence définit les standards d'analyse, de maintenance et d'optimisation pour les systèmes basés sur Delphi (VCL/FMX).

## Principes d'Expertise
1. **Analyse Systémique :** Toujours inspecter les fichiers projet (`.dproj`, `.dpr`) et l'arborescence des bibliothèques avant toute modification pour identifier les dépendances tierces (Indy, DevExpress, etc.).
2. **Gestion de Mémoire :** Utilisation stricte de blocs `try...finally` pour toute création d'objet.
3. **Sécurité Thread-Safe :** Utilisation des primitives de synchronisation (TThread.Synchronize, TThread.Queue) pour l'accès aux interfaces utilisateur depuis des processus en arrière-plan.
4. **Intégration Industrielle :** Prioriser l'interfaçage via des DLL documentées pour les drivers PLC (Beckhoff ADS, Siemens S7, Modbus) plutôt que des wrappers bruts.

## Pitfalls (Erreurs classiques à éviter)
- **Fuites Mémoire (Memory Leaks) :** Objets créés dans une méthode mais non détruits en sortie.
- **Accès Multi-thread :** Manipulation directe de composants VCL depuis un thread secondaire (source de crashes).
- **Dépendances Obsolètes :** Usage de composants BDE ou ADO dépréciés sans planification de migration vers FireDAC.

## Références
- `references/debug.md` : Guide de diagnostic pour les crashs d'applications Delphi.
- `scripts/check_leaks.pas` : Script de vérification de fuites mémoire simple si FastMM est activé.
