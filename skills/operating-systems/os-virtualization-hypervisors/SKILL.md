---
name: os-virtualization-hypervisors
description: "Déployer, configurer et optimiser des hyperviseurs de type 1 (Bare-metal) comme VMware ESXi, Proxmox VE (KVM/LXC) et Microsoft Hyper-V, allouer les ressources physiques et configurer le stockage réseau."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [hypervisor, virtualization, esxi, vmware, proxmox, kvm, hyper-v, storage, san, nas, network, system-ops]
  helios:
    related_skills: [os-linux-admin, os-windows-admin]
---

# Hyperviseurs et Virtualisation de type 1 (Bare-Metal)

## Vue d'ensemble

Cette compétence guide le déploiement, la configuration et l'optimisation d'infrastructures de virtualisation basées sur des hyperviseurs de type 1 (s'exécutant directement sur le matériel physique, dit *Bare-Metal*). Elle couvre les solutions majeures du marché : **VMware ESXi** (vSphere), **Proxmox VE** (KVM/LXC) et **Microsoft Hyper-V**. La virtualisation de type 1 assure le cloisonnement étanche des serveurs virtuels, le découpage optimal des ressources matérielles (processeurs, mémoire RAM, stockage, cartes réseau) et la mise en réseau via des commutateurs virtuels (vSwitches).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Installer ou configurer des machines virtuelles (VMs) et des conteneurs système (LXC).
- Allouer ou dimensionner les ressources physiques pour éviter la sur-allocation (Overcommit) critique.
- Configurer les interfaces réseau virtuelles (liaisons de cartes pour redondance/NIC Teaming, isolation par VLANs).
- Raccorder des hyperviseurs à des volumes de stockage réseau distants (**SAN/NAS** via protocoles iSCSI, NFS ou Fiber Channel).
- Mettre en place des mécanismes de haute disponibilité (HA, réplication, migration à chaud).

## Comparatif des Technologies d'Hyperviseur Type 1

| Solution | Technologie de Cœur | Type de Conteneurs | Console de Gestion | Rangement Stockage |
| :--- | :--- | :--- | :--- | :--- |
| **VMware ESXi** | Propriétaire (VMkernel) | VMs complètes | vSphere Client / vCenter | VMFS (Volume partagé VM) |
| **Proxmox VE** | Linux KVM | VMs & conteneurs LXC | Interface Web intégrée | ZFS, Ceph, LVM-Thin, NFS |
| **Hyper-V** | Windows Hypervisor | VMs Windows/Linux | Hyper-V Manager / SCVMM | VHDX / CSV (Clustered Shared Vol) |

### Concepts d'allocation de ressources :
- **vCPU** : Cœur de processeur virtuel attribué à la VM. Éviter d'attribuer plus de vCPUs à une seule VM que le nombre de cœurs physiques réels disponibles sur le serveur (sans hyperthreading) sous peine de subir des latences d'ordonnancement élevées (CPU Ready Time).
- **Sur-allocation (Overcommit)** : Allouer plus de RAM ou de CPU à l'ensemble des VMs que la capacité réelle du serveur physique. Très dangereux pour la RAM car cela provoque de l'échange (swapping) sur disque, écrasant les performances.

## Gestion des Commutateurs Virtuels (vSwitches)

Les hyperviseurs utilisent des commutateurs virtuels pour relier les cartes réseau physiques (pNICs) aux cartes réseau virtuelles (vNICs) des VMs :

```text
    [ Machine Virtuelle 1 ]      [ Machine Virtuelle 2 ]
             │ (vNIC)                     │ (vNIC)
             └──────────────┬─────────────┘
                            ▼
                ┌───────────────────────┐
                │  Commutateur Virtuel  │ (vSwitch / Port Group)
                │ (Gestion des VLANs)   │
                └───────────┬───────────┘
                            ▼
                ┌───────────────────────┐
                │   Agrégation LACP     │ (NIC Teaming / Bond)
                └───────┬───────┬───────┘
                        │(pNIC) │(pNIC)
                        ▼       ▼
               [ Commutateurs Physiques ]
```

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Sur-allocation massive de RAM :**
   * *Erreur :* Assigner 32 Go de RAM à 4 machines virtuelles sur un serveur physique qui ne possède que 96 Go de RAM de capacité réelle. Dès que les VMs utiliseront leur mémoire, l'hyperviseur commencera à swapper sur son disque local, effondrant les performances de tout le serveur.
   * *Correction :* Réserver de la RAM physique pour l'hyperviseur lui-même (garder 4 à 8 Go libres) et n'utiliser la sur-allocation de mémoire qu'avec des technologies de ballooning et uniquement pour des VMs non critiques.

2. **Perte de redondance réseau par manque de séparation physique :**
   * *Erreur :* Associer l'interface de gestion de l'hyperviseur et le réseau de données de production sur un seul commutateur virtuel relié à une seule carte réseau physique. Si le câble réseau se débranche, le serveur est totalement isolé.
   * *Correction :* Utiliser au moins deux cartes réseau physiques en mode agrégation (LACP / Active-Backup) branchées sur deux commutateurs physiques séparés en amont pour éviter tout point de défaillance unique (SPOF).

## Liste de vérification (Checklist)

- [ ] L'ordonnancement CPU (CPU Ready Time) est surveillé et reste inférieur à 5% par VM pour éviter les temps d'attente d'accès au processeur.
- [ ] La mémoire RAM globale allouée ne dépasse pas 90% de la RAM physique de l'hôte afin de préserver l'hyperviseur.
- [ ] Les connexions de stockage SAN (iSCSI, FC) utilisent le multipathing (MPIO) pour garantir la continuité d'accès en cas de coupure d'un câble ou d'un switch de stockage.
- [ ] Le trafic d'administration (Management) et de migration de VMs (vMotion) est isolé sur des VLANs dédiés non accessibles depuis les réseaux d'utilisateurs.

