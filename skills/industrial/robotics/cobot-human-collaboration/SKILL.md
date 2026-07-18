---
name: cobot-human-collaboration
description: "Utiliser quand l'utilisateur demande de concevoir des applications collaboratives de robotique (Cobots), de configurer les fonctions de limitation de force/vitesse ou de programmer des modèles courants (UR, Fanuc CRX)."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [cobot, human-robot-collaboration, safety-standards, universal-robots, fanuc-crx, industrial-robotics]
  related_skills: [iso-safety, robotics-fanuc]
---

# Robotique Collaborative (Cobotique) & Sécurité

## Vue d'ensemble

La **Robotique Collaborative (Cobotique)** désigne les applications où des robots partagent un espace de travail commun avec des opérateurs humains sans barrières physiques de protection. Contrairement aux robots industriels classiques enfermés dans des cages, le cobot possède des capteurs d'efforts internes et des fonctions de sécurité intégrées pour éviter les blessures graves en cas de contact.

La mise en œuvre d'une application collaborative est régie par la spécification technique **ISO/TS 15066** et la norme **ISO 10218-1/2**. Elle définit 4 modes de collaboration :
1.  **Arrêt de sécurité contrôlé (Monitored Stop) :** Le robot s'arrête dès qu'un humain pénètre dans sa zone de travail (détecté par scrutateur laser).
2.  **Guidage manuel (Hand Guiding) :** L'opérateur guide le robot directement à la main pour lui apprendre des trajectoires.
3.  **Contrôle de la distance (Speed and Separation Monitoring) :** Le robot ralentit à mesure que l'opérateur s'approche et s'arrête s'il est trop près.
4.  **Limitation de la force et de la puissance (PFL - Power and Force Limiting) :** Le robot peut entrer en contact physique avec l'humain ; sa force et sa pression sont bridées logiciellement sous les seuils de douleur et de blessure définis par l'ISO/TS 15066.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De configurer les paramètres de sécurité (limites de force en Newtons, vitesse en mm/s, puissance en Watts) d'un cobot (ex: Universal Robots UR Polyscope, Fanuc CRX).
- De concevoir ou programmer une application collaborative en script (ex: URScript).
- De comprendre ou appliquer les exigences de la norme ISO/TS 15066 pour une analyse de risques d'impact.
- De programmer des capteurs externes de détection de présence (scrutateurs lasers Sick/Keyence, tapis de sécurité) raccordés au contrôleur du robot.

**Ne pas utiliser pour :**
- Les robots industriels classiques rapides nécessitant des barrières physiques de protection obligatoires.

---

## 1. Programmation en langage URScript (Universal Robots)

Universal Robots utilise un langage propriétaire textuel nommé **URScript**. Les scripts peuvent être envoyés directement au contrôleur du robot sur le port TCP `30002`.

### Exemple de script de palettisation collaborative simple avec arrêt sécurisé :

```text
def collaborative_palletizing():
  # 1. Configurer les paramètres de mouvement
  global target_pos = p[0.4, 0.2, 0.3, 0, 3.14, 0]
  global home_pos = p[0.1, -0.4, 0.5, 0, 3.14, 0]
  
  # Vitesse d'approche sécurisée (limite collaborative)
  # Max 250 mm/s dans l'espace partagé pour respecter l'ISO/TS 15066
  local_speed = 0.250
  local_accel = 1.2
  
  # Déplacement au point Home
  movej(home_pos, a=local_accel, v=local_speed)
  
  while (True):
    # Attendre que la pièce soit présente sur le convoyeur d'alimentation
    # di_part_present est une entrée numérique du contrôleur
    while (read_port_register(129) == 0):
      sync()
    end
    
    # 2. Trajectoire de prise avec surveillance de force intégrée
    # Si le robot rencontre un obstacle de plus de 50 N pendant la descente, il s'arrête
    # force() renvoie la force mesurée au poignet
    
    movej(appro(target_pos, p[0,0,-0.1,0,0,0]), a=local_accel, v=local_speed)
    
    # Descente linéaire prudente
    movel(target_pos, a=0.5, v=0.100)
    
    # Activer l'outil (ventouse pneumatique)
    set_tool_digital_out(0, True)
    
    # Attente du vide (validation prise)
    sleep(0.5)
    
    # Dégagement
    movel(appro(target_pos, p[0,0,-0.1,0,0,0]), a=local_accel, v=local_speed)
    movej(home_pos, a=local_accel, v=local_speed)
    
    # Relâcher la pièce au point Home
    set_tool_digital_out(0, False)
    sleep(0.5)
  end
end
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Croire que l'achat d'un cobot dispense d'une analyse de risques :**
    *   *Erreur :* Installer un cobot équipé d'un outil tranchant (ex: couteau de découpe ou préenseur avec broches pointues) et laisser des opérateurs s'en approcher sans protection sous prétexte que le robot est "collaboratif". Le robot s'arrêtera au contact, mais l'outil aura déjà blessé l'opérateur.
    *   *Correction :* La sécurité concerne l'**application globale** (Robot + Outil/Pince + Pièce transportée), pas seulement le bras. Si l'outil ou la pièce présente un danger de perforation, des protections physiques ou des scrutateurs lasers de sécurité sont obligatoires.
2.  **Niveaux de force configurés trop élevés :**
    *   *Erreur :* Régler les seuils de détection de force au maximum (ex: 150 N ou plus) sur le contrôleur pour éviter les faux déclenchements d'arrêts. En cas de collision avec le visage ou le cou d'un opérateur, les forces de pression dépasseront largement les seuils limites autorisés par l'ISO/TS 15066.
    *   *Correction :* Réaliser des mesures physiques de force d'impact à l'aide d'un dynamomètre de collision certifié et ajuster les seuils logiciels du robot pour qu'ils soient conformes aux limites de la norme pour chaque zone du corps exposée.

---

## Liste de vérification (Checklist)

- [ ] L'analyse de risques de l'application collaborative prend en compte le bras du robot, l'outil d'extrémité (pince/ventouse) et la pièce transportée.
- [ ] La vitesse maximale du robot dans la zone de collaboration humaine est limitée logiciellement sous 250 mm/s (recommandation ISO/TS 15066).
- [ ] Les fonctions de sécurité du robot (Force Limit, Power Limit, Speed Limit) sont verrouillées par mot de passe de sécurité dans le contrôleur.
- [ ] En cas de contact ou de blocage, le robot s'arrête en sécurité et nécessite un acquittement manuel pour redémarrer (pas de redémarrage automatique).

