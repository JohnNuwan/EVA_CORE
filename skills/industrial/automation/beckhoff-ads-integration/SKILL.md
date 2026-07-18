---
name: beckhoff-ads-integration
description: "Générer et intégrer du code Structured Text Beckhoff."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [beckhoff, twincat, ads, plc, structured-text, automation-engineering]
  related_skills: [industrial-plc-connectivity]
---

# Intégration ADS et Programmation Structured Text TwinCAT (Beckhoff)

## Vue d'ensemble

Cette compétence guide l'agent pour concevoir, structurer et intégrer des projets TwinCAT 3 en Structured Text (ST) et configurer les liaisons de communication via le protocole ADS (Automation Device Specification) de Beckhoff.

---

## Outils Associés

Les outils de communication directe suivants peuvent être mobilisés :
- `` `beckhoff_ads_get_info` `` : Lecture du statut du runtime TwinCAT.
- `` `beckhoff_ads_read_tag` `` : Lecture de variables PLC par leur nom de symbole.
- `` `beckhoff_ads_write_tag` `` : Écriture de variables PLC par leur nom de symbole.

---

## Guide d'Ingénierie & Patterns de Code TwinCAT

### 1. Configuration des Routes Réseau ADS
Pour établir un dialogue entre Helios (ou toute application hôte) et le contrôleur Beckhoff via ADS, les routes doivent être mutuellement déclarées.
* **AMS Net ID de la cible** : C'est l'identifiant du routeur ADS, composé de 6 octets (ex: `192.168.1.100.1.1`).
* **Port ADS standard** :
  * `851` : Premier runtime PLC de TwinCAT 3.
  * `10000` : Système de diagnostic ou routeur ADS lui-même.
* **Ajout d'une route via script ou terminal** :
  Sous Linux, le fichier `/etc/ads/StaticRoutes.xml` doit être configuré de la sorte :
  ```xml
  <TcConfig>
    <RemoteConnections>
      <Route>
        <Name>HeliosAgent</Name>
        <Address>192.168.1.50</Address> <!-- IP de la machine Helios -->
        <NetId>192.168.1.50.1.1</NetId>   <!-- AMS Net ID de la machine Helios -->
        <Type>TCP_IP</Type>
      </Route>
    </RemoteConnections>
  </TcConfig>
  ```

### 2. Écriture de fichiers locaux depuis TwinCAT en ST
Beckhoff propose des blocs fonctionnels asynchrones (dans la bibliothèque `Tc2_System`) pour interagir avec le système de fichiers de l'OS (Windows ou TwinCAT RTOS). Ces opérations s'exécutent sur plusieurs cycles en utilisant les variables `bExecute`, `bBusy` et `bError`.

```pascal
PROGRAM PRG_FileLog
VAR
    fbFileOpen      : FB_FileOpen;      // Bloc d'ouverture de fichier
    fbFileWrite     : FB_FileWrite;     // Bloc d'écriture de fichier
    fbFileClose     : FB_FileClose;     // Bloc de fermeture de fichier
    hHeaderFile     : UINT := 0;        // Handle du fichier ouvert
    sLogLine        : STRING := 'Vitesse: 1450 rpm; Defaut: False$N'; // Ligne à écrire ($N = CR/LF)
    
    bWriteTrigger   : BOOL;             // Déclencheur d'écriture
    iState          : INT := 0;         // État de la machine d'état
    bBusy           : BOOL;
    bError          : BOOL;
END_VAR

CASE iState OF
    0: // Attente d'un déclenchement
        IF bWriteTrigger THEN
            bWriteTrigger := FALSE;
            bBusy := TRUE;
            bError := FALSE;
            iState := 10;
        END_IF;
        
    10: // Ouverture du fichier en mode Append
        fbFileOpen(
            sNetId := '',               // Machine locale
            sPathName := 'C:\Logs\production.csv',
            nMode := FOPEN_MODEAPPEND OR FOPEN_MODETEXT,
            bExecute := TRUE
        );
        IF NOT fbFileOpen.bBusy THEN
            IF NOT fbFileOpen.bError THEN
                hHeaderFile := fbFileOpen.hFile;
                fbFileOpen(bExecute := FALSE); // Reset du bloc
                iState := 20;
            ELSE
                bError := TRUE;
                iState := 99; // État d'erreur
            END_IF;
        END_IF;
        
    20: // Écriture de la ligne de log
        fbFileWrite(
            sNetId := '',
            hFile := hHeaderFile,
            pWriteBuff := ADR(sLogLine),
            cbWriteLen := INT_TO_UDINT(LEN(sLogLine)),
            bExecute := TRUE
        );
        IF NOT fbFileWrite.bBusy THEN
            fbFileWrite(bExecute := FALSE);
            iState := 30; // Fermeture obligatoire même après erreur
        END_IF;
        
    30: // Fermeture du fichier
        fbFileClose(
            sNetId := '',
            hFile := hHeaderFile,
            bExecute := TRUE
        );
        IF NOT fbFileClose.bBusy THEN
            fbFileClose(bExecute := FALSE);
            bBusy := FALSE;
            iState := 0; // Retour à l'attente
        END_IF;
        
    99: // Gestion de l'erreur
        bBusy := FALSE;
        fbFileOpen(bExecute := FALSE);
        iState := 0;
END_CASE
```

---

## Bonnes Pratiques de Conception Beckhoff

1. **Mapping OPC UA dans TwinCAT 3** :
   Ajouter des attributs de pragma pour rendre des variables PLC directement éligibles au serveur OPC UA interne de Beckhoff :
   ```pascal
   {attribute 'OPC.UA.DA' := '1'}
   {attribute 'OPC.UA.DA.Description' := 'Consigne de vitesse de la pompe principal'}
   rPumpSpeed : REAL;
   ```
2. **Types de données et précisions** :
   * Privilégier `LREAL` (double précision 64 bits) pour les variables de position ou d'axes de mouvement (TwinCAT NC/MC).
   * Les types de temps (`TIME`, `LTIME`, `TOD`, `DT`) doivent être formatés selon le standard (ex: `T#500ms`, `DT#2026-07-06-10:40:00`).
