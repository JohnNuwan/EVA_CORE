# Matrice causes probables → signaux à vérifier

| Symptôme | Causes probables | Signaux / points à vérifier | Première action |
|---|---|---|---|
| Machine à l'arrêt sans cause évidente | défaut automate, permissif absent, sécurité ouverte | état CPU, défaut général, permissifs, Safe, dernier défaut | reconstruire la chronologie |
| Temps de cycle dégradé | attente robot, attente amont/aval, dérive process, sous-vitesse drive | cycle time, Busy robot, cadence, vitesse drive, analogiques | comparer au nominal |
| Défaut intermittent | capteur instable, réseau, surchauffe, reset manuel répété | top défauts, qualité com, température, nombre resets | chercher répétitivité et contexte |
| Robot bloqué | handshake incomplet, périphérique, vision, trajectoire | Ready/Busy/Fault/CycleDone, FaultCode, temps attente PLC | isoler si attente PLC ou robot |
| Consommation énergie anormale | marche à vide, fuite, réglage process, moteur en surcharge | puissance, énergie/lot, état machine, courant drive | corréler avec production réelle |
| Communication instable | switch OT, port, endpoint, saturation polling | état liaison, nombre reconnects, timeout, charge collecte | réduire fréquence et valider réseau |

## Règle d'usage
Toujours partir d'un symptôme observable, puis croiser :
1. état machine ;
2. défauts ;
3. communication ;
4. analogiques ;
5. contexte robot / drive / énergie selon le cas.
