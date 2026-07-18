---
name: cmms-gmao-integration
description: "Utiliser quand l'utilisateur demande d'interfacer des données automates (compteurs d'heures de marche, alarmes critiques) avec une GMAO (Maximo, Coswin) pour automatiser la maintenance."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [gmao, cmms, predictive-maintenance, maintenance-automation, industrial-databases]
  related_skills: [iso-55001, industrial-databases, industrial-reporting]
---

# Intégration GMAO (Gestion de Maintenance Assistée par Ordinateur)

## Vue d'ensemble

L'interfaçage entre le terrain (OT - automates/supervision) et le système de gestion de la maintenance (**GMAO** ou **CMMS** - Computerized Maintenance Management System, comme IBM Maximo, Coswin, Corim) permet de passer d'une maintenance planifiée arbitrairement (ex: vidange tous les 6 mois) à une **maintenance conditionnelle** basée sur l'utilisation réelle des machines.

Les flux d'intégration clés :
1.  **La remontée de compteurs d'exploitation :** Envoyer le nombre d'heures réelles de fonctionnement d'un moteur ou le nombre de cycles d'un vérin pour déclencher automatiquement un bon de travail (Work Order) dès qu'un seuil est atteint (ex: graissage toutes les 500 heures).
2.  **La création automatique de demandes d'intervention (DI) :** Déclencher une DI immédiate dans la GMAO lorsqu'un défaut bloquant ou une dérive physique (ex: vibrations élevées détectées par capteur) est remonté par l'automate.
3.  **La synchronisation d'état des équipements :** Mettre à jour le statut opérationnel d'une machine (En marche, En panne) dans la GMAO pour calculer la disponibilité globale.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'écrire des scripts (Python, SQL) pour lire des compteurs d'heures de marche sur des automates et les envoyer à la base de données de la GMAO.
- D'implémenter des requêtes d'insertion de demandes d'intervention (DI) en SQL ou via des APIs REST/Web Services.
- De concevoir la logique d'automate pour historiser et cumuler de manière robuste les temps de marche (Uptime) des moteurs.
- D'intégrer des alertes de maintenance basées sur des dérives de capteurs physiques (ex: pressostat encrassé).

**Ne pas utiliser pour :**
- L'utilisation courante ou le paramétrage interne des écrans utilisateurs de la GMAO sans interface temps réel.

---

## 1. Logique Automate robuste de cumul d'heures de marche

Dans l'automate (ST), il faut cumuler le temps de marche de façon à éviter les pertes de précision liées aux arrondis des variables flottantes (`REAL`) sur de grands nombres :

```pascal
// --- CUMULATEUR DE TEMPS DE MARCHE MOTEUR ---
// Variables :
//   Motor_Running         : BOOL (Retour de marche physique)
//   Timer_Pulse_1s        : TON (Timer impulsion de 1 seconde)
//   Accumulated_Seconds   : DINT (Compteur de secondes interne)
//   Accumulated_Hours     : DINT (Compteur d'heures final envoyé au SCADA/GMAO)

// Générateur d'impulsion 1 seconde
Timer_Pulse_1s(IN := NOT Timer_Pulse_1s.Q, PT := T#1s);

IF Motor_Running AND Timer_Pulse_1s.Q THEN
    Accumulated_Seconds := Accumulated_Seconds + 1;
END_IF;

// Conversion en heures toutes les 3600 secondes
IF Accumulated_Seconds >= 3600 THEN
    Accumulated_Hours := Accumulated_Hours + 1;
    Accumulated_Seconds := Accumulated_Seconds - 3600; // Conservation du reste
END_IF;
```

---

## 2. Exemple de Script Python d'intégration GMAO (API REST)

Ce script s'exécute sur une passerelle Edge ou un serveur SCADA pour envoyer périodiquement les compteurs automates à une GMAO possédant une API REST :

```python
import httpx
import logging

logger = logging.getLogger(__name__)

def update_cmms_meter(equipment_id, meter_name, current_value_hours):
    """
    Met à jour un compteur (Meter Reading) dans la GMAO via l'API REST.
    """
    api_url = "https://gmao.usine.local/api/v1/meters"
    headers = {
        "Authorization": "Bearer JWT_SECRET_TOKEN",
        "Content-Type": "application/json"
    }
    
    payload = {
        "equipmentId": equipment_id,
        "meterName": meter_name,
        "readingValue": float(current_value_hours),
        "source": "SCADA_AUTOMATION"
    }
    
    try:
        response = httpx.post(api_url, json=payload, headers=headers, timeout=10.0)
        if response.status_code == 200:
            logger.info(f"Compteur GMAO mis à jour avec succès pour l'équipement {equipment_id}")
            return {"success": True}
        else:
            logger.error(f"Erreur GMAO ({response.status_code}): {response.text}")
            return {"success": False, "error": response.text}
    except Exception as e:
        logger.error(f"Impossible de contacter le serveur GMAO: {e}")
        return {"success": False, "error": str(e)}
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Perte de précision par cumul de petits flottants (Float Precision Loss) :**
    *   *Erreur :* Ajouter directement le temps de cycle en heures sous forme de petit float (`Hours := Hours + (0.1 / 3600.0)`) à chaque pas de programme de 100 ms. Après quelques semaines, la valeur de `Hours` devient tellement grande par rapport au pas d'addition que l'automate n'incrémente plus la variable en raison des limites de précision des nombres réels 32 bits.
    *   *Correction :* Toujours utiliser des compteurs d'entiers (`DINT`) pour cumuler des secondes ou millisecondes, puis réaliser la division en heures uniquement pour l'affichage externe.
2.  **Création infinie de demandes d'intervention (DI Spam) :**
    *   *Erreur :* Déclencher une création de DI directe dans la GMAO sur chaque front d'un défaut fugitif (ex: un capteur thermique qui oscille au-dessus de la limite toutes les secondes). Le serveur de la GMAO sera submergé par des milliers de requêtes, ce qui bloquera la base de données.
    *   *Correction :* Implémenter un filtre anti-rebond (Debounce) ou un verrou logiciel (Latch) côté automate ou passerelle d'intégration. Une seule DI doit être active par code d'erreur tant que celle-ci n'est pas clôturée.

---

## Liste de vérification (Checklist)

- [ ] L'automate utilise des registres de type entier (`DINT`) non sujets aux pertes de précision d'arrondis pour cumuler les temps d'utilisation.
- [ ] Les cumuls d'heures de fonctionnement sont sauvegardés dans des registres persistants (Retentive Memory) résistants aux coupures de courant de l'automate.
- [ ] Un filtre logiciel empêche la création répétée de demandes d'intervention identiques pour le même défaut tant qu'il n'est pas acquitté.
- [ ] L'API de la GMAO est interrogée de manière asynchrone pour éviter de figer le programme d'acquisition principal en cas de latence réseau.

