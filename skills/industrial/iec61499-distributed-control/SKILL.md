---
name: iec61499-distributed-control
description: "Concevoir des systèmes distribués selon la norme IEC 61499."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, windows]
metadata:
  tags: [iec61499, distributed-control, function-blocks, 4diac, ecostruxure, industry4-0, events, runtime]
  related_skills: [iec61131-3-programming-standards, industrial-programming-languages]
---

# Conception et Programmation de Systèmes Distribués (IEC 61499)

Cette compétence encadre le développement d'architectures d'automatisation distribuées et orientées événements selon la norme IEC 61499 (utilisée via Eclipse 4diac ou Schneider EcoStruxure Automation Expert).

---

## 1. Modèle d'Exécution et Cycle de Vie d'un Bloc Fonctionnel Basique (BFB)

Dans la norme IEC 61499, l'ordonnancement est purement réactif (événementiel). L'arrivée d'un événement d'entrée déclenche le cycle de mise à jour interne.

```text
                  [ Événement d'entrée reçu ]
                              ||
                              \/
               [ Évaluation des transitions ECC ]
                              ||
                              \/
                [ Transition valide trouvée ? ]
                       //            \\
                     Oui              Non
                     //                \\
                    \/                  \/
        [ Passage au nouvel état ]   [ Mise en sommeil ]
                    ||
                    \/
        [ Exécution de l'algorithme ]
                    ||
                    \/
        [ Émission de l'événement de sortie ]
```

### Le protocole d'exécution interne (ECC Loop)
1. **Attente d'Événement** : Le runtime maintient le bloc en état de repos.
2. **Arrivée d'un Événement** : Un événement (ex: `REQ`) est reçu. Les variables associées via la directive `WITH` sont verrouillées dans la mémoire du bloc.
3. **Évaluation de l'ECC** : Le moteur d'exécution vérifie les transitions sortantes de l'état actuel.
   - Les conditions de transition combinent un événement d'entrée ET/OU une expression booléenne sur les données (garde).
   - Exemple de condition : `REQ AND (QI = TRUE)`
4. **Changement d'État et Action** :
   - Si une transition est valide, le bloc passe dans le nouvel état.
   - L'algorithme (ex: écrit en ST) associé à cet état s'exécute de manière synchrone.
   - À la fin de l'algorithme, l'événement de sortie associé (ex: `CNF`) est émis.

---

## 2. Structure XML Spécifiée d'un Basic Function Block (.fbt)

Les fichiers d'interface de blocs en IEC 61499 utilisent un format XML standardisé par l'organisation PLCopen. Voici la structure XML de référence pour déclarer un BFB.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE FBType SYSTEM "https://www.holobloc.com/xml/LibraryElement.dtd">
<FBType Name="CalculEcart" Comment="Calcule l ecart de process">
  <Identification Standard="IEC 61499-1" />
  <InterfaceList>
    <EventInputs>
      <Event Name="REQ" Comment="Calcul requis">
        <With Var="Consigne" />
        <With Var="Mesure" />
      </Event>
    </EventInputs>
    <EventOutputs>
      <Event Name="CNF" Comment="Calcul termine">
        <With Var="Ecart" />
        <With Var="Alerte" />
      </Event>
    </EventOutputs>
    <InputVars>
      <VarDeclaration Name="Consigne" Type="REAL" />
      <VarDeclaration Name="Mesure" Type="REAL" />
    </InputVars>
    <OutputVars>
      <VarDeclaration Name="Ecart" Type="REAL" />
      <VarDeclaration Name="Alerte" Type="BOOL" />
    </OutputVars>
  </InterfaceList>
  <BasicFB>
    <ECC>
      <ECEState Name="START" />
      <ECEState Name="REQ_STATE">
        <ECAction Algorithm="Calcul" Output="CNF" />
      </ECEState>
      <ECTransition Source="START" Destination="REQ_STATE" Condition="REQ" />
      <ECTransition Source="REQ_STATE" Destination="START" Condition="1" />
    </ECC>
    <Algorithm Name="Calcul">
      <ST Text="Ecart := Consigne - Mesure;&#10;Alerte := ABS(Ecart) > 5.0;&#10;" />
    </Algorithm>
  </BasicFB>
</FBType>
```

---

## 3. Blocs de Service Réseau (SIFB) pour l'Intégration Distribuée

Les SIFB de communication standardisent l'échange de données inter-automates sans imposer de modèle physique de bus.

### Communication UDP Multicast standardisée (FORTE / 4diac)
Pour propager l'état d'un bouton d'arrêt d'urgence de l'Automate A vers l'Automate B :
* **Sur l'Automate A (Emetteur)** :
  - Utilisation d'un bloc standard `PUBLISH_1`.
  - Configuration du paramètre `QI` à `TRUE`.
  - ID de connexion paramétré via la chaîne : `udp://239.192.1.100:61499` (Adresse IP de Multicast et port de communication).
  - Liaison du signal d'arrêt d'urgence sur l'entrée de données `SD_1`.
  - Le bloc envoie la trame sur le réseau dès que l'entrée d'événement `REQ` est activée.
* **Sur l'Automate B (Recepteur)** :
  - Utilisation du bloc standard `SUBSCRIBE_1`.
  - ID de connexion paramétré sur la même adresse : `udp://239.192.1.100:61499`.
  - Le bloc génère l'événement de sortie `IND` (Indication) dès qu'une trame réseau arrive, rendant la donnée de sortie `RD_1` disponible.

---

## 4. Règles d'Or de Conception de Réseaux de Blocs (FB Networks)

* **Pas de boucles infinies d'événements** : L'agent doit s'assurer que les connexions d'événements ne forment pas de cycle fermé direct (ex: sortie d'événement `CNF` d'un bloc A rebouclée directement sur l'entrée `REQ` d'un bloc B dont la sortie `CNF` réactive le bloc A) sous peine de figer le runtime de l'automate (boucle infinie de CPU).
* **Respecter les associations de variables (WITH)** : N'essayez jamais de lire une donnée de sortie si l'événement de confirmation associé n'a pas été déclenché. Les données lues sans événement associé sont considérées comme non déterministes et non fiables.
