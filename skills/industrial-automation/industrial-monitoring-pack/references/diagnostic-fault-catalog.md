# Catalogue de défauts types pour monitoring industriel

## Défauts automate / CPU
- CPU en STOP
- watchdog / surcharge cycle
- mémoire insuffisante
- perte communication module I/O
- défaut carte réseau / module bus

### Signaux à suivre
- état CPU ;
- temps de cycle ;
- défaut général ;
- disponibilité réseau ;
- buffer diagnostic.

## Défauts communication
- timeout protocole
- perte endpoint OPC UA
- perte session EtherNet/IP
- port indisponible
- qualité de donnée mauvaise / incertaine

### Signaux à suivre
- état liaison ;
- nombre d'échecs ;
- qualité ;
- timestamp des derniers échanges ;
- nombre de reconnects.

## Défauts process / machine
- capteur incohérent
- actionneur bloqué
- température hors plage
- pression hors plage
- défaut permissif production

### Signaux à suivre
- analogiques critiques ;
- permissifs ;
- alarmes process ;
- durées d'état ;
- corrélation avant / après défaut.

## Défauts variateur / motion
- drive en fault
- surcharge courant
- surtempérature moteur
- défaut retour vitesse / position
- homing impossible

### Signaux à suivre
- état drive ;
- code défaut ;
- vitesse réelle ;
- courant / charge ;
- température ;
- statut homing.

## Défauts robot
- robot non prêt
- Busy sans CycleDone
- défaut robot récurrent
- reset répétés
- perte synchronisation PLC ↔ robot

### Signaux à suivre
- Ready / Busy / Fault / CycleDone ;
- FaultCode ;
- ResetRequired ;
- temps de cycle ;
- temps d'attente handshake.

## Usage recommandé
Ce catalogue sert de point de départ pour définir :
- quoi historiser ;
- quoi alerter ;
- quoi afficher dans un dashboard maintenance ;
- quoi investiguer en priorité lors d'un arrêt.
