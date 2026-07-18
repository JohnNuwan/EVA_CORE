---
name: os-windows-admin
description: "Administrer les serveurs Windows (Windows Server), configurer les rôles standards (IIS, DHCP, DNS), manipuler la base de registre et automatiser les tâches d'administration via des scripts PowerShell."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [windows]
metadata:
  helios:
    tags: [windows, windows-server, powershell, administration, iis, dhcp, registry, systems-ops]
    related_skills: [os-windows-active-directory]
---

# Administration Windows Server & PowerShell

## Vue d'ensemble

Cette compétence guide l'administration système de serveurs et stations Windows (Windows Server 2019/2022 et Windows 10/11) dans un contexte professionnel. Elle couvre la configuration des rôles réseau (serveurs web IIS, DHCP, DNS), la manipulation de la base de registre pour les configurations système, et l'utilisation de **PowerShell** comme outil principal d'automatisation des tâches récurrentes.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Installer ou configurer des services IIS (Internet Information Services), DHCP ou DNS sous Windows Server.
- Rédiger des scripts PowerShell pour auditer les disques, gérer les services locaux ou créer des utilisateurs.
- Modifier des clés de registre Windows de manière sécurisée (HKLM / HKCU).
- Analyser des journaux d'événements Windows (Event Viewer) pour résoudre des pannes système ou de démarrage.

## Exemple d'Automatisation (Script PowerShell standard)

Voici un script d'audit des services Windows locaux critiques, configurés en démarrage automatique mais actuellement arrêtés, avec redémarrage automatique :

```powershell
# Définir les services critiques à surveiller
$CriticalServices = @("wuauserv", "LanmanServer", "Spooler")

foreach ($ServiceName in $CriticalServices) {
    $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    
    if ($Service) {
        if ($Service.Status -ne "Running") {
            Write-Warning "Le service critique $($Service.DisplayName) ($ServiceName) est arrêté. Tentative de démarrage..."
            Start-Service -Name $ServiceName
            
            # Vérification après démarrage
            $UpdatedStatus = (Get-Service -Name $ServiceName).Status
            Write-Host "Nouveau statut pour $ServiceName : $UpdatedStatus" -ForegroundColor Green
        } else {
            Write-Host "Le service $ServiceName fonctionne correctement." -ForegroundColor Green
        }
    } else {
        Write-Error "Le service $ServiceName n'est pas installé sur ce système."
    }
}
```

### Commandes utiles en base de registre (PowerShell) :
- **Lire une clé** : `Get-ItemProperty -Path "HKLM:\Software\Policies\Microsoft\Windows\WindowsUpdate"`
- **Écrire/Créer une clé** : `New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name "LimitBlankPasswordUse" -Value 1 -PropertyType DWord -Force`

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Scripts bloqués par la politique d'exécution (Execution Policy) :**
   * *Erreur :* Lancer un script PowerShell nouvellement créé et recevoir une erreur `UnauthorizedAccess` due à la politique par défaut `Restricted`.
   * *Correction :* Modifier temporairement la politique lors du lancement avec `powershell.exe -ExecutionPolicy Bypass -File .\script.ps1`, ou la configurer au niveau de l'utilisateur avec `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.

2. **Écritures de registre destructrices :**
   * *Erreur :* Modifier une clé de registre sans sauvegarde ou supprimer récursivement une branche critique de `HKLM:\System\CurrentControlSet`, rendant Windows non démarrable (BSOD).
   * *Correction :* Toujours exporter la clé dans un fichier `.reg` avant modification, ou utiliser l'option `-WhatIf` de PowerShell pour prévisualiser l'impact de la commande.

## Liste de vérification (Checklist)

- [ ] L'Execution Policy appropriée est configurée pour permettre l'exécution des scripts d'administration.
- [ ] Les scripts testent systématiquement l'existence des rôles ou services avant de tenter de les manipuler.
- [ ] Toutes les modifications de registre critiques sont précédées d'une commande de sauvegarde ou d'un bloc de secours.
- [ ] Les flux d'erreurs PowerShell (`Try-Catch` avec `-ErrorAction Stop`) sont utilisés pour intercepter les échecs de privilèges insuffisants.

