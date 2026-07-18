---
name: os-windows-active-directory
description: "Concevoir et administrer un domaine Active Directory (AD DS), gérer les utilisateurs, les ordinateurs et les contrôleurs de domaine, configurer les Group Policy Objects (GPOs), et implémenter LDAP et Kerberos."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [windows, linux]
metadata:
  helios:
    tags: [active-directory, ad-ds, gpo, kerberos, ldap, windows-server, identity-management]
    related_skills: [os-windows-admin, os-linux-admin]
---

# Active Directory & Gestion des Identités (AD DS)

## Vue d'ensemble

Cette compétence guide la conception, le déploiement et l'administration d'infrastructures d'identité basées sur **Active Directory Domain Services (AD DS)**. Standard de facto en entreprise, AD DS centralise la gestion des utilisateurs, des ordinateurs, des droits d'accès et des politiques de sécurité à travers les **GPOs** (Group Policy Objects). Elle nécessite également la maîtrise des protocoles d'authentification associés : **Kerberos** (sécurisé, par tickets) et **LDAP/LDAPS** (requêtes d'annuaire).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Créer ou structurer des unités d'organisation (OU) pour organiser les objets d'un domaine.
- Configurer ou dépanner des stratégies de groupe (GPOs) applicables aux machines ou aux utilisateurs (ex: restriction d'exécution, configuration de proxy).
- Gérer l'authentification et l'intégration de machines Linux/Unix au domaine AD (via SSSD, Realmd ou Samba).
- Dépanner des problèmes de réplication Active Directory entre plusieurs contrôleurs de domaine (DC).
- Configurer des liaisons LDAPS (LDAP sur TLS sur port 636) sécurisées avec des serveurs tiers.

## Exemple d'Administration AD (PowerShell ActiveDirectory)

Exemple de script pour identifier les comptes d'utilisateurs inactifs depuis plus de 90 jours dans une Unité d'Organisation (OU) spécifique et désactiver ces comptes :

```powershell
Import-Module ActiveDirectory

# Paramètres
$TargetOU = "OU=Utilisateurs,OU=Actemium,DC=entreprise,DC=local"
$DaysInactive = 90
$CutoffDate = (Get-Date).AddDays(-$DaysInactive)

# Recherche des utilisateurs inactifs
$InactiveUsers = Get-ADUser -SearchBase $TargetOU -Filter {Enabled -eq $true} -Properties LastLogonDate | 
                 Where-Object { $_.LastLogonDate -lt $CutoffDate -and $_.LastLogonDate -ne $null }

# Désactivation et log
foreach ($User in $InactiveUsers) {
    Write-Host "Désactivation du compte inactif : $($User.UserPrincipalName) (Dernier logon : $($User.LastLogonDate))" -ForegroundColor Yellow
    # Désactiver le compte
    Disable-ADAccount -Identity $User.SID
}
```

## Protocoles d'authentification AD :
*   **Kerberos** : Protocole d'authentification par défaut dans un domaine AD (port 88 TCP/UDP). Il utilise un centre de distribution de clés (KDC) pour délivrer des tickets de session (TGT, TGS) assurant une authentification mutuelle forte.
*   **LDAP (TCP 389) / LDAPS (TCP 636)** : Protocole de requêtes d'annuaire permettant à des applications tierces (ex: GMAO, supervision) de lire les groupes d'utilisateurs pour les autorisations. *Recommandation* : Toujours utiliser le LDAPS chiffré.

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Ordre d'application des GPOs incorrect :**
   * *Erreur :* Déclarer des GPOs contradictoires sur l'OU parent et l'OU enfant, et ne pas comprendre pourquoi une politique de sécurité n'est pas appliquée sur une station.
   * *Correction :* Respecter l'ordre d'application par défaut (LSDOU : Local, Site, Domaine, OU). Une politique sur une OU enfant l'emporte sur l'OU parent, sauf si le paramètre "Appliquer" (Enforced) est coché sur le parent, ou si "Héritage bloqué" (Block Inheritance) est coché sur l'enfant.

2. **Désalignement temporel des horloges système :**
   * *Erreur :* Avoir un décalage de plus de 5 minutes entre l'horloge d'un poste client et le contrôleur de domaine AD. L'authentification Kerberos échouera systématiquement avec une erreur de sécurité.
   * *Correction :* Configurer un serveur NTP de référence unique sur le contrôleur de domaine principal (détenteur du rôle FSMO PDC Emulator) et synchroniser tous les postes clients et autres DCs sur celui-ci.

## Liste de vérification (Checklist)

- [ ] L'horloge de tous les serveurs et postes clients est synchronisée par NTP sur le contrôleur de domaine (tolérance Kerberos < 5 minutes).
- [ ] Les connexions LDAP provenant d'équipements tiers utilisent exclusivement LDAPS (port 636) ou la négociation StartTLS pour chiffrer les identifiants.
- [ ] L'outil `gpresult /h report.html` a été exécuté sur le poste client pour valider que les stratégies (GPOs) attendues sont bien appliquées.
- [ ] Les structures d'unités d'organisation (OU) séparent clairement les comptes d'utilisateurs, de serveurs, et de postes de travail.
- [ ] La santé de la réplication Active Directory est vérifiée à l'aide de l'outil en ligne de commande `repadmin /replsummary`.

