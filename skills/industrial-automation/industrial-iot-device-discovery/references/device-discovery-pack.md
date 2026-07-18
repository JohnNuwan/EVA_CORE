# Découverte Dynamique d'Équipements IIoT via Web of Things (WoT) et OPC UA

Ce document de référence décrit la méthodologie d'intégration basée sur les travaux du CEA LIST (*Towards a web-of-things approach for OPC UA field device discovery in the industrial IoT*, 2022) pour automatiser l'enregistrement d'objets connectés industriels.

---

## 1. Contexte de l'IIoT et de l'Interopérabilité

Dans les usines du futur (Industrie 4.0), de nombreux capteurs intelligents et objets IoT sont installés de manière ponctuelle ou temporaire. Configurer manuellement chaque nouvel équipement dans l'espace d'adressage du serveur OPC UA de l'atelier de production est inefficace. 

L'approche Web of Things (WoT) standardisée par le W3C propose de formaliser les capacités d'un équipement dans un fichier de description JSON-LD appelé **Thing Description (TD)**.

---

## 2. Processus d'Enregistrement Dynamique

Le flux de découverte dynamique s'établit de la manière suivante :

1.  **Annonce** : Un nouvel équipement physique se connecte au réseau local et envoie une notification de présence (Multicast DNS ou protocole de registre de découverte).
2.  **Lecture de la Description (TD)** : Le serveur d'intégration (ou le serveur OPC UA lui-même) interroge le périphérique pour obtenir son fichier JSON-LD Thing Description.
3.  **Traduction en Nœuds OPC UA** : Un parseur interprète la description et instancie dynamiquement les objets (`UAObject`), les variables (`UAVariable`) et les méthodes (`UAMethod`) correspondants dans son espace d'adressage.
4.  **Souscription** : Les clients SCADA s'abonnent immédiatement aux nouvelles variables créées sans redémarrage du serveur.

---

## 3. Exemple de Correspondance Technique (JSON-LD vers XML NodeSet)

### Source : Thing Description (WoT) en JSON
```json
{
  "id": "urn:EVA:sensor:temp123",
  "title": "Smart Temperature Sensor",
  "properties": {
    "temperature": {
      "type": "number",
      "unit": "degree Celsius"
    }
  }
}
```

### Cible : Nœuds d'Espace d'Adressage OPC UA (XML)
```xml
<!-- Objet modélisant le capteur dynamique -->
<UAObject NodeId="ns=1;s=sensor_temp123" BrowseName="1:Smart_Temperature_Sensor">
  <DisplayName>Smart Temperature Sensor</DisplayName>
  <References>
    <Reference ReferenceType="HasTypeDefinition">i=58</Reference> <!-- BaseObjectType -->
  </References>
</UAObject>

<!-- Variable de température dynamique -->
<UAVariable NodeId="ns=1;s=sensor_temp123_temp" BrowseName="1:temperature" DataType="Float" ParentNodeId="ns=1;s=sensor_temp123">
  <DisplayName>temperature</DisplayName>
  <References>
    <Reference ReferenceType="HasComponent" IsForward="false">ns=1;s=sensor_temp123</Reference>
  </References>
</UAVariable>
```
