# Intégration SysML vers Modèle d'Information OPC UA (Robotics Spec)

Ce document de référence est fondé sur les travaux de recherche du CEA LIST (*Bridging the Gap between SysML and OPC UA Information Models for Industry 4.0*, 2023) visant à unifier la modélisation système haut niveau et l'implémentation de serveurs d'interopérabilité.

---

## 1. Principes d'Ingénierie Système Unifiée

La conception d'une cellule robotique industrielle moderne requiert une modélisation multidisciplinaire (mécanique, électrique, logicielle). SysML est utilisé pour spécifier les exigences et l'architecture logique. OPC UA sert de standard de communication et de sémantique terrain.

L'objectif est d'éliminer la double saisie et les erreurs d'intégration en utilisant des profils UML/SysML spécifiques qui permettent de générer automatiquement les structures XML `UANodeSet2.xml`.

---

## 2. Règles de Correspondance (Mapping Rules)

| Élément SysML | Concept OPC UA équivalent | Règle de Structuration |
| :--- | :--- | :--- |
| **Block** (ex: `RoboticArm`) | **UAObjectType** / **UAObject** | Génère un type d'objet ou une instance d'objet réutilisable. |
| **Part Property** (ex: `axis1 : Joint`) | **UAObject** imbriqué (Relation `HasComponent`) | Les relations d'agrégation se traduisent par des références sémantiques. |
| **Flow Port** (Input/Output data) | **UAVariable** (avec son `DataType`) | Les données d'entrée/sortie physiques sont mappées à des variables d'adresse. |
| **Operation / Function** | **UAMethod** | Les fonctions comportementales deviennent des méthodes appelables à distance. |

---

## 3. Profil spécifique pour OPC UA Robotics (VDMA Spec)

Lors de l'application de la spécification compagnon VDMA Robotics :
*   Chaque équipement robotique doit dériver du type d'objet `3:MotionDeviceSystemType` (Namespace d'index 3 défini par le standard VDMA).
*   Les axes physiques et moteurs sont rattachés sous forme de composants de type `3:MotionDeviceType` ou `3:AxisType`.
*   Les contrôleurs de puissance et interfaces de programmation sont modélisés via le type `3:ControllerType`.

---

## 4. Exemple de Mappage XML NodeSet Généré

Voici la forme structurelle attendue pour une instance de robot issue du design SysML :

```xml
<!-- Instance de bras robotique déduite d'un bloc SysML -->
<UAObject NodeId="ns=1;i=5001" BrowseName="1:RoboticArm_CellA" ParentNodeId="ns=1;i=1001">
  <DisplayName>RoboticArm CellA</DisplayName>
  <References>
    <!-- Type de base de la spécification compagnon VDMA Robotics (ex: MotionDeviceSystemType) -->
    <Reference ReferenceType="HasTypeDefinition">ns=3;i=1002</Reference>
    <Reference ReferenceType="Organizes" IsForward="false">ns=1;i=1001</Reference>
    <!-- Lien vers ses composants internes mappés depuis les Part Properties SysML -->
    <Reference ReferenceType="HasComponent">ns=1;i=6001</Reference>
  </References>
</UAObject>
```
