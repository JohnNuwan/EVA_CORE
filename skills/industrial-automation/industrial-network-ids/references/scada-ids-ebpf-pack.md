# Systèmes de Détection d'Intrusions (IDS) SCADA et Filtrage eBPF

Ce document de référence décrit la mise en œuvre de sondes de sécurité industrielles basées sur l'analyse de données SCADA (OpenReview, 2025) et le filtrage noyau eBPF pour le protocole Modbus TCP (arXiv).

---

## 1. Vulnérabilités de Modbus TCP et Principes IDS

Le protocole Modbus TCP n'intègre nativement aucun mécanisme d'authentification ni de chiffrement. Un attaquant connecté au réseau local (niveau de contrôle de la norme ISA-62443) peut envoyer des trames directes pour forcer l'état des bobines physiques (`Coils`) ou réécrire des registres de consigne (`Holding Registers`).

### Détection d'Anomalies SCADA (Machine Learning)
Les IDS industriels modernes analysent les valeurs de registres lues périodiquement :
*   **Analyse de corrélation temporelle** : Des changements brusques ou incompatibles avec les lois physiques du procédé (ex. : une pression de cuve qui augmente sans activation de la pompe) signalent une injection de fausses données (False Data Injection Attack - FDIA).
*   **Modélisation d'états stables** : Des modèles de type forêt d'arbres décisionnels (Random Forest) ou auto-encodeurs entraînés sur un état stable détectent les dérives suspectes dans le comportement des registres.

---

## 2. Sécurisation au Niveau Noyau (eBPF / Express Data Path)

Pour pallier le manque de sécurité de Modbus TCP sans modifier le firmware des automates, nous pouvons déployer des filtres eBPF (Extended Berkeley Packet Filter) au sein des commutateurs ou des passerelles industrielles Linux placées en frontal des automates.

### Architecture de Filtrage eBPF
Les programmes eBPF s'exécutent directement dans le noyau Linux au passage des paquets réseau, éliminant le surcoût de transfert vers l'espace utilisateur.

```
       [ Trame Réseau Modbus TCP ]
                   │
                   ▼
       ┌────────────────────────┐
       │   Noyau Linux (eBPF)   │  <─── Profil de signatures (IPs SCADA permises)
       │  - Inspecte en-tête MBAP│
       │  - Vérifie Code Fonction│
       └───────────┬────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
    [ PASS / OK ]      [ DROP / BLOCK ]  (Si IP non autorisée ou FC d'écriture forcé)
```

### Signature eBPF pour Modbus TCP
Le filtre inspecte le port `502` et analyse la structure de la trame :
1.  **En-tête MBAP** (Modbus Application Protocol) :
    *   `Transaction Identifier` (2 octets)
    *   `Protocol Identifier` (2 octets, doit valoir `0` pour Modbus)
    *   `Length` (2 octets)
    *   `Unit Identifier` (1 octet)
2.  **Unité de Données PDU** (Protocol Data Unit) :
    *   `Function Code` (1 octet) : Les codes d'écriture (`05` - Write Single Coil, `06` - Write Single Register, `15` - Write Multiple Coils, `16` - Write Multiple Registers) doivent être bloqués s'ils ne proviennent pas de l'IP du SCADA légitime.

---

## 3. Exemple Conceptuel de Code de Filtre eBPF (C)

```c
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/tcp.h>

SEC("filter_modbus")
int block_unauthorized_modbus(struct __sk_buff *skb) {
    void *data = (void *)(long)skb->data;
    void *data_end = (void *)(long)skb->data_end;

    struct ethhdr *eth = data;
    if ((void *)eth + sizeof(*eth) > data_end)
        return BPF_OK;

    if (eth->h_proto != __constant_htons(ETH_P_IP))
        return BPF_OK;

    struct iphdr *ip = (void *)eth + sizeof(*eth);
    if ((void *)ip + sizeof(*ip) > data_end)
        return BPF_OK;

    if (ip->protocol != IPPROTO_TCP)
        return BPF_OK;

    struct tcphdr *tcp = (void *)ip + (ip->ihl * 4);
    if ((void *)tcp + sizeof(*tcp) > data_end)
        return BPF_OK;

    // Cible le port Modbus 502
    if (tcp->dest == __constant_htons(502)) {
        unsigned char *payload = (void *)tcp + (tcp->doff * 4);
        if (payload + 8 > (unsigned char *)data_end)
            return BPF_OK;

        // payload[7] correspond au Function Code (après l'en-tête MBAP de 7 octets)
        unsigned char function_code = payload[7];
        
        // Bloque l'écriture si l'IP source n'est pas celle du SCADA de confiance (ex: 192.168.1.10)
        if (ip->saddr != __constant_htonl(0xC0A8010A)) { // 192.168.1.10
            if (function_code == 5 || function_code == 6 || function_code == 15 || function_code == 16) {
                return BPF_DROP; // Bloque la trame d'écriture malveillante
            }
        }
    }
    return BPF_OK;
}
```
