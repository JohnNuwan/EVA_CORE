---
name: schneider-xef-generation
description: "Générer et structurer des exports XML Schneider XEF."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [schneider, eco-struxure, control-expert, xef, plc, xml, automation-engineering]
  related_skills: [industrial-plc-connectivity]
---

# Génération et Structure de Fichiers Schneider XEF (Control Expert)

## Vue d'ensemble

Cette compétence guide l'agent pour concevoir, structurer, valider et éditer des fichiers d'export XML au format `.XEF` (Unity Pro / EcoStruxure Control Expert) de Schneider Electric. Ces fichiers permettent de configurer les types de données dérivés (DDT), les variables (localisées ou symboliques) et les programmes PLC.

---

## Outils Associés

Les outils de communication directe suivants peuvent être mobilisés :
- `` `modbus_read_registers` `` : Lecture en direct de variables de mots Modbus.
- `` `modbus_write_register` `` : Écriture en direct de variables de mots Modbus.
- `` `modbus_write_coil` `` : Écriture de variables de bits Modbus.

---

## Guide d'Ingénierie & Structures XML Détaillées Schneider

### 1. Variables Localisées (%MW / %M) et DDT (Derived Data Types)
EcoStruxure utilise des variables localisées (mappées sur des registres physiques de la mémoire de la CPU) ou des variables symboliques (non localisées).
* **`%MW<index>`** : Registre interne 16 bits (mot). Correspond à l'adresse Modbus `<index> + 1`.
* **`%M<index>`** : Bit interne (bobine). Correspond à l'adresse de Coil Modbus `<index>`.
* **DDT (Derived Data Type)** : L'équivalent Schneider d'un UDT.

Voici comment structurer l'export XML des types DDT et des variables dans un fichier XEF :

```xml
<KConfSource ProductVersion="15.0">
  <!-- Déclaration des types dérivés DDT -->
  <DDTExchange>
    <DDTName name="DDT_Sensor" version="0.1">
      <Comment>Structure d'acquisition analogique standard</Comment>
      <Structure>
        <TypeField name="iRawValue" type="INT"/>
        <TypeField name="rScaledValue" type="REAL"/>
        <TypeField name="bHighAlarm" type="BOOL"/>
      </Structure>
    </DDTName>
  </DDTExchange>

  <!-- Déclaration et mapping des variables globales -->
  <VariablesExchange>
    <!-- Variable localisée sur l'adresse de mot %MW100 (Modbus 40101) -->
    <Variable name="SystemStatus" type="INT" address="%MW100">
      <Comment>Statut général du système</Comment>
    </Variable>
    
    <!-- Variable non localisée de type DDT -->
    <Variable name="TempSensor1" type="DDT_Sensor">
      <Comment>Capteur de température cuve principale</Comment>
    </Variable>
  </VariablesExchange>
</KConfSource>
```

### 2. Structure d'un Programme et Section logique en Structured Text (ST)
Les programmes d'EcoStruxure sont découpés en tâches (`Mast`, `Fast`, `Aux`), contenant des sections écrites dans un langage donné (ST, FBD, LD).

```xml
<ProgramExchange>
  <Section name="Section_PumpControl" behavior="MastTask" language="ST">
    <Comment>Logique de contrôle de la pompe principale</Comment>
    <STSource><![CDATA[
(* Commande de la pompe avec sécurité défaut *)
IF NOT TempSensor1.bHighAlarm AND SystemStatus = 1 THEN
    (* Démarrage de la pompe *)
    %Q0.2.0 := TRUE; 
ELSE
    (* Arrêt de sécurité *)
    %Q0.2.0 := FALSE;
END_IF;

(* Mise à l'échelle simplifiée de la température *)
TempSensor1.rScaledValue := INT_TO_REAL(TempSensor1.iRawValue) * 0.01;
]]>
    </STSource>
  </Section>
</ProgramExchange>
```

---

## Bonnes Pratiques de Conception Schneider (Unity/Control Expert)

1. **Particularité du Structured Text Schneider** :
   * Les commentaires s'enveloppent avec des parenthèses et des étoiles `(* commentaire *)` et non des barres obliques.
   * La syntaxe des sorties physiques est sous la forme `%Q<rack>.<module>.<voie>` (ex: `%Q0.2.0` pour la première voie de sortie du module du slot 2).
   * L'écriture des types de fonctions de conversion est obligatoire pour les opérations mathématiques mixtes (ex: `INT_TO_REAL`).
2. **Robustesse de l'importation XML** :
   * Conserver les balises racines `<KConfSource>` avec la bonne version du logiciel (`ProductVersion="15.0"` ou similaire) pour éviter des erreurs lors de l'importation manuelle par les automaticiens.
   * Toujours encapsuler le code ST source dans des sections `<![CDATA[ ... ]]>` pour prévenir toute corruption du XML par des caractères logiques ou de comparaison.
