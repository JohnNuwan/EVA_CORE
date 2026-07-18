---
name: process-pharma
description: "Utiliser quand l'utilisateur demande d'écrire du code, de configurer des systèmes SCADA ou d'analyser des procédés pour les secteurs pharmaceutique et biologique sous contraintes réglementaires GAMP 5 et FDA 21 CFR Part 11."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [pharma, biological, gamp5, 21-cfr-part-11, audit-trail, isa-88, validation, industrial-automation]
    related_skills: [simplify-code, plan]
---

# Procédés Pharmaceutiques & Biologiques (GAMP 5 & FDA 21 CFR Part 11)

## Vue d'ensemble

Les industries pharmaceutiques et biologiques sont soumises à des contraintes réglementaires strictes visant à garantir la sécurité du patient et la qualité constante des produits. Les deux principaux piliers sont :
1. **GAMP 5 (Good Automated Manufacturing Practice) :** Un guide méthodologique de cycle de vie pour la validation des systèmes automatisés (Spécifications, Qualification de Conception, Qualification d'Installation QI, Qualification Opérationnelle QO, Qualification de Performance QP).
2. **FDA 21 CFR Part 11 (et son équivalent européen Annexe 11 des BPF) :** Exigences sur la sécurité des données, l'intégrité des enregistrements électroniques (ALCOA+), les signatures électroniques et l'**Audit Trail** (journal d'événements inaltérable).

Cette compétence guide l'agent EVA pour écrire du code et concevoir des systèmes de traçabilité conformes à ces contraintes.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De concevoir ou de programmer un journal d'événements ou un système d'Audit Trail dans une IHM/SCADA (ex: Ignition).
- D'implémenter des règles de traçabilité et de double signature électronique (ex: approbation de recettes).
- De structurer des programmes automates de fabrication par lots selon la norme **ISA-88**.
- De rédiger des fiches de tests de qualification (QI/QO) pour du code.

**Ne pas utiliser pour :**
- Des applications grand public ou des applications industrielles hors des sciences de la vie (sans contrainte réglementaire de santé).

---

## 1. Conception d'un Audit Trail (Journal d'Événements Inaltérable)

Un Audit Trail conforme à la norme 21 CFR Part 11 doit enregistrer de manière sécurisée et chronologique : *Qui a fait l'action, Quoi (ancienne/nouvelle valeur), Quand (horodatage), Pourquoi (justification) et depuis Où (poste client)*. Les enregistrements ne doivent jamais pouvoir être modifiés ou supprimés.

### Exemple de script d'Audit Trail (Jython Ignition) lors d'une modification de paramètre :

```python
def log_parameter_change(username, tag_path, old_value, new_value, reason, client_ip):
    """Enregistre une action opérateur de manière sécurisée dans la table Audit Trail.
    
    La table SQL associée doit être configurée en lecture seule pour les utilisateurs standard
    et ne posséder aucun droit d'exécution de DELETE ou UPDATE (Audit Trail inaltérable).
    """
    if not reason or len(reason.strip()) < 5:
        raise ValueError("Une justification d'au moins 5 caractères est requise pour modifier ce paramètre.")
        
    query = """
        INSERT INTO audit_trail (t_stamp, username, action_type, detail, old_value, new_value, reason, client_ip)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # Détails de l'action
    action_type = "VALVE_LIMIT_CHANGE"
    detail = "Modification du tag: %s" % tag_path
    
    # Insertion sécurisée via requête préparée
    system.db.runPrepUpdate(query, [
        system.date.now(),
        username,
        action_type,
        detail,
        str(old_value),
        str(new_value),
        reason,
        client_ip
    ], "DB_Pharma_Audit")
```

---

## 2. Structure ISA-88 pour la Fabrication par Lots (Batch Control)

La norme ISA-88 définit un modèle physique et un modèle procédural. La logique automate doit être découpée en phases d'équipement (Equipment Phases) contrôlées par un gestionnaire d'états (State Machine) standardisé :

```
          [ IDLE ] ──( Start )──> [ RUNNING ] ──( Complete )──> [ COMPLETED ]
             │                         │
          ( Abort )                 ( Hold )
             │                         │
             v                         v
        [ ABORTING ]               [ HOLDING ]
             │                         │
        ( Aborted )                 ( Held )
             │                         │
             v                         v
        [ ABORTED ]                [ HELD ] ──( Restart )──> [ RESTARTING ]
```

### Exemple de structure d'état de Phase en SCL Siemens :

```scl
CASE #stat_PhaseState OF
    1:  // IDLE (Attente consigne)
        #q_Actuator := FALSE;
        IF #i_CmdStart THEN
            #stat_PhaseState := 2; // Passage à RUNNING
        END_IF;
        
    2:  // RUNNING (Phase active de mélange par exemple)
        #q_Actuator := TRUE;
        IF #i_TempReached AND #i_TimerDone THEN
            #stat_PhaseState := 3; // Passage à COMPLETED
        END_IF;
        
    3:  // COMPLETED (Terminé avec succès)
        #q_Actuator := FALSE;
        #q_PhaseDone := TRUE;
        
    4:  // HELD (Mise en pause de sécurité)
        #q_Actuator := FALSE;
        IF #i_CmdRestart THEN
            #stat_PhaseState := 2; // Retour à RUNNING
        END_IF;
END_CASE;
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Possibilité d'effacer les journaux (Audit Trail contournable) :**
   * *Erreur :* Stocker l'Audit Trail dans une table de base de données standard où les utilisateurs du système IHM ou de simples techniciens ont le droit de faire un `DROP TABLE` ou des requêtes de suppression `DELETE`.
   * *Correction :* Configurer des droits stricts sur le serveur SQL de sorte que l'utilisateur de l'application SCADA possède uniquement des droits d'insertion (`INSERT`) sur la table Audit Trail, et aucun droit de modification/suppression.

2. **Absence de justification opérateur obligatoire :**
   * *Erreur :* Autoriser la modification de consignes critiques (ex: température de stérilisation) sans forcer la saisie d'un commentaire expliquant la raison du changement.
   * *Correction :* Bloquer l'écriture dans l'IHM tant qu'un champ texte de justification n'est pas rempli et validé.

---

## Liste de vérification (Checklist)

- [ ] L'Audit Trail enregistre l'identité de l'opérateur, l'horodatage, l'ancienne valeur, la nouvelle valeur et la justification.
- [ ] La base de données de l'Audit Trail est sécurisée (droit d'insertion uniquement pour le compte applicatif).
- [ ] Les étapes de fabrication de lots respectent la hiérarchie physique et logique de la norme ISA-88 (Machine d'état à phases).
- [ ] Tout code généré intègre des mécanismes d'authentification ou de double signature pour les opérations critiques.

