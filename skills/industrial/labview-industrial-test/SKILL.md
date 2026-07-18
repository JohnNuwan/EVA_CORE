---
name: labview-industrial-test
description: "Concevoir en LabVIEW pour les bancs de test et la mesure."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [windows]
metadata:
  tags: [labview, g-code, daqmx, visa, gpib, instruments, signal-processing, test-benches, fat-sat]
  related_skills: [fat-sat-iq-oq-pq-automation, industrial-programming-languages]
---

# Programmation LabVIEW (Langage G) pour les Bancs d'Essai et d'Acquisition

Cette compétence régit le développement d'applications sous LabVIEW (langage graphique G) pour la commande d'instruments, l'acquisition de signaux physiques haute vitesse, le traitement du signal et l'intégration logicielle de bancs d'essai industriels (processus de tests FAT/SAT).

---

## 1. Modèle de Conception Producteur-Consommateur (QMH)

Ce modèle de conception (Design Pattern) est le standard industriel pour concevoir des applications réactives sous LabVIEW. Il permet d'acquérir des données physiques en continu sans geler l'interface graphique opérateur.

### Fonctionnement du Pattern
* **Boucle Producteur (Interface Utilisateur & Acquisition)** :
  - Contient une structure d'événements (*Event Structure*) qui intercepte les clics sur les boutons (ex: "Démarrer Test") ou une boucle d'acquisition de données cadencée.
  - Utilise la fonction **Obtain Queue** pour initialiser une file d'attente d'instructions.
  - Appelle **Enqueue Element** pour envoyer des messages structurés (chaîne de caractères de commande + variant de données) dans la file d'attente.
* **Boucle Consommateur (Traitement, Logique de Test & Sauvegarde)** :
  - S'exécute dans une boucle While parallèle.
  - Bloque sur la fonction **Dequeue Element** jusqu'à ce qu'un message arrive.
  - Utilise une structure Conditionnelle (*Case Structure*) pour exécuter la logique correspondant au message reçu ("Initialiser Instrument", "Acquérir", "Enregistrer", "Arrêter").
  - Gère les données persistantes via des registres à décalage (*Shift Registers*).

---

## 2. Acquisition Physique Haute Vitesse avec NI-DAQmx

NI-DAQmx est l'API de référence pour piloter le matériel de mesure National Instruments. Le flux d'exécution suivant doit être implémenté de façon séquentielle via le fil de liaison d'erreur (*Error Cluster*).

```text
+-----------------------+      +-----------------------+      +-----------------------+
|  DAQmx Create Task    | ===> | DAQmx Create Channel  | ===> |   DAQmx Timing        |
+-----------------------+      +-----------------------+      +-----------------------+
                                                                          ||
+-----------------------+      +-----------------------+                  ||
|  DAQmx Clear Task     | <=== |   DAQmx Read (Loop)   | <================//
+-----------------------+      +-----------------------+
```

### Étapes Clés et Paramètres
1. **DAQmx Create Task** : Initialise une tâche logique sous forme de référence.
2. **DAQmx Create Virtual Channel (Analog Input - Voltage)** :
   - *Physical Channels* : Adresse de la carte et du canal (ex: `Dev1/ai0`).
   - *Terminal Configuration* : Indispensable de spécifier la méthode de mesure électrique :
     - `Differential` (pour éliminer les bruits de mode commun sur de faibles signaux).
     - `RSE` (Referenced Single-Ended) ou `NRSE` (Non-Referenced Single-Ended) selon la topologie des masses.
   - *Min/Max limits* : Spécifier la plage attendue (ex: `-10.0` à `10.0` Volts) pour optimiser la résolution du convertisseur analogique-numérique (ADC).
3. **DAQmx Timing (Sample Clock)** :
   - *Source* : Laisser vide par défaut pour utiliser l'horloge interne de la carte (`OnboardClock`).
   - *Rate (Hz)* : Fréquence d'échantillonnage (ex: `1000.0` Hz).
   - *Sample Mode* : Choisir `Continuous Samples` pour un monitoring en continu.
4. **DAQmx Read (Analog 1D Wform NChan NSamples)** :
   - Placé dans une boucle de lecture. Lit un nombre défini d'échantillons (ex: `100` échantillons) à chaque itération.
   - Retourne une structure de forme d'onde (*Waveform*) contenant : le temps de départ ($t_0$), le pas de temps ($\Delta t$), et le tableau de valeurs réelles.
5. **DAQmx Clear Task** : Appelé à la fermeture du VI pour restituer les ressources matérielles et éviter des conflits au lancement suivant.

---

## 3. Commande d'Instruments VISA et Requêtes SCPI

NI-VISA est utilisé pour communiquer avec les alimentations, multimètres ou générateurs de signaux tiers en utilisant le protocole SCPI.

### Bonnes Pratiques de Communication VISA
* **VISA Configure Serial Port** : Toujours initialiser explicitement la vitesse de transmission (Baud Rate, ex: `9600`), le bit de parité, les bits d'arrêt, et activer le caractère de fin de ligne (Termination Character, ex: `\n` ou code décimal `10`).
* **VISA Write** : Envoyer la commande textuelle SCPI en s'assurant qu'elle se termine par le délimiteur configuré (ex: `MEASure:VOLTage:DC?\n`).
* **VISA Read** : Lire la réponse en allouant un nombre de caractères maximal suffisant (ex: `256`). La lecture s'arrête automatiquement dès que le caractère de fin de ligne (`\n`) est détecté.
* **Gestion des Erreurs Instrument** : Après chaque commande d'écriture/lecture de configuration, interrogez l'instrument avec la commande standard `SYSTem:ERRor?` pour vous assurer que l'appareil n'a pas rejeté la syntaxe ou rencontré un défaut matériel.

---

## 4. Structuration des Données de Mesure (Format TDMS)

Pour l'historisation des données d'acquisition haute vitesse (vibrations, transitoires électriques), le format binaire **TDMS** (Technical Data Management Streaming) doit être utilisé.

* **TDMS Open** : Ouvre ou crée un fichier `.tdms` en spécifiant l'opération d'écriture.
* **TDMS Write** : Écrit les formes d'ondes brutes de façon optimisée sur disque. Les données sont structurées en trois niveaux :
  1. *Fichier* : Propriétés générales du test (Date, Nom de l'opérateur, Référence du banc).
  2. *Groupe de canaux* : Par exemple "Vibrations Moteur" ou "Pressions Hydrauliques".
  3. *Canal* : Échantillons unitaires du capteur.
* **TDMS Close** : Ferme la référence du fichier pour valider l'intégrité de la structure binaire.
