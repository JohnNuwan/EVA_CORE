---
name: plc-robot-dialogue
description: "Concevoir le dialogue et la synchronisation PLC/Robot."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [plc, robot, synchronization, handshake, industrial-protocols, communication, safety, collision-avoidance]
  related_skills: [siemens-scl-generation, robotics-fanuc, robotics-kuka, robotics-abb]
---

# Dialogue, Synchronisation & Sécurisation de Collision PLC / Robot

## Vue d'ensemble

Cette compétence régit la conception de protocoles de communication temps réel et sécurisés (handshakes) pour le dialogue entre un automate programmable (PLC) et des contrôleurs de robots industriels. Elle traite spécifiquement de la gestion d'évitement de collision physique via des **Zones d'Interférence Mutuelle** et de l'intégration des réseaux de sécurité (**PROFIsafe / CIP Safety**).

---

## Intégration de la Sécurité Machine (PROFIsafe / CIP Safety)

En plus de l'échange de données de process standards, les îlots robotisés s'appuient sur des protocoles de sécurité réseaux sécurisés (certifiés SIL 3 / PL e) pour transférer les signaux d'arrêts et d'autorisation de mouvements.

### Mots de Sécurité type (PROFIsafe) :
* **Sécurité PLC -> Robot** :
  * `Safety_ES_OK` : Signal de l'arrêt d'urgence général de la ligne OK.
  * `Safety_Gate_Closed` : Protecteurs mobiles (portes grillagées) fermés et verrouillés.
  * `Safety_Enable_Robot` : Autorisation de puissance variateur du robot.
* **Safety Robot -> PLC** :
  * `Safety_ES_Pressed` : Bouton d'arrêt d'urgence de la console robot appuyé.
  * `Safety_In_SafeState` : Le robot est sous contrôle de sa boucle de sécurité (axes immobiles ou vitesse limitée de sécurité).

---

## Logique de Synchronisation de Zone d'Interférence (Collision)

Lorsque deux robots (Robot A et Robot B) ou un robot et une machine partagent un même volume physique de travail, le PLC doit allouer l'accès à ce volume de manière exclusive afin d'éviter toute collision mécanique.

### Algorithme de Handshake de Zone :
1. Le robot arrive à la frontière de la zone. Il s'arrête et met son bit de requête à 1 (`bReq_Zone1`).
2. Le PLC analyse la table d'allocation. Si la zone est libre, il alloue l'accès au robot en mettant le bit d'autorisation à 1 (`bGrant_Zone1`).
3. Le robot détecte `bGrant_Zone1 = TRUE`, pénètre dans la zone, exécute sa tâche, puis ressort.
4. Dès qu'il a franchi la frontière de sortie, le robot repasse `bReq_Zone1` à 0.
5. Le PLC détecte le relâchement et repasse `bGrant_Zone1` à 0. La zone est à nouveau disponible.

---

## Code d'Allocation de Zone d'Interférence Mutuelle (PLC ST)

Ce bloc fonctionnel gère l'autorisation d'accès exclusif à une zone partagée pour deux robots et génère un défaut de collision imminent si un robot pénètre sans autorisation.

```pascal
FUNCTION_BLOCK "FB_CollisionAvoidance"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 1.0
   VAR_INPUT 
      bReqRobotA     : Bool;     // Demande d'accès de la zone 1 par Robot A
      bInZoneRobotA  : Bool;     // Capteur / Bit de présence physique effectif du Robot A dans la zone 1
      
      bReqRobotB     : Bool;     // Demande d'accès de la zone 1 par Robot B
      bInZoneRobotB  : Bool;     // Capteur / Bit de présence physique effectif du Robot B dans la zone 1
   END_VAR

   VAR_OUTPUT 
      bGrantRobotA   : Bool;     // Autorisation accordée au Robot A
      bGrantRobotB   : Bool;     // Autorisation accordée au Robot B
      bCollisionFault: Bool;     // Alarme critique : Pénétration non autorisée (Risque de collision !)
   END_VAR

   VAR 
      iCurrentAlloc  : Int := 0;  // 0 = Libre, 1 = Alloué Robot A, 2 = Alloué Robot B
      instTmrFault   : TON;      // Timer de validation d'alarme
   END_VAR

BEGIN
    // 1. MACHINE D'ALLOCATION LOGIQUE DE LA ZONE
    CASE #iCurrentAlloc OF
        0:  // ZONE LIBRE
            #bGrantRobotA := FALSE;
            #bGrantRobotB := FALSE;
            
            // Priorité au premier demandeur
            IF #bReqRobotA THEN
                #iCurrentAlloc := 1;
            ELIF #bReqRobotB THEN
                #iCurrentAlloc := 2;
            END_IF;
            
        1:  // ALLOUÉE AU ROBOT A
            #bGrantRobotA := TRUE;
            #bGrantRobotB := FALSE;
            
            // Libération de la zone dès que le robot A relâche sa demande et est physiquement sorti
            IF NOT #bReqRobotA AND NOT #bInZoneRobotA THEN
                #iCurrentAlloc := 0;
            END_IF;
            
        2:  // ALLOUÉE AU ROBOT B
            #bGrantRobotA := FALSE;
            #bGrantRobotB := TRUE;
            
            // Libération de la zone dès que le robot B relâche sa demande et est physiquement sorti
            IF NOT #bReqRobotB AND NOT #bInZoneRobotB THEN
                #iCurrentAlloc := 0;
            END_IF;
    END_CASE;
    
    // 2. DIAGNOSTIC ET SÉCURITÉ DE COLLISION
    // Génère une alarme si un robot est détecté dans la zone sans que l'autorisation lui ait été formellement donnée
    #instTmrFault(IN := (#bInZoneRobotA AND NOT #bGrantRobotA) OR (#bInZoneRobotB AND NOT #bGrantRobotB), PT := T#0.5s);
    
    IF #instTmrFault.Q THEN
        #bCollisionFault := TRUE;
        // Coupure de sécurité immédiate des puissances robots par PROFIsafe
        #bGrantRobotA := FALSE;
        #bGrantRobotB := FALSE;
    ELSE
        #bCollisionFault := FALSE;
    END_IF;
END_FUNCTION_BLOCK
```
