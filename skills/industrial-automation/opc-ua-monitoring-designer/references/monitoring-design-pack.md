# Modélisation Sémantique de Lignes de Production sous OPC UA

Ce document de référence est basé sur les retours d'expérience du CEA LIST (*From requirement specification to OPC UA information model design: A product assembly line monitoring case study*, 2022) pour la conversion systématique des exigences en modèle d'information.

---

## 1. Cycle de Transformation des Exigences

La modélisation s'organise en quatre phases successives :

1.  **Identification des Équipements physiques et logiques** (ex: convoyeurs, automates, robots, capteurs).
2.  **Définition des États et Comportements** (ex: états de marche, défauts, modes manuel/automatique).
3.  **Spécification des Variables et Signaux** : regrouper les données d'entrées, de sorties, de configuration et statistiques.
4.  **Déclaration des Types de Base** : encapsuler ces éléments dans des types d'objets réutilisables (ObjectTypes) avec héritage sémantique.

---

## 2. Métadonnées Sémantiques Obligatoires

Pour chaque variable de mesure physique exposée dans le modèle d'information, les métadonnées suivantes doivent être déclarées comme propriétés :

*   **EURange** (Type: `Range`) : Définit la plage de valeurs réelles valides (ex: `0` à `100` pour un pourcentage, `-50` à `150` pour une température).
*   **EngineeringUnits** (Type: `EUInformation`) : Spécifie l'unité physique de mesure (conforme au standard international UNECE, ex: code `CEL` pour les degrés Celsius, `MTR` pour les mètres).
*   **ValuePrecision** (Type: `Double`) : Précision numérique de la valeur mesurée.

---

## 3. Modélisation Standard d'un Équipement de Convoyage

Voici un exemple de structure type de modélisation pour un convoyeur (`ConveyorType`) :

```xml
<!-- Définition du type d'objet ConveyorType -->
<UAObjectType NodeId="ns=1;i=2001" BrowseName="1:ConveyorType">
  <DisplayName>ConveyorType</DisplayName>
  <References>
    <Reference ReferenceType="HasSubtype" IsForward="false">i=58</Reference> <!-- Dérive de BaseObjectType -->
  </References>
</UAObjectType>

<!-- Propriété de vitesse (Speed) associée au ConveyorType -->
<UAVariable NodeId="ns=1;i=3001" BrowseName="1:Speed" DataType="Float" ParentNodeId="ns=1;i=2001">
  <DisplayName>Speed</DisplayName>
  <References>
    <Reference ReferenceType="HasComponent" IsForward="false">ns=1;i=2001</Reference>
    <!-- Métadonnées sémantiques indispensables -->
    <Reference ReferenceType="HasProperty">ns=1;i=3002</Reference> <!-- EURange -->
  </References>
</UAVariable>
```
