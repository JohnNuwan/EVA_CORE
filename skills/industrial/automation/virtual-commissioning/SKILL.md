---
name: virtual-commissioning
description: "Simuler des automates et configurer la mise en service."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [virtual-commissioning, simulation, plc-emulation, digital-twins, industrial-automation]
  related_skills: [digital-twins, systematic-debugging]
---

# Mise en Service Virtuelle (Virtual Commissioning)

## Vue d'ensemble

La **Mise en Service Virtuelle (Virtual Commissioning)** consiste à connecter le véritable programme d'un automate (exécuté sur un automate physique ou émulé) à un modèle tridimensionnel et physique de la machine (jumeau numérique). Cette simulation reproduit le comportement dynamique de la machine (déplacement mécanique, capteurs, gravité, flux de produits).

Avantages de la mise en service virtuelle :
1.  **Réduction drastique des temps de chantier :** Les tests de logique et de trajectoires sont validés à 95% en bureau d'études.
2.  **Sécurité des équipements et du personnel :** Détection des risques de collision machine ou de blocages sans risque de détruire du matériel réel.
3.  **Validation précoce des cadences (TRS) :** Analyse des goulots d'étranglement cinématiques avant la fabrication de la machine.

Les outils standards de l'industrie :
*   **Émulation de l'automate :** PLCSIM Advanced (Siemens), TwinCAT Real-Time Virtual (Beckhoff), Logix Emulate (Rockwell).
*   **Simulation comportementale et de flux :** SIMIT (Siemens), Emulate3D (Rockwell), Process Simulate (Siemens Tecnomatix).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De configurer une liaison de données (ex: OPC UA, PLCSIM API, Shared Memory) entre un émulateur de PLC et un outil de simulation.
- D'écrire des scripts de simulation comportementale (ex: modéliser un capteur de proximité qui s'active lorsqu'un modèle 3D passe devant).
- De concevoir la logique automate de simulation pour bypasser les sécurités physiques de terrain lors des tests.
- De structurer des scénarios de test d'injection de pannes (ex: simuler un disjoncteur moteur qui saute pour vérifier la réaction du programme).

**Ne pas utiliser pour :**
- La simple modélisation CAO de pièces en 3D sans notion de comportement dynamique ou de simulation physique.

---

## 1. Architecture de Communication pour la Simulation

La mise en service virtuelle nécessite un canal de communication temps réel bidirectionnel rapide entre l'automate de contrôle et le modèle de simulation.

```text
  [ LOGICIEL AUTOMATE (Studio 5000 / TIA Portal) ]
                        │  Chargement du programme
                        ▼
  [ ÉMULATEUR DE PLC (PLCSIM Advanced / Logix Emulate) ]
                        ▲
                        │  Protocole API locale (ou OPC UA)
                        ▼
  [ LOGICIEL DE SIMULATION 3D (Emulate3D / SIMIT) ]
  (Lit la sortie physique PLC ➔ Anime le modèle 3D)
  (Modèle 3D touche un capteur virtuel ➔ Écrit l'entrée physique PLC)
```

---

## 2. Exemple de Script de Simulation d'un Actionneur (Vérin)

Dans l'outil de simulation (ici représenté sous forme de logique de script Python générique utilisable dans des outils comme Emulate3D), il faut simuler le temps physique de déplacement des équipements.

```python
# --- SCRIPT DE SIMULATION DE VÉRIN PNEUMATIQUE DOUBLE EFFET ---
# Ce script simule le comportement d'un vérin physique.
# Il lit la commande PLC et écrit les fins de course en retour.

class CylinderSimulation:
    def __init__(self, stroke_time_seconds):
        self.stroke_time = stroke_time_seconds
        self.current_position = 0.0 # 0.0 = Rentre (Home), 1.0 = Sorti (Work)
        
    def update(self, cmd_sortir, cmd_rentrer, delta_time_seconds):
        """
        Appelé à chaque pas de calcul de la simulation (ex: toutes les 10 ms).
        """
        # Constante de vitesse (déplacement par seconde)
        speed = 1.0 / self.stroke_time
        
        if cmd_sortir and not cmd_rentrer:
            # Le vérin sort
            self.current_position += speed * delta_time_seconds
            if self.current_position > 1.0:
                self.current_position = 1.0
        elif cmd_rentrer and not cmd_sortir:
            # Le vérin rentre
            self.current_position -= speed * delta_time_seconds
            if self.current_position < 0.0:
                self.current_position = 0.0
                
        # Calcul des signaux de fin de course renvoyés à l'automate (Entrées PLC)
        # On ajoute une marge de tolérance physique (butée à 1% de la course)
        sensor_rentre = self.current_position <= 0.01
        sensor_sorti = self.current_position >= 0.99
        
        # Détection de collision (défaut double commande)
        sensor_fault = cmd_sortir and cmd_rentrer
        
        return {
            "sensor_rentre": sensor_rentre,
            "sensor_sorti": sensor_sorti,
            "error_collision": sensor_fault
        }
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Désynchronisation temporelle (Time Scaling) :**
    *   *Erreur :* Exécuter la simulation 3D en temps réel non synchronisé alors que l'automate émulé s'exécute en mode "temps accéléré" ou subit des dérives de calcul de tâche de la machine Windows. Les temporisations automates expireront trop tôt.
    *   *Correction :* Utiliser une synchronisation de pas d'horloge (Clock Sync) entre le simulateur et l'émulateur d'automate (ex: PLCSIM Advanced gère le mode "Synchrone" où il attend l'autorisation de pas de calcul du jumeau numérique).
2.  **Ignorer le rebond et l'inertie physique :**
    *   *Erreur :* Écrire un simulateur qui renvoie une valeur d'entrée à `TRUE` instantanément à l'écriture de la commande. Les filtres d'entrées ou les détections de front de l'automate ne réagiront pas comme avec du matériel physique.
    *   *Correction :* Intégrer des temps de réponse physiques réalistes (ex: 200 ms pour l'ouverture d'une vanne pneumatique) et des bruits ou rebonds de capteurs si nécessaire.

---

## Liste de vérification (Checklist)

- [ ] L'émulateur d'automate et le simulateur 3D sont synchronisés sur la même horloge logique de simulation (Clock Sync).
- [ ] Tous les actionneurs physiques majeurs (moteurs, vérins, vannes) possèdent un script de comportement simulant leur temps de déplacement réel.
- [ ] Les arrêts d'urgence et barrières physiques de sécurité sont simulés pour vérifier les coupures d'énergies automates.
- [ ] Un test de robustesse par injection de défauts (ex: bloquer un capteur) valide la mise en sécurité de la machine émulée.

