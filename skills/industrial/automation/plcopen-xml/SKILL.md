---
name: plcopen-xml
description: "Générer et structurer des fichiers d'échange PLCopen XML."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [industrial, automation, plcopen, xml, codesys, twincat, iec61131-3]
    related_skills: [rockwell-studio5000, siemens-scl]
---

# Standard d'Échange Automate PLCopen XML (CEI 61131-3)

## Vue d'ensemble

Le standard **PLCopen XML** définit un schéma d'échange ouvert et neutre (indépendant des constructeurs) pour les projets d'automatisation conformes à la norme CEI 61131-3. Il permet d'importer et d'exporter des structures de données (DUT), des variables globales (GVL) et des unités d'organisation de programme (POU) sous forme textuelle XML dans des environnements comme CODESYS, Beckhoff TwinCAT, Schneider Machine Expert ou Omron Sysmac.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De générer des blocs fonctionnels (FB, FC) ou des structures de données exportables en PLCopen XML.
- De concevoir des scripts ou des outils de génération universels pour CODESYS ou TwinCAT.
- De convertir du code automate propriétaire vers un format XML ouvert CEI 61131-3.

---

## 1. Structure Globale d'un Fichier PLCopen XML

Un document PLCopen XML valide respecte l'arborescence racine `<project>` et doit déclarer les namespaces officiels.

```xml
<?xml version="1.0" encoding="utf-8"?>
<project xmlns="http://www.plcopen.org/xml/tc6_0201" 
         xmlns:xhtml="http://www.w3.org/1999/xhtml" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
         xsi:schemaLocation="http://www.plcopen.org/xml/tc6_0201 tc6_0201.xsd">
  <fileHeader companyName="EVA" productName="EVA Agent" productVersion="1.0" creationDateTime="2026-06-17T12:00:00"/>
  <contentHeader name="Export_Universal">
    <coordinateInfo>
      <fbd><x>100</x><y>100</y></fbd>
      <ld><x>100</x><y>100</y></ld>
      <sfc><x>100</x><y>100</y></sfc>
    </coordinateInfo>
  </contentHeader>
  <types>
    <dataTypes>
      <!-- Définition des structures de données (DUT) -->
    </dataTypes>
    <pous>
      <!-- Définition des blocs logiques (POU) -->
    </pous>
  </types>
  <instances>
    <configurations/>
  </instances>
</project>
```

---

## 2. Déclaration d'un Type de Données Utilisateur (DUT / Structure)

Les structures de données sont déclarées sous l'élément `<dataTypes>` à l'aide de structures de variables :

```xml
<dataType name="ST_Motor_Signals">
  <baseType>
    <struct>
      <variable name="bStart">
        <type><BOOL/></type>
        <initialValue><simpleValue value="false"/></initialValue>
        <documentation><xhtml:p>Commande Marche</xhtml:p></documentation>
      </variable>
      <variable name="bStop">
        <type><BOOL/></type>
        <initialValue><simpleValue value="false"/></initialValue>
        <documentation><xhtml:p>Commande Arret</xhtml:p></documentation>
      </variable>
      <variable name="fSpeed">
        <type><REAL/></type>
        <initialValue><simpleValue value="0.0"/></initialValue>
        <documentation><xhtml:p>Consigne de vitesse (Hz)</xhtml:p></documentation>
      </variable>
    </struct>
  </baseType>
</dataType>
```

---

## 3. Structure d'un Function Block (POU) en Structured Text (ST)

Les blocs logiques définissent leurs variables d'interface (Entrées, Sorties, Internes) et leur code source ST encapsulé dans un bloc CDATA :

```xml
<pou name="FB_UniversalScale" pouType="functionBlock">
  <interface>
    <inputVars>
      <variable name="rInput">
        <type><REAL/></type>
      </variable>
      <variable name="rMinRaw">
        <type><REAL/></type>
      </variable>
      <variable name="rMaxRaw">
        <type><REAL/></type>
      </variable>
    </inputVars>
    <outputVars>
      <variable name="rOutput">
        <type><REAL/></type>
      </variable>
    </outputVars>
    <localVars>
      <variable name="rSpan">
        <type><REAL/></type>
      </variable>
    </localVars>
  </interface>
  <body>
    <ST>
      <xhtml:p><![CDATA[
// Calcul d'echelle universelle
rSpan := rMaxRaw - rMinRaw;
IF rSpan <> 0.0 THEN
    rOutput := rInput / rSpan;
ELSE
    rOutput := 0.0;
END_IF;
      ]]></xhtml:p>
    </ST>
  </body>
</pou>
```

---

## Pièges Courants (Common Pitfalls)

1. **Namespace et validation XSD manquante :**
   * *Erreur :* Omettre les attributs XMLNS racines. Le fichier est alors rejeté par l'importateur CODESYS.
   * *Correction :* Toujours inclure `xmlns="http://www.plcopen.org/xml/tc6_0201"` à la racine.

2. **Échappement des caractères spéciaux dans le ST :**
   * *Erreur :* Écrire des caractères `<` ou `>` dans le code Texte Structuré sans protection.
   * *Correction :* Envelopper impérativement la section de code ST dans une balise `<![CDATA[ ... ]]>`.

3. **Noms de variables et casse :**
   * *Erreur :* Changer la casse des types de base (ex: `<bool/>` au lieu de `<BOOL/>`).
   * *Correction :* Les balises de types CEI (BOOL, INT, DINT, REAL, LREAL, WORD, etc.) doivent impérativement être écrites en **lettres majuscules** et fermées.

---

## Liste de vérification (Checklist)

- [ ] L'élément racine `<project>` déclare les bons namespaces et schémas XSD.
- [ ] La structure des variables de l'interface respecte les groupes `<inputVars>`, `<outputVars>` et `<localVars>`.
- [ ] Tout code logique Structured Text est encapsulé dans une section `<![CDATA[ ... ]]>`.
- [ ] Les types de base CEI 61131-3 sont écrits en majuscules (ex. `<REAL/>`).
- [ ] Les en-têtes de fichier et de contenu (`fileHeader`, `contentHeader`) sont présents et correctement formatés.

